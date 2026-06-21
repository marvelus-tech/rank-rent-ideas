=== AI CUSTOMER SERVICE BOT FOR SHOPIFY — Build Prompt ===

Build an AI email auto-responder for Shopify stores.

PRODUCT: ReplyBot — "Your 24/7 customer service agent"

CORE FEATURES:
- Connects to Gmail/Outlook inbox via OAuth
- Reads incoming customer emails
- AI auto-responds using:
  * Store's FAQ page (scraped)
  * Return policy (uploaded PDF)
  * Shipping policy (uploaded)
  * Previous email thread context
- Handoff: forwards to human if confidence < 70%
- Dashboard: shows resolved vs escalated tickets
- Learns from corrections (human edits improve future replies)

TECH STACK:
- Frontend: Next.js dashboard
- Backend: Node.js + Express
- AI: OpenAI GPT-4o-mini
- Email: Gmail API + Nodemailer
- Shopify: Shopify API (for order lookup)
- Database: PostgreSQL (conversation history)
- Payments: Stripe ($49/month per store)
- Hosting: Railway + Vercel

TARGET: Shopify store owners doing $10K-500K/year

SUCCESS CRITERIA:
- 80%+ of common questions answered without human
- Setup in < 10 minutes (connect email, upload FAQ)
- Human handoff is smooth (includes full context)
