#!/usr/bin/env node
/**
 * find-builders-scraper.js — Scrape Zillow directly for new construction builders
 * Uses Playwright for browser automation (more reliable than API)
 * 
 * Usage:
 *   node find-builders-scraper.js "Austin, TX" --days 365 --output builders.json
 *   node find-builders-scraper.js "78701" --headless false
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const location = args[0] || 'Austin, TX';
const daysOnZillow = parseInt(getArg('--days')) || 365;
const outputFile = getArg('--output') || `builders-${slugify(location)}.json`;
const headless = !args.includes('--headless') || args[args.indexOf('--headless') + 1] !== 'false';
const limit = parseInt(getArg('--limit')) || 100;

function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null;
}

function slugify(str) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

// Builder patterns
const BUILDER_PATTERNS = [
  /built by ([A-Z][A-Za-z\s&]+?)(?:\.|,|;|\s+in|\s+on|\s+at)/i,
  /([A-Z][A-Za-z\s&]+?)\s+(?:homes?|builders?)\s+presents?/i,
  /([A-Z][A-Za-z\s&]+?)\s+is\s+(?:building|developing)/i,
];

const KNOWN_BUILDERS = [
  'Lennar', 'D.R. Horton', 'Pulte', 'Taylor Morrison',
  'Meritage', 'KB Home', 'Ryan Homes', 'Century Communities',
  'Ashton Woods', 'David Weekley', 'Perry Homes', 'Highland Homes',
  'Drees Homes', 'M/I Homes', 'Beazer', 'Toll Brothers'
];

async function scrapeZillow(location, days) {
  console.log('🚀 Launching browser...');
  
  const browser = await chromium.launch({ 
    headless,
    executablePath: '/Users/oktos/Library/Caches/ms-playwright/chromium-1217/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 }
  });
  
  const page = await context.newPage();

  // Build search URL for new construction
  const encodedLocation = encodeURIComponent(location);
  const searchUrl = `https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22${encodedLocation}%22%2C%22mapBounds%22%3A%7B%7D%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Atrue%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%7D%7D`;

  console.log(`🔍 Navigating to Zillow...`);
  console.log(`   URL: ${searchUrl.substring(0, 100)}...`);
  
  try {
    await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  } catch (e) {
    console.log('⚠️  Timeout loading page, continuing...');
  }

  // Wait for page to settle
  await page.waitForTimeout(5000);

  // Handle cookie consent if present
  try {
    const cookieBtn = await page.$('button:has-text("Accept all")');
    if (cookieBtn) await cookieBtn.click();
  } catch (e) {}

  // Take screenshot for debugging
  await page.screenshot({ path: 'zillow-search.png', fullPage: false });
  console.log('📸 Screenshot saved: zillow-search.png');

  // Try multiple selectors for listings
  console.log('📊 Extracting listings...');
  
  const listings = await page.evaluate(() => {
    const data = [];
    
    // Try multiple card selectors
    const selectors = [
      '[data-testid="property-card"]',
      '.list-card',
      '.property-card',
      '[data-testid="card"]',
      'article',
      '[role="article"]'
    ];
    
    let cards = [];
    for (const selector of selectors) {
      cards = document.querySelectorAll(selector);
      if (cards.length > 0) break;
    }
    
    console.log(`Found ${cards.length} cards`);
    
    cards.forEach(card => {
      const text = card.textContent || '';
      const html = card.innerHTML || '';
      
      // Check for new construction indicators
      const isNewConstruction = 
        text.toLowerCase().includes('new construction') ||
        text.toLowerCase().includes('new home') ||
        text.toLowerCase().includes('builder') ||
        text.toLowerCase().includes('community') ||
        html.includes('New Construction') ||
        html.includes('new-construction');
      
      // Get price
      const priceMatch = text.match(/\$[\d,]+/);
      const price = priceMatch ? priceMatch[0] : null;
      
      // Get address
      const addressEl = card.querySelector('address, [data-testid="property-card-addr"], .list-card-addr');
      const address = addressEl ? addressEl.textContent.trim() : null;
      
      // Get link
      const linkEl = card.querySelector('a[href*="/homedetails/"]');
      const url = linkEl ? linkEl.href : null;
      
      data.push({
        price,
        address,
        url,
        isNewConstruction,
        textPreview: text.substring(0, 200),
      });
    });
    
    return data;
  });

  console.log(`   Found ${listings.length} total listings`);
  console.log(`   ${listings.filter(l => l.isNewConstruction).length} marked as new construction`);

  await browser.close();

  return listings;
}

function extractBuilderName(text) {
  if (!text) return null;
  
  for (const pattern of BUILDER_PATTERNS) {
    const match = text.match(pattern);
    if (match) return match[1].trim();
  }
  
  const lower = text.toLowerCase();
  for (const builder of KNOWN_BUILDERS) {
    if (lower.includes(builder.toLowerCase())) return builder;
  }
  
  return null;
}

async function main() {
  console.log(`🏗️  Zillow Builder Scraper`);
  console.log(`   Location: ${location}`);
  console.log(`   Days: ${daysOnZillow}`);
  console.log(`   Headless: ${headless}\n`);

  try {
    const listings = await scrapeZillow(location, daysOnZillow);
    
    if (listings.length === 0) {
      console.log('\n⚠️  No listings found');
      console.log('   Try: node find-builders-scraper.js "Austin, TX" --headless false');
      process.exit(0);
    }

    // Group by builder
    const builderMap = new Map();
    
    for (const listing of listings) {
      const builderName = extractBuilderName(listing.textPreview) || 'Unknown Builder';
      
      if (!builderMap.has(builderName)) {
        builderMap.set(builderName, {
          builder_name: builderName,
          listings: [],
          count: 0,
        });
      }
      
      const builder = builderMap.get(builderName);
      builder.listings.push(listing);
      builder.count++;
    }

    const builders = Array.from(builderMap.values());
    builders.sort((a, b) => b.count - a.count);

    const output = {
      search_params: {
        location,
        days_on_zillow: daysOnZillow,
        total_listings: listings.length,
        unique_builders: builders.length,
        scraped_at: new Date().toISOString(),
      },
      builders: builders.slice(0, limit),
    };

    fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));

    console.log(`\n✅ Done! Found ${builders.length} builders`);
    console.log(`   Output: ${path.resolve(outputFile)}`);
    console.log(`\n📈 Top Builders:`);
    builders.slice(0, 5).forEach((b, i) => {
      console.log(`   ${i + 1}. ${b.builder_name} — ${b.count} listings`);
    });

  } catch (e) {
    console.error(`\n❌ Error: ${e.message}`);
    console.error(e.stack);
    process.exit(1);
  }
}

main();
