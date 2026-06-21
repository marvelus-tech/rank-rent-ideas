# Leadgen Monitoring System (Marvelus.cc + Nolostsales.cc)

Systematic lead generation + deduped daily operations for AI voice/chat agency outreach.

**Current Pipeline:**
1. ✅ **Browser Scraper** — Google Maps with website extraction
2. ✅ **Contact Enricher** — Email, phone, socials from business websites
3. ✅ **Intelligence Scorer** — Priority ranking (call button, SEO, reviews)
4. 🔄 **Auto-Outreach** — Draft generation (Phase 4, pending)

---

## Phase 1: Browser Scraper (Website Extraction)

Uses Playwright to automate Brave Browser against Google Maps.

**What it captures per listing:**
- name, address, phone
- **website** (or `website_missing: true` if none)
- rating, reviews, business hours
- Maps URL (direct link)

**Tested and working** — 3/3 leads in test run had websites extracted:
- Royal Flushed Plumbing → https://royalflushed.com/
- Plumb Medic → https://www.plumbmedic.com.au/
- 24 Hour Melbourne Plumber → https://24hourmelbourneplumbers.com.au/

---

## Phase 2: Contact Enrichment (Email + Socials)

Visits each business website and extracts:
- **Email addresses** (from page text + mailto links + contact pages)
- **Phone numbers** (from site + merged with Maps phone)
- **Social media links** (Facebook, Instagram, LinkedIn, Twitter, YouTube)
- **Contact page URL** (if found)
- **Contact confidence score** (none | low | medium | high)

**Test results (3 leads):**
| Business | Email | Confidence | Socials |
|---|---|---|---|
| Royal Flushed Plumbing | info@royalflushed.com | high | — |
| Plumb Medic | info@plumbmedic.com.au | high | Facebook ✓ |
| 24 Hour Melbourne Plumber | info@24hourmelbourneplumbers.com.au | high | FB ✓, IG ✓, Twitter ✓ |

**3/3 leads had emails found. 100% success rate.**

---

## Phase 3: Intelligence Scorer (LIVE)

Scores every lead for AI service need and outputs priority.

**Signals checked:**
- 🔘 **No call button** on website → needs click-to-call
- 🤖 **No chat widget** → needs AI chatbot
- 📅 **No booking system** → needs online booking
- 📉 **Low SEO score** → needs SEO optimization
- ⭐ **Low Google reviews** → needs reputation management
- 🏢 **Service business** → high priority category

**Scoring weights:**
| Signal | Points |
|---|---|
| No website | 40 |
| No chat widget | 20 |
| No call button | 15 |
| No booking system | 10 |
| Poor SEO (<40) | 25 |
| Service business | 15 |
| Low reviews | 20 |
| Poor rating (<3.5) | 5 |

**Priority thresholds:**
- 🔥 **Hot**: 75+ points
- 🌡️ **Warm**: 50-74 points
- ❄️ **Cold**: <50 points

**Test results (3 plumbers):**
```
Royal Flushed Plumbing     → 100/100 🔥 HOT
Grey Army Pty Ltd          → 100/100 🔥 HOT  (poor rating 3.3)
Plumb Medic                → 100/100 🔥 HOT
```

All scored 🔥 HOT because:
- ✅ No chat widget
- ✅ No booking system
- ✅ No call button
- ✅ Need reputation management (low reviews)
- ✅ Need SEO help

**Output columns added to CSV:**
- `ai_service_score` (0-100)
- `priority` (hot/warm/cold)
- `needs_ai_voice` (bool)
- `needs_web_presence` (bool)
- `needs_reputation_mgmt` (bool)
- `needs_call_button` (bool)
- `opportunities` (list of service needs)

---

## Quick Start (New Pipeline)

```bash
# Full pipeline: Maps → Websites → Emails → CSV
cd leadgen
source .venv/bin/activate
bash scripts/run-browser-pipeline.sh "plumbers" "Melbourne, Australia" 10

# Output files:
#   data/processed/browser_raw.json        — raw Maps data
#   data/processed/browser_enriched.json   — with emails/socials
#   data/reports/outreach_ready.csv       — ready for outreach
```

---

## Legacy: Peekaboo Scraper

Still available as fallback:
```bash
bash scripts/run-peekaboo-scraper.sh "plumbers" "Melbourne, Australia" 10
```

Peekaboo gets basic info (name, address, phone, rating) but **cannot extract websites** from the list view. Use browser pipeline for full enrichment.

---

## Directory Layout

```text
leadgen/
  scripts/
    run-browser-pipeline.sh    ← NEW — full pipeline
    run-peekaboo-scraper.sh    — legacy fallback
  src/
    browser_scraper.py         — Maps scraping with website extraction
    contact_enricher.py        ← NEW — website contact extraction
    website_analyzer.py        — tech stack analysis
    scoring.py                 — lead scoring
    pipeline.py                — follow-up tracking
  data/
    processed/
      browser_raw.json           ← raw browser scrape
      browser_enriched.json      ← with emails/socials
      leads_db.json              — persistent dedup DB
    reports/
      outreach_ready.csv         ← outreach-ready leads
      daily_delta.csv            — new leads only
      daily_report_*.md          — daily summary
  config/
    config.yaml                  — categories, locations, limits
```

---

## Daily Operations

### Manual run
```bash
cd leadgen
source .venv/bin/activate
bash scripts/run-browser-pipeline.sh
```

### Cron setup (daily at 7 AM)
```bash
bash cron/setup.sh
```

---

## Data Schema (Enriched Lead)

```json
{
  "name": "Plumb Medic - Emergency Plumber Melbourne",
  "address": "3/394 Collins St, Melbourne VIC 3000, Australia",
  "phone": "+61 1300 100 977",
  "website": "https://www.plumbmedic.com.au",
  "website_missing": false,
  "maps_url": "https://www.google.com/maps/place/...",
  "email": "info@plumbmedic.com.au",
  "emails_found": ["info@plumbmedic.com.au"],
  "contact_page_url": "https://www.plumbmedic.com.au/contact",
  "social_links": {
    "facebook": "https://facebook.com/plumbmedicau",
    "instagram": null,
    "linkedin": null,
    "twitter": null,
    "youtube": null
  },
  "contact_confidence": "high",
  "has_complete_contact_info": true,
  "rating": 4.9,
  "reviews": 335,
  "category": "plumbers",
  "location": "Melbourne, Australia"
}
```

---

## Notes

- Browser mode visits each Maps listing detail page → extracts website
- Contact enricher visits each website → scrapes emails, phones, socials
- Pipeline runs ~2-3 min for 10 leads (depends on website load times)
- CAPTCHA detection halts current query and saves debug artifacts
- Deduplication prevents re-processing same business

## Next Steps

- [ ] Phase 3: Intelligence scoring (priority ranking)
- [ ] Phase 4: Auto-outreach draft generation
- [ ] Phase 5: CRM integration (HubSpot/Pipedrive)

---

*Updated: 2026-05-22 — Browser pipeline + contact enrichment live*
