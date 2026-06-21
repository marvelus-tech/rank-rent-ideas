# OpenClaw Feature Audit Report

**Date:** 2026-06-11
**Auditor:** Sonnet subagent (timed out) + manual compilation
**Status:** 10 features analyzed, 7 underutilized

---

## Executive Summary

We're using ~30% of OpenClaw's capabilities. The biggest gaps are in:
- **Inter-session data routing** (not used)
- **TaskFlow durable jobs** (DB exists, barely used)
- **Token/cost tracking** (not configured)
- **Canvas presentations** (no nodes connected)
- **Credential scoping** (not configured)

---

## 1. Inter-Session Messaging (subagent_announce)
**Status:** NOT USED ❌
**Priority:** HIGH

**What it does:**
Allows subagents to pass structured data back to parent sessions via the `subagent_announce` channel, not just text messages.

**How we could use it:**
- Research subagent returns JSON data directly to parent
- Analysis subagent consumes research output without text parsing
- Build persistent research memory across runs

**Current problem:**
We're only using `sessions_spawn` + `sessions_yield` which returns text. The subagent's output is parsed as chat text, not structured data.

**Benefit:**
- Eliminates text parsing errors
- Enables pipeline architectures (research → analysis → report)
- Reduces token waste on formatting

**Action:**
Use `delivery: {mode: "announce", channel: "subagent_announce"}` with JSON payloads

---

## 2. Session Key Tracking (Hierarchical Agents)
**Status:** PARTIALLY USED ⚠️
**Priority:** MEDIUM

**What it does:**
Session keys like `agent:main:subagent:8270b9ed-...` form a tree. We can nest subagents (parent → child → grandchild) with proper relationships.

**How we could use it:**
- Research agent (depth 1) → Analysis agent (depth 2) → Report agent (depth 3)
- Each level passes refined data down
- Parent can track all descendants

**Current problem:**
We're spawning flat subagents (all depth 1). No chaining.

**Benefit:**
- Better organization of complex tasks
- Easier debugging (know which subagent failed)
- Natural pipeline architecture

**Action:**
Chain subagents: spawn research → on completion, spawn analysis with research data → on completion, spawn report

---

## 3. Stats Collection (Token/Cost Tracking)
**Status:** NOT CONFIGURED ❌
**Priority:** HIGH

**What it does:**
Track token usage, costs, runtime per model, per task.

**How we could use it:**
- See which subagents burn the most tokens
- Optimize model selection (use cheaper models for simple tasks)
- Budget alerts when approaching limits

**Current problem:**
`runtime 9s • tokens 0` in logs — tracking exists but not configured/stored.

**Benefit:**
- Cost optimization (Flash for research, Opus only for hard problems)
- Identify expensive cron jobs
- Data-driven model selection

**Action:**
Configure `stats` section in openclaw.json or use `session_status` after each subagent

---

## 4. Channel Features (Multi-Channel Routing)
**Status:** NOT USED ❌
**Priority:** MEDIUM

**What it does:**
Messages can be routed to different channels based on content type. Raw data to logs, summaries to chat.

**How we could use it:**
- Detailed research → file/obsidian
- Summary → Telegram
- Errors → alert channel
- Reports → canvas/web

**Current problem:**
Everything goes to Telegram direct.

**Benefit:**
- Reduce chat noise
- Persistent storage for research
- Separate alerts from regular messages

**Action:**
Use `delivery: {mode: "webhook", to: "file://..."}` for raw data, `announce` for summaries

---

## 5. Credential Scoping (Per-Model API Keys)
**Status:** NOT CONFIGURED ❌
**Priority:** HIGH

**What it does:**
Bind specific API keys to specific models or subagent types. Prevent 401 errors when subagents use different providers.

**How we could use it:**
- Kimi K2.5 → Moonshot API key
- Claude → Anthropic API key
- Gemini → Google API key
- Each subagent gets the right key

**Current problem:**
Kimi K2 subagent failed with HTTP 401 — wrong/no credentials bound.

**Benefit:**
- Eliminates auth failures
- Enables multi-model workflows
- Secure credential isolation

**Action:**
Configure `credentials` per model in openclaw.json

---

## 6. Memory System (memory_search, corpus)
**Status:** PARTIALLY USED ⚠️
**Priority:** MEDIUM

**What it does:**
- `memory_search` — semantic search across MEMORY.md + memory/*.md + session transcripts
- `corpus=wiki` — search compiled wiki supplements
- `corpus=sessions` — search session transcripts only

**How we could use it:**
- Search past decisions before making new ones
- Find related work from previous sessions
- Build institutional knowledge

**Current problem:**
We use `memory_search` but not `corpus=wiki` or `corpus=sessions`. No systematic indexing.

**Benefit:**
- Avoid repeating work
- Contextual recall of past decisions
- Better continuity across sessions

**Action:**
Use `corpus=sessions` to find related past work, `corpus=wiki` for documentation

---

## 7. TaskFlow (Durable Multi-Step Jobs)
**Status:** UNDERUTILIZED ⚠️
**Priority:** HIGH

**What it does:**
Durable task orchestration with state, waits, child tasks. Survives session restarts.

**How we could use it:**
- Pain point research pipeline as a TaskFlow
- Each phase = child task
- State persists across sessions
- Automatic retry on failure

**Current problem:**
TaskFlow DB exists (`~/.openclaw/tasks/runs.sqlite`) but minimal usage. We're building ad-hoc scripts instead.

**Benefit:**
- Reliable pipelines (survive crashes)
- State tracking (know which phase failed)
- Parallel execution (child tasks)
- Less custom code

**Action:**
Convert pain-point-research pipeline to TaskFlow

---

## 8. Canvas (HTML Presentations on Nodes)
**Status:** NOT USED ❌
**Priority:** LOW

**What it does:**
Display HTML content on connected OpenClaw nodes (other devices, browsers).

**How we could use it:**
- Show dashboards on secondary screens
- Present reports visually
- Real-time status boards

**Current problem:**
No nodes connected. Canvas skill exists but unused.

**Benefit:**
- Visual output beyond text
- Persistent displays
- Multi-screen workflows

**Action:**
Connect a node (browser, phone) and test canvas presentations

---

## 9. Gateway Features (config.schema.lookup)
**Status:** NOT USED ❌
**Priority:** LOW

**What it does:**
- `config.schema.lookup` — inspect config structure
- `gateway restart` — restart without CLI
- `gateway config` — manage gateway settings

**How we could use it:**
- Audit config programmatically
- Restart after config changes
- Validate settings before applying

**Current problem:**
We're using CLI commands instead of gateway tool.

**Benefit:**
- Safer config changes
- Programmatic gateway management
- Less shell dependency

**Action:**
Use `gateway` tool for config operations instead of exec

---

## 10. Native Subagents (context=fork, lightContext)
**Status:** PARTIALLY USED ⚠️
**Priority:** MEDIUM

**What it does:**
- `context=fork` — child gets parent transcript (for context-dependent tasks)
- `context=isolated` — clean slate (default, good for independent tasks)
- `lightContext` — reduced bootstrap context (faster, cheaper)

**How we could use it:**
- `context=fork` for tasks that need conversation history
- `lightContext` for simple, independent tasks (saves tokens)
- Proper context selection per task type

**Current problem:**
We're mostly using isolated (good) but not using `lightContext` for simple tasks. Missing `context=fork` when needed.

**Benefit:**
- Faster subagent startup (lightContext)
- Better context for dependent tasks (fork)
- Token savings

**Action:**
Use `lightContext=true` for simple research tasks, `context=fork` when child needs parent context

---

## Immediate Action Items

| Priority | Feature | Action | Effort |
|----------|---------|--------|--------|
| HIGH | Credential Scoping | Bind API keys per model | 30 min |
| HIGH | Stats Collection | Enable token/cost tracking | 15 min |
| HIGH | TaskFlow | Convert pipeline to durable tasks | 2 hours |
| MEDIUM | Inter-Session Messaging | Use JSON delivery mode | 1 hour |
| MEDIUM | Memory System | Use corpus=sessions/wiki | 30 min |
| MEDIUM | Native Subagents | Use lightContext for simple tasks | 15 min |
| LOW | Canvas | Connect a node | 1 hour |
| LOW | Gateway | Use gateway tool vs CLI | 30 min |

---

## Root Cause of Duplicate Messages

The duplicate messages you saw were caused by:
1. **Spawn acknowledgment** + **yield message** both sent to chat
2. **No idempotency check** — system didn't detect duplicate content
3. **Race condition** — completion event may have fired twice

**Fix implemented:**
- Added `DECISIONS.md` rule for duplicate prevention
- Pattern: Spawn → NO_REPLY, Yield → NO_REPLY, Wait for completion → Send ONCE
- If completion fires twice → second gets NO_REPLY

---

*Report compiled from subagent data collection + manual analysis*
