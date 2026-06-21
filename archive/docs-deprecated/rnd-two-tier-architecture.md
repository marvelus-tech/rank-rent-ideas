# R&D Department Architecture — Two-Tier Agent System

## Tier 1: SCOUT (Extractor)
**Role:** Monitor and extract raw content
**Model:** Flash (fast, cheap, polling)
**Schedule:** Every 6 hours

### Responsibilities
1. Poll TKO RSS feed
2. Check YouTube for new uploads
3. Extract transcripts (via yt-dlp)
4. Basic metadata capture:
   - Episode title & number
   - Duration
   - Key timestamps (if chapters available)
   - Raw transcript text

### Output Format (Raw Intel)
```json
{
  "source": "TKO Podcast",
  "episode": "#284",
  "title": "He Gave an AI $200. It Built Him a $100K Business in 13 Days",
  "url": "https://youtube.com/watch?v=...",
  "published": "2026-03-20",
  "transcript": "[full text]",
  "extracted_at": "2026-03-23T02:00:00Z",
  "scout_id": "scout-run-uuid"
}
```

### Triggers Tier 2
Saves raw intel to `.rnd/intel/raw/` and signals R&D Analyst to process.

---

## Tier 2: R&D ANALYST (Processor)
**Role:** Deep analysis and opportunity synthesis
**Model:** Opus or Sonnet (strategic thinking)
**Schedule:** Triggered by Scout (on-demand)

### Responsibilities
1. Read raw intel from Scout
2. Extract business ideas mentioned
3. Identify numbers (costs, revenue, timelines)
4. Classify opportunity type
5. Score match to Okeito's capabilities
6. Generate Opportunity Card
7. Research competitors/local market (if high match)

### Output Format (Opportunity Card)
```markdown
# OPPORTUNITY: AI-Powered Lead Gen Agency
**Source:** TKO Ep #284  
**Match Score:** 9/10

## The Play
[Detailed summary]

## Numbers
- Investment: $200-500
- Timeline: 2 weeks to first client
- Potential: $10-20K/month

## Okeito's Angle
[Specific execution path]

## Action Items
1. [Step one]
2. [Step two]

## Risk Assessment
[Barrier, competition, complexity]
```

### Deliverables
- Saves to `.rnd/opportunities/`
- High matches (>8/10): Immediate alert to Okeito
- Weekly digest of all opportunities

---

## Workflow Diagram

```
TKO Content (RSS/YouTube)
         ↓
    [SCOUT]  ←—— Every 6 hours
    (Flash model)
    Extract transcript
    Capture metadata
         ↓
  Saves to .rnd/intel/raw/
         ↓
  Triggers → [R&D ANALYST]
             (Opus/Sonnet)
             Deep analysis
             Generate card
                 ↓
        Match score ≥ 8? 
           YES → Alert Okeito immediately
           NO  → Queue for weekly digest
                 ↓
         Okeito reviews
                 ↓
         Priority opportunity?
            YES → Send to Night Owl (coding)
            NO  → Archive for future
```

---

## Why Two Tiers?

| Aspect | Scout | R&D Analyst |
|--------|-------|-------------|
| **Frequency** | Every 6 hours | Only when new content |
| **Cost** | ~$0.10-0.30 per check | ~$1-3 per analysis |
| **Model** | Flash (fast) | Opus/Sonnet (deep) |
| **Task** | Extract raw data | Strategic thinking |
| **Failure mode** | Retry cheaply | Human review if stuck |

**Benefits:**
- Scout runs constantly (cheap surveillance)
- Analyst only works on fresh intel (efficient)
- Separation prevents expensive re-processing
- Scout can batch multiple episodes for Analyst

---

## Activation Sequence

1. **Spawn Scout** — Configure RSS/YouTube monitoring
2. **Test run** — Scout extracts Ep #284 (or latest episode)
3. **Spawn R&D Analyst** — Process the raw intel
4. **Deliver first Opportunity Card** — Prove the chain works
5. **Schedule Scout** — Automated polling every 6 hours
6. **R&D Analyst** — On-demand trigger when Scout finds content

---

## File Structure

```
.rnd/
├── config.json                    # R&D settings
├── scout/
│   ├── last_check.json           # Timestamp tracking
│   └── sources.json              # RSS + YouTube feeds
├── intel/
│   └── raw/                      # Scout output
│       └── 2026-03-23-ep284.json
├── opportunities/                # Analyst output
│   ├── pending/                  # Awaiting review
│   ├── approved/                 # Sent to Night Owl
│   └── archived/                 # Low match / later
└── reports/
    └── weekly-digest.md
```

---

## Decision Point

**Which model tiers?**

**Option A: Economy**
- Scout: Flash (extract only)
- Analyst: Sonnet (analysis)
- Cost: ~$10-15/week

**Option B: Premium**
- Scout: Flash (extract only)
- Analyst: Opus (deep strategic analysis)
- Cost: ~$20-30/week

**Option C: Hybrid**
- Scout: Flash
- Analyst: Sonnet for most, Opus for high-match opportunities
- Cost: ~$15-20/week

**Recommended:** Option A (Economy) to start. Upgrade if Opportunity Cards need deeper strategic insight.
