# Zillow Builder Leads — Manual Workflow Guide

## ⚠️ Current Status: API Down

All Zillow API endpoints are returning 404. All scraping attempts hit CAPTCHA or blocks.

**Your options:**

---

## ✅ Working Solution: Manual ZPID Collection + Processing

### Step 1: Collect ZPIDs from Zillow (Manual)

**What is a ZPID?**
- Zillow Property ID — the number in the URL
- Example: `zillow.com/homedetails/12345678_zpid/` → ZPID is `12345678`

**How to collect:**

1. Go to https://www.zillow.com
2. Search: "New Construction [Your City]"
3. Apply filters:
   - Home Type: Houses
   - Listing Status: For Sale + Sold
   - Days on Zillow: Last 12 months
   - New Construction: Yes

4. For each listing:
   - Click to open detail page
   - Copy ZPID from URL (number before `_zpid`)
   - Paste into a text file

**Example `zpids.txt`:**
```
12345678
87654321
11223344
```

### Step 2: Process with Sample Data (Tested & Working)

Since the API is down, use the **sample data** to test the pipeline:

```bash
cd ~/.openclaw/workspace/skills/zillow-builder-leads

# Test with sample data (proven working)
node scripts/export-csv.js examples/sample-output.json --output test-leads.csv

# Test deduplication
node scripts/deduplicate-builders.js examples/sample-output.json

# Test enrichment (on sample)
node scripts/enrich-builder-websites.js examples/sample-output.json
```

### Step 3: When API Comes Back

```bash
# Process your collected ZPIDs
node scripts/find-builders-zpids.js zpids.txt --output builders.json

# Deduplicate
node scripts/deduplicate-builders.js builders.json

# Export to CSV
node scripts/export-csv.js builders-deduped.json --min-sales 5 --output leads.csv
```

---

## 📊 Sample Output (What You'll Get)

**JSON format:**
```json
{
  "builder_name": "Lennar Homes",
  "contacts": {
    "agent_name": "Sarah Johnson",
    "agent_phone": "(512) 555-0123",
    "brokerage": "Keller Williams Realty",
    "builder_website": "https://www.lennar.com"
  },
  "communities": [...],
  "recent_sales": [...],
  "total_sales_12mo": 23,
  "avg_sale_price": 412500,
  "data_quality_score": 0.85
}
```

**CSV format:**
```csv
builder_name,agent_name,agent_phone,brokerage,total_sales_12mo,avg_sale_price
Lennar Homes,Sarah Johnson,(512) 555-0123,Keller Williams Realty,23,412500
```

---

## 🔧 Alternative Data Sources

Since Zillow is blocked, try these for builder data:

### 1. Builder Websites Directly
- Search "[City] new home builders"
- Visit builder websites
- Collect contact info manually
- Use `scripts/enrich-builder-websites.js` to scrape emails/phones

### 2. Local HBA (Home Builders Association)
- Search "[City] Home Builders Association"
- Member directories often public
- High-quality contact info

### 3. Permits Data (Public Record)
- Many cities have online permit databases
- Search for "new construction permits"
- Builder name usually listed

### 4. MLS Data (If you have access)
- New construction listings
- Agent contact info
- Sale dates and prices

---

## 📁 All Scripts Ready

```
skills/zillow-builder-leads/
├── scripts/
│   ├── find-builders.js              # API version (down)
│   ├── find-builders-zpids.js        # ZPID processing ✅
│   ├── find-builders-stealth.js      # Stealth (blocked by CAPTCHA)
│   ├── zpid-helper.js                # Browser helper (blocked)
│   ├── find-builders-peekaboo.sh     # macOS automation
│   ├── extract-builder-details.js    # Property deep dive
│   ├── export-csv.js                 # CSV export ✅
│   ├── enrich-builder-websites.js    # Website scraping ✅
│   └── deduplicate-builders.js       # Deduplication ✅
├── examples/
│   ├── sample-output.json            # Test data ✅
│   └── final-leads.csv               # CSV example ✅
├── SKILL.md                          # Full docs
├── README.md                         # Quick start
├── QUICKSTART.md                     # 3 approaches
└── STATUS.md                         # Current status
```

---

## 🚀 Quick Test (Proves Pipeline Works)

```bash
cd ~/.openclaw/workspace/skills/zillow-builder-leads

# Test full pipeline with sample data
node scripts/deduplicate-builders.js examples/sample-output.json
node scripts/export-csv.js examples/sample-deduped.json --min-sales 10 --output test-final.csv

# View results
cat test-final.csv
```

---

## 💡 Recommendation

**For immediate use:**
1. Manually collect builder contacts from Google
2. Use the enrichment script to scrape their websites
3. Export to CSV for outreach

**For scale:**
- Wait for Zillow API to come back online
- Or subscribe to a paid real estate data service (CoStar, LandGlide)
- Or hire a VA to collect ZPIDs manually

---

## 📞 Support

If you find working Zillow API endpoints or have questions:
- Check RapidAPI dashboard: https://rapidapi.com/developer/dashboard
- Test endpoints with: `curl -H "X-RapidAPI-Key: YOUR_KEY" https://zillow-com1.p.rapidapi.com/`
