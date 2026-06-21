#!/bin/bash
# Search Google Maps in Brave Browser
# Usage: search-maps.sh "query"

set -e

if [ $# -eq 0 ]; then
    echo "Usage: search-maps.sh \"location query\""
    echo "Example: search-maps.sh \"Sydney Opera House\""
    exit 1
fi

QUERY="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HOME}/.brave-automation"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Install Playwright if needed
if [ ! -d "node_modules/playwright" ]; then
    echo "📦 Installing Playwright (one-time)..."
    [ ! -f "package.json" ] && npm init -y && npm pkg set name="brave-automation"
    npm install playwright
    npx playwright install chromium
fi

# Run the search
exec node "$SCRIPT_DIR/search-maps.js" "$QUERY"
