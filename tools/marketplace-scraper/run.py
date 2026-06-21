from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

from scraper.alerter import OpportunityAlerter
from scraper.marketplace_scraper import FacebookMarketplaceScraper
from scraper.price_analyzer import PriceAnalyzer


def expand_env(value: Any):
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, dict):
        return {k: expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_env(v) for v in value]
    return value


def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return expand_env(cfg)


def main():
    base_dir = Path(__file__).resolve().parent
    load_dotenv(base_dir / ".env")

    cfg = load_config(base_dir / "config.yaml")
    scraper = FacebookMarketplaceScraper(cfg)
    analyzer = PriceAnalyzer(cfg)
    alerter = OpportunityAlerter(cfg)

    all_listings = []
    for search in cfg.get("searches", []):
        keyword = search["keyword"]
        location = search.get("location", "")
        category = search.get("category", "default")
        max_listings = int(search.get("max_listings", 20))

        print(f"[run] Searching keyword='{keyword}', location='{location}', max={max_listings}")
        listings = scraper.search(keyword=keyword, location=location, max_listings=max_listings, category=category)
        print(f"[run] Found {len(listings)} listings")
        all_listings.extend(listings)

    output_dir = cfg.get("output", {}).get("directory", "output")
    prefix = cfg.get("output", {}).get("file_prefix", "marketplace_results")

    saved = scraper.save_results(all_listings, out_dir=base_dir / output_dir, base_name=prefix)
    print(f"[run] Saved raw listings: {saved}")

    analyzed = analyzer.analyze(all_listings)
    opportunities = analyzer.top_opportunities(analyzed, limit=20)
    alert_result = alerter.send(opportunities)

    analyzed_path = base_dir / output_dir / f"{prefix}_analyzed.json"
    analyzed_path.parent.mkdir(parents=True, exist_ok=True)
    import json

    with open(analyzed_path, "w", encoding="utf-8") as f:
        json.dump(analyzed, f, indent=2, ensure_ascii=False)

    print(f"[run] Analyzed listings saved to {analyzed_path}")
    print(f"[run] Opportunities flagged: {len(opportunities)} | Alerts: {alert_result}")


if __name__ == "__main__":
    main()
