# Okeito R&D Department System v2

## What this does
Runs a 3-agent strike team every session:
1. 🔬 **Research Analyst** (Gemini Flash) — scouts landscape, finds signal
2. ⚙️ **Systems Builder** (Codex) — proposes code/automation based on research
3. 🎯 **Strategic Director** (Kimi) — makes the call: bold move, safe move, experiment

Outputs are saved to `rnd/memos/YYYY-MM-DD-HH-mm.md`.

## Files
- `rnd/agents.json` — model + persona config
- `rnd/debate.js` — orchestrator (uses real model calls via `openclaw sessions spawn`)
- `rnd/memo-template.md` — memo structure
- `rnd/dashboard.html` — visual memo index + agent roster
- `rnd/cron-setup.sh` — scheduler helper

## Run manually
```bash
cd ~/.openclaw/workspace
node rnd/debate.js
```

## How it works
Each round spawns an isolated agent session with the configured model:
- Research round → Flash searches web, returns findings
- Build round → Codex writes code/pseudocode based on research
- Direct round → Kimi synthesizes into 3 strategic options

No mock mode. Every round hits a live model.

## Cron
Tue/Thu/Sat at 2am:
```bash
bash ~/.openclaw/workspace/rnd/cron-setup.sh
```

Direct registration:
```bash
openclaw cron add --json '{
  "name":"rnd-tuesday-thursday-saturday",
  "schedule":"0 2 * * 2,4,6",
  "timezone":"Australia/Melbourne",
  "payload":{"model":"kimi/k2p5","command":"node ~/.openclaw/workspace/rnd/debate.js"}
}'
```

## Cost estimate per run (rough)
- Research (Flash): ~$0.005–$0.03
- Build (Codex): ~$0.10–$0.30
- Direct (Kimi): ~$0.05–$0.15

**Estimated total:** ~$0.16 to ~$0.48 per full run.

## Topics the R&D scouts
The system auto-selects from:
- Competitors to Marvelus.cc / Nolostsales.cc
- New AI tools/APIs for lead generation
- Solana projects / DeFi mechanics
- UX/design trends for conversion
- Market shifts / regulations affecting AI-for-SMBs
