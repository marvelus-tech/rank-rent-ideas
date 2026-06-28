# OSINT Quick Reference — Your Rank & Rent Markets

## Files Created
| File | Purpose |
|------|---------|
| `osint_property_finder.py` | Full-featured tool with PropertyAPI.co, Whitepages, DNC |
| `osint_enrich.py` | **Production tool** — ACRIS + county portals + DNC + batch export |
| `dnc_list.txt` | DNC list template (populate from telemarketing.donotcall.gov) |
| `OSINT_Alternatives_Report.md` | Complete intelligence report on all alternatives |
| `acris_owners_20260628_*.csv` | Live demo output (81 NYC owner records) |

---

## Your US Markets — Portal Directory

Your database has **125 unique US cities**. Here are the portals for your top markets:

| City | State | Portal | Type |
|------|-------|--------|------|
| **Jersey City** | NJ | `taxmaps.nj.gov/pdfs/county/Hudson` | Direct |
| **Denton** | TX | `dentoncad.com` | Direct |
| **Fort Worth** | TX | `tarrant.tx.publicsearch.us` | Tyler |
| **Dallas** | TX | `dallascad.org` | Direct |
| **Houston** | TX | `hcad.org` | Direct |
| **Austin** | TX | `travisCAD.org` | Direct |
| **San Antonio** | TX | `bexar.org` | Direct |
| **Chicago** | IL | `datacatalog.cookcountyil.gov` | **Socrata API** |
| **New York** | NY | `data.cityofnewyork.us` | **Socrata API** |
| **Brooklyn** | NY | `data.cityofnewyork.us` | **Socrata API** |
| **Miami** | FL | `miamidade.gov/propertysearch` | Direct |
| **Fort Lauderdale** | FL | `browardpropertyappraisers.org` | Direct |
| **Orlando** | FL | `ocpafl.org` | Direct |
| **Phoenix** | AZ | `mcassessor.maricopa.gov` | Direct |
| **Las Vegas** | NV | `clarkcountynv.gov` | Direct |
| **Los Angeles** | CA | `portal.assessor.lacounty.gov` | Direct |
| **San Diego** | CA | `arcc.sdcounty.ca.gov` | Direct |
| **Philadelphia** | PA | `property.phila.gov` | Direct |
| **Atlanta** | GA | `fultoncountyga.gov` | Direct |
| **Charlotte** | NC | `mecknc.gov` | Direct |
| **Seattle** | WA | `blue.kingcounty.com/Assessor` | Direct |
| **Denver** | CO | `denvergov.org/property` | Direct |

**For any other city:**
```bash
python3 osint_enrich.py --city "Your City" --state "ST"
```

---

## TruePeopleSearch Replacement Workflow

### For NYC Properties (Free, No API Key)
```bash
# Live demo — pulls real owner records from ACRIS
python3 osint_enrich.py --demo

# Output: acris_owners_YYYYMMDD_HHMMSS.csv
```

### For Any US Property (Programmatic)
```bash
# 1. Sign up at PropertyAPI.co (100 free credits)
# 2. Edit osint_property_finder.py and set PROPERTY_API_KEY
# 3. Run:
python3 osint_property_finder.py --address "123 Main St, Denton, TX 76201"
```

### For Batch Processing
```bash
# Create CSV with columns: address, city, state, zip, owner_name (optional)
python3 osint_property_finder.py --batch-file leads.csv

# Output: leads_enriched.json
```

---

## DNC Compliance

### Option 1: DIY (Free)
1. Download DNC list from `telemarketing.donotcall.gov`
2. Place in `~/.openclaw/workspace/dnc_list.txt`
3. Script automatically checks all phone numbers

### Option 2: Integrated (Recommended)
Use **BatchData.io** or **SmartSkip.io** — both include:
- Phone number enrichment
- **Automatic DNC scrubbing**
- TCPA compliance flags
- Hit rates: 75-85%

### Option 3: Hybrid
Use government APIs for ownership data → Skip tracing service for phones → DNC check before outreach

---

## What Just Happened (Live Demo)

Ran `python3 osint_enrich.py --demo`:
- ✅ Connected to NYC ACRIS API (no auth, no Cloudflare)
- ✅ Retrieved 20 recent property documents
- ✅ Extracted **81 individual owner records**
- ✅ Exported to CSV + JSON
- ⚠️ DNC list empty (needs download from donotcall.gov)

**Sample output:**
```csv
owner_name,address,city,state,borough,party_type
"SOMSKY, FRANK J","576 WHITENACK RD, RIVERVALE, NJ",RIVERVALE,NJ,Manhattan,Grantee
"SOMSKY, CARMEN","576 WHITENACK RD, RIVERVALE, NJ",RIVERVALE,NJ,Manhattan,Grantee
```

---

## Recommended Next Steps

1. **Test your markets:**
   ```bash
   python3 osint_enrich.py --city "Fort Worth" --state "TX"
   python3 osint_enrich.py --city "Chicago" --state "IL"
   ```

2. **Get API keys for scale:**
   - PropertyAPI.co — 100 free credits (no CC)
   - Whitepages Pro — for phone enrichment
   - BatchData / SmartSkip — for DNC-compliant skip tracing

3. **Build into your pipeline:**
   - Your `rr-niche-finder` generates opportunities by city
   - Use county portals or PropertyAPI.co to find property owners
   - Enrich with skip tracing services
   - Check DNC before calling
   - Import into your dashboard

---

## Architecture for Your Agent

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  rr-niche-finder │────▶│  OSINT Enrichment │────▶│  Lead Record    │
│  (city + niche)  │     │  (this tool)      │     │  (JSON/CSV)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
   Denton TX              Denton CAD portal         Owner: John Doe
   Home battery           or PropertyAPI.co         Address: 123 Main
   backup                 or ACRIS (NYC)            Phone: 555-1234
                                                   DNC: ✓ Safe
```

---

## Key Insight

**You don't need TruePeopleSearch.** For your use case (property owner lookup):

| Source | Cost | Cloudflare | Best For |
|--------|------|------------|----------|
| **County Assessor Portals** | Free | ❌ None | Direct lookup |
| **ACRIS (NYC)** | Free | ❌ None | NYC metro |
| **Cook County (Chicago)** | Free | ❌ None | Chicago metro |
| **PropertyAPI.co** | 100 free, then pay | ❌ None | Programmatic, all US |
| **BatchData / SmartSkip** | Subscription | ❌ None | Phone + DNC scrubbing |

---

*Generated: 2026-06-28*
*Tools: osint_enrich.py, osint_property_finder.py*
