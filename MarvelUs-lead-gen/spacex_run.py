#!/usr/bin/env python3
"""SPACEX: Execute full pipeline on fresh leads.
Phases: 1 (analyze), 2 (score), 7 (outreach).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))

import pandas as pd
import yaml
from datetime import date

from website_analyzer import WebsiteAnalyzer
from multi_dimensional_scorer import score_lead_multi
from outreach_generator import generate_outreach_drafts
from lead_store import LeadStore
from pipeline import init_pipeline_fields
from reporting import write_daily_report
from dashboard import render_dashboard
from agent_bridge import package_daily_findings

print("=" * 70)
print("SPACEX MISSION CONTROL - FULL PIPELINE")
print("Date:", date.today().isoformat())
print("=" * 70)

df = pd.read_csv("data/reports/daily_delta.csv")
print(f"[DATA] Fresh leads discovered: {len(df)}")

batch = df.head(4).copy()
print(f"[EXEC] Applying Phases 1 + 2 + 7 to {len(batch)} leads\n")

with open("config/config.yaml") as f:\n    config = yaml.safe_load(f)\n\nif "outreach" not in config:
    config["outreach"] = {}
if "templates" not in config["outreach"]:
    config["outreach"]["templates"] = {}
tpls = config["outreach"]["templates"]
if "sms" not in tpls:
    tpls["sms"] = {
        "full_stack": "Hi {name_short}, I help {category} in {location} with AI receptionist + website/SEO. Open to 10-min chat?",
        "ai_voice": "Hi {name_short}, natural AI receptionist for {category} in {location}. 10-min chat?"
    }
if "email_subject" not in tpls:
    tpls["email_subject"] = {"full_stack": "AI + website for {name}", "ai_voice": "AI receptionist for {category}"}
if "email_body" not in tpls:
    tpls["email_body"] = {
        "full_stack": "Hi {name},\n\nHelp for {category} in {location}.\n\nMarvelus",
        "ai_voice": "Hi {name},\n\nAI voice for {category} in {location}.\n\nMarvelus"
    }

analyzer = WebsiteAnalyzer()
processed = []

for i, (_, row) in enumerate(batch.iterrows()):
    r = row.to_dict()
    name = str(r.get("name", "Unknown"))[:45]
    print(f"  [{i+1}/{len(batch)}] {name}")

    for k in ["reviews", "rating", "lead_score", "tech_sophistication_score", "seo_health_score"]:
        if pd.isna(r.get(k)):
            r[k] = 0
    r["reviews"] = int(r.get("reviews") or 0)

    # Phase 1
    try:
        a = analyzer.analyze(r.get("website"), maps_phone=str(r.get("phone") or ""), config=config)
        r.update(a)
        print(f"       Phase1 seo={r.get('seo_health_score')}")
    except Exception as e:\n        print(f"       Phase1: {e}")

    # Phase 2
    try:
        if config.get("features", {}).get("enable_multi_dimensional_scoring", True):
            s = score_lead_multi(r, config)
            r.update(s)
            print(f"       Phase2 overall={r.get('overall_help_score')} rec={r.get('recommended_primary_service')}")
    except Exception as e:\n        print(f"       Phase2: {e}")

    # Phase 7
    try:
        d = generate_outreach_drafts(r, config)
        r.update(d)
        print(f"       Phase7 outreach ready")
    except Exception as e:\n        print(f"       Phase7: {e}")

    processed.append(r)

new_df = pd.DataFrame(processed)
print(f"\n[OK] Pipeline complete on {len(new_df)} leads")

store = LeadStore(config["storage"].get("leads_db", "data/processed/leads_db.json"))
store.load()
store.add_new_records(new_df.to_dict(orient="records"))
store.save()

all_leads = pd.DataFrame(store.records)
if not all_leads.empty:
    all_leads = init_pipeline_fields(all_leads)

storage = config["storage"]
all_leads.to_csv(storage["leads_csv"], index=False)
new_df.to_csv("output/daily_complete.csv", index=False)

stats = {"total_scanned": len(df), "new_leads": len(new_df), "duplicates_skipped": len(df) - len(new_df)}
stage_counts = store.stage_counts()

report_path = write_daily_report(all_df=all_leads, new_df=new_df, stats=stats, stage_counts=stage_counts, output_dir=storage["daily_report_dir"])
bridge = package_daily_findings(new_leads=new_df.to_dict(orient="records"), stats=stats, max_review_leads=10, output_dir="output")
dash = render_dashboard(all_leads, pd.DataFrame(), storage["dashboard_html"])

print("\n" + "=" * 70)
print("TELEMETRY")
print("Report   :", report_path)
print("Bridge   :", bridge.get("markdown_path"))
print("Dashboard:", dash)
print("CSV      : output/daily_complete.csv")

print("\n=== PROCESSED LEADS (full intelligence) ===")
for i, r in enumerate(processed):
    print(f"\n{i+1}. {r.get('name')}")
    print(f"   SEO: {r.get('seo_health_score')} | Overall: {r.get('overall_help_score')} | Multi: {r.get('is_multi_opportunity')}")
    print(f"   Primary: {r.get('recommended_primary_service')}")
    print(f"   SMS: {str(r.get('outreach_sms', ''))[:70]}")

print("\n" + "=" * 70)
print("MISSION COMPLETE")
print("=" * 70)
