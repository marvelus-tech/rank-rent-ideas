#!/usr/bin/env node
/**
 * deduplicate-builders.js — Merge duplicate builder records
 * 
 * Usage:
 *   node deduplicate-builders.js builders-raw.json --output builders-clean.json
 *   node deduplicate-builders.js builders-raw.json --merge-threshold 0.8
 */

const fs = require('fs');

const args = process.argv.slice(2);
const inputFile = args[0];

if (!inputFile || !fs.existsSync(inputFile)) {
  console.error('❌ Usage: node deduplicate-builders.js <builders-json-file> [--output file.json] [--merge-threshold 0.0-1.0]');
  process.exit(1);
}

const outputFile = getArg('--output') || inputFile.replace('.json', '-deduped.json');
const mergeThreshold = parseFloat(getArg('--merge-threshold')) || 0.85;

function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null;
}

function normalizeName(name) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
    .replace(/(homes|builders|development|llc|inc|corp|ltd)/g, '');
}

function similarityScore(a, b) {
  const nameA = normalizeName(a.builder_name);
  const nameB = normalizeName(b.builder_name);
  
  // Exact match
  if (nameA === nameB) return 1.0;
  
  // One contains the other
  if (nameA.includes(nameB) || nameB.includes(nameA)) return 0.95;
  
  // Same agent
  if (a.contacts?.agent_name && a.contacts.agent_name === b.contacts?.agent_name) {
    return 0.90;
  }
  
  // Same phone
  if (a.contacts?.agent_phone && a.contacts.agent_phone === b.contacts?.agent_phone) {
    return 0.85;
  }
  
  // Same website
  if (a.contacts?.builder_website && a.contacts.builder_website === b.contacts?.builder_website) {
    return 0.95;
  }
  
  return 0;
}

function mergeBuilders(builders) {
  const merged = [];
  const processed = new Set();

  for (let i = 0; i < builders.length; i++) {
    if (processed.has(i)) continue;

    const base = { ...builders[i] };
    processed.add(i);

    for (let j = i + 1; j < builders.length; j++) {
      if (processed.has(j)) continue;

      const score = similarityScore(base, builders[j]);
      if (score >= mergeThreshold) {
        console.log(`   🔄 Merging: "${base.builder_name}" + "${builders[j].builder_name}" (score: ${score.toFixed(2)})`);
        
        // Merge sales
        base.recent_sales = [...base.recent_sales, ...builders[j].recent_sales];
        base.total_sales_12mo += builders[j].total_sales_12mo;
        
        // Merge communities
        const existingCommunities = new Set(base.communities.map(c => c.name));
        for (const comm of builders[j].communities) {
          if (!existingCommunities.has(comm.name)) {
            base.communities.push(comm);
          }
        }
        
        // Keep best contact info
        if (!base.contacts.agent_name && builders[j].contacts?.agent_name) {
          base.contacts.agent_name = builders[j].contacts.agent_name;
        }
        if (!base.contacts.agent_phone && builders[j].contacts?.agent_phone) {
          base.contacts.agent_phone = builders[j].contacts.agent_phone;
        }
        if (!base.contacts.builder_website && builders[j].contacts?.builder_website) {
          base.contacts.builder_website = builders[j].contacts.builder_website;
        }
        
        // Recalculate average
        const totalPrice = base.recent_sales.reduce((sum, s) => sum + (s.price || 0), 0);
        base.avg_sale_price = base.total_sales_12mo > 0 
          ? Math.round(totalPrice / base.total_sales_12mo) 
          : 0;
        
        processed.add(j);
      }
    }

    // Sort sales by date
    base.recent_sales.sort((a, b) => new Date(b.date) - new Date(a.date));
    base.recent_sales = base.recent_sales.slice(0, 20); // Keep top 20

    merged.push(base);
  }

  return merged;
}

function main() {
  console.log('🏗️  Builder Deduplication\n');

  const data = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
  const builders = data.builders || [];

  console.log(`📊 Processing ${builders.length} builders...`);
  console.log(`   Merge threshold: ${mergeThreshold}\n`);

  const merged = mergeBuilders(builders);

  console.log(`\n✅ Deduplication complete`);
  console.log(`   Original: ${builders.length} builders`);
  console.log(`   After merge: ${merged.length} builders`);
  console.log(`   Removed: ${builders.length - merged.length} duplicates\n`);

  const output = {
    ...data,
    builders: merged,
    deduplication: {
      original_count: builders.length,
      final_count: merged.length,
      duplicates_removed: builders.length - merged.length,
      threshold: mergeThreshold,
      processed_at: new Date().toISOString(),
    },
  };

  fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));
  console.log(`💾 Saved to: ${outputFile}`);
}

main();
