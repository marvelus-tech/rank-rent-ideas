#!/usr/bin/env node
/**
 * extract-builder-details.js — Deep dive on a specific builder community
 * 
 * Usage:
 *   node extract-builder-details.js "https://www.zillow.com/community/the-grove-at-austin/"
 *   node extract-builder-details.js "12345 Builder Way, Austin, TX"
 */

const https = require('https');
const fs = require('fs');

const API_KEY = process.env.RAPIDAPI_KEY;
if (!API_KEY) {
  console.error('❌ Error: RAPIDAPI_KEY environment variable required');
  process.exit(1);
}

const API_HOST = 'zillow-com1.p.rapidapi.com';

function makeRequest(path) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: API_HOST,
      path: path,
      method: 'GET',
      headers: {
        'X-RapidAPI-Key': API_KEY,
        'X-RapidAPI-Host': API_HOST,
      },
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error(`Invalid JSON: ${data.slice(0, 200)}`));
        }
      });
    });

    req.on('error', reject);
    req.setTimeout(30000, () => reject(new Error('Request timeout')));
    req.end();
  });
}

async function searchByAddress(address) {
  const encoded = encodeURIComponent(address);
  return makeRequest(`/propertyByAddress?address=${encoded}`);
}

async function getPropertyDetails(zpid) {
  return makeRequest(`/property?zpid=${zpid}`);
}

async function getPropertyPhotos(zpid) {
  return makeRequest(`/images?zpid=${zpid}`);
}

async function main() {
  const input = process.argv[2];
  if (!input) {
    console.log('Usage: node extract-builder-details.js <address-or-url>');
    process.exit(1);
  }

  console.log(`🔍 Looking up: ${input}\n`);

  let zpid;
  let propertyData;

  // Check if input is URL or address
  if (input.includes('zillow.com')) {
    // Extract zpid from URL
    const match = input.match(/(\d+)_zpid/);
    if (match) {
      zpid = match[1];
    } else {
      console.error('❌ Could not extract ZPID from URL');
      process.exit(1);
    }
  } else {
    // Search by address
    console.log('📍 Searching by address...');
    const searchResult = await searchByAddress(input);
    if (searchResult.zpid) {
      zpid = searchResult.zpid;
      propertyData = searchResult;
    } else {
      console.error('❌ No property found at that address');
      process.exit(1);
    }
  }

  console.log(`   Found ZPID: ${zpid}`);

  // Fetch details
  console.log('📋 Fetching property details...');
  const details = propertyData || await getPropertyDetails(zpid);

  // Fetch photos
  console.log('📸 Fetching photos...');
  let photos = null;
  try {
    photos = await getPropertyPhotos(zpid);
  } catch (e) {
    console.warn('   ⚠️  Could not fetch photos');
  }

  // Extract builder info
  const builderInfo = {
    property: {
      zpid: details.zpid,
      address: details.address,
      price: details.price,
      zestimate: details.zestimate,
      bedrooms: details.bedrooms,
      bathrooms: details.bathrooms,
      livingArea: details.livingArea,
      yearBuilt: details.yearBuilt,
      homeType: details.homeType,
      description: details.description,
      listingUrl: details.listingUrl,
    },
    builder: {
      name: null,
      website: null,
      phone: null,
      email: null,
    },
    agent: {
      name: details.agentName || null,
      phone: details.agentPhoneNumber || null,
      email: null, // Would need profile scraping
      brokerage: details.brokerName || null,
      license: null,
    },
    community: {
      name: details.communityName || null,
      builderName: details.builderName || null,
      planNames: details.homePlans?.map(p => p.name) || [],
      amenities: details.amenities || [],
    },
    photos: photos ? {
      count: photos.images?.length || 0,
      urls: photos.images?.slice(0, 5).map(img => img.url) || [],
    } : null,
    market: {
      daysOnZillow: details.daysOnZillow,
      priceHistory: details.priceHistory || [],
      taxHistory: details.taxHistory || [],
      schools: details.schools || [],
    },
  };

  // Try to extract builder from description
  const desc = details.description || '';
  const builderPatterns = [
    /built by ([A-Z][A-Za-z\s&]+?)(?:\.|,|;|\s+in|\s+on)/i,
    /([A-Z][A-Za-z\s&]+?)\s+homes?\s+presents?/i,
    /([A-Z][A-Za-z\s&]+?)\s+is\s+(?:building|developing)/i,
  ];

  for (const pattern of builderPatterns) {
    const match = desc.match(pattern);
    if (match) {
      builderInfo.builder.name = match[1].trim();
      break;
    }
  }

  // Use community builder name if available
  if (!builderInfo.builder.name && details.builderName) {
    builderInfo.builder.name = details.builderName;
  }

  // Output
  const outputFile = `builder-details-${zpid}.json`;
  fs.writeFileSync(outputFile, JSON.stringify(builderInfo, null, 2));

  console.log(`\n✅ Extracted builder details`);
  console.log(`   Builder: ${builderInfo.builder.name || 'Unknown'}`);
  console.log(`   Agent: ${builderInfo.agent.name || 'Unknown'}`);
  console.log(`   Brokerage: ${builderInfo.agent.brokerage || 'Unknown'}`);
  console.log(`   Output: ${outputFile}`);
}

main().catch(e => {
  console.error(`❌ Error: ${e.message}`);
  process.exit(1);
});
