# Agent Hierarchy Protocol — Solana Scout System

**Established:** 2026-03-20
**Purpose:** Daily automated token scouting with structured reporting

---

## Architecture

```
Okeito (Human)
    ↑
    ↓ Reports findings, gets approval for actions
Penelopi (Main Session)
    ↑
    ↓ Dispatches daily, receives structured handoffs
Solana Scout (Sub-agent / Isolated Session)
    ↑
    ↓ Executes search, compiles evidence
Web Sources (Brave Search, X/Twitter, Solana ecosystem)
```

---

## Flow

### 1. Daily Trigger (Cron)
- **When:** Every day at 09:00 Melbourne time (AEST/AEDT)
- **What:** Spawns isolated sub-agent with Solana scout task
- **Where:** Isolated session (doesn't block main session)

### 2. Scout Execution
- Receives mission briefing from `agents/solana-scout.md`
- Executes web searches for Solana small-cap hold-to-earn tokens
- Compiles findings using evidence gate template
- Generates structured handoff report

### 3. Handoff to Main Session
- Sub-agent completes and reports back to main session
- Report includes: tokens found, evidence, confidence scores
- Uses `templates/handoff.md` format

### 4. Main Session Review
- Penelopi receives handoff
- Filters: Only high-confidence finds (≥70/100) get immediate attention
- Aggregates lower-confidence finds for weekly digest
- **Decision point:** What to surface to Okeito?

### 5. Human Notification
- Immediate: High-confidence new opportunities
- Weekly: Digest of all finds with trend analysis
- Never: Spam or "maybe" tokens without evidence

---

## Cron Job Configuration

```json
{
  "name": "Solana Daily Scout",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *",
    "tz": "Australia/Melbourne"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "You are the Solana Scout agent. Your mission: find 3-5 Solana small-cap tokens (under $100M market cap) with hold-to-earn reward mechanics similar to solcard.cc. Read agents/solana-scout.md for full briefing. Use web search extensively. Report back to main session using templates/handoff.md format. Include: token name, market cap, what it does, reward mechanic, confidence score (0-100), and links. Quality over quantity."
  },
  "delivery": {
    "mode": "announce"
  }
}
```

---

## Ownership & File Locations

| File | Purpose | Owner |
|------|---------|-------|
| `agents/solana-scout.md` | Agent briefing and rules | Main session |
| `templates/handoff.md` | Handoff format template | Main session |
| `scripts/solana-scout-task.sh` | Task execution script | Main session |
| `memory/scout-findings/` | Daily reports storage | Scout writes, main owns |

---

## Escalation Rules

**Immediate notification to Okeito if:**
- Confidence ≥80/100 AND market cap under $50M
- Hold-to-earn mechanic is live (not just planned)
- Active development visible (recent commits, X posts)

**Weekly digest includes:**
- All finds with confidence ≥60/100
- Trending sectors (DeFi, gaming, infrastructure)
- Tokens to watch (not yet actionable)

**Never report:**
- Tokens without working links
- "Rumored" or "upcoming" without evidence
- Anything the scout can't explain in one sentence

---

## Quality Gates

Before the scout reports a find:
1. ✅ Can I explain what this token does in 10 words?
2. ✅ Is the reward mechanic clearly documented?
3. ✅ Are there verifiable links (site, X, docs)?
4. ✅ Is market cap under $100M?
5. ✅ Is my confidence score ≥60?

If any check fails, the token doesn't make the report.

---

## Success Metrics

- **Weekly:** 3-5 qualified tokens found per week
- **Monthly:** 1-2 tokens worth deeper analysis
- **Quarterly:** 1 position taken based on scout findings

---

Last updated: 2026-03-20
