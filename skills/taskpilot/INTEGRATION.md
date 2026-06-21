# TaskPilot OpenClaw Integration

## How Button Callbacks Work

When you click a button in Telegram:
1. Telegram sends `callback_query` to OpenClaw (via polling)
2. OpenClaw processes it as a user message with `callback_data`
3. We need to intercept this and route to TaskPilot handlers

## Current Behavior

The button click arrives as a message with `callback_data: taskpilot:...` but OpenClaw treats it as plain text.

## Solution Options

### Option A: OpenClaw Native Skill (Recommended)
Create an OpenClaw skill that:
- Detects `callback_data` starting with `taskpilot:`
- Calls the appropriate handler
- Sends response back to Telegram

### Option B: Standalone Bot (Current Attempt)
Run separate webhook server — conflicts with OpenClaw's polling

## Implementation

Since OpenClaw is already the bot, we should:
1. Add TaskPilot handlers to OpenClaw's message processing
2. Use OpenClaw's built-in Telegram API for responses
3. Remove standalone webhook approach

## Files

- `scripts/taskpilot-bot.mjs` — Callback handlers (pure logic, no server)
- `scripts/taskpilot-reminders.mjs` — Cron jobs with button sends
- `skills/taskpilot/` — OpenClaw skill manifest

## Next Steps

1. Create OpenClaw skill that intercepts callback queries
2. Route to taskpilot-bot handlers
3. Use OpenClaw's native send/reply for responses
