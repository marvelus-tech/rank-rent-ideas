#!/bin/bash
# Cron wrapper: daily lead generation (scripts over agents)
set -euo pipefail
LEADGEN="$HOME/.openclaw/workspace/leadgen"
LOG="$LEADGEN/logs/openclaw-cron-daily.log"
mkdir -p "$LEADGEN/logs"

# Run and capture only the summary line
SUMMARY=$(cd "$LEADGEN" && bash scripts/run-daily-leads.sh 2>&1 | tail -1)

# Log timestamp + summary
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") | $SUMMARY" >> "$LOG"

# Output just the summary to Telegram (1 line)
echo "$SUMMARY"
