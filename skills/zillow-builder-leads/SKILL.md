---
name: zillow-builder-leads
description: Find home builders who have built and sold homes in the past year. Extract builder contact information from Zillow listings and new construction data.
metadata:
  openclaw:
    requires:
      env: ["RAPIDAPI_KEY"]
    always: true
---

# Zillow Builder Leads Skill

Find active home builders in any market and extract their contact information. 

## What This Skill Does

1. **Searches new construction listings** on Zillow for a given area
2. **Filters to past 12 months** — only recently built/sold homes
3. **Identifies builders** from listing data and new construction communities
4. **Extracts contact info**: builder name, phone, website, address, agent contacts
5. **Outputs structured data** ready for CRM import or outreach

## Setup

Get a RapidAPI key for the Zillow API:
1. Go to https://rapidapi.com/apidojo/api/zillow1/
2. Subscribe (free tier: 100 requests/month)
3. Copy your API key

Set environment variable:
```bash
export RAPIDAPI_KEY="your-key-here"
```

## Usage Patterns

### Find Builders in a City

```bash
# Search for new construction in Austin, TX
node {baseDir}/scripts/find-builders.js "Austin, TX" --days 365 --output builders-austin.json
```

### Find Builders by ZIP Code

```bash
# Target specific ZIP
node {baseDir}/scripts/find-builders.js "78701" --days 365 --type new_construction
```

### Extract Full Contact Details

```bash
# Deep dive on a specific builder community
node {baseDir}/scripts/extract-builder-details.js "https://www.zillow.com/community/the-grove-at-austin/"
```

### Generate Outreach CSV

```bash
# Export to CSV for mail merge / CRM
node {baseDir}/scripts/export-csv.js builders-austin.json --output leads.csv
```

## Data Extracted

For each builder identified:

| Field | Source | Example |
|-------|--------|---------|
| `builder_name` | Listing agent / community page | "Lennar Homes" |
| `phone` | Listing contact / agent profile | "(512) 555-0123" |
| `email` | Agent profile / website scrape | "sales@lennar.com" |
| `website` | Builder website from listing | "https://www.lennar.com" |
| `address` | Community address | "12345 Builder Way, Austin, TX" |
| `agent_name` | Listing agent | "John Smith" |
| `agent_phone` | Agent direct line | "(512) 555-0199" |
| `agent_email` | Agent email | "john.smith@lennar.com" |
| `brokerage` | Agent's brokerage | "Keller Williams Realty" |
| `community_name` | New construction community | "The Grove at Austin" |
| `price_range` | From listings | "$350,000 - $500,000" |
| `home_types` | From listings | "Single Family, Townhomes" |
| `year_built` | Construction year | 2024 |
| `sale_date` | Recent sale date | "2024-03-15" |
| `sale_price` | Recent sale price | 425000 |
| `zpid` | Zillow property ID | 12345678 |
| `listing_url` | Direct Zillow link | "https://zillow.com/..." |

## How It Works

### Step 1: Search New Construction

Uses Zillow's `propertyExtendedSearch` with filters:
- `home_type=NewConstruction`
- `daysOnZillow=365` (past year)
- Location: city, ZIP, or coordinates

### Step 2: Identify Builders

From each listing, extracts:
- Builder name from description patterns ("built by X", "X Homes presents")
- Agent/broker info from listing attribution
- Community name from URL or page data

### Step 3: Enrich Contact Data

For each unique builder:
- Fetches agent profile page for contact details
- Searches builder website for corporate contact info
- Cross-references with public records where available

### Step 4: Deduplicate & Validate

- Merges duplicate builder entries
- Validates phone numbers (format check)
- Removes incomplete records (configurable threshold)

## Output Formats

### JSON (Detailed)
```json
{
  "search_params": {
    "location": "Austin, TX",
    "days": 365,
    "total_results": 156
  },
  "builders": [
    {
      "builder_name": "Lennar Homes",
      "contact": {
        "phone": "(512) 555-0123",
        "email": "austin@lennar.com",
        "website": "https://www.lennar.com/new-homes/texas/austin"
      },
      "communities": [
        {
          "name": "The Grove at Austin",
          "address": "12345 Builder Way, Austin, TX 78701",
          "price_range": { "min": 350000, "max": 500000 },
          "home_types": ["Single Family", "Townhomes"],
          "recent_sales": [
            { "date": "2024-03-15", "price": 425000, "zpid": 12345678 }
          ]
        }
      ],
      "agents": [
        {
          "name": "John Smith",
          "phone": "(512) 555-0199",
          "email": "john.smith@kw.com",
          "brokerage": "Keller Williams Realty"
        }
      ],
      "total_sales_12mo": 23,
      "avg_sale_price": 412500,
      "data_quality_score": 0.85
    }
  ]
}
```

### CSV (Outreach Ready)
```csv
builder_name,phone,email,website,community_count,total_sales_12mo,avg_price,primary_agent,agent_phone,first_sale_date
Lennar Homes,(512) 555-0123,austin@lennar.com,https://lennar.com,3,23,412500,John Smith,(512) 555-0199,2024-01-15
```

## Important Notes

### Data Limitations
- Zillow API rate limits: 100-10000 requests/month depending on plan
- Not all builders list on Zillow (some use MLS only)
- Contact info may be agent (not builder direct) — always verify
- New construction data varies by market density

### Legal & Ethical
- Comply with CAN-SPAM if emailing
- Respect Do Not Call registry for phone outreach
- Check state regulations for builder solicitation
- This tool is for research — verify all data before outreach

### Accuracy Tips
- Cross-reference builder websites for current info
- Call numbers to verify before adding to CRM
- Check for builder name variations ("Lennar" vs "Lennar Homes")
- Use multiple search areas to catch all active builders

## Related Skills
- `zillow-real-estate` — General property search
- `property-investment-analysis` — Analyze builder communities for investment
- `crm-import` — Import leads to your CRM

## Troubleshooting

**No results found?**
- Try broader location (city instead of ZIP)
- Increase daysOnZillow (some markets slower)
- Check if Zillow has new construction data for that area

**Missing contact info?**
- Agent profiles often have more detail than listing pages
- Builder websites usually have "Contact Us" pages
- Some builders only work through preferred agents

**Rate limited?**
- Upgrade RapidAPI plan
- Add delays between requests
- Use cached results when possible
