---
name: presence-detection
emoji: 🏠
description: Home/away presence detection via webhook endpoints. Handles geofence and WiFi triggers with smart away confirmation.
metadata:
  openclaw:
    os: ["darwin", "linux"]
---

# Presence Detection

Automated home/away detection using webhook endpoints from phone geofence or WiFi detection.

## Quick Start

**1. Run setup:**
```bash
~/.openclaw/workspace/skills/presence-detection/scripts/setup.sh
```

**2. Your webhook URL:**
```
http://192.168.1.16:8123/presence?user=okeito&status=home&source=wifi&confidence=1.0
```

**3. Test it:**
```bash
curl 'http://192.168.1.16:8123/presence?user=okeito&status=home&source=wifi&confidence=1.0'
```

## Endpoint

**Base URL:** `http://192.168.1.16:8123`

**Path:** `/presence`

**Method:** GET

**Parameters:**
- `user` — user identifier (e.g., "okeito")
- `status` — `home` or `away`
- `source` — `wifi` or `geofence`
- `confidence` — 0.0 to 1.0 certainty level

## iPhone Shortcuts Setup

### 1. Arrive Home (WiFi)
```
Trigger: Connect to WiFi "YourNetwork"
Action: GET http://192.168.1.16:8123/presence?user=okeito&status=home&source=wifi&confidence=1.0
```

### 2. Arrive by Car (Geofence)
```
Trigger: Enter Home Geofence
Action: GET http://192.168.1.16:8123/presence?user=okeito&status=home&source=geofence&confidence=1.0
```

### 3. Leave Home (Geofence)
```
Trigger: Exit Home Geofence
Action: GET http://192.168.1.16:8123/presence?user=okeito&status=away&source=geofence&confidence=1.0
```

## Handler Logic

### Status = Home

1. Log event to Obsidian daily note
2. If `source=geofence`: Trigger "arriving by car" logic (preheat, garage, etc.)
3. Trigger `home_mode` skill (lights, music, etc.)

### Status = Away

1. Log event to Obsidian daily note
2. Set 10-minute probation period
3. After delay: Trigger `away_mode` skill (security, lights off, etc.)

**Why probation?** Prevents false triggers from brief departures (getting mail, etc.)

## Files

| File | Purpose |
|------|---------|
| `presence-listener.js` | HTTP server that receives webhook calls |
| `~/Library/LaunchAgents/ai.openclaw.presence-listener.plist` | Auto-starts listener on boot |
| `scripts/setup.sh` | One-command setup |
| `scripts/check-status.sh` | Check current presence state |

## Logs

```bash
# View listener logs
tail -f /tmp/openclaw/presence-listener.log

# View errors
tail -f /tmp/openclaw/presence-listener.error.log

# Check if running
launchctl list | grep presence-listener
```

## Manual Control

```bash
# Start listener
launchctl start ai.openclaw.presence-listener

# Stop listener
launchctl stop ai.openclaw.presence-listener

# Restart
launchctl stop ai.openclaw.presence-listener && launchctl start ai.openclaw.presence-listener
```

## Test Commands

```bash
# Simulate arriving home
curl 'http://192.168.1.16:8123/presence?user=okeito&status=home&source=wifi&confidence=1.0'

# Simulate arriving by car
curl 'http://192.168.1.16:8123/presence?user=okeito&status=home&source=geofence&confidence=1.0'

# Simulate leaving
curl 'http://192.168.1.16:8123/presence?user=okeito&status=away&source=geofence&confidence=1.0'

# Health check
curl http://192.168.1.16:8123/health
```

## Memory Recording

Events are logged to:
```
~/Obsidian/Penelopi/Daily/YYYY-MM-DD.md
```

Example entry:
```markdown
## Presence Event - 2026-04-02T15:45:00.000Z
- User: okeito
- Status: home
- Source: wifi
- Confidence: 1
```

## Integration with Other Skills

The presence listener can trigger other skills. Edit `presence-listener.js` to add:

```javascript
// After line 45 (inside handlePresence function):
if (status === 'home') {
  // Add your custom actions here
  exec('openclaw skills run home-mode');
  exec('say "Welcome home"');
}
```

Create these skills to handle the triggers:
- `~/.openclaw/workspace/skills/home-mode/` — Lights on, music, temperature
- `~/.openclaw/workspace/skills/preheat-home/` — Pre-cool/heat, garage, outdoor lights
- `~/.openclaw/workspace/skills/away-mode/` — Security on, lights off, thermostat away

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Connection refused" | Check listener is running: `launchctl start ai.openclaw.presence-listener` |
| iPhone can't reach endpoint | Verify same WiFi network; check Mac firewall |
| Events not logging | Check Obsidian directory exists; verify file permissions |
| False triggers | Increase geofence radius in Shortcuts; rely on WiFi trigger for "home" |

## Security Notes

- Endpoint is on local network only (192.168.x.x)
- No authentication by default (trusted local network)
- To add API key, edit `presence-listener.js` and add validation

## Dependencies

- Node.js (installed via Homebrew)
- OpenClaw gateway (for future skill triggering)
- iPhone Shortcuts app
