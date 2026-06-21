#!/bin/bash
# Setup script for presence detection

echo "🏠 Setting up Presence Detection..."
echo "=================================="
echo ""

# Create log directory
mkdir -p /tmp/openclaw

# Load the LaunchAgent
echo "1. Loading presence listener LaunchAgent..."
launchctl load ~/Library/LaunchAgents/ai.openclaw.presence-listener.plist 2>/dev/null || echo "   Already loaded or needs unload first"
echo ""

# Start the service
echo "2. Starting presence listener..."
launchctl start ai.openclaw.presence-listener
sleep 2
echo ""

# Test if it's running
echo "3. Testing endpoint..."
RESPONSE=$(curl -s http://127.0.0.1:8123/health 2>/dev/null)
if echo "$RESPONSE" | grep -q "ok"; then
    echo "   ✅ Listener is running!"
    echo "   Response: $RESPONSE"
else
    echo "   ⚠️  Listener may not be responding yet"
    echo "   Try: tail -f /tmp/openclaw/presence-listener.error.log"
fi
echo ""

# Show the URLs
echo "4. Your iPhone Shortcuts should use:"
echo ""
echo "   ARRIVE HOME (WiFi):"
echo "   http://192.168.1.16:8123/presence?user=okeito&status=home&source=wifi&confidence=1.0"
echo ""
echo "   ARRIVE BY CAR (Geofence):"
echo "   http://192.168.1.16:8123/presence?user=okeito&status=home&source=geofence&confidence=1.0"
echo ""
echo "   LEAVE HOME:"
echo "   http://192.168.1.16:8123/presence?user=okeito&status=away&source=geofence&confidence=1.0"
echo ""

echo "5. Test manually:"
echo "   curl 'http://192.168.1.16:8123/presence?user=okeito&status=home&source=wifi&confidence=1.0'"
echo ""

echo "6. View logs:"
echo "   tail -f /tmp/openclaw/presence-listener.log"
echo ""

echo "✅ Setup complete!"
