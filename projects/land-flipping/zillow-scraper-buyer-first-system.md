# Buyer-First Land Flipping System
## Using Zillow Scraper + Apify for Builder-First Model

**Date:** 2026-06-21  
**Model:** Reverse wholesaling / builder-matchmaking  
**Core Tool:** https://apify.com/maxcopell/zillow-scraper

---

## 🎯 YOUR MODEL RECAP

**You're NOT:** Buying cheap land and hoping to find a buyer  
**You ARE:** Pre-qualifying builder demand → finding matching land → assigning contracts

**The Formula:**
```
Builder Ecosystem Depth × Off-Market Land Availability × Assignment Velocity = Profit
```

---

## 🛠️ THE ZILLOW SCRAPER SETUP

### Tool Specs
- **Cost:** $1.30 / 1,000 results (pay-per-event)
- **Free tier:** 2,000+ results free
- **Output:** JSON, CSV, Excel, HTML, XML
- **Data extracted:** Address, price, ZPID, zestimate, lot size, photos, broker name, days on Zillow
- **No daily limits** (unlike Zillow API)

### What You Need
1. **Apify account** (free to start)
2. **Zillow search URLs** with filters applied
3. **Apify API token** (for automation)

---

## 🔄 PHASE 1: BUILD BUILDER LIST (Using Zillow Scraper)

### Step 1: Find Active Builders (New Construction)

**Zillow Filters to Apply:**
- **Status:** For Sale
- **Home Type:** Houses (not lots)
- **Year Built:** 2025 or newer
- **Days on Zillow:** Anytime

**Why:** These are NEW CONSTRUCTION listings = builders actively building RIGHT NOW

**Zillow Scraper Input:**
```json
{
  "searchUrls": [
    {
      "url": "https://www.zillow.com/homes/for_sale/?searchQueryState={...filters...}"
    }
  ],
  "extractionMethod": "PAGINATION_WITH_ZOOM_IN"
}
```

**What You Get:**
| Field | Use For |
|-------|---------|
| `brokerName` | Builder name or agent representing builder |
| `address` | Location of new construction |
| `price` | Price point = buyer box indicator |
| `lotSize` | Lot sizes builder is using |
| `photos` | Verify it's actually new construction |
| `url` | Click through to get builder contact info |
| `ZPID` | Unique identifier for tracking |

---

### Step 2: Extract Builder Contact Info

**For Each Builder Found:**

1. **Click the Zillow listing URL** from scraper output
2. **Find builder name** in listing description
3. **Google builder name + "contact"** or:
   - Check builder website "Contact Us"
   - Look for "Land Acquisition" or "Lot Purchases" department
   - Find VP of Land or Director of Acquisitions
4. **Call and ask for buy box:**
   - "Hi, I'm a land scout. What size lots are you buying in [AREA]?"
   - "What price range per lot?"
   - "What utilities do you need?"
   - "How fast can you close?"
   - "Do you buy off-market?"

**Record in CRM:**
```
Builder: [Name]
Contact: [Phone/Email]
Markets: [Zip codes]
Buy Box: [Lot size, price, utilities]
Volume: [Permits/year]
Status: [Active/Interested/Not interested]
```

---

### Step 3: Build Buyer Box Database

**Target: 50 builder buy boxes per market**

**Example Database Structure:**

| Builder | Market | Lot Size | Price/Lot | Utilities | Timeline | Contact |
|---------|--------|----------|-----------|-----------|----------|---------|
| Lennar | Waller County, TX | 0.15-0.25 ac | $30K-$60K | Water/sewer | 30 days | [Phone] |
| Taylor Morrison | Bastrop County, TX | 0.5-1 ac | $60K-$120K | Septic OK | 45 days | [Phone] |
| Drees Homes | Johnston County, NC | 0.5-2 ac | $50K-$100K | City water | 30 days | [Phone] |

**Why 50 builders?**
> "Out of 163 people, you're telling me you can't sell your deal?" — YouTube speaker

More builders = more buyer boxes = higher probability of matching your land.

---

## 🔄 PHASE 2: FIND MATCHING LAND (Using Zillow Scraper)

### Step 1: Scrape Sold Lots (Market Validation)

**Zillow Filters:**
- **Status:** Sold
- **Home Type:** Lots/Land
- **Sold in last:** 30 days (or 90 days for more data)

**What You Get:**
- Yellow dots = proven sales
- Price points = what builders are paying
- Clusters = hot submarkets

**Analysis:**
```
If sold lots in [AREA] = $15K-$20K
And builder buy box = $10K-$15K/lot
Then your offer = $8K-$12K (10-15% below builder buy)
Your profit = $3K-$8K per deal
```

---

### Step 2: Scrape For-Sale Lots (Competition Check)

**Zillow Filters:**
- **Status:** For Sale
- **Home Type:** Lots/Land
- **Days on Zillow:** Anytime

**What You Get:**
- Current competition
- Price ranges
- How long lots sit on market

**Red flags:**
- Lots sitting 200+ days = weak market
- Prices dropping = oversupply
- Few listings = possible opportunity

---

### Step 3: Cross-Reference with Builder Buy Boxes

**The Matching Process:**

1. **Builder buy box:** 0.5-1 acre, $60K-$120K, septic OK, Bastrop County
2. **Scraped sold lots:** 0.6 acre sold for $85K, 0.8 acre sold for $95K
3. **Target:** Find off-market 0.5-1 acre parcels in Bastrop County
4. **Offer:** $50K-$70K (15% below market)
5. **Sell to builder:** $80K-$100K
6. **Profit:** $15K-$30K

---

## 🔄 PHASE 3: SOURCE OFF-MARKET LAND (PropStream + Direct Mail)

### Step 1: Pull Targeted Lists (PropStream)

**Filters:**
1. **Property type:** Vacant land
2. **Status:** Off-market
3. **Ownership length:** 10+ years
4. **Owner type:** Individual/mixed
5. **Last sale price:** Under $5,000 (or under market value)
6. **Lot size:** Match builder buy box
7. **County:** Match builder market

**Result:** 500-2,000 qualified leads per market

---

### Step 2: Skip Trace (Find Phone Numbers)

**Tools:**
- BatchSkipTracing.com ($0.10/record)
- PropStream (built-in skip tracing)
- TLO, LexisNexis (higher cost, higher accuracy)

**What you need:**
- Owner name
- Property address
- Mailing address (if different)
- Phone numbers (landline + cell)
- Email (if available)

---

### Step 3: Marketing Campaign

**Option A: Mass Texting (Recommended)**
- Cost: $0.03/text
- 1,000 texts = $30
- Response rate: 1-3%
- 1,000 texts → 10-30 responses → 1-3 deals

**Text Templates:**
```
"Hi [Name], I'm interested in buying your land at [Address]. 
Can you tell me if you'd consider selling? - [Your Name]"
```

```
"Hi [Name], I buy land in [County]. Would you consider 
an offer on your property at [Address]? Quick close possible. - [Your Name]"
```

**Option B: Cold Calling**
- Higher quality conversations
- More time-intensive
- Better for learning buy boxes

**Option C: Direct Mail**
- Postcards: $0.50-$1.00 each
- Letters: $1.00-$2.00 each
- Slower response but higher trust

---

## 🔄 PHASE 4: LOCK UP DEALS & ASSIGN TO BUILDERS

### Step 1: Make Offers

**The Offer Formula:**
```
Builder buy box price × 0.85 = Your offer price
(15% below builder's typical buy)
```

**Example:**
- Builder pays: $80K for 0.5-acre lot
- Your offer: $68K (15% below)
- Assignment fee: $12K

**How to present:**
"I'll buy your land for $68,000, close in 30 days, and pay all closing costs. No fees, no commissions, no hassle."

---

### Step 2: Sign Contract (PSA)

**Key Contract Terms:**
- **Purchase price:** Your offer
- **Earnest money:** $100-$500 (keeps it low)
- **Inspection period:** 10-30 days (time to find buyer)
- **Closing date:** 30-45 days
- **Assignment clause:** "Buyer may assign this contract"
- **Special stipulation:** "Subject to partner approval" (gives you exit)

**Use BuyerBridge contract templates** (if available) or hire real estate attorney.

---

### Step 3: Assign to Builder

**The Assignment Process:**

1. **Call builder:** "I have a 0.5-acre lot in [Area] that matches your buy box. Are you interested?"
2. **Send photos + details:** Address, lot size, utilities, price
3. **Builder says yes:** Send assignment agreement
4. **Assignment fee:** Your profit ($5K-$20K typical)
5. **Builder closes directly with seller:** You get paid at closing

**Assignment Agreement:**
```
Original contract: $68,000
Assignment fee: $12,000
Builder pays: $80,000 total
Seller gets: $68,000
You get: $12,000
```

---

## 📊 THE COMPLETE WORKFLOW

```
WEEK 1: BUILD BUILDER LIST
├── Day 1-2: Scrape Zillow for new construction (2025+ built)
├── Day 3-4: Extract builder contact info
├── Day 5-7: Call 20 builders, get buy boxes
└── Result: 20-50 builder buy boxes in database

WEEK 2: VALIDATE MARKET & FIND LAND
├── Day 1-2: Scrape Zillow sold lots (30 days) for price validation
├── Day 3-4: Pull PropStream lists matching buy boxes
├── Day 5-7: Skip trace 1,000 leads
└── Result: 1,000 qualified seller leads

WEEK 3: MARKET & LOCK UP
├── Day 1-2: Send 1,000 texts ($30)
├── Day 3-5: Follow up with responders
├── Day 6-7: Make offers, sign 1-2 contracts
└── Result: 1-2 properties under contract

WEEK 4: ASSIGN & CLOSE
├── Day 1-2: Call builders, match properties
├── Day 3-5: Send assignment agreements
├── Day 6-7: Close deals, collect fees
└── Result: $5K-$20K profit
```

---

## 💰 THE MATH

### Costs (Per Month)
| Item | Cost |
|------|------|
| Zillow Scraper (Apify) | $1.30/1,000 results (first 2,000 free) |
| PropStream | ~$100/month |
| Skip tracing | $0.10/record × 1,000 = $100 |
| Mass texting | $0.03/text × 1,000 = $30 |
| **Total** | **~$230/month** |

### Revenue (Per Deal)
| Scenario | Profit |
|----------|--------|
| Conservative | $5,000 |
| Average | $10,000 |
| Good | $15,000-$20,000 |

### Monthly Scenarios
| Deals/Month | Profit | Annual |
|-------------|--------|--------|
| 1 | $10,000 | $120,000 |
| 2 | $20,000 | $240,000 |
| 4 | $40,000 | $480,000 |
| 10 | $100,000 | $1,200,000 |

---

## 🎯 TIER 1 MARKETS TO TARGET

Based on your research + YouTube videos:

### Texas ⭐⭐⭐
- **Counties:** Waller, Montgomery, Bastrop, Kaufman
- **Builder count:** 50+ per county
- **Land source:** Agricultural transition, aging farmers
- **Zillow scraper focus:** New construction in Houston, DFW, Austin

### Florida (Inland) ⭐⭐⭐
- **Counties:** Polk, Lake, Marion, Sumter
- **Builder count:** 40+ per county
- **Land source:** Citrus groves, active adult adjacencies
- **Zillow scraper focus:** New construction in Orlando, Lakeland, Ocala

### North Carolina ⭐⭐
- **Counties:** Rowan, Cabarrus, Johnston, Harnett
- **Builder count:** 20-30 per county
- **Land source:** Generational farmland, estate sales
- **Zillow scraper focus:** New construction in Charlotte, RTP corridor

### Arizona ⭐⭐
- **Counties:** Maricopa, Pinal
- **Builder count:** 30+ in Phoenix metro
- **Land source:** Desert land, long-term holders
- **Zillow scraper focus:** New construction in Buckeye, Surprise, Goodyear

### Tennessee ⭐⭐
- **Counties:** Rutherford, Wilson, Sumner
- **Builder count:** 15-20 per county
- **Land source:** Generational farmland
- **Zillow scraper focus:** New construction in Nashville, Murfreesboro

---

## 🛠️ AUTOMATION SETUP

### Using Apify API (Node.js Example)

```javascript
const { ApifyClient } = require('apify-client');

const client = new ApifyClient({
  token: 'YOUR_API_TOKEN',
});

// Run Zillow scraper for new construction in Houston
const input = {
  "searchUrls": [
    {
      "url": "https://www.zillow.com/homes/for_sale/Houston-TX/?searchQueryState={...}"
    }
  ],
  "extractionMethod": "PAGINATION_WITH_ZOOM_IN"
};

const run = await client.actor('maxcopell/zillow-scraper').call(input);
const { items } = await client.dataset(run.defaultDatasetId).listItems();

// Extract builder names from brokerName field
const builders = items.map(item => ({
  name: item.brokerName,
  address: item.address,
  price: item.price,
  lotSize: item.lotSize,
  url: item.url
}));

console.log(`Found ${builders.length} new construction listings`);
```

### Schedule Weekly Runs

```javascript
// Run every Monday at 9 AM
const cron = '0 9 * * 1';

await client.schedules().create({
  cronExpression: cron,
  actorId: 'maxcopell/zillow-scraper',
  input,
  description: 'Weekly builder scan - Houston'
});
```

---

## ✅ ACTION ITEMS

### Today
- [ ] Create Apify account (free)
- [ ] Get API token
- [ ] Pick 1 market (recommend: Texas or Florida)
- [ ] Build Zillow search URL for new construction

### This Week
- [ ] Run Zillow scraper for new construction
- [ ] Extract 20 builder names + contact info
- [ ] Call 10 builders, get buy boxes
- [ ] Run Zillow scraper for sold lots (validation)
- [ ] Sign up for PropStream free trial

### Next Week
- [ ] Pull PropStream list matching buy boxes
- [ ] Skip trace 1,000 leads
- [ ] Send 1,000 texts
- [ ] Follow up with responders
- [ ] Lock up first contract

### Month 1 Goal
- [ ] 50 builder buy boxes in database
- [ ] 1,000 seller leads contacted
- [ ] 1-2 deals closed
- [ ] $10K-$20K profit

---

## 🎯 KEY INSIGHT

**The Zillow scraper is your reconnaissance tool.**

Use it to:
1. **Map builder activity** (new construction = active buyers)
2. **Validate market prices** (sold lots = what builders pay)
3. **Identify submarkets** (clusters = hot areas)

Then use PropStream + direct mail/text to find the actual land.

**You're not scraping to buy listings. You're scraping to build intelligence.**
