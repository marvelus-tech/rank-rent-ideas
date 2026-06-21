#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LEADGEN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$LEADGEN_DIR/logs"
DAILY_SCRIPT="$LEADGEN_DIR/scripts/run-daily-leads.sh"
LOG_FILE="$LOG_DIR/daily-cron.log"

# Daily at 7:00 AM Australia/Melbourne
CRON_CMD="cd $LEADGEN_DIR && bash $DAILY_SCRIPT >> $LOG_FILE 2>&1"
CRON_ENTRY="0 7 * * * TZ=Australia/Melbourne $CRON_CMD"

mkdir -p "$LOG_DIR"

DETECTED_SHELL="${SHELL##*/}"
echo "Detected shell: $DETECTED_SHELL"

CURRENT_CRON="$(crontab -l 2>/dev/null || true)"

if echo "$CURRENT_CRON" | grep -F "$CRON_CMD" >/dev/null 2>&1; then
  echo "Cron entry already exists. No changes made."
else
  {
    echo "$CURRENT_CRON"
    echo "$CRON_ENTRY"
  } | crontab -
  echo "✅ Cron entry added: Daily at 7:00 AM Melbourne"
fi

cat <<'EOF'

Done. Daily lead generation is now scheduled.

What happens every day at 7 AM:
1. Rotates through categories (plumbers → electricians → dentists → hvac → etc.)
2. Runs browser pipeline (Maps → Websites → Emails → Intelligence scoring)
3. Saves to Obsidian vault: ~/Obsidian/Penelopi/Leads/
4. Deduplicates master list

Useful commands:
- View cron jobs: crontab -l
- Edit cron jobs: crontab -e
- Remove all cron jobs: crontab -r
- Daily log: tail -f leadgen/logs/daily-cron.log

EOF
