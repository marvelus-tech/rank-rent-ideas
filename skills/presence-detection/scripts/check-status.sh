#!/bin/bash
# Check current presence status from OpenClaw memory

echo "🏠 Presence Status"
echo "=================="
echo ""

# Check if we can read from memory system
if command -v openclaw &> /dev/null; then
    echo "Checking memory keys..."
    # These would need to be implemented via openclaw CLI or file read
    # For now, document the expected keys
    echo ""
    echo "Expected memory keys:"
    echo "  - user_location"
    echo "  - last_home_detected"
    echo "  - pending_away"
    echo "  - pending_away_time"
    echo "  - last_away_confirmed"
else
    echo "OpenClaw CLI not found in PATH"
fi
