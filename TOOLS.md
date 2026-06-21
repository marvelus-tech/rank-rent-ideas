# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## Lazyweb MCP
- Token: `4623ba0e-2f03-49ee-9379-a181c3b2d178`
- URL: `https://www.lazyweb.com/mcp`
- Transport: Streamable HTTP
- Header: `Authorization: Bearer <token>`
- Skills installed at: `~/.openclaw/workspace/skills/lazyweb-*`
- Router installed for: codex
- Use for: design research, UI/UX references, screenshot search, A/B test research, paywall optimization, onboarding flows


## Related

- [Agent workspace](/concepts/agent-workspace)
