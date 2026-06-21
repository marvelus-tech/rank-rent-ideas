# Peekaboo Agent Upgrade — Architecture Notes

## What Was Built

Two new files that transform the lead scraper from a "script" into an "agent":

1. **`src/peekaboo_agent.py`** — Core vision-driven agent framework
2. **`src/peekaboo_maps_agent.py`** — Google Maps specialization

## The Manus Gap (And How We Closed It)

| Manus Feature | Before (Script) | After (Agent) |
|---|---|---|
| **Vision before action** | ❌ Blind coordinate clicks | ✅ `peekaboo see --annotate` before every click |
| **Self-correction** | ❌ One-shot, fail = done | ✅ Retry with exponential backoff + alternate strategies |
| **State awareness** | ❌ Stateless, no memory | ✅ JSON state file, resume after crash |
| **Verify outcomes** | ❌ Assume it worked | ✅ Screenshot verification after every action |
| **Adaptive strategy** | ❌ One extraction method | ✅ 3 strategies: vision → JS console → clipboard fallback |
| **Element targeting** | ❌ Hardcoded x,y coords | ✅ Element IDs (B1, B2) from annotated screenshots |
| **Error recovery** | ❌ Crash + manual restart | ✅ Auto-retry, alternate strategy, report failure |
| **Progress reporting** | ❌ Silent until done | ✅ Real-time phase/step logging |

## Agent Loop Architecture

```
OBSERVE   → peekaboo see --annotate --path /tmp/step_N.png
ANALYZE   → peekaboo image --path step_N.png --analyze "What do I see?"
PLAN      → Heuristic: element ID for search box? results? detail panel?
ACT       → peekaboo click --on B3  (not --coords 300,220)
VERIFY    → peekaboo see --annotate again — did the detail panel open?
RECOVER   → If no: press Escape, retry, or switch to alternate strategy
```

## Multi-Strategy Extraction

When opening a business detail panel, the agent tries in order:

1. **Vision extraction** (`_extract_via_vision`) — uses `peekaboo see --analyze` to read the detail panel directly
2. **JS console injection** (`_extract_via_js_console`) — opens DevTools, runs DOM query, copies JSON
3. **Clipboard fallback** (`_extract_via_clipboard`) — select all, copy, parse text

If strategy 1 fails, auto-switches to 2. If 2 fails, uses 3. Each strategy reports its confidence level.

## Phases

| Phase | What It Does | Verifies |
|---|---|---|
| **init** | Launch Brave, navigate to Maps | Maps UI is visible (search box, map canvas) |
| **search** | Type query, submit | Results panel appears with listings |
| **extract** | Click each listing, open detail, extract data | Detail panel opens, data successfully extracted |
| **scroll** | Scroll results to load more | New results loaded (text changed) |
| **score** | Run intelligence scorer on leads | Scores computed for all leads |
| **save** | Write JSON, CSV, Obsidian | Files exist and contain data |

## Resumability

State is saved to `data/agent_state.json` after every action. If the agent crashes:

```bash
python3 src/peekaboo_maps_agent.py --resume
```

It reads the state file, recovers extracted leads, and continues from the last phase.

## Cron Job Updated

The daily 9 AM cron now runs the agent with full reporting:
- Category searched
- Agent status (success/partial/failed)
- Lead counts + priority breakdown (hot/warm/cold)
- Top 3 leads with scores and missing signals
- Extraction strategy distribution
- Screenshot count (debug trail)
- Storage locations
- Error log + recovery actions
- Overall "worth following up?" assessment

## Files Changed

- **NEW** `src/peekaboo_agent.py` — Agent framework
- **NEW** `src/peekaboo_maps_agent.py` — Maps scraper using framework
- **UPDATED** Cron job payload — Uses new agent, richer reporting

## Old Files (Still Available)

- `src/peekaboo_scraper.py` — Fast clipboard bulk mode (kept as backup)
- `src/peekaboo_deep_scraper.py` — JS console deep mode (kept as backup)

## Usage

```bash
# Interactive mode (pauses on errors for manual fix)
cd /Users/oktos/.openclaw/workspace/leadgen
python3 src/peekaboo_maps_agent.py "plumbers" "Victoria, Australia" --limit 5 --interactive

# Autonomous mode (what cron uses)
python3 src/peekaboo_maps_agent.py "plumbers" "Victoria, Australia" --limit 10

# Resume after crash
python3 src/peekaboo_maps_agent.py --resume
```

## Debug Output

Every screenshot is saved to `data/debug/maps_agent/`:
- `agent_step_001_init_pre_0.png` — Before init action
- `agent_step_002_init_post_0.png` — After init action (verification)
- `agent_step_003_search_pre_0.png` — Before search
- etc.

This creates a complete visual trail of what the agent saw and did.

## Next Level (Future)

- **LLM Brain**: Plug in a vision-capable LLM (GPT-4V, Claude) for even smarter screenshot analysis instead of heuristics
- **Website crawling**: After extracting website URLs, spawn a sub-agent to visit and score SEO/chatbot/call-button
- **Parallel categories**: Run multiple agents in parallel for different categories
- **Human-in-the-loop**: Telegram button to approve/reject each lead before saving

---
*Built: 2026-05-24*
