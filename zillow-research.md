# Zillow Real Estate Skill — Research & Recommendation

## What We Found

### Existing Zillow MCP Packages (Not True OpenClaw Skills)

| Package | Approach | Pros | Cons |
|---------|----------|------|------|
| **zillow-mcp** (chrischall) | Browser proxy via fetchproxy extension | Full Zillow session access, saved searches, personal data | Requires browser extension, complex setup, ToS risk |
| **@striderlabs/mcp-zillow** | Playwright/Chromium scraping | No extension needed, headless browser | Heavier deps, still scraping, ToS risk |
| **zillow-mcp-server** (sap156) | Bridge API | Official data, clean API | Requires gated Bridge API key (MLS partners only) |

**Key Problem**: None are OpenClaw `SKILL.md` format — they're all MCP (Model Context Protocol) servers for Claude Desktop, not standalone agent skills.

---

## Recommendation: Build Our Own Enhanced Skill

### Architecture Decision

**Option A: Wrap zillow-mcp (Recommended for speed)**
- Install `zillow-mcp` as dependency
- Create OpenClaw SKILL.md that invokes it via `exec`
- Add our own caching, formatting, and business logic layer

**Option B: Build from scratch using RapidAPI**
- Use RapidAPI's Zillow endpoints (stable, documented)
- No browser scraping, no ToS issues
- Rate-limited but predictable

**Option C: Hybrid (Best long-term)**
- RapidAPI for search/listings (stable, bulk)
- zillow-mcp for personal data (saved searches, favorites)
- Fallback between sources

---

## Proposed OpenClaw Skill Structure

```
skills/zillow-enhanced/
├── SKILL.md              # Main skill definition
├── scripts/
│   ├── search.sh         # Property search wrapper
│   ├── details.sh        # Property details wrapper
│   ├── compare.sh        # Multi-property comparison
│   └── market-report.sh  # Market data wrapper
├── lib/
│   ├── cache.js          # Response caching (24hr)
│   ├── format.js         # Output formatting
│   └── rate-limit.js     # Rate limit handling
└── config/
    └── default.json      # Default search params
```

### Enhanced Features (Beyond Basic MCP)

1. **Smart Caching**: Cache results 24hr to avoid repeated API calls
2. **Batch Operations**: Compare 12+ properties side-by-side
3. **Market Alerts**: Monitor price drops, new listings in saved areas
4. **Investment Analysis**: Cap rate, cash flow, appreciation estimates
5. **Neighborhood Scoring**: Schools, crime, walkability aggregation
6. **Export Formats**: CSV, PDF, JSON for further analysis
7. **Lead Generation**: Extract agent contacts, FSBO identification

---

## Implementation Plan

### Phase 1: RapidAPI Foundation (Week 1)
- Sign up for RapidAPI Zillow API
- Build basic search/details/compare tools
- Add caching layer
- Create SKILL.md with clear usage patterns

### Phase 2: Enhanced Features (Week 2-3)
- Market report generation
- Investment calculator
- Neighborhood scoring
- Alert system (cron jobs)

### Phase 3: Integration (Week 4)
- PropertyPilot integration (if applicable)
- Export to Google Sheets/Airtable
- Email alerts setup

---

## Technical Notes

### RapidAPI Zillow Endpoints Available

```
propertyExtendedSearch  — Search by location, filters
property                — Details by ZPID
propertyByAddress       — Lookup by address
images                  — Photo gallery
zestimate               — Price estimate
comps                   — Comparable sales
marketReport            — Market data by ZIP
```

### Rate Limits
- Free tier: 100 requests/month
- Basic: 1000 requests/month ($10-20)
- Pro: 10000 requests/month ($50-100)

### Authentication
```bash
export RAPIDAPI_KEY="your-key-here"
export RAPIDAPI_HOST="zillow-com1.p.rapidapi.com"
```

---

## Files Created

| File | Description |
|------|-------------|
| `~/.openclaw/workspace/skills/zillow-real-estate/SKILL.md` | Basic Zillow skill (RapidAPI approach) |
| `~/.openclaw/workspace/SORTED-delivery.md` | SORTED landing page summary |

## Next Steps

1. **Choose approach**: RapidAPI (safe) vs zillow-mcp (full features)
2. **Get API keys**: RapidAPI signup + subscription
3. **Build enhanced skill**: Add caching, formatting, batch ops
4. **Test with real searches**: Verify data quality
5. **Document usage patterns**: Create examples for common workflows

Want me to build the enhanced skill now?
