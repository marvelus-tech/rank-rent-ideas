#!/usr/bin/env node
/**
 * enrich-builder-websites.js — Scrape builder websites for contact info
 * 
 * Usage:
 *   node enrich-builder-websites.js builders-austin.json --output enriched.json
 *   node enrich-builder-websites.js builders-austin.json --find-emails
 */

const https = require('https');
const fs = require('fs');
const { URL } = require('url');

const args = process.argv.slice(2);
const inputFile = args[0];

if (!inputFile || !fs.existsSync(inputFile)) {
  console.error('❌ Usage: node enrich-builder-websites.js <builders-json-file> [--output file.json] [--find-emails]');
  process.exit(1);
}

const outputFile = getArg('--output') || inputFile.replace('.json', '-enriched.json');
const findEmails = args.includes('--find-emails');

function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null;
}

function fetchWebsite(url) {
  return new Promise((resolve, reject) => {
    try {
      const parsed = new URL(url);
      const options = {
        hostname: parsed.hostname,
        path: parsed.pathname || '/',
        method: 'GET',
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; BuilderBot/1.0)',
        },
        timeout: 15000,
      };

      const req = https.request(options, (res) => {
        // Follow redirects
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          fetchWebsite(res.headers.location).then(resolve).catch(reject);
          return;
        }

        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve(data));
      });

      req.on('error', reject);
      req.on('timeout', () => reject(new Error('Timeout')));
      req.end();
    } catch (e) {
      reject(e);
    }
  });
}

function extractEmails(html) {
  const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
  const matches = html.match(emailRegex) || [];
  // Filter out common false positives
  return [...new Set(matches)].filter(e => 
    !e.match(/(\.png|\.jpg|\.gif|\.svg|@example\.com|@test\.com|@domain\.com)$/i)
  );
}

function extractPhones(html) {
  const phoneRegex = /\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g;
  const matches = html.match(phoneRegex) || [];
  return [...new Set(matches)];
}

function extractSocialLinks(html) {
  const links = {
    facebook: null,
    instagram: null,
    linkedin: null,
    twitter: null,
  };

  const fbMatch = html.match(/https?:\/\/(?:www\.)?facebook\.com\/[^"\s]+/i);
  const igMatch = html.match(/https?:\/\/(?:www\.)?instagram\.com\/[^"\s]+/i);
  const liMatch = html.match(/https?:\/\/(?:www\.)?linkedin\.com\/[^"\s]+/i);
  const twMatch = html.match(/https?:\/\/(?:www\.)?twitter\.com\/[^"\s]+/i);

  if (fbMatch) links.facebook = fbMatch[0];
  if (igMatch) links.instagram = igMatch[0];
  if (liMatch) links.linkedin = liMatch[0];
  if (twMatch) links.twitter = twMatch[0];

  return links;
}

async function enrichBuilder(builder) {
  const website = builder.contacts?.builder_website;
  if (!website) return builder;

  console.log(`🔍 Scraping: ${website}`);

  try {
    const html = await fetchWebsite(website);
    
    // Extract contact info
    const emails = findEmails ? extractEmails(html) : [];
    const phones = extractPhones(html);
    const social = extractSocialLinks(html);

    // Update builder record
    const enriched = { ...builder };
    
    if (!enriched.contacts) enriched.contacts = {};
    if (emails.length > 0 && !enriched.contacts.builder_email) {
      enriched.contacts.builder_email = emails[0];
    }
    if (phones.length > 0 && !enriched.contacts.builder_phone) {
      enriched.contacts.builder_phone = phones[0];
    }
    enriched.contacts.social_media = social;
    enriched.contacts.emails_found = emails;
    enriched.contacts.phones_found = phones;

    console.log(`   ✓ Found ${emails.length} emails, ${phones.length} phones`);

    return enriched;
  } catch (e) {
    console.warn(`   ⚠️  Could not scrape ${website}: ${e.message}`);
    return builder;
  }
}

async function main() {
  console.log('🏗️  Builder Website Enrichment\n');

  const data = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
  const builders = data.builders || [];

  console.log(`📊 Enriching ${builders.length} builders...\n`);

  const enrichedBuilders = [];
  for (const builder of builders) {
    const enriched = await enrichBuilder(builder);
    enrichedBuilders.push(enriched);
    
    // Rate limit protection
    await new Promise(r => setTimeout(r, 500));
  }

  const output = {
    ...data,
    builders: enrichedBuilders,
    enriched_at: new Date().toISOString(),
  };

  fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));

  console.log(`\n✅ Enriched data saved to: ${outputFile}`);
  console.log(`\n📈 Summary:`);
  const withEmail = enrichedBuilders.filter(b => b.contacts?.builder_email).length;
  const withPhone = enrichedBuilders.filter(b => b.contacts?.builder_phone).length;
  console.log(`   Builders with email: ${withEmail}`);
  console.log(`   Builders with phone: ${withPhone}`);
}

main().catch(e => {
  console.error(`❌ Error: ${e.message}`);
  process.exit(1);
});
