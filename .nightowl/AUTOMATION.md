# Night Owl Automation Guide

## How It Works

Night Owl now automatically activates every night at **2:00 AM** to work on your queued tasks.

```
Daily Schedule
==============
02:00 AM - Night Owl wakes up
         - Checks .nightowl/tasks/pending/
         - Picks highest priority task
         - Starts working (Codex sub-agent)
         
02:00-07:00 AM - Works on task
         - Commits progress
         - Updates status files
         - Generates morning report
         
07:00 AM - Completes or pauses
         - Saves deliverables
         - Reports to Penelopi
         - Goes back to sleep
```

## File Structure

```
.nightowl/
├── wake.sh              # 2 AM activation script
├── spawn-trigger.sh     # Task selector
├── setup-cron.sh        # One-time cron setup
├── config.json          # Settings (schedule, model, etc.)
├── tasks/
│   ├── pending/         # Waiting tasks
│   ├── active/          # Currently working
│   └── completed/       # Done with reports
├── status/
│   └── current.json     # Live status for Mission Control
└── logs/                # Daily activity logs
```

## Setup (One-Time)

```bash
cd /Users/oktos/.openclaw/workspace/.nightowl
./setup-cron.sh
```

This adds the 2 AM cron job to your system.

## How Tasks Are Queued

Add tasks to `.nightowl/tasks/pending/`:

**Naming convention for priority:**
- `2026-03-24-P0-mission-control.md` (Highest)
- `2026-03-24-P1-emojournal.md` (High)
- `2026-03-24-P2-solana-bot.md` (Medium)
- `2026-03-24-P3-refactor.md` (Low)

Night Owl picks P0 first, then P1, etc.

## Current Queue

```
pending/
├── 2026-03-24-mission-control-dashboard.md (P0 - Tonight)
└── 2026-03-25-solana-trading-bot-mvp.md (P1 - Tomorrow)

completed/
└── (Emojournal will go here after Mission Control)
```

## What Night Owl Does

1. **Reads task file** — Gets requirements, acceptance criteria
2. **Creates branch** — `nightowl/YYYY-MM-DD-task-name`
3. **Builds solution** — Codes MVP, tests, documents
4. **Commits regularly** — Every hour or major milestone
5. **Generates report** — What was built, what broke, next steps
6. **Moves to completed** — Task file + report

## Morning Report Format

Each morning you'll see:

```
🦉 NIGHT OWL REPORT — 2026-03-24
================================

Task: Mission Control Dashboard
Status: ✅ COMPLETED (5/5 hours)

Deliverables:
  - Working React dashboard
  - Agent status display
  - Task queue view
  - Activity feed
  - /Users/oktos/.openclaw/workspace/mission-control/

Commits:
  - 02:15 - Initial scaffold
  - 03:30 - Agent cards working
  - 04:45 - Task queue integrated
  - 06:00 - Activity feed live
  - 06:45 - Polish + README

Blockers: None

Next Task Ready: Emojournal Stage 1

Run it:
  cd mission-control && npm run dev
```

## Manual Override

**Skip the queue:**
```bash
# Move task to front
mv .nightowl/tasks/pending/task.md .nightowl/tasks/pending/2026-03-24-P0-task.md
```

**Wake Night Owl now:**
Tell me: "Activate Night Owl" and I'll spawn it immediately.

**Stop Night Owl:**
Create file `.nightowl/STOP` — Night Owl checks this and pauses.

## Cost Tracking

- **Night Owl run:** ~$1-3 USD per night (20k-40k tokens)
- **Monthly (30 nights):** ~$30-90 USD
- **Typical output:** 1 MVP or major feature per night

## Safety

- Works in feature branches only (never main)
- No destructive DB operations without explicit approval marker in task
- Max 5 hours per night (prevents runaway costs)
- Logs everything for review

## Questions?

**Q: What if no tasks are pending?**
A: Night Owl logs "No tasks, going back to sleep" and exits.

**Q: Can Night Owl work longer than 5 hours?**
A: No. Hard stop at 7 AM to prevent runaway costs. Task continues tomorrow if needed.

**Q: What if a task fails?**
A: Error is logged, partial work is saved, report explains what broke. You decide next steps.

**Q: Can I see what Night Owl is doing in real-time?**
A: Check `.nightowl/status/current.json` for live updates (once Mission Control is built, you'll see it there too).

---

**Next activation:** Tonight at 2:00 AM Melbourne time
**Building:** Mission Control Dashboard
**ETA:** 7:00 AM report
