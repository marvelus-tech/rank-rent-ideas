=== UPWORK SCRAPER WITH NLP SEARCH — Build Prompt ===

Build a better search tool for Upwork freelancers using natural language.

PRODUCT: TalentFinder — "Find freelancers with sentences, not filters"

CORE FEATURES:
- Natural language search: "Ukrainian mobile devs, 5+ yrs, 4.8★, $50K earnings"
- AI parses query into Upwork search parameters
- Scrape Upwork via Apify actor
- Results: name, photo, skills, rate, earnings, job success, portfolio links
- Compare view: side-by-side freelancer comparison
- Save to shortlist + export CSV
- "Invite to job" template generator

TECH STACK:
- Frontend: React + Tailwind
- Backend: Node.js + Express
- AI parsing: OpenAI GPT-4o-mini (converts natural language to search params)
- Scraper: Apify Upwork scraper
- Database: PostgreSQL
- Payments: Stripe ($99/month for recruiters, $29/month for founders)
- Hosting: Vercel + Railway

TARGET: Hiring agencies, recruiters, startup founders who hire freelancers

SUCCESS CRITERIA:
- Type sentence → get 20 matching freelancers in 20 seconds
- Side-by-side comparison with key stats highlighted
- One-click export for team review
