---
name: "fsbo-landfinder"
description: "Search byowner.com for FSBO land listings with pagination support"
---

# FSBO Land Finder Skill

## Trigger
User says: "FSBO land finder [location]" or "Find FSBO land in [location]"

## Purpose
Search byowner.com for land listings (property type = land) in a specified location. Extract listing details and output structured data with direct links back to listings.

## ELIMINATION CRITERIA
**REMOVE these owner types:**
- LLC (Limited Liability Company)
- Corp / Corporation
- LP / Limited Partnership
- Trust
- Holding Company
- Development Company
- Investment Group

**KEEP these owner types:**
- Individual / Person
- Family (mom, dad, estate)
- Couple (husband & wife)
- Estate (deceased owner)
- Heirs

## URL Pattern
```
https://www.byowner.com/{city}/{state}/property-type=land
https://www.byowner.com/{city}/{state}/property-type=land/page={n}
```

**Examples:**
- Austin, TX page 1: `https://www.byowner.com/austin/texas/property-type=land`
- Austin, TX page 2: `https://www.byowner.com/austin/texas/property-type=land/page=2`
- Austin, TX page 26: `https://www.byowner.com/austin/texas/property-type=land/page=26`

## Procedure

### Step 1: Determine Page Count
Load page 1 and check pagination for total pages. The site shows page numbers (1, 2, 3... 26) and a "Last" link.

### Step 2: Scrape Pages (Configurable Depth)
**Option A - Quick Scan (default):**
- Scrape only page 1 (20 listings)
- Fast, good for initial recon

**Option B - Deep Scan:**
- Scrape pages 1-5 (100 listings)
- Good for comprehensive search
- Add 2-second delay between pages to avoid rate limiting

**Option C - Full Scan:**
- Scrape ALL pages (up to 26 pages = 520 listings)
- Use only when needed
- Add 3-second delay between pages

### Step 3: Extract Data Per Page
For each listing card on the page, extract:
- **Address** (from listing title)
- **Price** (dollar amount)
- **Acreage** (from "X Acres(Lot)" or "X Acre(Lot)")
- **City, State, ZIP** (from address line)
- **Listing URL** (direct link to byowner.com page)
- **Status** (Active, Pending, Active Under Contract)
- **Bed/Bath/Sqft** (if present - indicates house on lot)

### Step 4: Filter by Owner Type
For each listing, determine if the seller is an individual or corporate entity:

**Corporate indicators (REMOVE):**
- Name contains: LLC, Inc, Corp, Ltd, LP, Trust, Holdings, Properties, Development, Investment, Group, Partners
- No individual name (just "FSBO Seller" or generic)
- Business email domain

**Individual indicators (KEEP):**
- First + Last name format
- "Estate of..." or "Heirs of..."
- Family references in description

### Step 5: Score Each Remaining Listing
Apply scoring rubric (1-10) for individual-owner listings only:

**Price vs Market (0-3):**
- 3: <50% of comparable land prices
- 2: 50-70% of comps
- 1: 70-90% of comps
- 0: >90% of comps

**Seller Motivation Signals (0-2):**
- 2: Keywords: "motivated," "must sell," "urgent," "reduced," "price drop"
- 1: Keywords: "flexible," "negotiable," "OBO"
- 0: No motivation signals

**Acreage Fit (0-2):**
- 2: 0.25-5 acres (ideal for residential flip)
- 1: 5-20 acres
- 0: <0.25 acres or >20 acres

**Location Quality (0-2):**
- 2: Near growing city, new development, good road access
- 1: Rural but accessible
- 0: Remote, no road access, flood zone

**Listing Quality (0-1):**
- 1: Has photos, detailed description, contact info
- 0: No photos, vague description

### Step 6: Output Format

Return results as markdown table with TOP DEALS highlighted:

```markdown
## ⭐ TOP DEALS (Individual Owners Only)
| Score | Address | Price | Acres | Status | Link |
|-------|---------|-------|-------|--------|------|
| 8 | 1201 Fort Branch Blvd, Austin TX | $135,000 | 0.23 | Active | [View](URL) |

## ALL OTHER LISTINGS (Individual Owners)
| Score | Address | Price | Acres | Status | Link |
|-------|---------|-------|-------|--------|------|
| 5 | 6631 Lost Horizon Dr, Austin TX | $425,000 | 0.25 | Under Contract | [View](URL) |
```

Also provide JSON export for dashboard integration:
```json
{
  "listings": [
    {
      "id": "fsbo_tx_001",
      "address": "1201 Fort Branch Blvd",
      "city": "Austin",
      "state": "TX",
      "zip": "78721",
      "price": 135000,
      "acreage": 0.23,
      "status": "Active",
      "url": "https://www.byowner.com/land/austin/1201-fort-branch-boulevard-tx-78721-4877039",
      "score": 8,
      "source": "ByOwner.com FSBO"
    }
  ]
}
```

### Step 7: Red Flags — SKIP These
- Corporate/trust owner (already filtered)
- No road access mentioned
- Price >150% of local comps
- "Owner financing" with high interest
- Vague location (no address or cross streets)
- Listed >180 days (stale)
- No photos AND no description

### Step 8: Green Flags — PRIORITIZE
- Individual owner (not corporate)
- "Motivated seller" in description
- Price reduced
- Inherited land
- Relocating / moving
- Multiple lots available
- Utilities already on site

## Usage Examples

**Quick scan (default):**
```
User: "FSBO land finder Austin TX"
```

**Deep scan (pages 1-5):**
```
User: "FSBO land finder Austin TX deep scan"
```

**Full scan (all pages):**
```
User: "FSBO land finder Austin TX all pages"
```

## Notes
- byowner.com listings are EXCLUSIVE (not on MLS)
- Direct owner contact — no realtor gatekeeping
- FSBO sellers often price below market (no agent commission)
- Check listings daily — new ones appear regularly
- Corporate owners = harder negotiation, less motivated
- Individual owners = more flexible, faster deals
- Always include `sourceUrl` linking back to original listing
- Page delay: 2-3 seconds between requests to avoid blocking
