#!/bin/bash
# Cron wrapper: Rank & Rent weekly pipeline
set -euo pipefail
SKILL="$HOME/.openclaw/workspace/skills/rr-niche-finder"
LOG="/tmp/weekly-niche-batch-cron.log"
{
  echo "▶ $(date -u +"%Y-%m-%dT%H:%M:%SZ") weekly niche batch"
  cd "$SKILL" && python3 scripts/weekly-pipeline.py
  echo "✓ done"
} | tee "$LOG"
tail -40 "$LOG"
