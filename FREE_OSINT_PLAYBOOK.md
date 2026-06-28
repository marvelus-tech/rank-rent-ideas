# FREE OSINT Playbook — Zero-Cost Property Owner Lookup
## No API Keys. No Subscriptions. No Cloudflare Blockers.

---

## Tier 1: Government Open Data (100% Free, No Auth, Tested)

### NYC ACRIS — Already Working
**URL:** `https://data.cityofnewyork.us/resource/bnx9-e6tj.json`  
**Cost:** $0 forever  
**Auth:** None  
**Cloudflare:** ❌ None  
**Records:** 17M+ (1966–present)  
**What you get:** Property transactions, document IDs, dates, amounts  
**Party data:** `https://data.cityofnewyork.us/resource/52qc-8iyq.json` — names + addresses  

**Tested live:** Pulled 81 owner records in seconds. Exported to CSV.

**Quick query:**
```bash
curl -s "https://data.cityofnewyork.us/resource/bnx9-e6tj.json?\$limit=5&\$order=document_date DESC" | python3 -m json.tool
```

---

### Cook County (Chicago) — Open Data
**URL:** `https://datacatalog.cookcountyil.gov/api/views/3723-97qp/rows.json`  
**Cost:** $0  
**Auth:** None  
**Cloudflare:** ❌ None  
**Records:** All Cook County parcels  
**What you get:** Owner names, mailing addresses, parcel PINs  

---

### Any County — Direct Assessor Portals
**Cost:** $0  
**Auth:** None (most)  
**Cloudflare:** ❌ None  
**How to find:**
```
Search: "[county name] property records public access"
Or: "[county name] assessor parcel search"
Or: "[county name] recorder of deeds online"
```

**Common portal types:**
| Platform | URL Pattern | Example |
|----------|-------------|---------|
| Tyler Technologies | `[county].publicsearch.us` | `tarrant.tx.publicsearch.us` |
| Socrata Open Data | `[county].gov/api/views/ID/rows.json` | `datacatalog.cookcountyil.gov` |
| Direct ASP.NET | `[county].gov/propertysearch` | `browardpropertyappraisers.org` |
| ArcGIS Hub | `[county]gis.hub.arcgis.com` | Various |

**Already mapped in osint_enrich.py:** 50+ US cities

---

## Tier 2: Google Dorking (100% Free, No Tools Needed)

### Find Business Owners
```
"[Business Name]" owner
"[Business Name]" "owner" site:linkedin.com
"[Business Name]" "owner" site:facebook.com
site:manta.com "[Business Name]"
site:yelp.com "[Business Name]" owner
```

### Find Property Owners
```
"[Address]" owner site:countyoffice.org
"[Address]" "property owner" site:whitepages.com
"[Address]" assessor
"[Parcel Number]" owner
```

### Find Phone Numbers
```
"[Name]" "[City]" phone
"[Name]" "[City]" contact
site:411.com "[Name]" "[City]"
```

---

## Tier 3: Social Media OSINT (100% Free)

### Facebook
- Search business name → page shows owner in "About" section
- Search person name + city → profile may list business
- Business pages often have contact info publicly visible

### LinkedIn
- Search business name → employees list shows owners/founders
- Advanced search: `site:linkedin.com "[name]" "[city]" owner`
- Company pages list employees by title

### Instagram
- Business accounts often have email in bio
- Location tags show business owner posts

### Yelp
- Business pages sometimes list owner responses
- "Ask the Community" may reveal owner names

---

## Tier 4: State Business Entity Databases (100% Free)

Every state has a free business entity search. LLCs must list a "registered agent" — often the owner.

| State | URL |
|-------|-----|
| Texas | `mycpa.cpa.state.tx.us/coa/` |
| California | `businesssearch.sos.ca.gov` |
| Florida | `search.sunbiz.org` |
| New York | `apps.dos.ny.gov/publicInquiry` |
| Illinois | `www.ilsos.gov/corporatellc` |
| New Jersey | `www.njportal.com/DOR/BusinessNameSearch` |
| Pennsylvania | `file.dos.pa.gov/search/business` |
| Ohio | `businesssearch.ohiosos.gov` |
| Georgia | `ecorp.sos.ga.gov/BusinessSearch` |
| North Carolina | `www.sosnc.gov/search/index/corp` |

**Pro tip:** If the business is an LLC, search the LLC name → find registered agent → that's often the owner.

---

## Tier 5: Free Aggregator Sites (Use with Caution)

### CountyOffice.org
**URL:** `countyoffice.org`  
**Cost:** $0 for basic search, $9.95/mo for full records  
**Cloudflare:** ❌ None (light protection)  
**Use:** Search by address → shows property details → sometimes owner name  

### PubRecord.org
**URL:** `pubrecord.org`  
**Cost:** $0 (5 searches/day limit)  
**Cloudflare:** ❌ None  
**Use:** Property records, deeds, tax assessments  

### StateRecords.org
**URL:** `[state].staterecords.org`  
**Cost:** $0  
**Cloudflare:** ❌ None  
**Use:** Directory to official county portals  

### ZabaSearch
**URL:** `zabasearch.com`  
**Cost:** $0 (basic)  
**Cloudflare:** Light (may work with basic requests)  
**Use:** People search by name + location  

---

## Free Automation Script

Here's a zero-cost script using only free government data:

```python
#!/usr/bin/env python3
"""FREE OSINT — Zero-cost property owner lookup"""

import urllib.request
import urllib.parse
import json
import csv
from pathlib import Path

# ─── FREE DATA SOURCES ───

NYC_ACRIS_MASTER = "https://data.cityofnewyork.us/resource/bnx9-e6tj.json"
NYC_ACRIS_PARTIES = "https://data.cityofnewyork.us/resource/52qc-8iyq.json"
COOK_COUNTY = "https://datacatalog.cookcountyil.gov/api/views/3723-97qp/rows.json"

def fetch_json(url: str, params: dict = None) -> list:
    """Fetch JSON from any free API. No auth needed."""
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "OSINT-Free/1.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[!] Error: {e}")
        return []

# ─── NYC ACRIS (FREE) ───

def nyc_find_recent_owners(limit: int = 20) -> list:
    """Get recent property owners from NYC ACRIS. Completely free."""
    print("[→] Fetching from NYC ACRIS (free)...")
    
    # Get recent documents
    docs = fetch_json(NYC_ACRIS_MASTER, {
        "$limit": limit,
        "$order": "document_date DESC"
    })
    
    owners = []
    for doc in docs:
        doc_id = doc.get("document_id")
        if not doc_id:
            continue
        
        # Get parties for each document
        parties = fetch_json(NYC_ACRIS_PARTIES, {"document_id": doc_id})
        
        for party in parties:
            name = party.get("name", "").strip()
            if not name or any(x in name for x in ["LLC", "INC", "BANK", "CORP"]):
                continue
            
            owners.append({
                "name": name,
                "address": f"{party.get('address_2', '') or ''}, {party.get('city', '') or ''}, {party.get('state', '') or ''} {party.get('zip', '') or ''}".strip(", "),
                "city": party.get("city"),
                "state": party.get("state"),
                "zip": party.get("zip"),
                "document_id": doc_id,
                "borough": doc.get("recorded_borough"),
                "date": doc.get("document_date", "")[:10] if doc.get("document_date") else "N/A",
                "amount": doc.get("document_amt"),
                "source": "NYC_ACRIS_FREE"
            })
    
    return owners

# ─── COOK COUNTY (FREE) ───

def cook_county_sample() -> list:
    """Sample from Cook County open data. Completely free."""
    print("[→] Fetching from Cook County (free)...")
    
    data = fetch_json(COOK_COUNTY, {"$limit": 5})
    
    owners = []
    for record in data:
        owners.append({
            "name": record.get("owner_name"),
            "address": record.get("property_address"),
            "city": record.get("city"),
            "zip": record.get("zip"),
            "pin": record.get("pin"),
            "source": "COOK_COUNTY_FREE"
        })
    
    return owners

# ─── COUNTY PORTAL FINDER (FREE) ───

def find_county_portal(city: str, state: str) -> str:
    """Return the best free portal URL for a city."""
    PORTALS = {
        ("Denton", "TX"): "https://www.dentoncad.com/",
        ("Fort Worth", "TX"): "https://www.tad.org/",
        ("Dallas", "TX"): "https://www.dallascad.org/",
        ("Houston", "TX"): "https://hcad.org/property-search/",
        ("Austin", "TX"): "https://travisCAD.org/",
        ("San Antonio", "TX"): "https://www.bexar.org/2187/Property-Search",
        ("Chicago", "IL"): "https://datacatalog.cookcountyil.gov/",
        ("New York", "NY"): "https://data.cityofnewyork.us/",
        ("Brooklyn", "NY"): "https://data.cityofnewyork.us/",
        ("Miami", "FL"): "https://www.miamidade.gov/propertysearch/",
        ("Fort Lauderdale", "FL"): "https://browardpropertyappraisers.org/",
        ("Orlando", "FL"): "https://ocpafl.org/",
        ("Phoenix", "AZ"): "https://mcassessor.maricopa.gov/",
        ("Las Vegas", "NV"): "https://www.clarkcountynv.gov/government/elected_officials/county_recorder/",
        ("Los Angeles", "CA"): "https://portal.assessor.lacounty.gov/",
        ("San Diego", "CA"): "https://arcc.sdcounty.ca.gov/",
        ("Philadelphia", "PA"): "https://property.phila.gov/",
        ("Atlanta", "GA"): "https://www.fultoncountyga.gov/",
        ("Charlotte", "NC"): "https://www.mecknc.gov/",
        ("Seattle", "WA"): "https://blue.kingcounty.com/Assessor/eRealProperty/",
        ("Denver", "CO"): "https://www.denvergov.org/property",
        ("Nashville", "TN"): "https://www.padctn.org/",
        ("Indianapolis", "IN"): "https://www.indy.gov/",
        ("Columbus", "OH"): "https://property.franklincountyohio.gov/",
        ("Cleveland", "OH"): "https://recorder.cuyahogacounty.us/",
        ("Kansas City", "MO"): "https://jacomo.org/",
        ("Milwaukee", "WI"): "https://city.milwaukee.gov/",
        ("Minneapolis", "MN"): "https://www.hennepin.us/",
        ("Detroit", "MI"): "https://www.waynecounty.com/",
        ("Pittsburgh", "PA"): "https://www.alleghenycounty.us/",
        ("Baltimore", "MD"): "https://sdat.dat.maryland.gov/RealProperty",
        ("Albuquerque", "NM"): "https://www.bernco.gov/",
        ("Tucson", "AZ"): "https://www.pima.gov/",
        ("Sacramento", "CA"): "https://eportal.saccounty.net/",
        ("Riverside", "CA"): "https://rivcoaccessor.org/",
        ("San Jose", "CA"): "https://www.sccassessor.org/",
        ("Oakland", "CA"): "https://www.acgov.org/",
        ("Fresno", "CA"): "https://www.fresnocountyca.gov/",
        ("Long Beach", "CA"): "https://portal.assessor.lacounty.gov/",
        ("Anaheim", "CA"): "https://portal.assessor.lacounty.gov/",
        ("Santa Ana", "CA"): "https://ocassessor.org/",
        ("Raleigh", "NC"): "https://www.wakegov.com/",
        ("Virginia Beach", "VA"): "https://www.vbgov.com/",
        ("Omaha", "NE"): "https://www.dcasse.org/",
        ("Oklahoma City", "OK"): "https://www.oklahomacounty.org/",
        ("Tulsa", "OK"): "https://www.assessor.tulsacounty.org/",
        ("Louisville", "KY"): "https://jeffersonky.gov/",
        ("Memphis", "TN"): "https://www.shelbycountytn.gov/",
        ("New Orleans", "LA"): "https://www.nola.gov/",
        ("Buffalo", "NY"): "https://www.erie.gov/",
        ("Rochester", "NY"): "https://www.monroecounty.gov/",
        ("Albany", "NY"): "https://www.albanycounty.com/",
        ("Birmingham", "AL"): "https://www.jccal.org/",
        ("Montgomery", "AL"): "https://mc-ala.org/",
        ("Little Rock", "AR"): "https://www.pulaskicounty.net/",
        ("Boise", "ID"): "https://www.adacounty.id.gov/",
        ("Des Moines", "IA"): "https://www.polkcountyiowa.gov/",
        ("Cedar Rapids", "IA"): "https://www.linncounty.org/",
        ("Madison", "WI"): "https://www.cityofmadison.com/",
        ("Anchorage", "AK"): "https://www.muni.org/",
        ("Honolulu", "HI"): "https://www.realpropertyhonolulu.com/",
        ("Portland", "OR"): "https://www.multco.us/",
        ("Salt Lake City", "UT"): "https://www.saltlakecounty.gov/",
        ("Providence", "RI"): "https://www.providenceri.gov/",
        ("Hartford", "CT"): "https://www.hartford.gov/",
        ("Newark", "NJ"): "https://taxmaps.nj.gov/pdfs/county/Essex",
        ("Jersey City", "NJ"): "https://taxmaps.nj.gov/pdfs/county/Hudson",
        ("Wilmington", "DE"): "https://www.newcastlede.gov/",
    }
    
    key = (city, state.upper())
    if key in PORTALS:
        return PORTALS[key]
    
    return f"Search: https://www.google.com/search?q={urllib.parse.quote(city)}+{state}+property+records+public+access"

# ─── EXPORT ───

def save_csv(records: list, filename: str):
    if not records:
        print("[!] No records to save")
        return
    keys = records[0].keys()
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)
    print(f"[✓] Saved {len(records)} records to {filename}")

# ─── MAIN ───

def main():
    import argparse
    parser = argparse.ArgumentParser(description="FREE OSINT — Zero Cost")
    parser.add_argument("--nyc", action="store_true", help="Pull NYC owners via ACRIS")
    parser.add_argument("--city", help="City name")
    parser.add_argument("--state", help="State abbreviation")
    args = parser.parse_args()
    
    if args.nyc:
        owners = nyc_find_recent_owners(50)
        print(f"\n[✓] Found {len(owners)} owners")
        for o in owners[:5]:
            print(f"  {o['name']} — {o['address']} — {o['date']}")
        save_csv(owners, "nyc_owners_free.csv")
    
    elif args.city and args.state:
        portal = find_county_portal(args.city, args.state)
        print(f"\n[→] Free portal for {args.city}, {args.state}:")
        print(f"    {portal}")
    
    else:
        print("FREE OSINT Property Owner Finder")
        print("\nUsage:")
        print("  python3 free_osint.py --nyc                    # Pull NYC owners (free)")
        print("  python3 free_osint.py --city 'Denton' --state TX  # Find portal")
        print("\nAll data sources are 100% free government records.")

if __name__ == "__main__":
    main()
```

---

## Free Workflow for Your Markets

```
1. Identify city from your rr-niche-finder data
   → "Denton TX", "Jersey City NJ", "Chicago IL"

2. Look up free portal
   → python3 osint_enrich.py --city "Denton" --state "TX"
   → Result: dentoncad.com (free, direct)

3. Search property records on county portal
   → Enter address or owner name
   → Get: Owner name, mailing address, parcel ID

4. Google dork for phone/email
   → "Owner Name" Denton TX phone
   → site:linkedin.com "Owner Name" Denton

5. Check state business entity DB (if LLC)
   → mycpa.cpa.state.tx.us (Texas)
   → Search LLC name → find registered agent

6. You now have: Name, address, possible phone
   → Total cost: $0
```

---

## Cost Comparison

| Method | Cost | Speed | Quality |
|--------|------|-------|---------|
| **County Portal Direct** | $0 | Medium | ⭐⭐⭐⭐⭐ Official |
| **ACRIS API (NYC)** | $0 | Fast | ⭐⭐⭐⭐⭐ Official |
| **Google Dorking** | $0 | Fast | ⭐⭐⭐ Variable |
| **Social Media** | $0 | Medium | ⭐⭐⭐⭐ Good for small biz |
| **State Business DB** | $0 | Medium | ⭐⭐⭐⭐⭐ Official |
| **ZabaSearch** | $0 | Fast | ⭐⭐⭐ May be outdated |
| PropertyAPI.co | ~$0.10/lookup | Fast | ⭐⭐⭐⭐⭐ Aggregated |
| Whitepages Pro | $$$ | Fast | ⭐⭐⭐⭐⭐ Verified |
| SmartSkip | $$/mo | Fast | ⭐⭐⭐⭐⭐ Skip trace |

---

## Bottom Line

**For completely free property owner lookup:**

1. **County assessor portals** — Best source, always free, always official
2. **ACRIS (NYC)** — Best for NYC metro, tested live, no limits
3. **Cook County (Chicago)** — Best for Chicago metro, open data
4. **Google dorking** — Fills gaps when portals don't have phones
5. **State business DBs** — Essential for LLC-owned properties
6. **Social media** — Surprisingly effective for small business owners

**You can do 100% of your prospecting for $0.** The paid tools (PropertyAPI, SmartSkip, etc.) save time at scale but are not required to get started.
