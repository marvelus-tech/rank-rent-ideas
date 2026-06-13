# Paste into ~/Obsidian/Penelopi/DECISIONS.md

Append this section above `## Previous Decisions (Archived)`.
Update the file footer `Last updated` line after paste.

---

## Storage & Workspace Hygiene

**Date:** 2026-06-13
**Status:** Active
**Priority:** P0

### Problem

`~/.openclaw` grew to ~5 GB: duplicate venvs, 68 `node_modules` trees, 371 MB session trajectories, pipeline artifacts (MP3/JSON/debug) never deleted, and 91 loose items in workspace root. Reliability hardening (Phase 1–5) never covered disk. Docs alone do not prevent bloat — gates and audits do.

### Hard Rules (Non-Negotiable)

1. **No new top-level workspace folders** without Okeito approval.
   - New experiments → `workspace/scratch/<name>/`
   - Revenue work → `workspace/active/<name>/` (after cleanup reorg)
   - Sunset work → `workspace/archive/<name>/`

2. **No new venv or `node_modules` if a shared one exists.**
   - Python: prefer `workspace/.venv` (one env, optional extras)
   - Node: prefer workspace-level pnpm/npm workspaces — not per-deck installs
   - Before `pip install` / `npm install`: run `bash scripts/pre-flight-create.sh` (when it exists)

3. **No ML stacks for light tasks.**
   - Transcription: `~/.openclaw/tools/whisper-env`, `faster-whisper`, or API
   - **Forbidden without explicit Okeito approval:** `torch`, `whisperx`, `tensorflow`, `onnxruntime` in project venvs

4. **Presentations = single self-contained HTML.**
   - Template: `workspace/presentations/2026-06-12-claude-for-business/index.html`
   - Do **not** scaffold Vite/React/npm for slides unless Okeito explicitly asks

5. **Pipeline artifacts are ephemeral.**
   - Keep one canonical store + one state file (e.g. `leads_db.json` + `scan_state.json`)
   - Delete intermediate stages (`*_raw.json`, `*_enriched.json`, `data/debug/*`) after merge
   - Delete `work/*.mp3`, `work/*.aiff` after publish (keep `state/processed-*.json`)

6. **No nested `.git` inside workspace.**
   - Standalone repos → `~/Projects/` or symlink in — not full git history under `.openclaw`

7. **Temp files live in `~/.openclaw/tmp/` only** — never workspace root.
   - Assume 7-day TTL; cron prunes via `scripts/prune-ephemeral.sh`

8. **No accidental paths.**
   - Never `mkdir {a,b,c}` without brace expansion
   - Never create dirs named with backticks, `EOF`, or shell metacharacters

### Before Reporting "Done" on Any Build / Install / Scrape Task

Evidence gate extension — all required:

| Field | Requirement |
|-------|-------------|
| Files created | Full paths listed |
| Disk delta | `du -sh` before/after on affected dirs |
| Permanence | Each file tagged `permanent` or `TTL` + expiry |
| Cleanup | Anything >10 MB with TTL must have delete step or cron target |

If disk delta >100 MB, **stop and ask Okeito** before proceeding.

### Correction Phrases (Okeito — use verbatim when I slip)

- "Stop. No new top-level workspace folder — use scratch/."
- "Stop. No Vite for slides — copy the HTML template."
- "Stop. No torch/whisperx venv — use whisper-env or faster-whisper."
- "Stop. Delete pipeline artifacts before marking done."

After the **same** correction twice → run `bash scripts/auto-escalate.sh` and script a gate (pre-flight or cron).

### Applied To

- All main-session and subagent work under `~/.openclaw/workspace`
- Cron jobs that write data, media, or build output
- Presentations, leadgen, brownstone-bleeding-edge, remotion-studio, consultation-webhook

### Verification

- [ ] Weekly: `bash scripts/disk-audit.sh` — warn/fail triggers Telegram alert
- [ ] `~/.openclaw` steady state **<2 GB** (fail audit at >4 GB)
- [ ] Workspace root entries **≤25** (fail at >40)
- [ ] `node_modules` dirs **≤3** (fail at >8)
- [ ] Python venvs **≤2** including `tools/whisper-env` (fail at >4)
- [ ] `agents/main/sessions` **≤200 MB** (fail at >400 MB)
- [ ] No new nested `.git` in workspace after cleanup

### Commands

```bash
# Audit (read-only)
bash ~/.openclaw/workspace/scripts/disk-audit.sh

# Inventory ground truth
bash ~/.openclaw/workspace/scripts/inventory.sh

# Escalate repeated storage mistakes
bash ~/.openclaw/workspace/scripts/auto-escalate.sh
```

### Related Config (human applies during cleanup)

`~/.openclaw/openclaw.json` → `session.maintenance` caps trajectory/jsonl growth (see prevention plan).
