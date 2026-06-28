# Agent-built project — Bugbot rules

Copy this file to `.cursor/BUGBOT.md` in any repo OpenClaw pushes to GitHub so **remote Bugbot on PRs** picks it up.

## Secrets (blocking)

- No API keys, tokens, passwords, or private webhook URLs in committed files.
- Use `.env` (gitignored) or GitHub Actions secrets — never commit `.env`.

## Static / dashboard apps

- Avoid `innerHTML` with untrusted or scraped data; prefer `textContent` or sanitize.
- Fetch/API calls should handle non-OK responses and show a user-visible error state.

## General

- Do not commit build artifacts, logs, or local-only data unless the repo explicitly tracks them.
- Prefer small, focused PRs over mixing unrelated features.
