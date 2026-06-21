=== APIFY ACTOR WRAPPER — Build Prompt ===

Build a simple SaaS website that wraps an existing Apify actor (pre-built scraper) and adds a payment layer.

PRODUCT: LeadScraper Pro — a tool that scrapes local business leads from Google Maps for a specific niche.

CORE FEATURES:
- Landing page with niche selector (e.g., dentists, roofers, plumbers)
- Simple input: city/zip + industry
- Backend calls Apify Google Maps scraper actor via API
- Returns CSV/downloadable list with: business name, phone, address, website, rating
- Credit system: user buys credits, each scrape costs X credits
- Stripe Checkout for payments
- User dashboard showing credit balance + download history

TECH STACK:
- Frontend: Next.js or simple HTML/CSS/JS (vibe code friendly)
- Backend: Node.js or Python FastAPI
- Payments: Stripe
- Scraper API: Apify (https://apify.com/api)
- Hosting: Vercel or Replit

API ARBITRAGE MATH:
- Apify cost: ~$0.01 per 100 results
- Sell: 100 results for $5-10 (500-1000x markup)
- Credit pack: $35 = 500 results

TARGET: B2B sales teams, cold callers, marketing agencies

SUCCESS CRITERIA:
- User can buy credits, run a scrape, download CSV in < 2 minutes
- No-code setup for you — just configure Apify API key + Stripe keys
