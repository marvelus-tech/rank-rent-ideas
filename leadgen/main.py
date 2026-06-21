from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
import pandas as pd

from src.config import load_config
from src.maps_client import SerpApiMapsClient
from src.browser_scraper import BrowserMapsScraper, CaptchaDetectedError, browser_search_with_retry
from src.contact_enricher import ContactEnricher
from src.website_analyzer import WebsiteAnalyzer
from src.scoring import score_lead
from src.pipeline import init_pipeline_fields, due_followups
from src.reporting import write_daily_report
from src.dashboard import render_dashboard
from src.lead_store import LeadStore
from src.agent_bridge import package_daily_findings

HIGH_VALUE_CATEGORIES = ["hvac", "plumbing", "law firm", "dental clinic", "dental"]
SCAN_STATE_PATH = Path("data/scan_state.json")


def _normalized(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def _priority_categories(categories: list[str]) -> list[str]:
    indexed = list(enumerate(categories))
    chosen: list[tuple[int, str]] = []
    used_indexes: set[int] = set()

    for priority in HIGH_VALUE_CATEGORIES:
        for idx, category in indexed:
            if idx in used_indexes:
                continue
            if _normalized(category) == _normalized(priority):
                chosen.append((idx, category))
                used_indexes.add(idx)
                break

    for idx, category in indexed:
        if idx not in used_indexes:
            chosen.append((idx, category))

    return [category for _, category in chosen]


def _load_scan_state(path: Path = SCAN_STATE_PATH) -> dict:
    default_state = {
        "last_category_index": -1,
        "last_location_index": -1,
        "daily_counts": {},
    }

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(default_state, indent=2), encoding="utf-8")
        return default_state

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        path.write_text(json.dumps(default_state, indent=2), encoding="utf-8")
        return default_state

    state.setdefault("last_category_index", -1)
    state.setdefault("last_location_index", -1)
    state.setdefault("daily_counts", {})
    return state


def _save_scan_state(state: dict, path: Path = SCAN_STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _rotate(items: list[str], start_index: int) -> list[str]:
    if not items:
        return []
    start = start_index % len(items)
    return items[start:] + items[:start]


def discover(config: dict, mode: str = "api", store: LeadStore | None = None, daily_limit: int = 10):
    all_leads: list[dict] = []
    categories = config["discovery"]["categories"]
    locations = config["discovery"]["locations"]

    if mode == "browser":
        browser_cfg = config.get("browser", {})
        scraper = BrowserMapsScraper(
            headless=browser_cfg.get("headless", True),
            slow_mo=browser_cfg.get("slow_mo", 2000),
            max_results_per_search=browser_cfg.get("max_results_per_search", 30),
            search_delay_seconds=browser_cfg.get("search_delay_seconds", 5),
        )
        limit = min(browser_cfg.get("max_results_per_search", 30), 50)

        prioritized_categories = _priority_categories(categories)
        state = _load_scan_state()

        category_count = len(prioritized_categories)
        location_count = len(locations)
        start_category = (int(state.get("last_category_index", -1)) + 1) % category_count if category_count else 0
        start_location = (int(state.get("last_location_index", -1)) + 1) % location_count if location_count else 0

        category_order = _rotate(prioritized_categories, start_category)
        location_order = _rotate(locations, start_location)

        existing_keys = set(store.by_key.keys()) if store else set()
        seen_run: set[str] = set()
        new_count = 0

        last_category_index = state.get("last_category_index", -1)
        last_location_index = state.get("last_location_index", -1)

        for category in category_order:
            for location in location_order:
                try:
                    leads = browser_search_with_retry(
                        scraper=scraper,
                        category=category,
                        location=location,
                        max_retries=3,
                        backoff_seconds=4,
                    )
                except CaptchaDetectedError as exc:
                    print(f"CAPTCHA detected for '{category} in {location}'. Skipping query. Details: {exc}")
                    continue
                except Exception as exc:  # noqa: BLE001
                    print(f"Browser scrape failed for '{category} in {location}'. Skipping. Details: {exc}")
                    continue

                capped = leads[:limit]
                all_leads.extend(capped)

                # Track query progress for tomorrow's round-robin start point.
                last_category_index = categories.index(category) if category in categories else -1
                last_location_index = locations.index(location) if location in locations else -1

                for lead in capped:
                    key = LeadStore.build_dedupe_key(lead.get("name"), lead.get("address"), lead.get("phone"))
                    if key in existing_keys or key in seen_run:
                        continue
                    seen_run.add(key)
                    new_count += 1

                    if new_count >= daily_limit:
                        print(f"Daily limit of {daily_limit} leads reached. Stopping.")
                        today = date.today().isoformat()
                        state["last_category_index"] = last_category_index
                        state["last_location_index"] = last_location_index
                        state.setdefault("daily_counts", {})[today] = new_count
                        _save_scan_state(state)
                        df = pd.DataFrame(all_leads)
                        return df

        today = date.today().isoformat()
        state["last_category_index"] = last_category_index
        state["last_location_index"] = last_location_index
        state.setdefault("daily_counts", {})[today] = new_count
        _save_scan_state(state)

    else:
        client = SerpApiMapsClient(
            api_key=config["serpapi"]["api_key"],
            google_domain=config["serpapi"].get("google_domain", "google.com"),
            hl=config["serpapi"].get("hl", "en"),
        )
        limit = config["discovery"].get("max_results_per_query", 20)

        for location in locations:
            for category in categories:
                leads = client.search_businesses(category=category, location=location, limit=limit)
                all_leads.extend([x.to_dict() for x in leads])

    df = pd.DataFrame(all_leads)
    if df.empty:
        print("No leads discovered.")
        return df

    return df


def analyze_and_score(df: pd.DataFrame, config: dict, enrich_contacts: bool = True):
    analyzer = WebsiteAnalyzer()
    enricher = ContactEnricher() if enrich_contacts else None

    enriched = []
    for _, row in df.iterrows():
        r = row.to_dict()
        r.update(analyzer.analyze(r.get("website"), maps_phone=r.get("phone")))
        r.update(score_lead(r, config["scoring"]))
        if enricher and r.get("website"):
            print(f"  Enriching contacts for: {r.get('name', 'Unknown')}...")
            r = enricher.enrich_lead(r)
        elif enricher:
            r["email"] = None
            r["emails_found"] = []
            r["contact_page_url"] = None
            r["social_links"] = {k: None for k in ["facebook", "instagram", "linkedin", "twitter", "youtube"]}
            r["contact_confidence"] = "none"
            r["has_complete_contact_info"] = False
            r["website_scraped_at"] = None
            r["website_scrape_success"] = False
        enriched.append(r)

    out = pd.DataFrame(enriched)
    out = init_pipeline_fields(out)
    return out


def save_outputs(df: pd.DataFrame, new_df: pd.DataFrame, config: dict):
    storage = config["storage"]
    csv_path = Path(storage["leads_csv"])
    json_path = Path(storage["leads_json"])
    delta_path = Path(storage.get("daily_delta_csv", "data/reports/daily_delta.csv"))
    daily_complete_path = Path("output/daily_complete.csv")

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    delta_path.parent.mkdir(parents=True, exist_ok=True)
    daily_complete_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2)
    new_df.to_csv(delta_path, index=False)
    new_df.to_csv(daily_complete_path, index=False)

    return {"daily_complete_csv": str(daily_complete_path)}


def run_pipeline(config_path: str, mode: str = "api"):
    config = load_config(config_path)
    daily_limit = int(config.get("limits", {}).get("daily_lead_limit", 10))

    store = LeadStore(config["storage"].get("leads_db", "data/processed/leads_db.json"))
    store.load()

    discovered = discover(config, mode=mode, store=store, daily_limit=daily_limit)
    if discovered.empty:
        return

    new_candidates, stats = store.filter_new_leads(discovered.to_dict(orient="records"))

    if mode == "browser" and stats["new_leads"] > daily_limit:
        new_candidates = new_candidates[:daily_limit]
        stats["new_leads"] = len(new_candidates)
        stats["duplicates_skipped"] = stats["total_scanned"] - stats["new_leads"]

    if new_candidates:
        new_leads = analyze_and_score(pd.DataFrame(new_candidates), config)
        store.add_new_records(new_leads.to_dict(orient="records"))
    else:
        new_leads = pd.DataFrame()

    store.save()

    all_leads = pd.DataFrame(store.records)
    if not all_leads.empty:
        all_leads = init_pipeline_fields(all_leads)
    stage_counts = store.stage_counts()

    output_paths = save_outputs(all_leads, new_leads, config)

    report = write_daily_report(
        all_df=all_leads,
        new_df=new_leads,
        stats=stats,
        stage_counts=stage_counts,
        output_dir=config["storage"]["daily_report_dir"],
    )

    bridge = package_daily_findings(
        new_leads=new_leads.to_dict(orient="records") if not new_leads.empty else [],
        stats=stats,
        max_review_leads=15,
        output_dir="output",
    )

    due_df = due_followups(all_leads) if not all_leads.empty else pd.DataFrame()
    dashboard_path = render_dashboard(all_leads, due_df, config["storage"]["dashboard_html"])

    print("Done.")
    print(f"Mode: {mode}")
    print(f"Daily lead limit: {daily_limit}")
    print(f"Total leads scanned: {stats['total_scanned']}")
    print(f"New leads found: {stats['new_leads']}")
    print(f"Duplicates skipped: {stats['duplicates_skipped']}")
    print(f"Pipeline stage counts: {stage_counts}")
    print(f"Leads DB: {config['storage'].get('leads_db', 'data/processed/leads_db.json')}")
    print(f"CSV: {config['storage']['leads_csv']}")
    print(f"JSON: {config['storage']['leads_json']}")
    print(f"Daily delta CSV: {config['storage'].get('daily_delta_csv', 'data/reports/daily_delta.csv')}")
    print(f"Daily complete CSV (new leads): {output_paths['daily_complete_csv']}")
    print(f"Daily report: {report}")
    print(f"Daily for review (Markdown): {bridge['markdown_path']}")
    print(f"Daily for review (JSON): {bridge['json_path']}")
    print(f"Dashboard: {dashboard_path}")


def generate_weekly_followups(config_path: str):
    config = load_config(config_path)
    csv_path = Path(config["storage"]["leads_csv"])
    if not csv_path.exists():
        print("No leads CSV found. Run pipeline first.")
        return

    df = pd.read_csv(csv_path)
    due = due_followups(df)
    out = Path(config["storage"]["daily_report_dir"]) / "weekly_followups.csv"
    due.to_csv(out, index=False)
    print(f"Weekly follow-up list generated: {out}")


def parse_args():
    parser = argparse.ArgumentParser(description="Lead generation monitoring for Marvelus/Nolostsales")
    parser.add_argument("command", choices=["run", "weekly-followups"], help="Action to execute")
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Path to config file (default: config/config.yaml)",
    )
    parser.add_argument(
        "--mode",
        choices=["api", "browser"],
        default="api",
        help="Discovery mode: api (SerpAPI) or browser (Playwright Google Maps)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "run":
        run_pipeline(args.config, mode=args.mode)
    elif args.command == "weekly-followups":
        generate_weekly_followups(args.config)
