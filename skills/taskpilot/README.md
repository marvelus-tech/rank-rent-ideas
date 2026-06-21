# TaskPilot 🎯

**AI-powered task management via Telegram with inline buttons**

## Architecture (OpenClaw Integration)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Telegram User  │────▶│     OpenClaw     │────▶│  TaskPilot Core │
│  (Clicks Button)│     │  (Bot + Router)  │     │  (Obsidian + JS)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                                               │
         │                                               ▼
         │                                       ┌──────────────┐
         │                                       │ TaskPilot-Master.md
         │                                       │ (Single source of truth)
         │                                       └──────────────┘
         │                                               │
         ▼                                               ▼
┌─────────────────┐                           ┌─────────────────┐
│ Button Response │◀──────────────────────────│  Morning Brief  │
│ ✅ Done         │                           │  Urgency Alerts │
│ ⏰ Snooze       │                           │  EOD Audit      │
│ 📋 View All     │                           │  Daily Snapshot │
│ ➕ Add Task     │                           │                 │
└─────────────────┘                           └─────────────────┘
```

## How Button Callbacks Work

Since **OpenClaw is the Telegram bot**, button clicks are received by OpenClaw as messages with `callback_data`. TaskPilot integrates via:

1. **OpenClaw detects** `callback_data` starting with `taskpilot:`
2. **Routes to** `taskpilot-bridge.mjs` with the callback data
3. **Handler processes** the action (done, snooze, view_all, add_task)
4. **Response sent** back through OpenClaw's native Telegram API

## Components

### Core Scripts

| Script | Purpose | Trigger |
|--------|---------|---------|
| `taskpilot-lib.mjs` | Shared library - parsing, Telegram API, file I/O | Imported by all |
| `taskpilot-reminders.mjs` | Morning brief + urgency alerts (with buttons) | Cron: 08:00, */15 |
| `taskpilot-capture.mjs` | Natural language task creation | Manual / Agent |
| `taskpilot-audit.mjs` | EOD summary + overdue marking | Cron: 18:00 |
| `taskpilot-bot.mjs` | Callback query handler logic | Called by bridge |
| `taskpilot-bridge.mjs` | OpenClaw integration bridge | Called by OpenClaw |

### Data Storage

- **Master Registry**: `~/Obsidian/Penelopi/Tasks/TaskPilot-Master.md`
- **Daily Snapshots**: `~/Obsidian/Penelopi/Tasks/Daily/YYYY-MM-DD.md`
- **State Files**: `~/.openclaw/workspace/data/alerted-tasks.json`, `morning-brief-sent.flag`

## Telegram Button Actions

### Morning Brief Buttons
```
☀️ Morning Brief — 2026-06-20

🚨 MUST-DO (2):
• Call client ⏰ 14:00
• Submit report ⏰ 16:00

📋 SHOULD-DO (1):
• Review budget

[✅ Call client] [✅ Submit report]
[📋 View All] [➕ Add Task]
```

### Urgency Alert Buttons
```
⏰ T-15min: Call client ⏰14:00

[✅ Done] [⏰ Snooze]
```

## Cron Schedule

```cron
# Morning brief with inline buttons
0 8 * * * node taskpilot-reminders.mjs morning

# Urgency checks (T-4h, T-1h, T-15min)
*/15 * * * * node taskpilot-reminders.mjs check

# EOD audit + tomorrow preview
0 18 * * * node taskpilot-audit.mjs
```

## Natural Language Capture

```bash
# Add tasks from terminal
node taskpilot-capture.mjs "Call client tomorrow 2pm #must-do"
node taskpilot-capture.mjs "Review budget by Friday #should-do"
node taskpilot-capture.mjs "Buy groceries #nice-to-have"

# Supported patterns
"task description tomorrow 2pm #must-do"
"urgent call client in 2 hours"
"submit report next monday 9am #should-do"
"review docs in 3 days"
```

## Button Callback Data Format

```javascript
// Format: taskpilot:<command>:<args>
taskpilot:done:abc123        // Mark task as done
taskpilot:snooze:abc123      // Snooze task to tomorrow
taskpilot:view_all           // Show all active tasks
taskpilot:add_task           // Prompt to add new task
```

## OpenClaw Integration

When a user clicks a button, OpenClaw receives:
```json
{
  "callback_query": {
    "id": "123",
    "data": "taskpilot:done:abc123",
    "message": { "chat": { "id": 47930691 }, "message_id": 456 }
  }
}
```

OpenClaw should call:
```bash
node taskpilot-bridge.mjs "taskpilot:done:abc123" 47930691 456
```

## State Management

### Deduplication
- **Morning Brief**: `morning-brief-sent.flag` (daily)
- **Urgency Alerts**: `alerted-tasks.json` (per-task per-bucket)
- **Overdue Sweep**: tracked in `alerted-tasks.json`

### Daily Flow
```
08:00 → Morning Brief (with buttons)
  ↓
Throughout day → Urgency alerts (T-4h, T-1h, T-15min)
  ↓
18:00 → EOD Audit + tomorrow snapshot
  ↓
User clicks buttons → Instant task updates via OpenClaw
```

## Future Enhancements

- [ ] Recurring tasks (daily/weekly/monthly)
- [ ] Project tags with filtering
- [ ] Time tracking integration
- [ ] Calendar sync (Google/Apple)
- [ ] Voice message task capture
- [ ] AI task prioritization suggestions
