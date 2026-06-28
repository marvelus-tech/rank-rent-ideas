# Wake County Land Deep Dive — All Filters Removed
**Date:** 2026-06-24  
**Criteria:** All strict filters removed (size, flood, slope, easements, price, street type)  
**Target ZIPs:** 27604 (primary), 27607, 27502  
**Builders:** Loyd Builders (919-387-1455, custom luxury BOYL/infill), Fuller Land & Development (919-417-0057, land dev + building)

## Top Priority Parcels (expert enriched)

### 1. 3504 Skycrest Dr, Raleigh, NC 27604 — **Highest priority**
- **Acres:** 0.24 (tax records)
- **Price:** $125,000 (listed)
- **PIN / APN:** 1725.18-40-7263-000
- **Zoning:** R-6
- **Flood:** Zone B/X (area of moderate flood hazard — between 100-year and 500-year limits)
- **Status:** Vacant land, cleared and level homesite
- **Notes:** No HOA. Quiet residential street in established neighborhood. Central Raleigh with quick I-440 access. Rare buildable lot in 27604. Strong match for Loyd Builders custom luxury.
- **Listing Agent:** Janet Callejas, Keller Williams Realty Cary — 984-520-3143
- **Source:** LoopNet, Redfin, TMLS #10158258, public tax records
- **iMAPS action:** Search PIN or address → check flood layer (confirm B/X), contours for slope, easements/plats, owner name, utilities.
- **Next:** Skip trace owner via truepeoplesearch + contact agent for showing / motivation.

### 2. 4106 N New Hope Rd, Raleigh, NC 27604 — **High priority (motivated)**
- **Acres:** 0.35
- **Price:** $70,000 (aggressively reduced — was $125k → $100k → $80k → $70k)
- **PIN:** 1726.19-70-3139-000 (approx 1726703139)
- **Zoning:** R6
- **Potential:** Duplex or fourplex (package deal with 4200 James Rd)
- **Utilities:** Public water, sewer, electric, cable available
- **Topography:** Partially cleared
- **Flood:** Minimal risk (1/10 per First Street)
- **Notes:** Strong motivated seller signal from repeated price drops. Good for investor or Fuller Land & Development.
- **Listing Agent:** Muhammad Omer, Boone, Hill, Allen & Ricks — (252) 443-4148
- **Source:** Redfin, Hive MLS #100447052, LoopNet, Land.com
- **iMAPS action:** Confirm exact PIN, flood, easements, slope via contours, ownership.
- **Next:** Contact agent immediately for package details + motivation. Truepeoplesearch owner.

### Other surfaced lots (lower priority until top 2 vetted)
- 524 Barksdale Dr, 27604 — 0.41ac @ $525k (higher price, verify easements)
- 212 Hunter St, Apex 27502 — 0.35ac @ $425k (Loyd territory, downtown Apex)
- 3213 Marie Dr, 27604 — 0.56ac @ $140k
- Others (larger parcels) for subdivision potential.

## Actions Executed
- All-filters-removed prompt created and run
- 8 lots captured in wake-2026-06-24-all-filters-removed.json
- Dashboard (land-flip-dashboard/index.html) updated with accurate Skycrest + New Hope data + Loyd/Fuller builders
- Top 2 parcels expert-enriched with PIN, flood, zoning, agent contacts, builder match

## Recommended Immediate Next Steps (expert sequence)
1. **Manual iMAPS deep dive** (https://maps.raleighnc.gov/imaps/):
   - Search "3504 Skycrest Dr" and PIN 172518407263000
   - Search "4106 N New Hope Rd" and PIN 1726703139
   - Layers to enable: Flood, Contours/LiDAR (slope), Easements, Plats, Ownership, Utilities
2. **Owner enrichment**: truepeoplesearch.com or similar on the two addresses.
3. **Agent outreach prep**: Draft short note for Loyd (Skycrest) and Fuller (New Hope duplex potential).
4. **Tax / delinquent check**: Wake County tax site or LienSuite for both PINs.
5. **Update dashboard** once iMAPS + owner data in.

**Status:** Volume now exists because filters removed. Every lot requires per-parcel underwriting. Top 2 have clear builder fits and motivation signals.

Next command from user will trigger iMAPS browser automation or outreach draft.