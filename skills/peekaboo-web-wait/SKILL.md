---
name: peekaboo-web-wait
emoji: 👀
description: Peekaboo wrapper for slow-loading websites. Handles retries, wait-for-element, and smart delays before interaction.
homepage: https://peekaboo.boo
metadata:
  openclaw:
    os: ["darwin"]
    requires:
      bins: ["peekaboo"]
---

# Peekaboo Web Wait

> **DEFAULT FOR ALL WEB AUTOMATION**: This skill replaces raw `peekaboo` for ANY webpage interaction. Always use this wait-first approach.

Wrapper around Peekaboo for websites that need time to load elements (SPAs, dashboards, auth flows).

## When to use this skill

**ALWAYS** — for every webpage interaction:
- Opening any website in a browser
- Clicking, typing, scrolling on web pages
- Login forms or modals that animate in
- Dashboards that fetch data on load
- SPAs (React/Vue/Angular) where elements appear after JS loads
- Any scenario where you'd reach for `peekaboo` + web

## Workflow (use this, not raw peekaboo)

```bash
# 1. Open browser and navigate
peekaboo app launch "Brave Browser" --open "https://example.com"

# 2. WAIT — let the page load (critical step)
peekaboo sleep --duration 3000  # 3s baseline

# 3. Capture to see current state
peekaboo see --app "Brave Browser" --annotate --path /tmp/step1.png

# 4. If element missing, wait more and retry
peekaboo sleep --duration 2000
peekaboo see --app "Brave Browser" --annotate --path /tmp/step2.png

# 5. Click only after element confirmed visible
peekaboo click --on B3 --app "Brave Browser"
```

## Scripts

### Quick wait-and-see
```bash
~/.openclaw/workspace/skills/peekaboo-web-wait/scripts/wait-and-see.sh "Brave Browser" 3000
```

### Wait for element pattern
```bash
~/.openclaw/workspace/skills/peekaboo-web-wait/scripts/wait-for-element.sh \
  --app "Brave Browser" \
  --element-id "B5" \
  --timeout 10000 \
  --interval 1000
```

## Examples

### Login flow with waits
```bash
# Open login page
peekaboo app launch "Brave Browser" --open "https://app.example.com/login"

# Initial load wait
peekaboo sleep --duration 4000

# See what's available
peekaboo see --app "Brave Browser" --annotate --path /tmp/login-1.png

# Click email field (might need extra wait if modal animates)
peekaboo sleep --duration 1000
peekaboo click --on B2 --app "Brave Browser"
peekaboo type "user@example.com" --app "Brave Browser"

# Tab to password
peekaboo press tab --app "Brave Browser"
peekaboo type "password123" --app "Brave Browser"

# Submit
peekaboo press return --app "Brave Browser"

# Wait for dashboard to load
peekaboo sleep --duration 5000
peekaboo see --app "Brave Browser" --annotate --path /tmp/dashboard.png
```

### SPA navigation (click → wait for content)
```bash
# Click nav item
peekaboo click --on "Settings" --app "Brave Browser"

# Wait for route change + data fetch
peekaboo sleep --duration 3000

# Now interact with new elements
peekaboo see --app "Brave Browser" --annotate --path /tmp/settings.png
peekaboo click --on B4 --app "Brave Browser"
```

## 💡 Pro Tips / Considerations

> **Always wait before trusting `see` output**
> 
> After `app launch --open`, the page is still loading. Always `sleep` at least 2-3s before `see`.

> **Double-capture for critical flows**
> 
> Capture once → check → capture again → click. The first capture shows you the state; the second confirms stability.

> **Use `--annotate` on every `see`**
> 
> You need element IDs (B1, B2, T1...). Without `--annotate`, you can't target clicks reliably.

> **Increment sleep for heavy SPAs**
> 
| Site type | Base wait | Retry wait |
|-----------|-----------|------------|
| Static HTML | 1s | +1s |
| React/Vue (light) | 3s | +2s |
| Dashboards / data-heavy | 5s | +3s |
| Auth0 / complex auth | 4s | +2s |

> **Check for loading states**
> 
> If you see spinners or skeleton screens in your capture, add more wait time. Interacting during loading = flaky automation.

> **Window focus matters**
> 
> Use `--bring-to-current-space` if the browser opens on another Space/Desktop. Elements won't be clickable if the window isn't focused.

> **Prefer `sleep` over `peekaboo see` polling**
> 
> While you could poll with `see`, it's slower and burns API calls. Fixed sleeps with generous buffers are more reliable for web automation.

## Anti-patterns (don't do this)

❌ **Immediate click after launch**
```bash
peekaboo app launch "Brave Browser" --open "https://site.com"
peekaboo click --on B1  # FAIL — page hasn't loaded!
```

❌ **Guessing element IDs**
```bash
peekaboo click --on B5  # FAIL — might be B2 on this page
# Always capture with --annotate first
```

❌ **No retry on missing element**
```bash
peekaboo click --on B3  # FAIL — element still loading
# Add sleep + recapture instead
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Element not found" | Increase `sleep` duration before `see` |
| Click does nothing | Check window focus; add `--bring-to-current-space` |
| Wrong element clicked | Re-capture with `--annotate` — IDs change as page loads |
| Stale snapshot error | Run `peekaboo clean` to clear cache |
| Permission denied | Run `peekaboo permissions` and grant Screen Recording + Accessibility |

## Dependencies

- `peekaboo` CLI (install via `brew install steipete/tap/peekaboo`)
- Brave Browser (or adjust `--app` for Safari/Chrome)
- macOS Screen Recording + Accessibility permissions
