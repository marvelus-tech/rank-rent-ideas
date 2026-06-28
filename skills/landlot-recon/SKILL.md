---
name: "landlot-recon"
description: "Find land lots in a given market: tax-delinquent seller sourcing, TRUEPEOPLESEARCH enrichment, 7-point underwriting checklist, buyers-first wholesaling."
---

# LandLot-recon Skill

## Overview
Execute the full land lot reconnaissance and wholesale pipeline for a given market location. Finds tax-delinquent land owners, enriches with contact info, screens via underwriting checklist, and prepares for land flipping. Appends findings to dashboard Lots table.

## Workflow

### Step 1: Identify Buyers for the Market (Buyers-First)
Before sourcing leads, know who will buy. This determines your buy box.

1. Go to **Zillow → New Home Builders** (zillow.com/new-home-builders)
2. Enter the target market/city
3. Collect the top 20-30 active builders
4. Visit each builder's "Contact Us" page
5. Ask for **Land Acquisition Department** (not sales)
6. Get their **Buy Box**:
   - What counties/areas do they buy in?
   - Minimum/Maximum lot size (e.g., lots 0.25-2 ac)
   - Price they'll pay per lot (e.g., $160k for infill)
   - Build-ready required? (utilities, road access, flat)
   - Timeline / number of homes per year

### Step 2: Find Tax-Delinquent Land Owners

#### Free Method (County Website):
1. Go to county assessor/treasurer website for target county
2. Find "Online Record Search" or "Tax Search"
3. Search for **tax-delinquent** properties
4. Filter for **land/vacant lots** (not improved property)
5. Export/gather:
   - Owner name
   - Parcel address
   - Assessed value
   - Tax amount owed
   - Parcel ID/APN

#### Paid Method (XLeads - ~$80/month):
1. Go to xleads.com
2. Search by target city/county
3. Filter: **Tax Delinquent** + **Land** type
4. Download results (includes phone numbers)
5. Can text-blast leads en masse

### Step 3: Owner/Contact Enrichment

#### Free Enrichment (for county-sourced leads):
1. Take owner name + property address from county records
2. Paste into **truepeoplesearch.com**
3. Extract phone number(s) and associated persons
4. Can also use: spokeo.com, beenverified.com, whitepages.com

#### Paid Enrichment (skip if using XLeads):
- Already included in XLeads download
- Skip to Step 4

### Step 4: Reach Out (Outbound)

#### Texting (mass scale):
- Use XLeads/SkipLeads download → import to texting platform
- Simple script: "Hey [First Name], I'm calling about your lot on [Address]. My partners and I are cash buyers looking for land in the area. By chance, are you interested in selling?"

#### Calling:
- Script: "Hi [Name], I'm [Your Name] — I was calling about your lot on [Street/Address]. My partners and I buy land in the area. We're cash buyers and can close very quickly. Are you interested in selling?"
- If interested → ask "How much do you want for it?"
- Know the buyer's max price — you'll offer less

### Step 5: Underwriting Checklist (7-Point Screen)

For each parcel, evaluate (use regrid.com or XLeads):

1. **Infill vs Raw Land** — Infill preferred (houses on both sides, build-ready)
2. **Utilities** — Electrical poles visible? Water/sewer at street?
3. **Terrain** — Flat or sloped? Buildable?
4. **Clearing** — Cleared or treed? Trees = expensive to clear
5. **Road Access** — Paved road frontage? If no, pass
6. **Flood Zone** — 500-yr OK, 100-yr BAD (check FEMA flood maps)
7. **Zoning** — Residential allowed? Density? Duplex/multifamily?

### Step 6: Comp & Price

Using Zillow:
- Filter for SOLD lots (last 6 months)
- Compare similar size/characteristics
- Cross-reference with buyer's stated max price
- Your offer = buyer's max price minus your assignment fee
- Target assignment fee: $10k-$40k+

### Step 7: Contract & Close

1. **PSA** (Purchase & Sale Agreement) — get signed by seller
2. **Assignment Agreement** — assign rights to buyer
3. **Title Company** — must be investor-friendly:
   - Ask: "Do you work with wholesalers?" → should say yes
   - Ask: "Do you do assignment of contracts?" → must be yes  
   - Ask: "Do you do double closing?" → bonus if yes
   - Find via: Facebook real estate investor groups for that area
4. Submit both contracts → title processes → funding

## Output Format (Dashboard Append)

Each lot record should be appended to the Lots table with these fields:

| Field | Type | Description |
|-------|------|-------------|
| propertyAddress | string | Street address of the lot |
| county | string | County name |
| state | string | State key (e.g., 'texas') |
| ownerName | string | Current owner from tax records |
| assessedValue | string | Tax assessed value |
| taxDelinquentAmount | string | Amount owed in back taxes |
| apn | string | Parcel ID/APN |
| lotSize | string | Acres or dimensions |
| buyBoxMatch | string | Which builder/lot size criteria it fits |
| buyerMax | number | What the buyer will pay |
| yourOffer | number | What you'll offer |
| estimatedFee | number | Estimated assignment fee |
| status | string | 'new' | 'contacted' | 'under-contract' | 'closed' | 'passed' |
| floodZone | string | 'none' | '500yr' | '100yr' |
| zoning | string | Zoning designation |
| infillStatus | boolean | Is it infill? |
| utilities | boolean | Utilities available? |
| roadAccess | boolean | Paved road access? |
| phone | string | Owner phone from enrichment |
| notes | string | Any notes |
| dateAdded | string | Date |
| alerts | string | CSV |

## Sub-agent Instructions

When running as a sub-agent:

1. **Read the target market** from the "Lots" page/dashboard config
2. **Execute Steps 1-6** using web research tools
3. **Underwrite** each lot found
4. **Return the structured data** as a JavaScript array that can be added to the Lots table
5. **Do not modify** any existing builder data

## Tools Required

- `web_search` — for Zillow builder research, county tax records
- `web_fetch` — for scraping county assessor pages, truepeoplesearch
- `exec` — for running data manipulation if needed

## Enrichment Sources

- truepeoplesearch.com (free phone/name lookup)
- county treasurer/assessor websites (tax delinquency records)
- regrid.com (zoning, flood zones, parcel data)
- FEMA flood maps (flood zone verification)
- Zillow sold comparables (price comps)

## Fallbacks

- If county website blocks automation → suggest user visit manually or use XLeads
- If TruePeopleSearch doesn't return a number → try spokeo.com
- If buyer won't share exact max price → estimate based on comps minus 30%
