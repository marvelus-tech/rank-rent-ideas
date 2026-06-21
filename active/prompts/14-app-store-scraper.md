=== APP STORE REVIEW SCRAPER — Build Prompt ===

Build a review intelligence tool for apps and services.

PRODUCT: AppReviewly — "What do users really think?"

CORE FEATURES:
- Input: App Store URL, Google Play URL, or Trustpilot URL
- Scrapes all reviews via Apify actors
- AI analysis: sentiment breakdown, feature requests, bugs mentioned, comparison vs competitors
- Report: one-page PDF with insights
- Track over time: "Your rating dropped 0.3 this month — here's why"
- Compare: your app vs 2 competitors side-by-side
- Alert: email when review volume spikes (new version released?)

TECH STACK:
- Frontend: Next.js + Tailwind
- Backend: Python FastAPI
- Scraper: Apify App Store + Google Play + Trustpilot scrapers
- AI: OpenAI GPT-4o-mini
- PDF: ReportLab
- Payments: Stripe ($29/app analysis, $99/month unlimited)
- Hosting: Railway + Vercel

TARGET: App developers, SaaS founders, product managers, UX researchers

SUCCESS CRITERIA:
- Paste App Store URL → PDF report in < 3 minutes
- Sentiment accuracy >85%
- Trend tracking shows correlation with app updates
