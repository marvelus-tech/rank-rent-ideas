#!/usr/bin/env node
/**
 * find-builders-realtor.js — Scrape Realtor.com for new construction builders
 * More scraper-friendly than Zillow
 * 
 * Usage:
 *   node find-builders-realtor.js "Austin, TX" --output builders.json
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const location = args[0] || 'Austin, TX';
const outputFile = getArg('--output') || `builders-realtor-${slugify(location)}.json`;
const headless = !args.includes('--headless') || args[args.indexOf('--headless') + 1] !== 'false';

function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null;
}

function slugify(str) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

const KNOWN_BUILDERS = [
  'Lennar', 'D.R. Horton', 'Pulte', 'Taylor Morrison',
  'Meritage', 'KB Home', 'Ryan Homes', 'Century Communities',
  'Ashton Woods', 'David Weekley', 'Perry Homes', 'Highland Homes',
  'Drees Homes', 'M/I Homes', 'Beazer', 'Toll Brothers',
  'TRI Pointe Homes', 'Woodside Homes', 'Gehan Homes'
];

async function scrapeRealtor(location) {
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

  // Search URL for new construction
  const encodedLocation = encodeURIComponent(location);
  const searchUrl = `https://www.realtor.com/realestateandhomes-search/${encodedLocation}/type-new-construction`;

  console.log(`🔍 Navigating to Realtor.com...`);
  console.log(`   URL: ${searchUrl}`);
  
  try {
    await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  } catch (e) {
    console.log('⚠️  Timeout loading page, continuing...');
  }

  // Wait for page to settle
  await page.waitForTimeout(5000);

  // Take screenshot
  await page.screenshot({ path: 'realtor-search.png', fullPage: false });
  console.log('📸 Screenshot saved: realtor-search.png');

  // Extract listings
  console.log('📊 Extracting listings...');
  
  const listings = await page.evaluate(() => {
    const data = [];
    
    // Try multiple card selectors
    const selectors = [
      '[data-testid="property-card"]',
      '.property-card',
      '[data-label="property-card"]',
      'article',
    ];
    
    let cards = [];
    for (const selector of selectors) {
      cards = document.querySelectorAll(selector);
      if (cards.length > 0) {
        console.log(`Found cards with: ${selector}`);
        break;
      }
    }
    
    // If no cards found, try broader search
    if (cards.length === 0) {
      // Look for any element with price
      const priceElements = document.querySelectorAll('*');
      const parentCards = new Set();
      priceElements.forEach(el => {
        if (el.textContent && el.textContent.match(/^\$[\d,]+$/)) {
          let parent = el.parentElement;
          for (let i = 0; i < 5 && parent; i++) {
            if (parent.textContent.length > 200) {
              parentCards.add(parent);
              break;
            }
            parent = parent.parentElement;
          }
        }
      });
      cards = Array.from(parentCards);
      console.log(`Found ${cards.length} cards via price search`);
    }
    
    cards.forEach(card => {
      const text = card.textContent || '';
      
      // Get price
      const priceMatch = text.match(/\$[\d,]+/);
      const price = priceMatch ? priceMatch[0] : null;
      
      // Get address - look for patterns
      let address = null;
      const addressPatterns = [
        /(\d+\s+[^,]+,\s*[^,]+,\s*[A-Z]{2}\s*\d{5})/,
        /(\d+\s+[^,]+,\s*[^,]+)/,
      ];
      for (const pattern of addressPatterns) {
        const match = text.match(pattern);
        if (match) {
          address = match[1];
          break;
        }
      }
      
      // Get beds/baths/sqft
      const bedsMatch = text.match(/(\d+)\s*bd/);
      const bathsMatch = text.match(/(\d+(?:\.\d+)?)\s*ba/);
      const sqftMatch = text.match(/([\d,]+)\s*sqft/);
      
      // Check for builder name
      const builderMatch = text.match(/(?:by|from)\s+([A-Z][A-Za-z\s&]+?)(?:\s|$|\.)/);
      const builderName = builderMatch ? builderMatch[1].trim() : null;
      
      // Check for new construction
      const isNew = text.toLowerCase().includes('new') || 
                    text.toLowerCase().includes('builder') ||
                    text.toLowerCase().includes('community');
      
      data.push({
        price,
        address,
        beds: bedsMatch ? bedsMatch[1] : null,
        baths: bathsMatch ? bathsMatch[1] : null,
        sqft: sqftMatch ? sqftMatch[1] : null,
        builderName,
        isNew,
        textPreview: text.substring(0, 300),
      });
    });
    
    return data;
  });

  console.log(`   Found ${listings.length} listings`);

  await browser.close();

  return listings;
}

async function main() {
  console.log(`🏗️  Realtor.com Builder Scraper`);
  console.log(`   Location: ${location}`);
  console.log(`   Headless: ${headless}\n`);

  try {
    const listings = await scrapeRealtor(location);
    
    if (listings.length === 0) {
      console.log('\n⚠️  No listings found');
      process.exit(0);
    }

    // Group by builder
    const builderMap = new Map();
    
    for (const listing of listings) {
      let builderName = listing.builderName;
      
      // Try to find known builder in text
      if (!builderName) {
        const lower = listing.textPreview.toLowerCase();
        for (const builder of KNOWN_BUILDERS) {
          if (lower.includes(builder.toLowerCase())) {
            builderName = builder;
            break;
          }
        }
      }
      
      builderName = builderName || 'Unknown Builder';
      
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
        source: 'realtor.com',
        total_listings: listings.length,
        unique_builders: builders.length,
        scraped_at: new Date().toISOString(),
      },
      builders,
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
