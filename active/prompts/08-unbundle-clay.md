=== UNBUNDLE CLAY.COM — Build Prompt ===

Build a single-feature data enrichment tool that's cheaper than Clay.

PRODUCT: LeadEnrich — "One feature, done perfectly"

CORE FEATURES:
- ONE feature only: enrich a CSV of leads with missing data
- Upload CSV with names + companies
- Returns: email, LinkedIn, job title, company size, industry, location
- Uses underlying APIs (not Clay): Hunter.io, Clearbit, Apify LinkedIn scraper
- Pay-per-enrichment: $0.10 per lead enriched
- Bulk upload: drag CSV, process 1000 leads overnight
- Download enriched CSV

TECH STACK:
- Frontend: Next.js + Tailwind
- Backend: Python FastAPI
- Enrichment APIs: Hunter.io (emails), Clearbit (company data), Apify (LinkedIn)
- Database: PostgreSQL
- Payments: Stripe (prepay credits, $0.10/enrichment)
- Hosting: Railway + Vercel

TARGET: B2B sales teams, SDRs, marketing agencies

SUCCESS CRITERIA:
- Upload CSV → enriched in < 5 minutes for 100 leads
- 80%+ email find rate
- Cost < 10% of Clay ($149/month) for same feature
