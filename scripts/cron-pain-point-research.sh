#!/bin/bash
# Cron wrapper: pain point research pipeline
set -euo pipefail
WS="$HOME/.openclaw/workspace"
LOG="/tmp/pain-point-research-cron.log"
{
  echo "▶ $(date -u +"%Y-%m-%dT%H:%M:%SZ") pain point research"
  bash "$WS/scripts/pain-point-research.sh"
  echo "✓ done"
} | tee "$LOG"

# Rich formatted summary for Telegram
echo "🔍 *Pain Point Research*

📊 *Weekly Update*
• New opportunities analyzed
• Report generated

🔗 [View Report](https://marvelus-tech.github.io/rank-rent-ideas/pain-point-research.html)"
