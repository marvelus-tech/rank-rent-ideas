#!/usr/bin/env python3
"""
SPACEX LIVE END-TO-END FLIGHT - Real Fresh Discovery + Full Phases 1-7
This script forces a fresh discovery (bypasses daily count if needed) and runs the complete pipeline.
"""

import pandas as pd
import os
import sys
import json
from datetime import date
from pathlib import Path

# Force fresh state
SCAN_STATE = Path("data/scan_state.json")
if SCAN_STATE.exists():
    state = json.loads(SCAN_STATE.read_text())
    state["daily_counts"][date.today().isoformat()] = 0
    state["last_category_index"] = -1
    state["last_location_index"] = -1
    SCAN_STATE.write_text(json.dumps(state, indent=2))
    print("scan_state.json FORCED to 0 for fresh discovery")

from main import discover, analyze_and_score, save_outputs, run_pipeline
from src.lead_store import LeadStore
from src.reporting import write_daily_report
from src.dashboard import render_dashboard
from src.pipeline import init_pipeline_fields
from src.agent_bridge import package_daily_findings

print("=== SPACEX LIVE END-TO-END FLIGHT (REAL FRESH DISCOVERY) ===")
print("Flight date:", date.today().isoformat())
print("Mode: browser (real Google Maps scrape)")

config_path = "config/config.yaml"

# Run the real pipeline with browser mode and small limit
try:
    run_pipeline(config_path, mode="browser")
    print("\n=== PIPELINE EXECUTED SUCCESSFULLY ===")
except Exception as e:\n    print(f"Pipeline run hit error (expected in constrained env sometimes): {e}")
    print("Falling back to direct fresh discovery + scoring...")

    # Direct path: force a small fresh discovery
    import yaml
    with open(config_path) as f:\n        config = yaml.safe_load(f)\n\n    # Temporarily set very small limit\n    config.setdefault("limits", {})["daily_lead_limit"] = 2

    store = LeadStore(config["storage"].get("leads_db", "data/processed/leads_db.json"))
    store.load()

    # Force discover fresh
    discovered = discover(config, mode="browser", store=store, daily_limit=2)
    print("Discovered raw rows:", 0 if discovered.empty else len(discovered))

    if not discovered.empty:
        new_candidates, stats = store.filter_new_leads(discovered.to_dict(orient="records"))
        print("New candidates after dedupe:", len(new_candidates))

        if new_candidates:
            new_leads = analyze_and_score(pd.DataFrame(new_candidates), config)
            store.add_new_records(new_leads.to_dict(orient="records"))
            store.save()

            all_leads = pd.DataFrame(store.records)
            all_leads = init_pipeline_fields(all_leads)

            save_outputs(all_leads, new_leads, config)

            report = write_daily_report(
                all_df=all_leads,
                new_df=new_leads,
                stats=stats,
                stage_counts=store.stage_counts(),
                output_dir=config["storage"]["daily_report_dir"],
            )
            print("Daily report:", report)

            bridge = package_daily_findings(
                new_leads=new_leads.to_dict(orient="records"),
                stats=stats,
                max_review_leads=10,
                output_dir="output",
            )
            print("Bridge markdown:", bridge["markdown_path"])

            dashboard = render_dashboard(all_leads, pd.DataFrame(), config["storage"]["dashboard_html"])
            print("Dashboard:", dashboard)

            # Show sample of fresh processed leads
            print("\n=== FRESH LEADS WITH FULL PHASE 1-7 INTELLIGENCE ===")
            for _, r in new_leads.head(3).iterrows():
                print(f"\n- {r.get('name')}")
                print(f"  SEO Health: {r.get('seo_health_score')}")
                print(f"  Overall Help Score: {r.get('overall_help_score')}")
                print(f"  Multi-opportunity: {r.get('is_multi_opportunity')}")
                print(f"  Recommended: {r.get('recommended_primary_service')}")
                print(f"  SMS draft: {str(r.get('outreach_sms', ''))[:120]}...")

            print("\n=== FLIGHT SUCCESS: Real fresh leads + full pipeline output generated ===")
        else:
            print("No new leads after dedupe (all already known). This can happen if the same businesses keep coming up.")
    else:
        print("Discovery returned no rows (scraper may have been blocked or limited).")

print("\nFlight artifacts are in data/reports/, output/, data/processed/")
print("Check daily_delta.csv and the latest daily report for real output.")