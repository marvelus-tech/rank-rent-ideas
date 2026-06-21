#!/usr/bin/env node

const { findBuilders } = require('../lib/scraper');
const { saveOutput } = require('../lib/formatter');

// Parse CLI arguments
const args = process.argv.slice(2);
const options = {
  city: 'Austin',
  state: 'TX',
  days: 365,
  enrich: false,
  output: 'builder-leads'
};

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--city':
      options.city = args[++i];
      break;
    case '--state':
      options.state = args[++i];
      break;
    case '--days':
      options.days = parseInt(args[++i]);
      break;
    case '--enrich':
      options.enrich = true;
      break;
    case '--output':
      options.output = args[++i];
      break;
    case '--help':
      showHelp();
      process.exit(0);
  }
}

function showHelp() {
  console.log(`
Zillow Builder Leads Finder

Usage:
  node find-builders.js [options]

Options:
  --city <name>      City to search (default: Austin)
  --state <abbr>     State abbreviation (default: TX)
  --days <n>         Number of days back (default: 365)
  --enrich           Enrich with contact info (slower, uses more credits)
  --output <name>    Output file base name (default: builder-leads)
  --help             Show this help

Examples:
  node find-builders.js --city Dallas --state TX --days 180
  node find-builders.js --city Houston --state TX --enrich --output houston-builders
`);
}

async function main() {
  console.log('🏗️  Zillow Builder Leads Finder');
  console.log('================================\n');
  
  try {
    const startTime = Date.now();
    
    const results = await findBuilders(
      options.city,
      options.state,
      options.days,
      options.enrich
    );
    
    // Save outputs
    const outputPath = `./${options.output}`;
    const outputs = await saveOutput(results, outputPath);
    
    const duration = ((Date.now() - startTime) / 1000).toFixed(1);
    
    console.log('\n✅ Search Complete!');
    console.log(`⏱️  Duration: ${duration}s`);
    console.log(`🏗️  Builders Found: ${results.totalBuilders}`);
    console.log(`🏠 Total Homes: ${results.totalHomes}`);
    console.log('\n📁 Output Files:');
    console.log(`   JSON: ${outputs.json}`);
    console.log(`   CSV:  ${outputs.csv}`);
    console.log(`   MD:   ${outputs.markdown}`);
    
    // Show top builders
    console.log('\n🏆 Top Builders:');
    results.builders.slice(0, 5).forEach((b, i) => {
      console.log(`   ${i + 1}. ${b.name} — ${b.homesSold} homes sold`);
    });
    
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

main();
