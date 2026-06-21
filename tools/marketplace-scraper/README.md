# Facebook Marketplace Scraper (Playwright MVP)

Python 3.10+ prototype for scraping Facebook Marketplace listings and flagging potentially underpriced resale opportunities.

## What this MVP does

- Logs into Facebook using email/password (supports session cookie reuse)
- Handles likely 2FA/checkpoint flow by pausing for manual completion
- Detects CAPTCHA/checkpoint pages and exits gracefully
- Searches Marketplace by keyword + location
- Scrolls results (infinite scroll) and extracts listing URLs
- Extracts listing details:
  - title
  - price (raw + parsed)
  - location
  - seller info
  - description
  - image URLs
  - listing date text
  - listing URL
- Saves raw results to JSON + CSV
- Runs price analysis to estimate market value and flag opportunities
- Sends alerts to console, file, and optional webhook with rate limiting

---

## Duplicate Tracking (Obsidian)

Instead of SQLite, this scraper uses **Obsidian notes** to track seen listings and prevent duplicate alerts:

- Each listing gets a markdown note in `Listings/` folder
- Notes use frontmatter with URL, first_seen date, price, location
- Before alerting, the system checks if a note exists for that URL
- New listings are automatically tracked after the first alert

### Obsidian Setup

1. **Install Obsidian**: `brew install --cask obsidian`
2. **Vault created at**: `~/Documents/Obsidian Vaults/MarketplaceScraper/`
3. **Auto-detection**: The tracker auto-detects your vault via `obsidian-cli`

### Viewing Tracked Listings

Open Obsidian and browse:
- `Listings/` — All tracked marketplace items
- Each note contains: price history, location, full JSON data, manual notes section

### Configuration

In `config.yaml`:
```yaml
alerts:
  dedup_enabled: true        # Toggle duplicate filtering
  obsidian_vault_path: ""    # Auto-detect (or set explicit path)
```

---

## Project structure

```text
tools/marketplace-scraper/
├── scraper/
│   ├── __init__.py
│   ├── marketplace_scraper.py
│   ├── price_analyzer.py
│   ├── alerter.py
│   └── obsidian_tracker.py   # ← NEW: Obsidian-based duplicate tracking
├── config.yaml
├── .env.example
├── requirements.txt
├── README.md
└── run.py
```

---

## Setup

```bash
cd ~/.openclaw/workspace/tools/marketplace-scraper
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

Create `.env` from the example:

```bash
cp .env.example .env
# fill FB_EMAIL + FB_PASSWORD
```

## Usage

```bash
cd ~/.openclaw/workspace/tools/marketplace-scraper
source .venv/bin/activate
python run.py
```

MVP default search is single keyword/location:
- keyword: `lawn mower`
- location: `Melbourne, VIC`
- max_listings: `20`

Outputs are written to `output/`:
- `marketplace_results.json`
- `marketplace_results.csv`
- `marketplace_results_analyzed.json`
- `opportunities_alerts.json` (if file alerts enabled)

---

## Configuration (`config.yaml`)

- `facebook`: credentials + cookies path
- `scraper`: headless mode, scroll count, delay controls, price range
- `searches`: keyword/location/category list
- `analyzer`: discount threshold, min profit, category rules, manual value overrides
- `alerts`: console/file/webhook/rate limit
- `output`: output directory and file prefix

You can add more searches later, but MVP is tuned for single search first.

---

## Anti-detection measures included (MVP)

1. Session reuse via saved cookies (reduces repeated logins)
2. Randomized delays between actions
3. Browser args reducing obvious automation fingerprints
4. Optional `playwright-stealth` integration
5. Conservative scroll + extraction pace
6. CAPTCHA/checkpoint detection and graceful stop

---

## Known limitations

- Facebook actively changes DOM and anti-bot behavior; selectors may break
- Full reliability requires periodic selector maintenance
- 2FA/CAPTCHA still often require manual intervention
- Seller info and listing date are best-effort text extraction
- Heavy scraping can trigger account restrictions
- This is an MVP focused on first successful extraction (10-20 listings), not enterprise scale

---

## Safety / compliance notes

- Only scrape data you are allowed to access
- Respect platform Terms of Service and local laws
- Use low request volume to reduce account risk

---

## Next upgrades (recommended)

1. Harden selectors with fallback locator strategies
2. Add retries + dead-letter logging for failed listing pages
3. ~~Add duplicate suppression across runs (SQLite)~~ ✅ **Replaced with Obsidian-based tracking**
4. Integrate external comps APIs (eBay sold listings, Gumtree) for stronger market value estimates
5. Add screenshot capture on errors and CAPTCHA detection
