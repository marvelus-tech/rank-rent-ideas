---
name: "craigslist-landfinder"
description: "Automated Craigslist land deal finder - scrapes FSBO land listings, filters for underpriced deals, and outputs structured data with links"
---

# Craigslist Land Finder Skill

## Overview

Systematically search Craigslist "real estate - by owner" sections across target markets to find underpriced land for sale by owner (FSBO). This is a proven strategy used by land wholesalers and flippers to find off-market deals before they hit MLS or investor networks.

## Why Craigslist Works for Land Deals

- **Free to list** → attracts FSBO sellers who want to avoid realtor fees
- **Local buyer reach** → sellers often don't know true market value
- **Underpriced listings** → owners often price based on tax value or emotional attachment, not comps
- **Less competition** → most investors focus on houses, not land
- **Direct owner contact** → no realtor gatekeeping

## Trigger

Use this skill when user says:
- "Find land deals on Craigslist"
- "Craigslist land finder [location]"
- "Search Craigslist for land for sale by owner"
- "Find underpriced land listings"
- "Craigslist land scraping"

## Procedure

### Step 1: Build Targeted Search URLs

For each target market, construct Craigslist search URLs:

```
https://[city].craigslist.org/search/rea?purveyor=owner&query=land
```

Replace `[city]` with Craigslist subdomain for target market:
- Austin: `austin`
- Houston: `houston`
- Raleigh: `raleigh`
- Nashville: `nashville`
- Charlotte: `charlotte`
- Dallas: `dallas`
- San Antonio: `sanantonio`
- Atlanta: `atlanta`
- Phoenix: `phoenix`
- Tampa: `tampa`

**Advanced search parameters:**
- `purveyor=owner` — FSBO only (no realtors)
- `query=land` — search term
- `min_price=0&max_price=50000` — price filter for underpriced deals
- `minSqft=10000` — minimum lot size (approx 0.25 acres)
- `postedToday=1` — only today's listings
- `sort=date` — newest first

### Step 2: Execute Search via Browser

Use `browser` tool to:
1. Navigate to constructed URL
2. Wait for listings to load
3. Extract listing data

### Step 3: Extract Listing Data

For each listing found, capture:

```json
{
  "title": "Listing title",
  "price": "$XX,XXX",
  "location": "City, State",
  "link": "https://[city].craigslist.org/reo/d/...",
  "postedDate": "2026-06-25",
  "description": "Listing description snippet",
  "acres": "X.X",
  "pricePerAcre": "$X,XXX",
  "redFlags": ["flag1", "flag2"],
  "opportunityScore": "1-10"
}
```

### Step 4: Filter & Score Opportunities

**Red flags to skip:**
- "owner financing" with high interest
- "RV park" or "mobile home" (unless that's your strategy)
- "land contract" (complicated legal structure)
- No photos or vague description
- Price per acre > 150% of local comps
- "Must sell today" (often scams)
- No road access mentioned

**Green flags to prioritize:**
- "Motivated seller"
- "Inherited land"
- "Unwanted land"
- "Vacant lot"
- "Buildable"
- "Utilities available"
- Price per acre < 70% of comps
- Listed > 30 days (seller fatigue)

**Scoring criteria (1-10):**
- Price vs comps (0-3 points)
- Seller motivation signals (0-2 points)
- Lot size fit (0-2 points)
- Location quality (0-2 points)
- Description completeness (0-1 point)

### Step 5: Output Structured Results

Format as markdown table or JSON for dashboard import:

```markdown
| Title | Price | Acres | $/Acre | Location | Score | Link |
|-------|-------|-------|--------|----------|-------|------|
| 5 Acres FSBO | $25,000 | 5.0 | $5,000 | Austin, TX | 8 | [View](link) |
```

### Step 6: Follow-Up Actions

For high-scoring deals (7+):
1. Open listing to get full description
2. Extract seller contact info
3. Cross-reference with county GIS/tax records
4. Check flood zones, zoning, utilities
5. Add to land flip dashboard "Lots" tab

## Example Search Commands

```bash
# Austin TX land under $50k
https://austin.craigslist.org/search/rea?purveyor=owner&query=land&max_price=50000

# Houston area land, newest first
https://houston.craigslist.org/search/rea?purveyor=owner&query=land&sort=date

# Raleigh NC, minimum 0.5 acres
https://raleigh.craigslist.org/search/rea?purveyor=owner&query=land&minSqft=20000
```

## Integration with Land Flip Dashboard

Export findings as CSV or directly update dashboard:

```json
{
  "id": 501,
  "address": "TBD - See Craigslist Listing",
  "county": "Travis County",
  "state": "texas",
  "city": "Austin",
  "zip": "787xx",
  "acres": 5.0,
  "price": 25000,
  "status": "identified",
  "date": "2026-06-25",
  "notes": "Craigslist FSBO. 5 acres. $5k/acre. Motivated seller. Link: [URL]",
  "source": "Craigslist FSBO",
  "craigslistLink": "https://austin.craigslist.org/reo/d/..."
}
```

## Daily Automation

For daily monitoring, set up:
1. Cron job to search each market at 8 AM local time
2. Compare new listings against previous day's results
3. Alert on new high-scoring opportunities (7+)
4. Skip duplicates by tracking listing IDs

## Tools Used

- `browser` — Navigate and scrape Craigslist
- `web_fetch` — Extract listing details
- `web_search` — Cross-reference pricing with comps
- `message` — Send alerts for hot deals
- `cron` — Schedule daily searches

## Output Format

Always include:
1. **Search summary** — Markets searched, listings found
2. **Top opportunities** — Scored 7+ with full details
3. **Direct links** — Back to original Craigslist listings
4. **Next steps** — Recommended follow-up actions
5. **Dashboard update** — JSON/CSV for import

## Notes

- Craigslist blocks aggressive scraping — use reasonable delays
- Listings expire quickly (7-45 days) — check daily
- "By owner" filter is critical — realtor listings are usually priced at market
- Always verify seller actually owns the property before making offers
- Price per acre is the key metric — compare to local comps on LandWatch, Zillow
- Best deals often have poor photos or minimal descriptions — diamonds in the rough
