# Zillow Builder Leads Skill

Find home builders who have completed and sold homes in the past year, with contact information extraction.

## What It Does

- Scrapes Zillow for new construction and recently sold homes
- Identifies builders by name from listing descriptions and agent info
- Cross-references with builder databases and public records
- Extracts builder contact information (phone, email, website)
- Outputs structured data for lead generation

## Requirements

- Node.js 18+
- Firecrawl API key (free tier: 500 credits)
- Environment variables (see `.env.example`)

## Installation

```bash
cd ~/.openclaw/workspace/skills/zillow-builder-leads
npm install
```

## Usage

### Basic Search
```bash
node scripts/find-builders.js --city "Austin" --state "TX" --days 365
```

### With Output
```bash
node scripts/find-builders.js --city "Dallas" --state "TX" --days 365 --output leads.json
```

### Enrich with Contact Info
```bash
node scripts/find-builders.js --city "Houston" --state "TX" --days 365 --enrich --output leads.json
```

## Output Format

```json
{
  "builders": [
    {
      "name": "Lennar Homes",
      "homesSold": 12,
      "priceRange": "$350K - $650K",
      "cities": ["Austin", "Round Rock"],
      "contact": {
        "phone": "(512) 555-0123",
        "website": "https://www.lennar.com",
        "email": "austin@lennar.com"
      },
      "listings": [...]
    }
  ]
}
```

## How It Works

1. **Scrape Zillow** — Uses Firecrawl to bypass bot detection
2. **Filter by Date** — Only homes sold/built in past year
3. **Identify Builders** — From listing descriptions, agent info, community names
4. **Extract Contact Info** — Scrape builder websites, public records
5. **Deduplicate** — Group by builder name, count homes sold
6. **Output** — Structured JSON with leads ranked by activity

## API Endpoints

If you want to use this as a service:

```bash
# Start the API server
node server.js

# Search for builders
curl "http://localhost:3000/api/builders?city=Austin&state=TX&days=365"
```

## Files

| File | Purpose |
|------|---------|
| `scripts/find-builders.js` | Main CLI script |
| `lib/scraper.js` | Zillow scraping logic |
| `lib/enricher.js` | Contact info extraction |
| `lib/formatter.js` | Output formatting |
| `examples/` | Example outputs |

## Notes

- Zillow changes their site frequently; scrapers may need updates
- Firecrawl handles bot detection but costs credits
- Builder contact info is public data from websites and records
- Always comply with CAN-SPAM and local regulations for outreach

## Built-in Skills to Add

Other skills planned for this ecosystem:
- **Redfin Builder Leads** — Alternative data source
- **Permit Scraper** — City permit data for new construction
- **Builder Website Scraper** — Extract contact info from builder sites
- **CRM Integration** — Export to HubSpot, Salesforce, Pipedrive
- **Email Sequencer** — Automated outreach campaigns
- **LinkedIn Enricher** — Find builder decision-makers
- **Google Maps Scraper** — Builder office locations and reviews
- **Apollo.io Integration** — B2B contact database enrichment

## License

MIT — Built for MarvelUs
