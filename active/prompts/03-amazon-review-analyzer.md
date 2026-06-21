=== AMAZON REVIEW ANALYZER — Build Prompt ===

Build a competitive intelligence tool for DTC brands that analyzes competitor Amazon reviews.

PRODUCT: ReviewIntel — "Spy on your competitors' customers"

CORE FEATURES:
- Input: Amazon product URL or ASIN
- Scrapes all reviews via Apify Amazon scraper
- AI analyzes reviews using OpenAI API:
  * What customers love (top 5 pros)
  * What customers hate (top 5 cons)
  * Feature requests (what's missing)
  * Sentiment breakdown (% positive/neutral/negative)
- Generates one-page PDF report
- Compare mode: analyze 2-3 competitor products side-by-side

TECH STACK:
- Frontend: React or Next.js
- Backend: Python (FastAPI)
- Scraper: Apify Amazon review scraper
- AI analysis: OpenAI GPT-4o-mini (cheap + fast)
- PDF generation: jsPDF or ReportLab
- Payments: Stripe ($29/report or $99/month unlimited)
- Hosting: Vercel + Railway

TARGET: Shopify brand owners, Amazon sellers, product managers

SUCCESS CRITERIA:
- Paste Amazon URL → get PDF report in < 3 minutes
- Report is actionable (not just stats — actual insights)
- Side-by-side comparison for competitive positioning
