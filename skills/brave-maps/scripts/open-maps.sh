#!/bin/bash
# Open Google Maps in Brave Browser
# Usage: open-maps.sh

set -e

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

# Run the opener
exec node "$SCRIPT_DIR/open-maps.js"
