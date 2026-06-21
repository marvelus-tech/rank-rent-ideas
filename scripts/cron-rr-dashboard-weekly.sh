#!/bin/bash
# Cron wrapper: RR dashboard git push (pipeline + commit)
set -euo pipefail
SKILL="$HOME/.openclaw/workspace/skills/rr-niche-finder"
WS="$HOME/.openclaw/workspace"
LOG="/tmp/rr-dashboard-cron.log"
{
  echo "▶ $(date -u +"%Y-%m-%dT%H:%M:%SZ") rr dashboard weekly"
  cd "$SKILL" && python3 scripts/weekly-pipeline.py
  cd "$WS"
  if git rev-parse --git-dir >/dev/null 2>&1; then
    git add skills/rr-niche-finder/dashboard.html skills/rr-niche-finder/data/all-batches.json 2>/dev/null || true
    if git diff --cached --quiet; then
      echo "ℹ️ No dashboard changes to commit."
    else
      git commit -m "Weekly RR dashboard update: $(date +%Y-%m-%d)" || true
      git push origin main 2>/dev/null || echo "⚠️ git push skipped (no remote or auth)"
    fi
  fi
  echo "✓ done"
} | tee "$LOG"

# Rich formatted summary for Telegram
BATCH_COUNT=$(python3 -c "
import json
from pathlib import Path
f = Path('$SKILL/data/all-batches.json')
if f.exists():
    data = json.loads(f.read_text())
    print(len(data.get('batches', [])))
else:
    print('0')
")

echo "🎯 *Rank & Rent Dashboard*

📊 *Weekly Update*
• Batches: \`$BATCH_COUNT\`
• Status: ✅ Complete

🔗 [View Dashboard](https://marvelus-tech.github.io/rank-rent-ideas/)"
