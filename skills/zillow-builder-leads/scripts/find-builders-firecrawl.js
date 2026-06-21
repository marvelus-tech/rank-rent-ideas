#!/usr/bin/env node
/**
 * find-builders-firecrawl.js — Scrape Zillow using Firecrawl (bypasses bot detection)
 * 
 * Usage:
 *   node find-builders-firecrawl.js "Austin, TX" --output builders.json
 *   node find-builders-firecrawl.js "Austin, TX" --pages 3 --headless false
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const location = args[0] || 'Austin, TX';
const outputFile = getArg('--output') || `builders-firecrawl-${slugify(location)}.json`;
const maxPages = parseInt(getArg('--pages')) || 1;

function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null;
}

function slugify(str) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function firecrawlScrape(url) {
  try {
    console.log(`   🔥 Firecrawling: ${url.substring(0, 80)}...`);
    
    const result = execSync(
      `firecrawl scrape "${url}" --format markdown`,
      { 
        encoding: 'utf8',
        timeout: 60000,
        maxBuffer: 10 * 1024 * 1024 // 10MB
      }
    );
    
    return result;
  } catch (e) {
    console.warn(`   ⚠️  Firecrawl error: ${e.message}`);
    return null;
  }
}

function extractListings(markdown) {
  const listings = [];
  
  // Find all price links which indicate listing starts
  const priceMatches = [...markdown.matchAll(/\[\$([\d,]+)\]\(https:\/\/www\.zillow\.com\/homedetails\/[^)]+\)/g)];
  
  for (const priceMatch of priceMatches) {
    const price = priceMatch[1].replace(/,/g, '');
    const listingUrl = priceMatch[0];
    
    // Get ZPID from URL
    const zpidMatch = listingUrl.match(/(\d+)_zpid/);
    const zpid = zpidMatch ? zpidMatch[1] : null;
    
    // Find the block around this price (200 chars before and after)
    const index = priceMatch.index;
    const block = markdown.substring(Math.max(0, index - 200), Math.min(markdown.length, index + 400));
    
    // Look for address in the block
    const addressMatch = block.match(/\[([^\]]+,\s*Austin,\s*TX\s*\d{5})\]/);
    const address = addressMatch ? addressMatch[1] : null;
    
    // Look for beds/baths/sqft
    const bedsMatch = block.match(/\*\*(\d+)\*\*\s*bds?/);
    const bathsMatch = block.match(/\*\*(\d+(?:\.\d+)?)\*\*\s*ba/);
    const sqftMatch = block.match(/\*\*([\d,]+)\*\*\s*sqft/);
    
    // Look for agent/broker
    const agentMatch = block.match(/\n([A-Z][A-Za-z\s&]+(?:LLC|INC|REALTY|REAL ESTATE|PROPERTIES))\s*\n/);
    const agent = agentMatch ? agentMatch[1].trim() : null;
    
    // Check for new construction indicators
    const isNew = block.toLowerCase().includes('new construction') ||
                  block.toLowerCase().includes('new home') ||
                  block.toLowerCase().includes('builder');
    
    if (address) {
      listings.push({
        price,
        address,
        zpid,
        isNew,
        beds: bedsMatch ? bedsMatch[1] : null,
        baths: bathsMatch ? bathsMatch[1] : null,
        sqft: sqftMatch ? sqftMatch[1].replace(/,/g, '') : null,
        agent,
        textPreview: block.substring(0, 200),
      });
    }
  }
  
  return listings;
}

function extractBuilderName(text) {
  if (!text) return null;
  
  const patterns = [
    /built by ([A-Z][A-Za-z\s&]+?)(?:\.|,|;|\s+in)/i,
    /([A-Z][A-Za-z\s&]+?)\s+homes?\s+presents?/i,
    /([A-Z][A-Za-z\s&]+?)\s+is\s+(?:building|developing)/i,
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) return match[1].trim();
  }
  
  const knownBuilders = [
    'Lennar', 'D.R. Horton', 'Pulte', 'Taylor Morrison',
    'Meritage', 'KB Home', 'Ryan Homes', 'Century Communities',
    'Ashton Woods', 'David Weekley', 'Perry Homes', 'Highland Homes',
    'Drees Homes', 'M/I Homes', 'Beazer', 'Toll Brothers',
  ];
  
  const lower = text.toLowerCase();
  for (const builder of knownBuilders) {
    if (lower.includes(builder.toLowerCase())) return builder;
  }
  
  return null;
}

async function main() {
  console.log(`🏗️  Zillow Builder Finder via Firecrawl`);
  console.log(`   Location: ${location}`);
  console.log(`   Pages: ${maxPages}\n`);

  const allListings = [];

  for (let page = 1; page <= maxPages; page++) {
    console.log(`📄 Scraping page ${page}...`);
    
    // Build Zillow search URL - use city-specific new construction page
    const encodedLocation = location.toLowerCase().replace(/,\s*/g, '-').replace(/\s+/g, '-');
    const searchUrl = `https://www.zillow.com/${encodedLocation}/new-construction/`;
    
    const markdown = firecrawlScrape(searchUrl);
    
    if (!markdown) {
      console.log(`   ✗ Failed to scrape page ${page}`);
      continue;
    }
    
    // Save raw markdown for debugging
    fs.writeFileSync(`zillow-page-${page}.md`, markdown);
    
    const listings = extractListings(markdown);
    console.log(`   ✓ Found ${listings.length} listings`);
    
    allListings.push(...listings);
    
    // Rate limit
    if (page < maxPages) {
      console.log('   ⏳ Waiting 3s...');
      await new Promise(r => setTimeout(r, 3000));
    }
  }

  if (allListings.length === 0) {
    console.log('\n⚠️  No listings found');
    process.exit(0);
  }

  // Group by builder
  const builderMap = new Map();
  
  for (const listing of allListings) {
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
      source: 'zillow-firecrawl',
      total_listings: allListings.length,
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
  
  console.log(`\n📝 Raw markdown saved as zillow-page-*.md for inspection`);
}

main().catch(e => {
  console.error(`\n❌ Error: ${e.message}`);
  console.error(e.stack);
  process.exit(1);
});
