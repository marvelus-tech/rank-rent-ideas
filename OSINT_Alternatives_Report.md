# OSINT Intelligence Report: TruePeopleSearch Alternatives
## Classification: Operational Use — Property Owner Lookup & Skip Tracing

---

## Executive Summary

TruePeopleSearch has implemented aggressive Cloudflare bot protection (IUAM/Challenge pages), making it unusable for automated agent workflows. This report identifies **viable alternatives** across four tiers:

1. **Government Open Data APIs** — No Cloudflare, free, authoritative
2. **Commercial Property Data APIs** — RESTful, programmatic, pay-per-use
3. **People Search Alternatives** — Some with APIs, lighter bot protection
4. **Skip Tracing Services** — Purpose-built for real estate OSINT

---

## Tier 1: Government Open Data (No Cloudflare, Free, Authoritative)

### NYC ACRIS (Automated City Register Information System)
**URL:** `https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Master/bnx9-e6tj`  
**Coverage:** Manhattan, Brooklyn, Queens, Bronx (1966–present)  
**Records:** 17M+ property transactions  
**API:** Socrata Open Data API (RESTful JSON)  
**Rate Limit:** None enforced  
**Cloudflare:** ❌ None  
**Best For:** NYC property ownership, deed history, party names

**Endpoints:**
- OData V4: `https://data.cityofnewyork.us/api/odata/v4/bnx9-e6tj`
- Socrata API: `https://data.cityofnewyork.us/resource/bnx9-e6tj.json`

**Key Fields:** `document_id`, `recorded_borough`, `doc_type`, `document_date`, `document_amt`, `recorded_datetime`

**Companion Dataset — ACRIS Parties:**
- **URL:** `https://data.cityofnewyork.us/City-Government/ACRIS-2007-Forward/52qc-8iyq`
- **Records:** 46.2M party records
- **Key Fields:** `name`, `address_1`, `address_2`, `city`, `state`, `zip`
- **Use Case:** Link party names to property transactions

---

### Cook County (Chicago) Open Data Portal
**URL:** `https://datacatalog.cookcountyil.gov/api/views/3723-97qp/rows.json`  
**Coverage:** Cook County, IL (all of Chicago metro)  
**API:** Socrata JSON endpoint  
**Cloudflare:** ❌ None  
**Data:** Parcel addresses, owner names, taxpayer info, mailing addresses

---

### County Assessor / Recorder Portals (Direct Access)

Many counties maintain their own public record portals **without** Cloudflare. Examples confirmed:

| County | Portal | Search By | Notes |
|--------|--------|-----------|-------|
| **Tarrant County, TX** | `tarrant.tx.publicsearch.us` | Name, Address, Doc # | Deeds, plats, liens |
| **Broward County, FL** | `browardpropertyappraisers.org` | Address, Owner, Parcel ID | Free, no account |
| **Johnson County, KS** | `ims.jocogov.org` | Location/Map | Owner lookup available |
| **Chester County, PA** | `chestercountypa-web.tylerhost.net` | Public Access DB | Images from 1993+ |
| **Middlesex County, MA** | `masslandrecords.com` | Address, Name | Free 24/7 access |
| **Maryland (Statewide)** | `sdat.dat.maryland.gov/RealProperty` | Address, Account # | All 24 jurisdictions |

**Approach:** For any target market, search `[county name] property records public access` or `[county name] recorder of deeds online search`. Most use Tyler Technologies, Socrata, or custom ASP.NET portals — **no Cloudflare**.

---

### StateRecords.org Aggregator
**URL:** `https://[state].staterecords.org/[county]/property`  
**Coverage:** All 50 states, county-level  
**Cost:** Free  
**Cloudflare:** ❌ None (static info, links to official portals)  
**Use:** Directory to find the correct county portal quickly

---

## Tier 2: Commercial Property Data APIs (Automation-Ready)

### PropertyAPI.co ⭐ Top Pick for API-First
**URL:** `https://propertyapi.co/`  
**Coverage:** 158M+ US properties, all 50 states  
**API:** RESTful JSON, self-service onboarding  
**Pricing:** 100 free credits (no CC), then pay-as-you-go  
**Response Time:** ~10ms average  
**Cloudflare:** ❌ None (developer-first, API only)  
**Endpoints:**
- `GET /api/v1/parcels/get` — Single property lookup
- `POST /api/v1/parcels/bulk` — Batch search
- `GET /api/v1/parcels/comparables` — Comps
- `GET /api/v1/deeds/get` — Deed retrieval (PDF)

**Returns:** `ownerName`, `formattedAddress`, `propertyType`, `bedrooms`, `bathrooms`, `livingArea`, `lotSize`, `yearBuilt`, `lastSaleDate`, `lastSalePrice`, `latitude`, `longitude`

---

### PubRec (PropMix)
**URL:** `https://pubrec.propmix.io/`  
**Coverage:** 155M+ properties  
**API:** RESTful, RESO standardized  
**Features:** Property, tax, deed, mortgage, foreclosure data  
**Cloudflare:** ❌ None (enterprise API)  
**Pricing:** Custom (enterprise)  
**Best For:** Large-scale operations

---

### Melissa Property API
**URL:** `https://developer.melissa.com/apis/property`  
**API:** RESTful, OpenAPI spec  
**Endpoints:**
- `GET /LookupDeeds` — Deed history by FIPS+APN or MAK
- `GET /LookupHomesByOwner` — Find all properties owned by a person
- `POST /LookupDeeds` — Batch deed lookup
**Cloudflare:** ❌ None  
**Pricing:** Pay-as-you-go, credits-based

---

### ATTOM Data
**URL:** `https://www.attomdata.com/data/property-data/assessor-data`  
**Coverage:** 160M properties, 3,000+ counties  
**Data:** Owner names (up to 4), mailing addresses, APN, FIPS, assessed values, property characteristics  
**API:** Available  
**Cloudflare:** ❌ None (enterprise API)  
**Pricing:** Enterprise (contact for quote)

---

### TaxNetUSA
**URL:** `https://www.taxnetusa.com/data/web-service-api/`  
**Coverage:** 300+ counties (TX, FL primarily)  
**API:** XML/JSON web services  
**Features:** Appraisal data, tax collector data, GIS parcel data  
**Cloudflare:** ❌ None  
**Pricing:** Request quote

---

### Realie.ai
**URL:** `https://www.realie.ai/info/county-parcel-data-search`  
**Coverage:** 3,100+ counties, 100+ attributes per parcel  
**API:** RESTful  
**Cloudflare:** ❌ None  
**Pricing:** Freemium (developer tier available)

---

## Tier 3: People Search Alternatives (Lighter Protection)

### Whitepages Pro API ⭐ Best Programmatic Option
**URL:** `https://api.whitepages.com/docs`  
**API:** Official REST API (not scraping)  
**Features:** People search, reverse phone, reverse address, identity verification  
**Cloudflare:** ❌ None (direct API)  
**Pricing:** Free trial, then subscription  
**Authentication:** API key required  
**Endpoint:** `https://api.whitepages.com/v1/person`  
**Note:** This is the **legitimate API** — no scraping needed

---

### ZabaSearch
**URL:** `https://www.zabasearch.com/`  
**Type:** Free people search engine  
**Cloudflare:** Unknown (likely light protection)  
**Best For:** Quick manual lookups

---

### Nuwber
**URL:** `https://nuwber.com/`  
**Type:** People search + background check  
**Cloudflare:** Unknown  
**Features:** Phone, address, social profiles

---

### FastPeopleSearch
**URL:** `https://www.fastpeoplesearch.com/`  
**Type:** Free people search  
**Cloudflare:** Unknown (may have protection)  
**Note:** Frequently mentioned as TruePeopleSearch alternative

---

## Tier 4: Skip Tracing Services (Built for Real Estate)

### BatchData (BatchSkipTracing)
**URL:** `https://batchdata.io/`  
**Hit Rate:** 75–85% phone numbers  
**Features:** Batch processing, DNC scrubbing, CRM integrations (Podio, Follow Up Boss, REsimpli)  
**Pricing:** Pay-as-you-go  
**Cloudflare:** ❌ None (authenticated API)  
**Best For:** High-volume skip tracing

---

### SmartSkip
**URL:** `https://smartskip.io/`  
**Coverage:** 98%+ US population  
**Features:** Phone numbers, verified emails, address history, relatives & associates, deceased flags  
**Pricing:** Subscription  
**Cloudflare:** ❌ None (authenticated app)  
**Best For:** Hard-to-reach owners, relative contacts

---

### Skip Genie
**URL:** `https://skipgenie.com/` (implied from search)  
**Focus:** Hard-to-reach property owners  
**Pricing:** Per-search or subscription  
**Best For:** Deep skip tracing when standard sources fail

---

### PropStream
**URL:** `https://trial.propstreampro.com/`  
**Coverage:** 153M+ property records  
**Features:** 120+ property filters, absentee owners, foreclosure, vacant properties, skip tracing  
**Pricing:** Subscription  
**Cloudflare:** ❌ None (authenticated platform)  
**Best For:** Data-heavy users, list stacking

---

### REsimpli
**URL:** `https://resimpli.com/`  
**Type:** All-in-one CRM with built-in skip tracing  
**Features:** List stacking, direct mail, driving for dollars, call tracking  
**Pricing:** Subscription (includes skip tracing credits)  
**Cloudflare:** ❌ None (authenticated)  
**Best For:** Investors wanting everything in one platform

---

### Enformion
**URL:** `https://www.enformion.com/`  
**Coverage:** 98% of US adults  
**Features:** Skip tracing, background checks, relative linking  
**Pricing:** Enterprise/contact  
**Best For:** Corporate/legal-level tracing

---

## Tier 5: Cloudflare Bypass (Last Resort)

If a target site has critical data but uses Cloudflare, these tools can bypass:

| Tool | Type | GitHub |
|------|------|--------|
| **undetected-chromedriver** | Selenium wrapper | `ultrafunkamsterdam/undetected-chromedriver` (12.7k stars) |
| **cloudscraper** | Python module | `VeNoMouS/cloudscraper` (6.6k stars) |
| **botasaurus** | All-in-one framework | `omkarcloud/botasaurus` (4.8k stars) |
| **patchright** | Playwright patch | `Kaliiiiiiiiii-Vinyzu/patchright` (3.5k stars) |
| **camofox-browser** | Stealth browser | `jo-inc/camofox-browser` (6.8k stars) |

**⚠️ Warning:** Using these against protected sites may violate Terms of Service. Use for legitimate OSINT only.

---

## Recommended Agent Architecture

```
┌─────────────────────────────────────────┐
│  OSINT Agent Workflow (No Cloudflare)   │
├─────────────────────────────────────────┤
│ 1. Input: Property Address / City       │
│ 2. Identify County → County Assessor    │
│    Portal (Tier 1)                      │
│ 3. If no portal: Use PropertyAPI.co     │
│    or PubRec (Tier 2)                   │
│ 4. Extract Owner Name                   │
│ 5. Enrich: Whitepages Pro API or        │
│    SmartSkip (Tier 3/4)                 │
│ 6. Output: Owner Name, Mailing Address, │
│    Phone, Email                         │
└─────────────────────────────────────────┘
```

---

## Market-Specific Playbook

For your Rank & Rent markets (various US cities), the workflow is:

1. **Extract city/county** from your opportunity data
2. **Search:** `[county] property records online` or `[county] assessor parcel search`
3. **Most counties** use one of these systems:
   - **Tyler Technologies:** `publicsearch.us` or `[county].publicsearch.us`
   - **Socrata:** `[county].gov/api/views/[id]/rows.json`
   - **Custom ASP.NET:** `[county].gov/propertysearch` or `[county].gov/assessor`
   - **GIS:** `[county]gis.org` or `[county].hub.arcgis.com`
4. **If county has no online search:** Fall back to PropertyAPI.co or PubRec

---

## Quick Reference: Best Tools by Use Case

| Use Case | Primary Tool | Fallback Tool |
|----------|-------------|---------------|
| **NYC Properties** | ACRIS Open Data API | PropertyAPI.co |
| **Chicago Properties** | Cook County Open Data | PropertyAPI.co |
| **General US Property** | County Assessor Portal | PropertyAPI.co |
| **Batch Owner Lookup** | PropertyAPI.co (bulk) | PubRec / ATTOM |
| **Find Phone/Email** | Whitepages Pro API | SmartSkip / BatchData |
| **Deep Skip Trace** | SmartSkip | Skip Genie / Enformion |
| **All-in-One CRM** | REsimpli | PropStream |

---

## End of Report

*Compiled: 2026-06-28*  
*Classification: Operational — For agent automation workflows*
