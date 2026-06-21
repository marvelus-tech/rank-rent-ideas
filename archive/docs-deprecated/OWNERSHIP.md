# OWNERSHIP.md — File & Domain Ownership

**Purpose:** Before parallelizing any work, ownership must be explicit. Two agents working on the same files without knowing = guaranteed conflicts.

---

## Core Files (Main Session Only)
These files are owned by the main session. No sub-agent modifies these directly.

| File | Owner | Purpose |
|------|-------|---------|
| SOUL.md | Main | Identity & personality |
| IDENTITY.md | Main | Name & creature type |
| USER.md | Main | Human's profile & preferences |
| AGENTS.md | Main | Operating rules & protocols |
| MEMORY.md | Main | Long-term curated memory |
| decisions.md | Main | Persistent corrections log |
| SYSTEM_HARDENING.md | Main | Hardening progress tracker |
| HEARTBEAT.md | Main | Heartbeat checklist |
| TOOLS.md | Main | Local environment notes |

## Daily Logs (Main Session Primary, Sub-agents Append)
| Path | Owner | Notes |
|------|-------|-------|
| memory/YYYY-MM-DD.md | Main | Sub-agents may append findings but main owns the file |

## Scripts (Whoever Creates, Documents)
| Path | Owner | Notes |
|------|-------|-------|
| scripts/* | Documented per script | Each script header must state its purpose and owner |

## Sub-Agent Rules
1. Sub-agents work in their own scope — they do NOT modify core files
2. Sub-agents return results to main session, which decides what to persist
3. If two sub-agents need overlapping files, they run sequentially, not in parallel
4. Sub-agents report back using the evidence gate template
