#!/usr/bin/env node
/**
 * zpid-helper.js — Help extract ZPIDs from Zillow search pages
 * 
 * This script helps you manually collect ZPIDs from Zillow:
 * 1. Opens browser to Zillow new construction search
 * 2. Lets you browse and copy ZPIDs from URLs
 * 3. Saves ZPIDs to file for processing
 * 
 * Usage:
 *   node zpid-helper.js "Austin, TX"
 *   node zpid-helper.js "Austin, TX" --auto-extract
 */

const { chromium } = require('playwright');
const fs = require('fs');
const readline = require('readline');

const args = process.argv.slice(2);
const location = args[0] || 'Austin, TX';
const autoExtract = args.includes('--auto-extract');
const outputFile = `zpids-${location.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.txt`;

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function ask(question) {
  return new Promise(resolve => rl.question(question, resolve));
}

async function openZillowSearch(location) {
  console.log('🚀 Opening browser for manual ZPID collection...');
  console.log('   Browser will open to Zillow new construction search\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    executablePath: '/Users/oktos/Library/Caches/ms-playwright/chromium-1217/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    viewport: { width: 1920, height: 1080 }
  });
  
  const page = await context.newPage();

  // Navigate to Zillow new construction
  const encodedLocation = encodeURIComponent(location);
  const searchUrl = `https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22${encodedLocation}%22%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Atrue%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%7D%7D`;
  
  await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
  
  console.log('✅ Browser opened!');
  console.log('   Instructions:');
  console.log('   1. Browse listings on the page');
  console.log('   2. Click listings to open detail pages');
  console.log('   3. Copy ZPID from URL (the number before _zpid)');
  console.log('   4. Paste ZPIDs here, one per line');
  console.log('   5. Type "done" when finished\n');
  
  return { browser, page };
}

async function autoExtractZPIDs(page) {
  console.log('🔍 Attempting to auto-extract ZPIDs from page...');
  
  // Wait for listings to load
  await page.waitForTimeout(5000);
  
  // Extract ZPIDs from links
  const zpids = await page.evaluate(() => {
    const links = document.querySelectorAll('a[href*="_zpid"]');
    const ids = new Set();
    
    links.forEach(link => {
      const match = link.href.match(/(\d+)_zpid/);
      if (match) ids.add(match[1]);
    });
    
    return Array.from(ids);
  });
  
  console.log(`   Found ${zpids.length} ZPIDs on current page`);
  return zpids;
}

async function manualEntry() {
  const zpids = [];
  
  console.log('📝 Enter ZPIDs (one per line, type "done" to finish):\n');
  
  while (true) {
    const input = await ask('ZPID: ');
    
    if (input.toLowerCase() === 'done') break;
    
    // Extract ZPID from URL or direct input
    const match = input.match(/(\d+)/);
    if (match) {
      zpids.push(match[1]);
      console.log(`   ✓ Added: ${match[1]} (total: ${zpids.length})`);
    } else {
      console.log('   ✗ Invalid input, try again');
    }
  }
  
  return zpids;
}

async function main() {
  console.log(`🏗️  ZPID Helper for Zillow Builder Search`);
  console.log(`   Location: ${location}\n`);

  const { browser, page } = await openZillowSearch(location);
  
  let zpids = [];
  
  if (autoExtract) {
    zpids = await autoExtractZPIDs(page);
  }
  
  // Always allow manual entry too
  const manualZpids = await manualEntry();
  zpids = [...new Set([...zpids, ...manualZpids])];
  
  await browser.close();
  rl.close();
  
  if (zpids.length === 0) {
    console.log('\n⚠️  No ZPIDs collected');
    process.exit(0);
  }
  
  // Save to file
  fs.writeFileSync(outputFile, zpids.join('\n'));
  
  console.log(`\n✅ Saved ${zpids.length} ZPIDs to: ${outputFile}`);
  console.log(`\nNext steps:`);
  console.log(`   node scripts/find-builders-zpids.js ${outputFile}`);
  console.log(`   node scripts/export-csv.js builders-*.json --output leads.csv`);
}

main().catch(e => {
  console.error(`❌ Error: ${e.message}`);
  process.exit(1);
});
