#!/bin/bash
# Brave Browser Automation Setup
# Source this file: source ~/.brave-automation.sh

# Path to Brave executable
BRAVE_PATH="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

# Launch Brave with remote debugging enabled (for automation)
brave-debug() {
    local port="${1:-9222}"
    echo "Starting Brave with remote debugging on port $port..."
    "$BRAVE_PATH" \
        --remote-debugging-port="$port" \
        --no-first-run \
        --no-default-browser-check \
        --user-data-dir="/tmp/brave-debug-profile" \
        "$@" 2>/dev/null &
    echo "Remote debugging available at: http://localhost:$port"
    echo "Connect Playwright/Puppeteer to ws://localhost:$port"
}

# Launch Brave in headless mode for scripts
brave-headless() {
    local url="${1:-about:blank}"
    "$BRAVE_PATH" \
        --headless \
        --disable-gpu \
        --no-sandbox \
        --disable-setuid-sandbox \
        --disable-dev-shm-usage \
        "$url" 2>/dev/null
}

# Launch Brave with a clean profile for testing
brave-clean() {
    local url="${1:-about:blank}"
    "$BRAVE_PATH" \
        --temp-profile \
        --no-first-run \
        --no-default-browser-check \
        "$url" 2>/dev/null &
}

# Check if Brave is running with debug port
brave-debug-check() {
    local port="${1:-9222}"
    if curl -s "http://localhost:$port/json/version" > /dev/null 2>&1; then
        echo "✅ Brave debugging active on port $port"
        echo "Version info:"
        curl -s "http://localhost:$port/json/version" | head -5
    else
        echo "❌ No Brave instance found on debug port $port"
        echo "Start with: brave-debug $port"
    fi
}

# Get WebSocket URL for connecting automation tools
brave-ws-url() {
    local port="${1:-9222}"
    curl -s "http://localhost:$port/json/version" | grep -o 'ws://[^"]*' | head -1
}

echo "Brave automation functions loaded. Available commands:"
echo "  brave-debug [port]     - Start Brave with remote debugging"
echo "  brave-headless [url]   - Run Brave headless"
echo "  brave-clean [url]      - Start Brave with clean profile"
echo "  brave-debug-check      - Check debug port status"
echo "  brave-ws-url           - Get WebSocket URL for tools"
