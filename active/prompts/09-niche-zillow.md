=== NICHE ZILLOW — Build Prompt ===

Build a real estate marketplace for niche property types.

PRODUCT: NicheREI — "Zillow for RV parks, self-storage & laundromats"

CORE FEATURES:
- Browse niche real estate: RV parks, mobile home parks, self-storage, laundromats, car washes, billboards
- Search by: location, price range, cap rate, occupancy rate
- Listing pages: photos, financials (if available), location map, contact broker
- Scrape data from Crexi, LoopNet, BizBuySell via Apify
- Alert system: "Notify me when RV park listed in Florida"
- Investor tools: cap rate calculator, cash flow estimator
- Save favorites + compare listings

TECH STACK:
- Frontend: Next.js + Tailwind + Mapbox
- Backend: Node.js + Express
- Scraper: Apify actors for Crexi, LoopNet, BizBuySell
- Database: PostgreSQL
- Payments: Stripe ($79/month for investors, free basic search)
- Hosting: Vercel + Railway

TARGET: Real estate investors, RV park buyers, self-storage investors

SUCCESS CRITERIA:
- Search "RV parks under $500K in Florida" → results in 5 seconds
- Cap rate calculator on every listing
- Email alerts for new listings matching saved searches
