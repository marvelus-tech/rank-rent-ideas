#!/bin/bash
# Cron wrapper: weekly memory maintenance (Obsidian, no agent)
set -euo pipefail
VAULT="$HOME/Obsidian/Penelopi"
REPORT_DIR="$VAULT/maintenance"
DATE=$(date +%Y-%m-%d)
REPORT="$REPORT_DIR/${DATE}-weekly.md"
mkdir -p "$REPORT_DIR"

MEMORY="$VAULT/MEMORY.md"
DAILY_COUNT=$(find "$VAULT/Daily" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
OLD_DAILY=$(find "$VAULT/Daily" -name "*.md" -mtime +90 2>/dev/null | wc -l | tr -d ' ')
PROJECTS=$(find "$VAULT/Projects" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
MEM_LINES=$(wc -l < "$MEMORY" 2>/dev/null | tr -d ' ')

# Rich formatted summary for Telegram
SUMMARY="🧠 *Weekly Memory Report*

📊 *Stats*
• Daily notes: \`$DAILY_COUNT\`
• Old notes (>90d): \`$OLD_DAILY\`
• Project files: \`$PROJECTS\`
• MEMORY.md: \`${MEM_LINES} lines\`

⚡ *Actions*
• Review entries >30d
• Archive stale >90d
• Update PROJECTS status"

cat > "$REPORT" <<EOF
# Weekly Memory Maintenance — $DATE

$SUMMARY

Actions: review >30d entries | archive >90d | update PROJECTS status
EOF

echo "$SUMMARY"
