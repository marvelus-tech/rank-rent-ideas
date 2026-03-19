# System Hardening Plan
**Source:** @kloss_xyz article on OpenClaw reliability failures
**Created:** 2026-03-19
**Status:** IN PROGRESS

---

## Priority Order (from article's recommended fix sequence)

### 🔴 Phase 1: Stop the Lying (Critical — Do First)

| # | Fix | Status | Notes |
|---|-----|--------|-------|
| 1.1 | **Context gate** — Load corrections, decisions, and recent memory before responding | ✅ DONE | Added decisions.md to mandatory startup gate in AGENTS.md |
| 1.2 | **Decisions log** (`decisions.md`) — Every redirect/correction saved permanently, loaded at session start | ✅ DONE | Created decisions.md, added to startup sequence |
| 1.3 | **Evidence gate for "done" claims** — Repo, branch, commit, files changed, proof it works | 🟡 PARTIAL | Rule in AGENTS.md, needs script enforcement |
| 1.4 | **Write first, speak second** — Persist state to file before reporting completion | ✅ DONE | Added as mechanical rule in AGENTS.md |
| 1.5 | **Persistent daily logs** — Never skip a day's log; missing logs = wasted sessions | ✅ DONE | Pattern exists, rule reinforced in AGENTS.md |

### 🟠 Phase 2: Health & Integrity Scoring

| # | Fix | Status | Notes |
|---|-----|--------|-------|
| 2.1 | **Health score system** — Timestamps, freshness checks, category-level detail | ⬜ TODO | Build `scripts/health-check.sh` |
| 2.2 | **Integrity multiplier** — High activity + broken integrity = bad score | ⬜ TODO | Part of health score system |
| 2.3 | **Structured reports** — No more "things look good"; explicit pass/fail + JSON artifact | ⬜ TODO | Template for all status reports |
| 2.4 | **Stale score detection** — Health scores must include when they were last calculated | ⬜ TODO | Timestamp in health output |

### 🟡 Phase 3: Agent Architecture & Routing

| # | Fix | Status | Notes |
|---|-----|--------|-------|
| 3.1 | **Strict agent hierarchy** — Main orchestrates, specialists execute, subagents are disposable | ⬜ TODO | SOUL.md has model routing but no hierarchy enforcement |
| 3.2 | **Explicit file ownership** — Define who owns what before parallelizing | ⬜ TODO | Create `OWNERSHIP.md` |
| 3.3 | **Structured handoffs** — Who, what, when, where results go, evidence | ⬜ TODO | Handoff template for sub-agent spawns |
| 3.4 | **One problem per agent** — Clean scope, clean output | ⬜ TODO | Add as rule in AGENTS.md |
| 3.5 | **Fast ack + background work** — Quick response, long work in separate session | ⬜ TODO | Already partially in place with sub-agent model |
| 3.6 | **Exact trigger matching** — No fuzzy word matching for action commands | ⬜ TODO | Audit current routing for collision risk |

### 🟢 Phase 4: Operational Discipline

| # | Fix | Status | Notes |
|---|-----|--------|-------|
| 4.1 | **Incremental commits** — Small commits, frequent saves, never gamble on session timeout | ⬜ TODO | Add as rule in AGENTS.md |
| 4.2 | **Don't poll in loops** — Wait for events, escalate on timeout | ⬜ TODO | Already in system prompt, reinforce |
| 4.3 | **Cron job audit** — Kill jobs that don't produce actionable output | ⬜ TODO | Audit current cron jobs |
| 4.4 | **Structured cron output** — What happened, why it matters, what's next, confidence, evidence | ⬜ TODO | Create cron output template |
| 4.5 | **No duplicate cron runs** — Trust the active loop, don't stack | ⬜ TODO | Add guard logic |
| 4.6 | **CLI output ≠ truth** — Always verify against source files | ⬜ TODO | Add as rule in AGENTS.md |
| 4.7 | **Inventory scripts** — Count what actually exists on disk | ⬜ TODO | Build `scripts/inventory.sh` |

### 🔵 Phase 5: Safety & Change Management

| # | Fix | Status | Notes |
|---|-----|--------|-------|
| 5.1 | **Snapshot before any config change** — No exceptions | ⬜ TODO | Build snapshot script |
| 5.2 | **Advisory-only mode** — Test new rules in read-only before enforcing | ⬜ TODO | Process for rule changes |
| 5.3 | **Sequential safety gates** — Numbered steps with pass/fail, harder to skip than do | ⬜ TODO | Gate template |
| 5.4 | **Human checkpoint for irreversible actions** — Branch first, pause before merge | ⬜ TODO | Already partially in SOUL.md safety rules |
| 5.5 | **Script-enforced rules** — If corrected twice, becomes a script not a doc line | ⬜ TODO | Track repeated failures → scripts |
| 5.6 | **One fix at a time for security** — Phased hardening with rollback plans | ⬜ TODO | Process doc |
| 5.7 | **Repo dedup audit** — One location per repo, check for duplicates | ⬜ TODO | Build `scripts/repo-audit.sh` |
| 5.8 | **Workspace on GitHub** — Version control the OpenClaw workspace | ⬜ TODO | Init git repo in workspace |
| 5.9 | **Rule setup order** — Identity → routing → comms → stress test | ⬜ TODO | We're early enough to do this right |

---

## Completion Tracking

- **Total items:** 28
- **Completed:** 4
- **In progress:** 1
- **Remaining:** 23
- **Last updated:** 2026-03-19

## Weekly Review Questions (from article)
1. What broke this week?
2. Why did it break?
3. What's working that we should protect?
4. What should we improve?
5. Do improvements come from auditing what exists (good) or importing external configs (bad)?

---

## Implementation Log

### 2026-03-19 — Plan Created
- Extracted 28 fixes from @kloss_xyz article
- Organized into 5 phases by priority
- Ready to begin Phase 1
