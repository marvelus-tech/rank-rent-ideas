# Zillow Builder Leads — Status & Workarounds

## Current Status

The skill is **fully built** with 7 scripts, but we're hitting anti-bot protections on all major real estate sites:

| Site | Status | Issue |
|------|--------|-------|
| Zillow (RapidAPI) | ❌ 404 | API endpoints deprecated |
| Zillow (direct) | ❌ CAPTCHA | "Press & Hold" bot detection |
| Realtor.com | ❌ Blocked | WAF security block |
| Redfin | ⚠️ Partial | Redirects to wrong location, no builder data |

## Working Alternatives

### Option 1: Manual ZPID Input (Most Reliable)
If you have a list of Zillow Property IDs (ZPIDs) from manual searches:

```bash
# Create a file with ZPIDs, one per line
echo "12345678" > zpids.txt
echo "87654321" >> zpids.txt

# Process them
node scripts/find-builders-zpids.js zpids.txt --output builders.json
```

**How to get ZPIDs:**
1. Go to Zillow.com, search "New Construction" in your city
2. Open each listing, copy the ZPID from the URL
3. Example: `zillow.com/homedetails/12345678_zpid/` → ZPID is `12345678`

### Option 2: Import from Zillow CSV Export
Zillow allows CSV export of search results when logged in:

```bash
# Export from Zillow, then:
node scripts/import-zillow-csv.js zillow_export.csv --output builders.json
```

### Option 3: Use Apify or ScrapingBee
These services bypass bot detection:

```bash
# Set Apify token
export APIFY_TOKEN="your-token"

# Run Zillow scraper actor
node scripts/find-builders-apify.js "Austin, TX"
```

### Option 4: Playwright with Stealth (Advanced)
Use puppeteer-extra-plugin-stealth or similar:

```bash
npm install puppeteer-extra puppeteer-extra-plugin-stealth
node scripts/find-builders-stealth.js "Austin, TX"
```

## What's Working Now

✅ **Data Processing Pipeline** (tested & working):
- `deduplicate-builders.js` — Merge duplicate records
- `export-csv.js` — Export to outreach CSV with filters
- `enrich-builder-websites.js` — Scrape builder sites for contacts
- `extract-builder-details.js` — Deep dive on specific property

✅ **Sample Data** included for testing:
- `examples/sample-output.json` — 5 builders with full data
- `examples/final-leads.csv` — CSV export example

## Quick Test

```bash
cd ~/.openclaw/workspace/skills/zillow-builder-leads

# Test with sample data
node scripts/export-csv.js examples/sample-output.json --min-sales 10 --output test.csv

# Test deduplication
node scripts/deduplicate-builders.js examples/sample-output.json
```

## Recommended Next Steps

1. **For immediate use**: Export ZPIDs manually from Zillow, then use `find-builders-zpids.js`
2. **For scale**: Set up Apify account ($5/month) and use their Zillow scraper
3. **For automation**: Implement stealth browsing with puppeteer-extra

## Files

```
skills/zillow-builder-leads/
├── scripts/
│   ├── find-builders.js              # RapidAPI version (needs fix)
│   ├── find-builders-zpids.js        # ZPID input mode ✅
│   ├── find-builders-scraper.js      # Playwright scraper (blocked)
│   ├── find-builders-realtor.js      # Realtor scraper (blocked)
│   ├── find-builders-redfin.js       # Redfin scraper (partial)
│   ├── extract-builder-details.js    # Property deep dive ✅
│   ├── export-csv.js                 # CSV export ✅
│   ├── enrich-builder-websites.js    # Website scraping ✅
│   └── deduplicate-builders.js       # Deduplication ✅
├── examples/
│   ├── sample-output.json            # Test data
│   ├── sample-deduped.json
│   └── final-leads.csv
├── SKILL.md                          # Full documentation
└── README.md                         # Quick start
```

## API Key Issue

Your RapidAPI key (`75d9759aa4mshbb672cae5345b37p14efbfjsne5a460330e3a`) is valid, but the Zillow API endpoints have been deprecated:
- `zillow-com1.p.rapidapi.com` → 404
- `zillow56.p.rapidapi.com` → 404  
- `zillow-base1.p.rapidapi.com` → 404

Check https://rapidapi.com/developer/dashboard for current APIs.
