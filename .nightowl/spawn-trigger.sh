#!/bin/bash
# Night Owl Spawn Trigger
# This script is called by the OpenClaw system to spawn Night Owl sub-agent
# It prepares the task and returns the task file path

NIGHTOWL_DIR="/Users/oktos/.openclaw/workspace/.nightowl"
TASKS_PENDING="$NIGHTOWL_DIR/tasks/pending"
TASKS_ACTIVE="$NIGHTOWL_DIR/tasks/active"

# Find highest priority task (P0 > P1 > P2 > P3)
# Files should be named with priority prefix: 2026-03-24-P0-task-name.md
TASK_FILE=$(ls -1 "$TASKS_PENDING"/*-P0-*.md 2>/dev/null | head -1)

if [ -z "$TASK_FILE" ]; then
    TASK_FILE=$(ls -1 "$TASKS_PENDING"/*-P1-*.md 2>/dev/null | head -1)
fi

if [ -z "$TASK_FILE" ]; then
    TASK_FILE=$(ls -1 "$TASKS_PENDING"/*.md 2>/dev/null | head -1)
fi

if [ -z "$TASK_FILE" ]; then
    echo "NO_TASK"
    exit 0
fi

# Move to active
TASK_NAME=$(basename "$TASK_FILE")
mv "$TASK_FILE" "$TASKS_ACTIVE/"

# Output task path for the spawner
echo "$TASKS_ACTIVE/$TASK_NAME"
