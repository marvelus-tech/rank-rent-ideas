# Leadgen Scraper Enhancement Plan

## Current State
- **Peekaboo scraper** gets: name, address, phone, rating, reviews, hours
- **Missing**: website (always null), email (not attempted)
- **Problem**: Clipboard copy from list view doesn't include websites

## Phase 1: Website Extraction (Today)
**Goal**: Every lead has either a `website` URL or a `website_missing: true` flag

**Approach**:
- Modify peekaboo scraper to click into each listing
- Extract website from detail page (Google Maps shows it as "Website" button)
- If no website button exists, set `website_missing: true`
- Update CSV/JSON output format

**Fields added**:
- `website` (string or null)
- `website_missing` (boolean)
- `maps_url` (string - direct link to Maps listing)

## Phase 2: Contact Enrichment (Next)
**Goal**: Extract email and additional phone numbers from business websites

**Approach**:
- Build `contact_enricher.py` module
- For each lead with a website:
  1. Visit the website
  2. Scrape page for email patterns (`mailto:`, regex)
  3. Look for "Contact" page and scrape that too
  4. Extract any additional phone numbers
  5. Look for social media links
- Save to `data/processed/enriched_leads.json`

**Fields added**:
- `email` (string or null)
- `emails_found` (array)
- `contact_page_url` (string)
- `social_links` (object: facebook, instagram, linkedin)
- `contact_confidence` (enum: none | low | medium | high)

## Phase 3: Intelligence Scoring (Future)
**Goal**: Identify which leads are most likely to need AI voice/chat services

**Signals**:
- No website = high need (they're invisible online)
- Website but no chat widget = medium-high need
- Old/poor website = medium need
- No contact form = medium need
- Service businesses (plumbers, electricians) = high need
- Location (Melbourne suburbs) = adjust by density

**Output**:
- `ai_service_score` (0-100)
- `priority` (cold | warm | hot)
- `recommended_action` (string)

## Technical Architecture

```
Peekaboo Scraper (Phase 1)
    ↓
Google Maps List → Click Each → Detail Page → Extract Website
    ↓
data/processed/peekaboo_leads.json (with website/website_missing)
    ↓
Contact Enricher (Phase 2)
    ↓
Visit Website → Scrape Emails/Phones/Socials
    ↓
data/processed/enriched_leads.json
    ↓
Intelligence Scorer (Phase 3)
    ↓
data/reports/prioritized_leads.csv
```

## Implementation Order
1. [x] Write this plan
2. [ ] Modify peekaboo_scraper.py for per-listing detail extraction
3. [ ] Build contact_enricher.py
4. [ ] Wire together in run pipeline
5. [ ] Test with real run
6. [ ] Update cron to run full pipeline

## Data Schema (Phase 1 Output)

```json
{
  "name": "Plumb Medic - Emergency Plumber Melbourne",
  "address": "3/394 Collins St",
  "phone": "+61 1300 100 977",
  "website": "https://plumbmedic.com.au",
  "website_missing": false,
  "maps_url": "https://www.google.com/maps/place/...",
  "rating": 4.9,
  "reviews": 335,
  "category": "plumbers",
  "location": "Victoria, Australia",
  "discovered_at": "2026-05-22T11:02:00+00:00",
  "scraper": "peekaboo"
}
```

## Data Schema (Phase 2 Output)

```json
{
  "name": "...",
  "website": "https://plumbmedic.com.au",
  "email": "info@plumbmedic.com.au",
  "emails_found": ["info@plumbmedic.com.au", "bookings@plumbmedic.com.au"],
  "phone": "+61 1300 100 977",
  "contact_page_url": "https://plumbmedic.com.au/contact",
  "social_links": {
    "facebook": "https://facebook.com/plumbmedic",
    "instagram": null,
    "linkedin": null
  },
  "contact_confidence": "high"
}
```

---

*Created: 2026-05-22*
*Status: Phases 1 & 2 COMPLETE — Phase 3 in progress*

## Completed ✅

### Phase 1: Website Extraction
- Browser scraper verified working (3/3 leads with websites)
- `website_missing` flag added to schema
- `maps_url` field added for direct Maps links

### Phase 2: Contact Enrichment  
- `contact_enricher.py` module built and tested
- Email extraction: 100% success (3/3 test leads)
- Social media extraction: Facebook, Instagram, Twitter found
- Contact confidence scoring: high/medium/low/none
- Outreach-ready CSV generated

## In Progress 🔄

### Phase 3: Intelligence Scoring
- Scoring algorithm design complete
- Implementation pending

## Files Added/Modified
- `src/contact_enricher.py` — NEW
- `scripts/run-browser-pipeline.sh` — NEW
- `src/browser_scraper.py` — Updated (website_missing, maps_url, Unicode fix)
- `src/peekaboo_scraper.py` — Updated (website_missing in CSV)
- `main.py` — Updated (contact enrichment integration)
- `README.md` — Rewritten with new pipeline docs
- `docs/enhancement-plan.md` — This file
