#!/usr/bin/env python3
"""
SPACEX MISSION: Execute full pipeline on fresh leads.
Phases 1 (website/SEO analysis) + 2 (multi-dimensional scoring) + 7 (outreach generation).
Deterministic execution with full telemetry.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

import pandas as pd
import yaml
from datetime import date

from main import analyze_and_score

print("=" * 72)
print("SPACEX - FULL PIPELINE EXECUTION")
print("Date:", date.today().isoformat())
print("Target: Fresh med spa leads from daily_delta.csv")
print("=" * 72)

df = pd.read_csv("data/reports/daily_delta.csv")
print(f"[DATA] Fresh leads loaded: {len(df)}")

batch = df.head(4).copy()
print(f"[EXEC] Running full pipeline (Phases 1+2+7) on {len(batch)} leads...\n")

config = yaml.safe_load(open("config/config.yaml"))

processed = analyze_and_score(batch, config)

print("\n[TELEMETRY] Full pipeline complete. Rows processed:", len(processed))

print("\n=== EVIDENCE: Full intelligence applied ===")
for i, row in processed.iterrows():
    print("")
    print(str(i+1) + ". " + str(row["name"]))
    print("   SEO Health Score     : " + str(row.get("seo_health_score")))
    print("   Overall Help Score   : " + str(row.get("overall_help_score")))
    print("   Is Multi-opportunity : " + str(row.get("is_multi_opportunity")))
    print("   Recommended Service  : " + str(row.get("recommended_primary_service")))
    print("   Priority             : " + str(row.get("priority")))
    sms = str(row.get("outreach_sms", ""))[:85].replace("\n", " ")
    print("   Outreach SMS         : " + sms + "...")

processed.to_csv("output/spacex_flight_complete.csv", index=False)

print("\n" + "=" * 72)
print("[ARTIFACT] output/spacex_flight_complete.csv")
print("=== MISSION COMPLETE ===")
print("Full pipeline executed. SpaceX-grade precision.")
print("=" * 72)
