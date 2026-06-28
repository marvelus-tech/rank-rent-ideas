#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LEADGEN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$LEADGEN_DIR/logs"
LOG_FILE="$LOG_DIR/daily-run.log"
CRON_CMD="cd $LEADGEN_DIR && /usr/bin/env python3 main.py run --config config/config.yaml --mode browser >> $LOG_FILE 2>&1"
CRON_ENTRY="0 7 * * * TZ=Australia/Melbourne $CRON_CMD"

mkdir -p "$LOG_DIR"

DETECTED_SHELL="${SHELL##*/}"
echo "Detected shell: $DETECTED_SHELL"

echo "Installing daily cron job for 7:00 AM Australia/Melbourne..."

CURRENT_CRON="$(crontab -l 2>/dev/null || true)"

if echo "$CURRENT_CRON" | grep -F "$CRON_CMD" >/dev/null 2>&1; then
  echo "Cron entry already exists. No changes made."
else
  {
    echo "$CURRENT_CRON"
    echo "$CRON_ENTRY"
  } | crontab -
  echo "Cron entry added."
fi

cat <<'EOF'

Done.

Useful commands:
- View cron jobs: crontab -l
- Edit cron jobs: crontab -e
- Remove all cron jobs: crontab -r
- Tail daily log: tail -f MarvelUs-lead-gen/logs/daily-run.log

EOF
