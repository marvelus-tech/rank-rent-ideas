=== YELP SCRAPER FOR LOCAL INTEL — Build Prompt ===

Build a lead generation tool from Yelp data.

PRODUCT: YelpLeads — "Turn Yelp into your lead database"

CORE FEATURES:
- Search by: business type + city (e.g., "plumbers in Austin")
- Scrape: business name, phone, address, owner name (if listed), review count, rating, website
- Filter by: rating threshold, review count, has website (yes/no)
- Export to CSV
- Map view: see leads on interactive map
- "Verified" check: confirm phone still works
- Save lists + add notes

TECH STACK:
- Frontend: Next.js + Tailwind + Mapbox
- Backend: Node.js + Express
- Scraper: Apify Yelp scraper
- Database: PostgreSQL
- Payments: Stripe ($39/month, $99 for agencies)
- Hosting: Vercel + Railway

TARGET: Local service businesses wanting competitors, suppliers pitching locally, marketing agencies

SUCCESS CRITERIA:
- Search "plumbers Austin" → 200 leads in 30 seconds
- 90%+ phone numbers accurate
- Map view shows geographic clusters
