# TaskPilot Manual Button Handling Guide

## How It Works

Since OpenClaw doesn't auto-route Telegram callback queries, we use **manual handling**:

1. **You click a button** in Telegram
2. **OpenClaw receives** the callback but presents it as text
3. **I detect** `callback_data: taskpilot:...` in your message
4. **I call** `taskpilot-bridge.mjs` to process the action
5. **Response sent** back to you

## Current Button Actions

| Button | callback_data | What It Does |
|--------|--------------|--------------|
| ✅ Done | `taskpilot:done:<task-id>` | Marks task as completed |
| ⏰ Snooze | `taskpilot:snooze:<task-id>` | Moves task to tomorrow |
| 📋 View All | `taskpilot:view_all` | Shows all active tasks |
| ➕ Add Task | `taskpilot:add_task` | Prompts for new task input |

## Manual Workflow

### When Morning Brief Arrives (08:00 daily)
```
☀️ Morning Brief — 2026-06-20

🚨 MUST-DO (2):
• Call client ⏰ 14:00
• Submit report ⏰ 16:00

[✅ Call client] [✅ Submit report]
[📋 View All] [➕ Add Task]
```

### You Click "✅ Call client"
Telegram sends: `callback_data: taskpilot:done:call-client-123`

### I Handle It
I see your message, call the bridge:
```bash
node taskpilot-bridge.mjs "taskpilot:done:call-client-123" 47930691
```

### Result
- Task marked as done in TaskPilot-Master.md
- Confirmation sent: "✅ Marked as done: Call client"

## Commands You Can Send Me

Instead of clicking buttons, you can also just tell me:

| What You Say | What Happens |
|-------------|--------------|
| "Mark Call client as done" | Marks task done |
| "Snooze Submit report" | Moves to tomorrow |
| "Show my tasks" | Lists all active tasks |
| "Add task: Call dentist tomorrow 2pm #must-do" | Adds new task |

## Files

- `scripts/taskpilot-bridge.mjs` — Bridge script (I call this)
- `scripts/taskpilot-bot.mjs` — Handler logic
- `scripts/taskpilot-reminders.mjs` — Sends Morning Brief with buttons
- `Obsidian/Penelopi/Tasks/TaskPilot-Master.md` — Task registry

## Tomorrow's Test

At 08:00, you'll get the Morning Brief with buttons. Click one and I'll handle it manually.

If you want **fully automated** button handling without me, that requires OpenClaw core changes or a standalone bot.
