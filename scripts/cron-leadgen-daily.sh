#!/bin/bash
# Cron wrapper: daily lead generation (scripts over agents)
set -euo pipefail
LEADGEN="$HOME/.openclaw/workspace/leadgen"
LOG="$LEADGEN/logs/openclaw-cron-daily.log"
mkdir -p "$LEADGEN/logs"
{
  echo "=== $(date -u +"%Y-%m-%dT%H:%M:%SZ") leadgen daily ==="
  cd "$LEADGEN" && bash scripts/run-daily-leads.sh
  echo "=== done ==="
} >> "$LOG" 2>&1
tail -30 "$LOG"
