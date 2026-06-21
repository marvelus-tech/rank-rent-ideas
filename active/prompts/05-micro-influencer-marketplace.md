=== MICRO-INFLUENCER MARKETPLACE — Build Prompt ===

Build a tool that finds micro-influencers (5K-100K followers) in specific niches.

PRODUCT: MicroFindr — "Discover influencers your competitors don't know about"

CORE FEATURES:
- Search by niche (fitness, beauty, food, finance, etc.)
- Filter by: follower count, engagement rate, location, platform (IG/TikTok/YouTube)
- Scrape profile data via Apify actors
- Show: follower count, avg likes, engagement rate, email (if public), recent posts
- Export to CSV
- "Save to list" feature for campaign tracking
- Email outreach templates built-in

TECH STACK:
- Frontend: Next.js + Tailwind
- Backend: Node.js + Express
- Scraper: Apify Instagram/TikTok/YouTube scrapers
- Database: PostgreSQL (influencer data + user lists)
- Payments: Stripe ($39/month or $199/month for agencies)
- Hosting: Vercel + Railway

TARGET: Small DTC brands, marketing agencies, e-commerce sellers

SUCCESS CRITERIA:
- Search "vegan fitness micro influencers" → get 50 results in 30 seconds
- CSV export with email + engagement stats
- Engagement rate calculated accurately (not just follower count)
