#!/usr/bin/env bash
set -euo pipefail

# Default schedule: daily 2:00 AM (Australia/Melbourne local machine time)
CRON_EXPR="${1:-0 2 * * *}"
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
JOB_NAME="rnd-daily-debate"

read -r -d '' PAYLOAD <<JSON || true
{
  "name": "${JOB_NAME}",
  "schedule": "${CRON_EXPR}",
  "timezone": "Australia/Melbourne",
  "payload": {
    "model": "opencode/gpt-5.3-codex",
    "command": "node ${WORKSPACE}/rnd/debate.js"
  }
}
JSON

echo "Registering cron job: ${JOB_NAME}"
echo "Schedule: ${CRON_EXPR}"
echo ""
echo "openclaw cron add --json '$PAYLOAD'"

openclaw cron add --json "$PAYLOAD"

echo "Done. Verify with: openclaw cron list"
