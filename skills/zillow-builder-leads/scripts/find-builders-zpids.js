#!/usr/bin/env node
/**
 * find-builders-zpids.js — Find builders from a list of ZPIDs or addresses
 * 
 * Usage:
 *   node find-builders-zpids.js zpids.txt --output builders.json
 *   node find-builders-zpids.js addresses.txt --type addresses
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const inputFile = args[0];
const isAddresses = args.includes('--type') && getArg('--type') === 'addresses';
const outputFile = getArg('--output') || 'builders-from-zpids.json';

function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null;
}

const API_KEY = process.env.RAPIDAPI_KEY || '75d9759aa4mshbb672cae5345b37p14efbfjsne5a460330e3a';
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

async function getPropertyByZpid(zpid) {
  return makeRequest(`/property?zpid=${zpid}`);
}

async function searchByAddress(address) {
  const encoded = encodeURIComponent(address);
  return makeRequest(`/propertyByAddress?address=${encoded}`);
}

// Builder name patterns
const BUILDER_PATTERNS = [
  /built by ([A-Z][A-Za-z\s&]+?)(?:\.|,|;|\s+in|\s+on|\s+at|\s+with|\s+featuring|\s+offering|\s+\d)/i,
  /([A-Z][A-Za-z\s&]+?)\s+(?:homes?|builders?|development|communities?|properties)\s+presents?/i,
  /([A-Z][A-Za-z\s&]+?)\s+is\s+(?:building|developing|offering)/i,
  /(?:from|by)\s+([A-Z][A-Za-z\s&]+?)\s+(?:homes?|builders?)/i,
];

const KNOWN_BUILDERS = [
  'Lennar', 'D.R. Horton', 'PulteGroup', 'NVR', 'Taylor Morrison',
  'Meritage Homes', 'KB Home', 'Ryan Homes', 'Century Communities',
  'Tri Pointe Homes', 'Woodside Homes', 'Ashton Woods', 'David Weekley',
  'Perry Homes', 'Highland Homes', 'Gehan Homes', 'Drees Homes',
  'M/I Homes', 'Beazer Homes', 'Richmond American', 'Shea Homes',
  'The New Home Company', 'Toll Brothers', 'CalAtlantic', 'William Lyon'
];

function extractBuilderName(listing) {
  const description = listing.description || '';
  for (const pattern of BUILDER_PATTERNS) {
    const match = description.match(pattern);
    if (match) {
      const name = match[1].trim();
      if (name.length > 2 && name.length < 50) {
        return cleanBuilderName(name);
      }
    }
  }

  const text = `${description} ${listing.brokerName || ''} ${listing.agentName || ''}`.toLowerCase();
  for (const builder of KNOWN_BUILDERS) {
    if (text.includes(builder.toLowerCase())) {
      return builder;
    }
  }

  if (listing.brokerName && !listing.brokerName.match(/realty|realtors?|estate/i)) {
    return cleanBuilderName(listing.brokerName);
  }

  return listing.builderName || null;
}

function cleanBuilderName(name) {
  return name
    .replace(/\s+/g, ' ')
    .replace(/^(the|a|an)\s+/i, '')
    .replace(/\s+(llc|inc|corp|ltd)\.?$/i, '')
    .trim();
}

async function main() {
  if (!inputFile || !fs.existsSync(inputFile)) {
    console.error('❌ Usage: node find-builders-zpids.js <zpids.txt|addresses.txt> [--type addresses] [--output file.json]');
    process.exit(1);
  }

  const lines = fs.readFileSync(inputFile, 'utf8')
    .split('\n')
    .map(l => l.trim())
    .filter(l => l.length > 0);

  console.log(`🏗️  Zillow Builder Finder (ZPID mode)`);
  console.log(`   Input: ${inputFile}`);
  console.log(`   Items: ${lines.length}`);
  console.log(`   Type: ${isAddresses ? 'Addresses' : 'ZPIDs'}\n`);

  const allProperties = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    console.log(`🔍 [${i + 1}/${lines.length}] Looking up: ${line}`);

    try {
      let property;
      if (isAddresses) {
        property = await searchByAddress(line);
      } else {
        property = await getPropertyByZpid(line);
      }

      if (property && property.zpid) {
        allProperties.push(property);
        console.log(`   ✓ Found: ${property.address?.streetAddress || 'Unknown address'}`);
      } else {
        console.log(`   ✗ Not found`);
      }
    } catch (e) {
      console.warn(`   ⚠️  Error: ${e.message}`);
    }

    // Rate limit
    if (i < lines.length - 1) {
      await new Promise(r => setTimeout(r, 1000));
    }
  }

  console.log(`\n📊 Processing ${allProperties.length} properties...`);

  // Group by builder
  const builderMap = new Map();

  for (const property of allProperties) {
    const builderName = extractBuilderName(property) || 'Unknown Builder';
    
    if (!builderMap.has(builderName)) {
      builderMap.set(builderName, {
        builder_name: builderName,
        contacts: {
          agent_name: property.agentName || null,
          agent_phone: property.agentPhoneNumber || null,
          brokerage: property.brokerName || null,
          builder_website: null,
        },
        communities: [],
        properties: [],
        total_sales_12mo: 0,
        avg_sale_price: 0,
        price_sum: 0,
        data_quality_score: 0,
      });
    }

    const builder = builderMap.get(builderName);
    const price = property.price || property.zestimate || 0;
    
    if (price > 0) {
      builder.price_sum += price;
      builder.total_sales_12mo++;
    }

    builder.properties.push({
      zpid: property.zpid,
      address: property.address,
      price: price,
      yearBuilt: property.yearBuilt,
      dateSold: property.dateSold,
      homeType: property.homeType,
      bedrooms: property.bedrooms,
      bathrooms: property.bathrooms,
      livingArea: property.livingArea,
      description: property.description?.substring(0, 200),
    });
  }

  // Format output
  const builders = [];
  for (const [name, builder] of builderMap) {
    if (builder.total_sales_12mo > 0) {
      builder.avg_sale_price = Math.round(builder.price_sum / builder.total_sales_12mo);
    }

    let score = 0;
    if (builder.contacts.agent_name) score += 0.2;
    if (builder.contacts.agent_phone) score += 0.2;
    if (builder.contacts.brokerage) score += 0.1;
    if (builder.builder_name !== 'Unknown Builder') score += 0.3;
    if (builder.properties.length > 0) score += 0.2;

    builders.push({
      builder_name: builder.builder_name,
      contacts: builder.contacts,
      properties: builder.properties.slice(0, 10),
      total_sales_12mo: builder.total_sales_12mo,
      avg_sale_price: builder.avg_sale_price,
      data_quality_score: Math.round(score * 100) / 100,
    });
  }

  builders.sort((a, b) => b.total_sales_12mo - a.total_sales_12mo);

  const output = {
    search_params: {
      input_file: inputFile,
      type: isAddresses ? 'addresses' : 'zpids',
      total_input: lines.length,
      properties_found: allProperties.length,
      unique_builders: builders.length,
      generated_at: new Date().toISOString(),
    },
    builders,
  };

  fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));

  console.log(`\n✅ Done! Found ${builders.length} unique builders`);
  console.log(`   Output: ${path.resolve(outputFile)}`);
  console.log(`\n📈 Top Builders:`);
  builders.slice(0, 5).forEach((b, i) => {
    console.log(`   ${i + 1}. ${b.builder_name} — ${b.total_sales_12mo} properties, avg $${b.avg_sale_price.toLocaleString()}`);
  });
}

main().catch(e => {
  console.error(`❌ Fatal error: ${e.message}`);
  process.exit(1);
});
