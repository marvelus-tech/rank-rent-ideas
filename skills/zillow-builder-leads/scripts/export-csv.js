#!/usr/bin/env node
/**
 * export-csv.js — Convert builder JSON to outreach-ready CSV
 * 
 * Usage:
 *   node export-csv.js builders-austin.json --output leads.csv
 *   node export-csv.js builders-austin.json --min-sales 5 --quality 0.6
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const inputFile = args[0];

if (!inputFile || !fs.existsSync(inputFile)) {
  console.error('❌ Usage: node export-csv.js <builders-json-file> [--output file.csv] [--min-sales N] [--quality 0.0-1.0]');
  process.exit(1);
}

const outputFile = getArg('--output') || inputFile.replace('.json', '.csv');
const minSales = parseInt(getArg('--min-sales')) || 0;
const minQuality = parseFloat(getArg('--quality')) || 0;

function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null;
}

function escapeCSV(str) {
  if (str === null || str === undefined) return '';
  str = String(str);
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

const data = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
const builders = data.builders || [];

// Filter
const filtered = builders.filter(b => {
  if (minSales > 0 && b.total_sales_12mo < minSales) return false;
  if (minQuality > 0 && b.data_quality_score < minQuality) return false;
  return true;
});

console.log(`📊 Exporting ${filtered.length} of ${builders.length} builders to CSV`);

// CSV Header
const headers = [
  'builder_name',
  'agent_name',
  'agent_phone',
  'agent_email',
  'brokerage',
  'builder_website',
  'community_count',
  'total_sales_12mo',
  'avg_sale_price',
  'primary_community',
  'community_address',
  'price_range_min',
  'price_range_max',
  'home_types',
  'data_quality_score',
  'first_sale_date',
  'latest_sale_date',
  'source_location',
];

let csv = headers.map(escapeCSV).join(',') + '\n';

for (const builder of filtered) {
  const primaryCommunity = builder.communities?.[0] || {};
  const sales = builder.recent_sales || [];
  const dates = sales.map(s => s.date).filter(Boolean).sort();
  
  const row = [
    builder.builder_name,
    builder.contacts?.agent_name,
    builder.contacts?.agent_phone,
    builder.contacts?.agent_email,
    builder.contacts?.brokerage,
    builder.contacts?.builder_website,
    builder.communities?.length || 0,
    builder.total_sales_12mo,
    builder.avg_sale_price,
    primaryCommunity.name,
    primaryCommunity.address,
    primaryCommunity.price_range?.min,
    primaryCommunity.price_range?.max,
    (primaryCommunity.home_types || []).join('; '),
    builder.data_quality_score,
    dates[0] || '',
    dates[dates.length - 1] || '',
    data.search_params?.location || '',
  ];

  csv += row.map(escapeCSV).join(',') + '\n';
}

fs.writeFileSync(outputFile, csv);

console.log(`✅ Exported to: ${path.resolve(outputFile)}`);
console.log(`\n📈 Summary:`);
console.log(`   Total builders: ${filtered.length}`);
console.log(`   Total sales (12mo): ${filtered.reduce((sum, b) => sum + b.total_sales_12mo, 0)}`);
console.log(`   Avg sale price: $${Math.round(filtered.reduce((sum, b) => sum + b.avg_sale_price, 0) / filtered.length).toLocaleString()}`);
