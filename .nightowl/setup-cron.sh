#!/bin/bash
# Setup Night Owl Cron Job
# Run this once to enable automatic 2 AM activation

echo "Setting up Night Owl daily automation..."
echo ""

# Check if cron is available
if ! command -v crontab &> /dev/null; then
    echo "Error: crontab not found. Please install cron."
    exit 1
fi

NIGHTOWL_DIR="/Users/oktos/.openclaw/workspace/.nightowl"
CRON_JOB="0 2 * * * cd $NIGHTOWL_DIR && ./wake.sh >> $NIGHTOWL_DIR/logs/cron.log 2>&1"

# Check if already exists
if crontab -l 2>/dev/null | grep -q "nightowl/wake.sh"; then
    echo "Night Owl cron job already exists."
    echo ""
    echo "Current crontab:"
    crontab -l | grep nightowl
    echo ""
    read -p "Remove and re-add? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        crontab -l 2>/dev/null | grep -v "nightowl/wake.sh" | crontab -
        echo "Removed old entry."
    else
        echo "Keeping existing cron job."
        exit 0
    fi
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Night Owl cron job added!"
echo ""
echo "Schedule: Every day at 2:00 AM Australia/Melbourne"
echo "Logs: $NIGHTOWL_DIR/logs/cron.log"
echo ""
echo "Night Owl will:"
echo "  1. Wake up at 2:00 AM"
echo "  2. Check for pending tasks in .nightowl/tasks/pending/"
echo "  3. Work on the highest priority task until 7:00 AM"
echo "  4. Report results and go back to sleep"
echo ""
echo "To verify:"
echo "  crontab -l"
echo ""
echo "To manually trigger Night Owl now:"
echo "  ./wake.sh"
