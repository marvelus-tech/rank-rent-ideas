#!/bin/bash
# Quick setup and run Google Maps in Brave via Playwright

set -e

INSTALL_DIR="${HOME}/.brave-automation"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Install if needed
if [ ! -d "node_modules/playwright" ]; then
    echo "📦 Installing Playwright (one-time)..."
    [ ! -f "package.json" ] && npm init -y && npm pkg set name="brave-automation"
    npm install playwright
    npx playwright install chromium
fi

# Create Google Maps script
cat > google-maps.js << 'EOF'
const { chromium } = require('playwright');

(async () => {
    console.log('🚀 Launching Brave Browser...');
    
    const browser = await chromium.launch({
        headless: false,
        executablePath: '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
        args: ['--disable-blink-features=AutomationControlled']
    });
    
    const context = await browser.newContext({
        viewport: { width: 1400, height: 900 }
    });
    
    const page = await context.newPage();
    
    console.log('🗺️  Navigating to Google Maps...');
    await page.goto('https://maps.google.com', { waitUntil: 'networkidle' });
    
    console.log('✅ Google Maps is open in Brave');
    console.log('   Close the browser when done');
    
    // Keep browser open
})();
EOF

# Run it
echo "🎯 Starting Google Maps..."
node google-maps.js
