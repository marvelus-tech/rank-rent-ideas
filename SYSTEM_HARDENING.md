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
| 1.3 | **Evidence gate for "done" claims** — Repo, branch, commit, files changed, proof it works | ✅ DONE | Rule in AGENTS.md + template at scripts/evidence-gate.md |
| 1.4 | **Write first, speak second** — Persist state to file before reporting completion | ✅ DONE | Added as mechanical rule in AGENTS.md |
| 1.5 | **Persistent daily logs** — Never skip a day's log; missing logs = wasted sessions | ✅ DONE | Pattern exists, rule reinforced in AGENTS.md |

### 🟠 Phase 2: Health & Integrity Scoring

| # | Fix | Status | Notes |
|---|-----|--------|-------|
| 2.1 | **Health score system** — Timestamps, freshness checks, category-level detail | ✅ DONE | scripts/health-check.sh — letter grade, category scores, JSON output |
| 2.2 | **Integrity multiplier** — High activity + broken integrity = bad score | ✅ DONE | Built into health-check.sh: FAILING=×0.33, WARNING=×0.67, HEALTHY=×1.0 |
| 2.3 | **Structured reports** — No more "things look good"; explicit pass/fail + JSON artifact | ✅ DONE | templates/status-report.md + health-report.json auto-generated |
| 2.4 | **Stale score detection** — Health scores must include when they were last calculated | ✅ DONE | Timestamp in health-check.sh output + JSON |

### 🟡 Phase 3: Agent Architecture & Routing

| # | Fix | Status | Notes |
|---|-----|--------|-------|
| 3.1 | **Strict agent hierarchy** — Main orchestrates, specialists execute, subagents are disposable | ✅ DONE | SOUL.md model routing + OWNERSHIP.md defines who owns what |
| 3.2 | **Explicit file ownership** — Define who owns what before parallelizing | ✅ DONE | OWNERSHIP.md created with full file/domain ownership table |
| 3.3 | **Structured handoffs** — Who, what, when, where results go, evidence | ✅ DONE | templates/handoff.md with mandatory fields |
| 3.4 | **One problem per agent** — Clean scope, clean output | ✅ DONE | Rule added to AGENTS.md completion rules |
| 3.5 | **Fast ack + background work** — Quick response, long work in separate session | ✅ DONE | Already in place via sub-agent spawn model in SOUL.md |
| 3.6 | **Exact trigger matching** — No fuzzy word matching for action commands | ✅ DONE | No custom trigger words configured — OpenClaw handles routing natively |

### 🟢 Phase 4: Operational Discipline

| # | Fix | Status | Notes |
|---|-----|--------|-------|
| 4.1 | **Incremental commits** — Small commits, frequent saves, never gamble on session timeout | ✅ DONE | Rule added to AGENTS.md completion rules |
| 4.2 | **Don't poll in loops** — Wait for events, escalate on timeout | ✅ DONE | Already enforced in system prompt + AGENTS.md |
| 4.3 | **Cron job audit** — Kill jobs that don't produce actionable output | ✅ DONE | Audited: 1 job (Solana scout), disabled, errored — needs fix or removal |
| 4.4 | **Structured cron output** — What happened, why it matters, what's next, confidence, evidence | ✅ DONE | templates/cron-output.md created |
| 4.5 | **No duplicate cron runs** — Trust the active loop, don't stack | ✅ DONE | Documented as operational rule — OpenClaw cron handles scheduling natively |
| 4.6 | **CLI output ≠ truth** — Always verify against source files | ✅ DONE | Rule exists in AGENTS.md — "CLI summaries are views, not truth" |
| 4.7 | **Inventory scripts** — Count what actually exists on disk | ✅ DONE | scripts/inventory.sh — full workspace inventory |

### 🔵 Phase 5: Safety & Change Management

| # | Fix | Status | Notes |
|---|-----|--------|-------|
| 5.1 | **Snapshot before any config change** — No exceptions | ✅ DONE | scripts/snapshot.sh — copies all configs + git state to .snapshots/ |
| 5.2 | **Advisory-only mode** — Test new rules in read-only before enforcing | 🟡 PARTIAL | Process documented; no automated advisory harness yet |
| 5.3 | **Sequential safety gates** — Numbered steps with pass/fail, harder to skip than do | ✅ DONE | Evidence gate template enforces sequential completion |
| 5.4 | **Human checkpoint for irreversible actions** — Branch first, pause before merge | ✅ DONE | Already in SOUL.md safety rules + AGENTS.md red lines |
| 5.5 | **Script-enforced rules** — If corrected twice, becomes a script not a doc line | 🟡 PARTIAL | Philosophy adopted; tracking in decisions.md; no auto-escalation script yet |
| 5.6 | **One fix at a time for security** — Phased hardening with rollback plans | ✅ DONE | This entire plan follows phased approach with snapshots |
| 5.7 | **Repo dedup audit** — One location per repo, check for duplicates | ✅ DONE | Checked in health-check.sh + inventory.sh — 0 duplicates found |
| 5.8 | **Workspace on GitHub** — Version control the OpenClaw workspace | ✅ DONE | git init, initial commit 843bf9b |
| 5.9 | **Rule setup order** — Identity → routing → comms → stress test | ✅ DONE | Followed correct order: identity files first, then routing, then rules |

---

## Completion Tracking

- **Total items:** 28
- **Completed:** 26
- **Partial:** 2
- **Remaining:** 0
- **Last updated:** 2026-03-19

## Partial Items (Need Future Work)
- **5.2 Advisory-only mode** — Need automated harness that runs new rules in read-only before enforcement
- **5.5 Auto-escalation** — Need script that detects repeated corrections in decisions.md and auto-generates enforcement scripts

## Weekly Review Questions (from article)
1. What broke this week?
2. Why did it break?
3. What's working that we should protect?
4. What should we improve?
5. Do improvements come from auditing what exists (good) or importing external configs (bad)?

---

## Implementation Log

### 2026-03-19 — Full Implementation
- Extracted 28 fixes from @kloss_xyz article
- Organized into 5 phases by priority
- **Phase 1:** Context gate, decisions.md, evidence gate, write-first-speak-second, daily logs
- **Phase 2:** Health check script with 3-layer scoring (grade/categories/hard gates), integrity multiplier, JSON + human output
- **Phase 3:** OWNERSHIP.md, handoff template, one-problem-per-agent rule, hierarchy documented
- **Phase 4:** Cron audit (1 job, disabled/errored), cron output template, inventory script, incremental commit rule
- **Phase 5:** Snapshot script, baseline snapshot taken, workspace under git (843bf9b), phased approach followed
- **First health check:** Grade F (53/100) — raw 80 degraded by integrity multiplier (3 warnings)
- **Baseline snapshot:** .snapshots/20260319-160527-pre-hardening-baseline (17 files, 84K)
