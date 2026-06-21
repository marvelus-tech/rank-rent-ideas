# Land Lead Gen Workflow — Knox County, TN (Vacant Land)

## Reality Check

**County assessor sites block scraping.** Knox County explicitly prohibits data mining in their TOS. Regrid requires account (free tier: 25 lookups/day).

## Approach: Hybrid Manual + Automation

### Phase 1: Identify Targets (Regrid Free)

**Step 1: Create Regrid Free Account**
- Go to https://regrid.com
- Sign up for free Starter account (25 lookups/day)
- Navigate to Knox County, TN

**Step 2: Filter for Vacant Land**
- Use Filter tool → Land Use = "Vacant" or "Agricultural"
- Acreage: Set minimum (e.g., 0.5 acres)
- Look for parcels with no building footprint

**Step 3: Extract Parcel IDs**
- Click each target parcel
- Copy: Parcel ID (APN), Owner Name, Address
- Paste into spreadsheet

**Daily limit**: 25 parcels × 30 days = 750 parcels/month

### Phase 2: Enrich Data (County Assessor — Manual)

**Step 1: Cross-reference with Knox County**
- Go to https://propertyinfo.knoxcountytn.gov/
- Click "Agree" on TOS
- Search by Parcel ID

**Step 2: Extract Key Data**
For each parcel, record:
- Owner Name (check if individual — no LLC/Corp/Trust)
- Mailing Address
- Purchase Date
- Purchase Price
- Current Land Value
- Current Total Value
- Acreage

**Step 3: Calculate Criteria**
- Owned > 5 years? → Purchase date < 2020
- Individual owner? → Name doesn't contain LLC, Inc, Corp, Trust
- Bought below market? → Purchase price < 50% of current land value

### Phase 3: Build Database

**Spreadsheet columns:**
```
Parcel ID | Owner Name | Mailing Address | Purchase Date | Purchase Price | Current Value | Acreage | Equity % | Phone | Notes
```

**Scoring:**
- High equity (>50%): Hot lead
- Medium equity (30-50%): Warm lead
- Low equity (<30%): Cold lead

## Automation Opportunities

### What CAN be automated:
1. **Spreadsheet formulas** — Calculate equity, filter by criteria
2. **Phone lookup** — Whitepages API, Spokeo (paid)
3. **Skip tracing** — Batch skip trace services (paid)
4. **Mail merge** — Generate letters from spreadsheet

### What CANNOT be automated (legally/technically):
1. **Scraping county assessor** — TOS violation, legal risk
2. **Bulk Regrid export** — Requires paid Pro account ($50-150/mo)
3. **Automated phone enrichment** — Rate limits, paid APIs

## Free Tier Path

**Month 1**: Regrid free (750 parcels) → Manual county lookup → 100 qualified leads
**Month 2**: Repeat with next county
**Month 3**: Evaluate ROI → Decide on paid tools

## Paid Tools (for scale)

| Tool | Cost | Value |
|------|------|-------|
| Regrid Pro | $50-150/mo | Export parcels, bulk data |
| PropStream | $100/mo | Owner info, equity, filters |
| BatchLeads | $150/mo | Vacant land, skip trace |
| DataTree | Custom | Bulk county data purchase |

## Recommendation

Start with **Regrid free + manual county lookup**. Build a proof-of-concept list of 50-100 qualified vacant land leads in Knox County. If the list performs, invest in PropStream for scale.

## Next Steps

1. Create Regrid account (5 min)
2. Filter Knox County for vacant land (15 min)
3. Extract 25 parcel IDs (30 min)
4. Look up 5 parcels on county site (30 min)
5. Build spreadsheet with criteria (15 min)

**Total time**: ~2 hours for first batch of 5-10 qualified leads

## Script Support

I can build:
- Spreadsheet template with formulas
- Phone enrichment script (if you get phone numbers)
- Mail merge script for outreach letters
- CRM import script (if you use HubSpot/Pipedrive)

Want me to create the spreadsheet template?
