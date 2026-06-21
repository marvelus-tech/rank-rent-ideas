=== BIZBUYSELL ANALYZER — Build Prompt ===

Build an analytics tool for business buyers.

PRODUCT: BizIntel — "Know which businesses sell fastest"

CORE FEATURES:
- Scrape BizBuySell listings via Apify
- Analyze: time-to-sale by category, average asking vs selling price, top categories
- Dashboard: charts showing hottest business types
- Search by: industry, location, price range, cash flow
- "Deal score" — AI rates each listing (overpriced/fair/underpriced)
- Save searches + get alerts
- Export data to CSV

TECH STACK:
- Frontend: Next.js + Recharts (charts)
- Backend: Python FastAPI
- Scraper: Apify BizBuySell scraper
- AI scoring: OpenAI GPT-4o-mini
- Database: PostgreSQL
- Payments: Stripe ($59/month for serious buyers)
- Hosting: Railway + Vercel

TARGET: Business buyers, brokers, aspiring entrepreneurs

SUCCESS CRITERIA:
- Dashboard shows "restaurants sell in 90 days avg, laundromats in 45 days"
- Deal score helps buyers avoid overpriced listings
- Alert when matching business listed
