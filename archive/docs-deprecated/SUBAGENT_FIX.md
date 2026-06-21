# OpenCode Subagents — Fixed 2026-06-09

## What broke

1. **Wrong API endpoint** — `models.providers.opencode.baseUrl` was `https://api.opencode.ai/v1` (dead). Correct: `https://opencode.ai/zen/v1`
2. **Stale model IDs** — OpenCode renamed models (`gemini-3-flash` → `gemini-3.5-flash`, `claude-sonnet-4.6` → `claude-sonnet-4-6`, etc.)
3. **Truncated catalog** — Provider config had only one model, so Codex/Gemini aliases existed but had no backend entry → silent failures or "Unknown model"
4. **Wrong subagent default** — Was `google/gemini-3.1-pro-preview` (no Google auth configured)

## Current routing

| Task | Model | Alias | Spawn |
|------|-------|-------|-------|
| Coding | `opencode/gpt-5.3-codex` | Codex | `sessions_spawn(model="Codex")` |
| General / research | `opencode/gemini-3.5-flash` | Flash | `sessions_spawn(model="Flash")` |
| General fallback | `opencode/grok-build-0.1` | Grok | `sessions_spawn(model="Grok")` |
| Coding | `opencode/gpt-5.3-codex` | Codex | `sessions_spawn(model="Codex")` |
| Subagent default | Flash → **Grok** fallback | — | auto |

## Verified working

- Codex (`opencode/gpt-5.3-codex`) — OK
- Kimi K2.5 (`opencode/kimi-k2.5`) — OK (good general fallback)

## Gemini Flash — enabled in dashboard, broken on API

Your Zen dashboard shows **Gemini 3.5 Flash** enabled (green toggle). Config uses the correct ID: `gemini-3.5-flash`.

Direct API test still returns:
```
401 No provider available
```

This is an **OpenCode backend bug** — toggle is on but no provider is wired up. Not an OpenClaw config issue.

**Things to try on OpenCode:**
1. Toggle Gemini 3.5 Flash **off → save → on → save**
2. Or enable **Gemini 3 Flash** instead (currently disabled; API returns `"Model is disabled"` when off — enabling may work)
3. Contact OpenCode support with: `gemini-3.5-flash` returns "No provider available" despite being enabled

**Interim routing (auto-fallback configured):**
Subagent default tries Flash first, then falls back to:
1. `opencode/grok-build-0.1` (Grok) — verified working

Manual spawns while waiting:
```
sessions_spawn(model="Grok")      # general (Grok Build 0.1)
sessions_spawn(model="Sonnet")    # general/research (Claude)
sessions_spawn(model="Codex")     # coding
```

## Refresh models after OpenCode updates

```bash
~/.openclaw/workspace/scripts/refresh-opencode-models.sh
openclaw gateway restart
```
