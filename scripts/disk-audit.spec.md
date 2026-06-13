# disk-audit.sh — Specification

**Version:** 1.0
**Date:** 2026-06-13
**Owner:** workspace/scripts/
**Status:** Draft — implement in `disk-audit.sh`, wire into weekly cron after cleanup

---

## Purpose

Read-only disk hygiene audit for `~/.openclaw`. Produces human summary + `disk-audit-report.json`. Complements `health-check.sh` (reliability) with storage metrics. Fails loudly before the junkyard returns.

---

## Invocation

```bash
bash ~/.openclaw/workspace/scripts/disk-audit.sh
bash ~/.openclaw/workspace/scripts/disk-audit.sh --json-only   # stdout JSON only
bash ~/.openclaw/workspace/scripts/disk-audit.sh --quiet       # no stdout; still writes JSON
```

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | All checks PASS |
| 1 | One or more WARN, no FAIL |
| 2 | One or more FAIL (includes critical) |

---

## Paths

| Variable | Default |
|----------|---------|
| `OPENCLAW_HOME` | `$HOME/.openclaw` |
| `WORKSPACE` | `$OPENCLAW_HOME/workspace` |
| `SESSIONS_DIR` | `$OPENCLAW_HOME/agents/main/sessions` |
| `TMP_DIR` | `$OPENCLAW_HOME/tmp` |
| `REPORT_JSON` | `$WORKSPACE/disk-audit-report.json` |

Override via env vars for testing.

---

## Checks

Each check calls `check(name, status, detail, critical?)` — same pattern as `health-check.sh`.

### 1. Total OpenClaw size

**Measure:** `du -sk "$OPENCLAW_HOME"` → bytes

| Status | Condition |
|--------|-----------|
| PASS | ≤ 2 GiB |
| WARN | > 2 GiB and ≤ 4 GiB |
| FAIL | > 4 GiB |

**Detail example:** `5.1G total`

---

### 2. Workspace root entry count

**Measure:** count of non-hidden entries in `$WORKSPACE` (maxdepth 1). Include files and directories; exclude `.git`, `.snapshots`.

| Status | Condition |
|--------|-----------|
| PASS | ≤ 25 |
| WARN | 26–40 |
| FAIL | > 40 |

**Detail example:** `91 top-level entries`

---

### 3. `node_modules` directory count

**Measure:** `find "$OPENCLAW_HOME" -type d -name node_modules 2>/dev/null | wc -l`

| Status | Condition |
|--------|-----------|
| PASS | ≤ 3 |
| WARN | 4–8 |
| FAIL | > 8 |

**Detail example:** `68 node_modules trees`

---

### 4. Python virtualenv count

**Measure:** directories matching any of:
- name `venv`
- name `.venv`
- name `.venv-*` (e.g. `.venv-youtube-extract`)

Under `$OPENCLAW_HOME`. Include `tools/whisper-env` if present (counts toward limit).

| Status | Condition |
|--------|-----------|
| PASS | ≤ 2 |
| WARN | 3–4 |
| FAIL | > 4 |

**Detail example:** `7 venvs (consultation-webhook, leadgen, …)`

---

### 5. Agent sessions directory size

**Measure:** `du -sk "$SESSIONS_DIR"` if exists; else PASS with "no sessions dir"

| Status | Condition |
|--------|-----------|
| PASS | ≤ 200 MiB |
| WARN | > 200 MiB and ≤ 400 MiB |
| FAIL | > 400 MiB |

**Detail example:** `371M, 1597 files`

**Optional sub-metrics** (detail string only, not separate checks):
- `.trajectory.jsonl` file count
- `sessions.json` size

---

### 6. Temp directory size

**Measure:** `du -sk "$TMP_DIR"` if exists

| Status | Condition |
|--------|-----------|
| PASS | ≤ 100 MiB |
| WARN | > 100 MiB and ≤ 300 MiB |
| FAIL | > 300 MiB |

**Detail example:** `220M, 11079 files`

---

### 7. Nested git repositories in workspace

**Measure:** `find "$WORKSPACE" -type d -name .git | wc -l`

Workspace root `.git` counts as 1. Nested skill/project repos count separately.

| Status | Condition |
|--------|-----------|
| PASS | ≤ 1 |
| WARN | 2–3 |
| FAIL | > 3 |

**Detail example:** `13 .git directories`

---

### 8. Large files outside archive

**Measure:** files under `$OPENCLAW_HOME` where:
- size > 50 MiB (`find -size +50M`)
- path does **not** match `*/archive/*`, `*/.snapshots/*`, `*/node_modules/*`, `*/venv/*`, `*/.venv/*`

| Status | Condition |
|--------|-----------|
| PASS | 0 files |
| WARN | 1–3 files |
| FAIL | > 3 files |

**Detail:** list up to 5 largest paths with human sizes in check detail.

---

### 9. Forbidden ML packages in project venvs (optional v1.1)

**Deferred** — requires parsing `requirements.txt` + site-packages. Track in Phase 6 hardening TODO.

---

## Scoring

Same model as `health-check.sh`:

```
RAW_SCORE = pass * 100 / total_checks
INTEGRITY:
  CRITICAL_FAIL > 0  → FAILING  × 0.33
  WARN > 2           → WARNING  × 0.67
  else               → HEALTHY  × 1.0
FINAL_SCORE = RAW_SCORE * multiplier
Grade: A≥90, B≥80, C≥70, D≥60, F<60
```

Checks marked `critical=true`: total size FAIL, sessions FAIL (optional — use for total + sessions only).

---

## JSON report schema

Written to `$WORKSPACE/disk-audit-report.json`:

```json
{
  "timestamp": "2026-06-13T12:00:00Z",
  "grade": "F",
  "score": 35,
  "rawScore": 44,
  "integrity": "FAILING",
  "multiplier": 0.33,
  "openclawHomeBytes": 5476083302,
  "checks": {
    "pass": 0,
    "warn": 5,
    "fail": 3,
    "criticalFail": 2
  },
  "metrics": {
    "totalBytes": 5476083302,
    "workspaceRootEntries": 91,
    "nodeModulesCount": 68,
    "venvCount": 7,
    "sessionsBytes": 389231104,
    "tmpBytes": 230686720,
    "nestedGitCount": 13,
    "largeFilesOutsideArchive": 12
  },
  "largeFiles": [
    { "path": "/Users/oktos/.openclaw/...", "bytes": 449839104 }
  ],
  "details": [
    { "name": "Total OpenClaw size", "status": "FAIL", "detail": "5.1G total" }
  ]
}
```

---

## Cron integration (after cleanup)

**Schedule:** Weekly Sunday 09:00 local (or piggyback on existing health cron)

**Behavior:**
1. Run `disk-audit.sh`
2. If exit code ≥ 1 → Telegram summary with grade + top 3 failures
3. Do **not** auto-delete — audit only; `prune-ephemeral.sh` handles deletes

**Telegram template:**

```
Disk audit: Grade F (35/100)
FAIL: Total 5.1G, node_modules×68, venvs×7
WARN: tmp 220M, nested git×13
Run: bash scripts/disk-audit.sh
```

---

## Integration with health-check.sh (Phase 6)

Future: `health-check.sh` sources or calls `disk-audit.sh` and merges grades. v1 keeps scripts separate to avoid breaking existing health-report.json consumers.

---

## Test cases

| Scenario | Expected |
|----------|----------|
| Fresh install <500MB | Grade A, exit 0 |
| Current prod (~5.1GB) | Grade F, exit 2 |
| After cleanup (~1.5GB) | Grade B–C, exit 0 or 1 |
| Missing sessions dir | PASS on sessions check |
| `--json-only` | Valid JSON on stdout, no banner |

---

## Non-goals (v1)

- Does not delete files
- Does not modify `openclaw.json`
- Does not scan Obsidian vault
- Does not duplicate `inventory.sh` file listing — only sizes/counts
