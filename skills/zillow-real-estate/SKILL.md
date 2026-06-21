---
name: zillow-real-estate
description: Search Zillow property listings, get home details, estimates, and market data via the Zillow API.
metadata:
  openclaw:
    requires:
      env: ["ZILLOW_API_KEY"]
---

# Zillow Real Estate Skill

Search and retrieve real estate data from Zillow's API endpoints.

## Setup

Requires a Zillow API key. Get one at:
- Bridge Data Output (bridgedataoutput.com) — official Zillow data partner
- Or RapidAPI (rapidapi.com/apidojo/api/zillow1)

Set as environment variable:
```bash
export ZILLOW_API_KEY="your_key_here"
```

## Available Operations

### 1. Search Properties

Search for properties by location, price range, beds/baths, etc.

```bash
curl -X GET "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch?location=seattle%2C%20wa&home_type=Houses&minPrice=300000&maxPrice=800000&bedsMin=2&bathsMin=2" \
  -H "X-RapidAPI-Key: $ZILLOW_API_KEY" \
  -H "X-RapidAPI-Host: zillow-com1.p.rapidapi.com"
```

**Parameters:**
- `location` — City, state, or address (URL encoded)
- `home_type` — Houses, Townhomes, Condos, etc.
- `minPrice`, `maxPrice` — Price range
- `bedsMin`, `bathsMin` — Minimum beds/baths
- `sqftMin`, `sqftMax` — Square footage range
- `daysOnZillow` — How long listed
- `sort` — Price, Newest, etc.

### 2. Get Property Details

Get full details for a specific property by Zillow ID.

```bash
curl -X GET "https://zillow-com1.p.rapidapi.com/property?zpid=12345678" \
  -H "X-RapidAPI-Key: $ZILLOW_API_KEY" \
  -H "X-RapidAPI-Host: zillow-com1.p.rapidapi.com"
```

### 3. Get Property Images

```bash
curl -X GET "https://zillow-com1.p.rapidapi.com/images?zpid=12345678" \
  -H "X-RapidAPI-Key: $ZILLOW_API_KEY" \
  -H "X-RapidAPI-Host: zillow-com1.p.rapidapi.com"
```

### 4. Get Zestimate (Price Estimate)

```bash
curl -X GET "https://zillow-com1.p.rapidapi.com/zestimate?zpid=12345678" \
  -H "X-RapidAPI-Key: $ZILLOW_API_KEY" \
  -H "X-RapidAPI-Host: zillow-com1.p.rapidapi.com"
```

### 5. Search by Address

```bash
curl -X GET "https://zillow-com1.p.rapidapi.com/propertyByAddress?address=123%20Main%20St%2C%20Seattle%2C%20WA" \
  -H "X-RapidAPI-Key: $ZILLOW_API_KEY" \
  -H "X-RapidAPI-Host: zillow-com1.p.rapidapi.com"
```

### 6. Get Comparable Sales (Comps)

```bash
curl -X GET "https://zillow-com1.p.rapidapi.com/comps?zpid=12345678&count=10" \
  -H "X-RapidAPI-Key: $ZILLOW_API_KEY" \
  -H "X-RapidAPI-Host: zillow-com1.p.rapidapi.com"
```

### 7. Get Market Data

```bash
curl -X GET "https://zillow-com1.p.rapidapi.com/marketReport?zip=98101" \
  -H "X-RapidAPI-Key: $ZILLOW_API_KEY" \
  -H "X-RapidAPI-Host: zillow-com1.p.rapidapi.com"
```

## Response Format

All endpoints return JSON. Common fields:

```json
{
  "zpid": "12345678",
  "address": {
    "streetAddress": "123 Main St",
    "city": "Seattle",
    "state": "WA",
    "zipcode": "98101"
  },
  "price": 750000,
  "bedrooms": 3,
  "bathrooms": 2,
  "livingArea": 2100,
  "homeType": "SINGLE_FAMILY",
  "daysOnZillow": 5,
  "zestimate": 745000,
  "rentZestimate": 3200,
  "photos": ["https://...", "https://..."],
  "description": "Beautiful home...",
  "latitude": 47.6062,
  "longitude": -122.3321
}
```

## Usage Examples

**Find 3-bedroom houses in Austin under $600k:**
```bash
curl -X GET "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch?location=austin%2C%20tx&home_type=Houses&maxPrice=600000&bedsMin=3" \
  -H "X-RapidAPI-Key: $ZILLOW_API_KEY" \
  -H "X-RapidAPI-Host: zillow-com1.p.rapidapi.com"
```

**Get details for a specific property:**
```bash
curl -X GET "https://zillow-com1.p.rapidapi.com/property?zpid=12345678" \
  -H "X-RapidAPI-Key: $ZILLOW_API_KEY" \
  -H "X-RapidAPI-Host: zillow-com1.p.rapidapi.com"
```

## Rate Limits

RapidAPI free tier: 100 requests/month
Paid tiers: 1000-10000+ requests/month

## Error Handling

Common errors:
- `401` — Invalid API key
- `429` — Rate limit exceeded
- `404` — Property not found
- `500` — Server error

Always check response status and handle errors gracefully.
