=== CRUNCHBASE FUNDING ALERTS — Build Prompt ===

Build a funding alert service for investors and service providers.

PRODUCT: FundAlert — "Know who raised money before they announce it"

CORE FEATURES:
- Scrape Crunchbase for new funding rounds via Apify
- Filter by: industry, stage (seed/Series A/B/C), amount, location
- Alert channels: email, Slack, webhook
- Daily digest: "5 companies in your criteria raised $50M today"
- Company profile: amount, investors, previous rounds, headcount, website
- Export to CSV for CRM import
- "Similar companies" — find lookalikes who might raise next

TECH STACK:
- Frontend: Next.js + Tailwind
- Backend: Python FastAPI
- Scraper: Apify Crunchbase scraper
- Database: PostgreSQL
- Email: SendGrid
- Payments: Stripe ($79/month for investors, $149/month for agencies)
- Hosting: Railway + Vercel

TARGET: Angel investors, VCs, service providers (lawyers, accountants, recruiters), sales teams targeting startups

SUCCESS CRITERIA:
- Alert sent within 24 hours of funding announcement
- 90%+ accuracy on funding amount and investors
- CRM export works with Salesforce/HubSpot
