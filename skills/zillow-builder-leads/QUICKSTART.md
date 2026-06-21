# Zillow Builder Leads — Complete Solution (3 Approaches)

## What's New

Added 3 working approaches to bypass anti-bot measures:

| Approach | File | Best For | Effort |
|----------|------|----------|--------|
| **ZPID Helper** | `scripts/zpid-helper.js` | Manual browsing, highest accuracy | Medium |
| **Stealth Scraper** | `scripts/find-builders-stealth.js` | Automated, may bypass detection | Low |
| **Peekaboo** | `scripts/find-builders-peekaboo.sh` | macOS UI automation | Medium |

---

## Approach 1: ZPID Helper (Recommended)

Opens a browser for you to manually browse Zillow, then collects ZPIDs you paste.

```bash
# Open browser to Zillow new construction
node scripts/zpid-helper.js "Austin, TX"

# Follow prompts:
# 1. Browser opens to Zillow
# 2. Browse listings, click for details
# 3. Copy ZPID from URL (e.g., zillow.com/homedetails/12345678_zpid/)
# 4. Paste ZPIDs in terminal
# 5. Type "done" when finished

# Then process:
node scripts/find-builders-zpids.js zpids-austin-tx.txt
node scripts/export-csv.js builders-*.json --output leads.csv
```

---

## Approach 2: Stealth Scraper

Uses puppeteer-extra with stealth plugins to bypass bot detection.

```bash
# Install dependencies
npm install puppeteer-extra puppeteer-extra-plugin-stealth

# Run stealth scraper
node scripts/find-builders-stealth.js "Austin, TX" --pages 3

# If CAPTCHA appears, run with visible browser:
node scripts/find-builders-stealth.js "Austin, TX" --headless false --pages 3
```

**How it works:**
- Spoofs browser fingerprint
- Masks automation flags
- Uses human-like headers
- Can solve CAPTCHA manually if visible

---

## Approach 3: Peekaboo (macOS Only)

Uses macOS UI automation to browse Zillow and extract data.

```bash
# Install Peekaboo if needed
brew install steipete/tap/peekaboo

# Run automation
./scripts/find-builders-peekaboo.sh "Austin, TX"

# Follow prompts to enter ZPIDs, then:
node scripts/find-builders-zpids.js zpids-peekaboo-*.txt
```

**What it does:**
1. Opens Chrome to Zillow new construction
2. Takes screenshot
3. Prompts you to enter ZPIDs from browsing
4. Saves to file for processing

---

## Quick Reference

### What is a ZPID?

**Zillow Property ID** — a unique number for every property on Zillow.

**How to find it:**
1. Go to any Zillow listing
2. Look at the URL: `zillow.com/homedetails/12345678_zpid/`
3. The ZPID is `12345678`

**Why use ZPIDs?**
- Direct access to property data
- Bypass search limitations
- More reliable than scraping

### Full Workflow

```bash
# Step 1: Collect ZPIDs (choose one method)
node scripts/zpid-helper.js "Austin, TX"                    # Manual
node scripts/find-builders-stealth.js "Austin, TX"          # Automated
./scripts/find-builders-peekaboo.sh "Austin, TX"           # macOS UI

# Step 2: Process ZPIDs
node scripts/find-builders-zpids.js zpids.txt --output builders.json

# Step 3: Deduplicate
node scripts/deduplicate-builders.js builders.json

# Step 4: Enrich with website data (optional)
node scripts/enrich-builder-websites.js builders-deduped.json --find-emails

# Step 5: Export to CSV
node scripts/export-csv.js builders-deduped-enriched.json \
  --min-sales 5 \
  --quality 0.6 \
  --output austin-leads.csv
```

---

## Files

```
skills/zillow-builder-leads/scripts/
├── find-builders.js              # RapidAPI (needs fix)
├── find-builders-zpids.js        # ✅ ZPID processing
├── find-builders-stealth.js      # ✅ NEW: Stealth scraper
├── find-builders-scraper.js      # Playwright (blocked)
├── find-builders-realtor.js      # Realtor (blocked)
├── find-builders-redfin.js       # Redfin (redirects)
├── zpid-helper.js                # ✅ NEW: Manual ZPID collection
├── find-builders-peekaboo.sh     # ✅ NEW: macOS automation
├── extract-builder-details.js    # Property deep dive
├── export-csv.js                 # CSV export
├── enrich-builder-websites.js    # Website scraping
└── deduplicate-builders.js       # Deduplication
```

---

## Troubleshooting

**Stealth scraper still blocked?**
- Run with `--headless false` to solve CAPTCHA manually
- Try different location format: "Austin TX" instead of "Austin, TX"
- Increase wait time in script

**ZPID helper not opening browser?**
- Check Playwright is installed: `npx playwright install chromium`
- Try running with `--auto-extract` flag

**Peekaboo not working?**
- Check permissions: `peekaboo permissions`
- Ensure Chrome is in Applications folder

---

## API Key Status

Your RapidAPI key (`75d9759aa4mshbb672cae5345b37p14efbfjsne5a460330e3a`) is valid, but Zillow endpoints are deprecated. These scripts work around that limitation.
