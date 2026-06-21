#!/bin/bash
# Night Owl Wake Script
# Spawns Night Owl sub-agent at 2:00 AM to work on queued tasks
# Run via: crontab -e -> 0 2 * * * /Users/oktos/.openclaw/workspace/.nightowl/wake.sh

NIGHTOWL_DIR="/Users/oktos/.openclaw/workspace/.nightowl"
TASKS_PENDING="$NIGHTOWL_DIR/tasks/pending"
TASKS_ACTIVE="$NIGHTOWL_DIR/tasks/active"
TASKS_COMPLETED="$NIGHTOWL_DIR/tasks/completed"
LOG_FILE="$NIGHTOWL_DIR/logs/nightowl-$(date +%Y%m%d).log"

# Ensure log directory exists
mkdir -p "$NIGHTOWL_DIR/logs"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Night Owl waking up..." >> "$LOG_FILE"

# Check if there's already an active Night Owl session
# (Prevent duplicate runs)
if pgrep -f "night-owl-session" > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Night Owl already active. Exiting." >> "$LOG_FILE"
    exit 0
fi

# Find the highest priority pending task
# Priority order: P0, P1, P2, P3
TASK_FILE=$(ls -1 "$TASKS_PENDING"/*.md 2>/dev/null | head -1)

if [ -z "$TASK_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No pending tasks. Night Owl going back to sleep." >> "$LOG_FILE"
    exit 0
fi

TASK_NAME=$(basename "$TASK_FILE")
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Found task: $TASK_NAME" >> "$LOG_FILE"

# Move task to active
mv "$TASK_FILE" "$TASKS_ACTIVE/"

# Create status file for Mission Control tracking
STATUS_FILE="$NIGHTOWL_DIR/status/current.json"
cat > "$STATUS_FILE" << EOF
{
  "agent": "night-owl",
  "status": "working",
  "currentTask": "$TASK_NAME",
  "startedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "estimatedEnd": "$(date -u -v+5H +%Y-%m-%dT%H:%M:%SZ)",
  "progress": 0
}
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task activated: $TASK_NAME" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Night Owl is working..." >> "$LOG_FILE"

# Note: Actual sub-agent spawn happens via OpenClaw gateway
# This script prepares the environment and task state
# The sub-agent will be spawned via sessions_spawn with mode=run

# Mark session identifier for process checking
touch "$NIGHTOWL_DIR/.night-owl-session"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Night Owl environment ready." >> "$LOG_FILE"
