#!/bin/bash
# Install Playwright for Brave Browser automation
# Run: ./install-playwright.sh

set -e

echo "🎭 Setting up Playwright for Brave Browser automation..."

# Check if npm/node is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Install Node.js first: https://nodejs.org"
    exit 1
fi

# Create project directory
INSTALL_DIR="${HOME}/.brave-automation"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Initialize if needed
if [ ! -f "package.json" ]; then
    npm init -y
fi

# Install Playwright
echo "📦 Installing Playwright..."
npm install playwright

# Install browsers (Chromium, which Brave is based on)
echo "🌐 Installing Chromium browsers..."
npx playwright install chromium

# Create example script
cat > "brave-example.js" << 'EOF'
const { chromium } = require('playwright');

(async () => {
    // Launch Brave (Chromium-based)
    const browser = await chromium.launch({
        headless: false,
        executablePath: '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
        args: ['--disable-blink-features=AutomationControlled']
    });
    
    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 }
    });
    
    const page = await context.newPage();
    
    // Example: Navigate and take screenshot
    await page.goto('https://example.com');
    await page.screenshot({ path: 'example.png' });
    console.log('Screenshot saved to example.png');
    
    await browser.close();
})();
EOF

# Create connect-to-existing script (uses brave-debug)
cat > "brave-connect.js" << 'EOF'
const { chromium } = require('playwright');

(async () => {
    // Connect to existing Brave instance (start with: brave-debug)
    const browser = await chromium.connectOverCDP('http://localhost:9222');
    const context = browser.contexts()[0] || await browser.newContext();
    const page = context.pages()[0] || await context.newPage();
    
    await page.goto('https://example.com');
    console.log('Connected to existing Brave instance');
    
    // Don't close - we're attached to existing browser
})();
EOF

echo ""
echo "✅ Playwright setup complete!"
echo ""
echo "📁 Installation directory: $INSTALL_DIR"
echo ""
echo "Usage:"
echo "  1. Source bash helpers:  source ~/.openclaw/workspace/scripts/brave-automation.sh"
echo "  2. Start Brave debug:    brave-debug"
echo "  3. Run automation:       node brave-example.js"
echo "  4. Or connect to debug:  node brave-connect.js"
echo ""
echo "📚 Playwright docs: https://playwright.dev"
