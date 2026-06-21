---
name: brave-maps
description: Automate Brave Browser to open and interact with Google Maps. Use when the agent needs to launch Google Maps in Brave, perform map searches, take screenshots, or automate map-based workflows. Triggers on requests like "open Google Maps", "search maps", "show me a map", "automate Google Maps", "use Brave for maps".
---

# Brave Maps Automation

Automate Brave Browser to open and control Google Maps via Playwright.

## Requirements

- Brave Browser installed at `/Applications/Brave Browser.app`
- Node.js and npm
- Playwright (auto-installed on first run)

## Quick Start

```bash
# Open Google Maps in Brave
~/.openclaw/workspace/skills/brave-maps/scripts/open-maps.sh

# Search for a location
~/.openclaw/workspace/skills/brave-maps/scripts/search-maps.sh "Melbourne Australia"
```

## Scripts

### open-maps.sh
Launch Google Maps in Brave Browser.

### search-maps.sh [query]
Search for a location on Google Maps.

Example:
```bash
search-maps.sh "Sydney Opera House"
search-maps.sh "coffee shops near me"
```

## Programmatic Use

Use the Playwright scripts directly:

```javascript
const { openGoogleMaps } = require('./scripts/maps-core.js');
await openGoogleMaps(); // Opens maps
await searchLocation('query'); // Searches
```

## Notes

- Browser launches visible (not headless) for interaction
- First run installs Playwright automatically
- Uses clean profile to avoid interfering with main browser
