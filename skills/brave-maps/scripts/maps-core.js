const { chromium } = require('playwright');

const BRAVE_PATH = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser';

async function openGoogleMaps() {
    console.log('🚀 Launching Brave Browser...');
    
    const browser = await chromium.launch({
        headless: false,
        executablePath: BRAVE_PATH,
        args: ['--disable-blink-features=AutomationControlled']
    });
    
    const context = await browser.newContext({
        viewport: { width: 1400, height: 900 }
    });
    
    const page = await context.newPage();
    
    console.log('🗺️  Navigating to Google Maps...');
    await page.goto('https://maps.google.com', { waitUntil: 'domcontentloaded' });
    
    console.log('✅ Google Maps is open in Brave');
    
    // Return page for further automation
    return { browser, page };
}

async function searchLocation(query) {
    const { browser, page } = await openGoogleMaps();
    
    console.log(`🔍 Searching for: ${query}`);
    
    // Wait for search box and search
    const searchBox = await page.waitForSelector('input[name="q"], input[id="searchboxinput"]', { timeout: 10000 });
    await searchBox.fill(query);
    await searchBox.press('Enter');
    
    console.log('✅ Search submitted');
    
    return { browser, page };
}

// CLI usage
if (require.main === module) {
    // Check if query was provided
    const query = process.argv[2];
    if (query) {
        searchLocation(query).catch(err => {
            console.error('❌ Error:', err.message);
            process.exit(1);
        });
    } else {
        openGoogleMaps().catch(err => {
            console.error('❌ Error:', err.message);
            process.exit(1);
        });
    }
}

module.exports = { openGoogleMaps, searchLocation };
