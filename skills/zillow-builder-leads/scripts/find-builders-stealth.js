#!/usr/bin/env node
/**
 * find-builders-stealth.js — Stealth scraper using puppeteer-extra
 * Bypasses bot detection with stealth plugins
 * 
 * Usage:
 *   node find-builders-stealth.js "Austin, TX" --output builders.json
 *   node find-builders-stealth.js "Austin, TX" --headless false --pages 3
 */

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');

puppeteer.use(StealthPlugin());

const args = process.argv.slice(2);
const location = args[0] || 'Austin, TX';
const outputFile = getArg('--output') || `builders-stealth-${slugify(location)}.json`;
const headless = !args.includes('--headless') || args[args.indexOf('--headless') + 1] !== 'false';
const maxPages = parseInt(getArg('--pages')) || 1;

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

async function scrapeWithStealth(location) {
  console.log('🕵️  Launching stealth browser...');
  
  const browser = await puppeteer.launch({
    headless,
    executablePath: '/Users/oktos/Library/Caches/ms-playwright/chromium-1217/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--disable-gpu',
      '--window-size=1920,1080',
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  // Set extra headers to look more human
  await page.setExtraHTTPHeaders({
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  });

  // Navigate to Zillow
  const encodedLocation = encodeURIComponent(location);
  const searchUrl = `https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22${encodedLocation}%22%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Atrue%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%7D%7D`;

  console.log(`🔍 Navigating to Zillow...`);
  await page.goto(searchUrl, { waitUntil: 'networkidle2', timeout: 60000 });

  // Wait for content
  await new Promise(r => setTimeout(r, 8000));

  // Check for CAPTCHA
  const pageContent = await page.content();
  if (pageContent.includes('Press & Hold') || pageContent.includes('captcha')) {
    console.log('⚠️  CAPTCHA detected!');
    if (!headless) {
      console.log('   Please solve the CAPTCHA in the browser...');
      console.log('   Waiting 30 seconds...');
      await new Promise(r => setTimeout(r, 30000));
    } else {
      console.log('   Try running with --headless false to solve manually');
      await browser.close();
      return [];
    }
  }

  // Take screenshot
  await page.screenshot({ path: 'zillow-stealth.png', fullPage: false });
  console.log('📸 Screenshot saved: zillow-stealth.png');

  // Extract listings
  console.log('📊 Extracting listings...');
  
  const allListings = [];
  
  for (let currentPage = 1; currentPage <= maxPages; currentPage++) {
    console.log(`   Processing page ${currentPage}...`);
    
    const listings = await page.evaluate(() => {
      const data = [];
      
      // Try multiple selectors
      const selectors = [
        '[data-testid="property-card"]',
        '.list-card',
        '.property-card',
        'article',
      ];
      
      let cards = [];
      for (const selector of selectors) {
        cards = document.querySelectorAll(selector);
        if (cards.length > 0) break;
      }
      
      cards.forEach(card => {
        const text = card.textContent || '';
        const html = card.innerHTML || '';
        
        // Get price
        const priceMatch = text.match(/\$[\d,]+/);
        const price = priceMatch ? priceMatch[0] : null;
        
        // Get address
        let address = null;
        const addressEl = card.querySelector('address, [data-testid="property-card-addr"]');
        if (addressEl) address = addressEl.textContent.trim();
        
        // Get ZPID from link
        let zpid = null;
        const linkEl = card.querySelector('a[href*="_zpid"]');
        if (linkEl) {
          const match = linkEl.href.match(/(\d+)_zpid/);
          if (match) zpid = match[1];
        }
        
        // Check for new construction indicators
        const isNew = text.toLowerCase().includes('new') ||
                      text.toLowerCase().includes('construction') ||
                      text.toLowerCase().includes('builder');
        
        data.push({ price, address, zpid, isNew, textPreview: text.substring(0, 200) });
      });
      
      return data;
    });
    
    allListings.push(...listings);
    console.log(`   ✓ Found ${listings.length} listings on page ${currentPage}`);
    
    // Try to go to next page
    if (currentPage < maxPages) {
      try {
        const nextBtn = await page.$('a[title="Next page"], [aria-label="Next page"]');
        if (nextBtn) {
          await nextBtn.click();
          await new Promise(r => setTimeout(r, 5000));
        } else {
          console.log('   No next page button found');
          break;
        }
      } catch (e) {
        console.log('   Could not navigate to next page');
        break;
      }
    }
  }

  await browser.close();
  return allListings;
}

function extractBuilderName(text) {
  if (!text) return null;
  
  const patterns = [
    /built by ([A-Z][A-Za-z\s&]+?)(?:\.|,|;|\s+in)/i,
    /([A-Z][A-Za-z\s&]+?)\s+homes?\s+presents?/i,
  ];
  
  for (const pattern of patterns) {
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
  console.log(`🏗️  Zillow Stealth Scraper`);
  console.log(`   Location: ${location}`);
  console.log(`   Pages: ${maxPages}`);
  console.log(`   Headless: ${headless}\n`);

  try {
    const listings = await scrapeWithStealth(location);
    
    if (listings.length === 0) {
      console.log('\n⚠️  No listings found');
      console.log('   Try: node find-builders-stealth.js "Austin, TX" --headless false');
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
        source: 'zillow-stealth',
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
