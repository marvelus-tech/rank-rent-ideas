=== REDDIT SENTIMENT SCRAPER — Build Prompt ===

Build a brand monitoring tool for Reddit.

PRODUCT: RedditMonitor — "What Reddit really thinks about your brand"

CORE FEATURES:
- Monitor subreddits for mentions of brand/product/keyword
- Scrape Reddit via Apify actors
- Sentiment analysis: positive/negative/neutral per mention
- Trend tracking: sentiment over time
- Alert: email/Slack when sentiment drops or spikes
- Competitor comparison: your brand vs 2 competitors on Reddit
- "Crisis detector" — flag threads with high negative sentiment
- Dashboard: word cloud of most mentioned features/issues

TECH STACK:
- Frontend: Next.js + Tailwind + Recharts
- Backend: Python FastAPI
- Scraper: Apify Reddit scraper
- AI: OpenAI GPT-4o-mini (sentiment analysis)
- Database: PostgreSQL
- Alerts: SendGrid + Slack API
- Payments: Stripe ($49/month per brand monitored)
- Hosting: Railway + Vercel

TARGET: Brand managers, product managers, marketing teams, PR agencies

SUCCESS CRITERIA:
- Monitor 10 subreddits, detect mentions in < 1 hour
- Sentiment accuracy >80%
- Crisis alert sent within 2 hours of negative thread going viral
