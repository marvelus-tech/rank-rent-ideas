# Geographic Scanning Strategy

## Objective
Systematically cover target geographies without overlap and with measurable density thresholds.

## 1) Grid-Based Google Maps Scanning

Use a square grid per metro area with fixed cell size (recommended: **2 km × 2 km** urban, **4 km × 4 km** suburban).

For each cell:
1. Build location query using suburb/locality name plus category.
2. Run all Tier 1 categories first.
3. Record leads scanned, new leads found, and duplicates.
4. Move to next cell only when density threshold is reached or exhausted.

Track each cell in a scan ledger (CSV/JSON):
- `grid_id`
- `centroid_lat`
- `centroid_lng`
- `scan_date`
- `categories_scanned`
- `total_scanned`
- `new_leads`
- `duplicates`
- `new_density_per_km2`

## 2) Melbourne Start Point + Expansion Rings

Start centroid: **-37.8136, 144.9631** (Melbourne CBD)

Expansion approach:
- **Ring 1 (0–8 km):** CBD + inner suburbs, highest business density.
- **Ring 2 (8–18 km):** middle suburbs, strong trade and clinic mix.
- **Ring 3 (18–35 km):** outer growth corridors, lower density but less competition.

Order of execution each day:
1. Ring 1 Tier 1 categories
2. Ring 2 Tier 1 categories
3. Ring 1 Tier 2 categories
4. Ring 3 Tier 1 categories

## 3) Overlap Prevention

- Use deterministic `grid_id` naming (e.g., `MEL_R2_X03_Y07`).
- Re-scan cadence: minimum every 7 days unless seasonal surge.
- Do not re-run same category + grid cell on same day.
- Deduplicate at lead level using `business_name + address + phone` hash.

## 4) Density Targets (Move/Stay Rule)

Suggested threshold before moving to next zone:
- **Urban core:** continue scanning cell while `new leads >= 3 per km²`
- **Middle suburbs:** continue while `new leads >= 1.5 per km²`
- **Outer suburbs:** continue while `new leads >= 0.8 per km²`

If below threshold for 2 consecutive scans in a zone, expand outward.

## 5) US Expansion Plan (Ranked)

Prioritize metros with high SMB density, strong home services demand, and call-heavy service sectors.

1. Dallas–Fort Worth, TX
2. Houston, TX
3. Phoenix, AZ
4. Miami–Fort Lauderdale, FL
5. Atlanta, GA
6. Tampa, FL
7. Austin, TX
8. Las Vegas, NV
9. Charlotte, NC
10. Nashville, TN

Execution model for US:
- Launch with top 3 metros first.
- Apply same ring + grid strategy.
- Promote categories based on local seasonality (e.g., HVAC in hot-climate metros).
