#!/bin/bash
# Cron wrapper: pain point research pipeline
set -euo pipefail
WS="$HOME/.openclaw/workspace"
LOG="/tmp/pain-point-research-cron.log"
{
  echo "=== $(date -u +"%Y-%m-%dT%H:%M:%SZ") pain point research ==="
  bash "$WS/scripts/pain-point-research.sh"
  echo "Report: $WS/pain-point-research.html"
  echo "=== done ==="
} | tee "$LOG"
tail -20 "$LOG"
