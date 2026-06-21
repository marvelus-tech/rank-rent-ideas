=== IMPORT YETI WRAPPER — Build Prompt ===

Build a cheaper, simpler version of ImportYeti for a specific audience.

PRODUCT: SupplierSpy — "See where any company manufactures"

CORE FEATURES:
- Search by company name (e.g., "Lululemon", "Nike")
- Shows: supplier names, locations, shipment counts, product categories
- Scrape ImportYeti data via Apify actor
- Simple dashboard with search + results table
- Export to CSV
- "Alert me" when new shipments detected

TECH STACK:
- Frontend: HTML + Tailwind + vanilla JS
- Backend: Python FastAPI
- Scraper: Apify ImportYeti scraper
- Database: SQLite or PostgreSQL
- Payments: Stripe ($49/month for unlimited searches)
- Hosting: Railway + Vercel

TARGET: Shopify store owners, Amazon sellers, product sourcers, competitor researchers

SUCCESS CRITERIA:
- Search "Lululemon" → see top 10 suppliers in 10 seconds
- CSV export with supplier contact info (if available)
- Alert system: email when new shipment data appears
