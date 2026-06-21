# Night Owl 🦉

Autonomous overnight coding workflow for Okeito.

Location: `/Users/oktos/.openclaw/workspace/.nightowl/`

## What Night Owl Does
Night Owl runs development tasks during off-hours (23:00–07:00 Australia/Melbourne), executes scoped coding work, and leaves a structured morning report with diffs, tests, blockers, and next steps.

## Directory Structure
```text
.nightowl/
  config.json
  README.md
  tasks/
    template.md
    pending/
    active/
    completed/
  reports/
    template.md
    example-morning-report.md
```

## How Okeito Assigns a Task
1. Copy `tasks/template.md` into `tasks/pending/`.
2. Name the file with date + slug, e.g.:
   - `YYYY-MM-DD-short-task-name.md`
3. Fill in:
   - Project/context
   - Specific requirements
   - Acceptance criteria
   - Priority (P0–P3)
   - Estimated hours
   - Dependencies
4. Night Owl moves the task from `pending/` → `active/` when it starts.
5. On completion, Night Owl moves task to `completed/` and writes a report in `reports/`.

## Autonomous Workflow
- Picks highest-priority task from `tasks/pending/`.
- Creates/uses branch prefix `nightowl/`.
- Implements changes with focused commits.
- Runs tests and captures outputs.
- Produces markdown morning report.
- Archives task and links report artifacts.

## Reporting
Reports follow `reports/template.md` and include:
- Summary of completed work
- Files changed + git diff output
- Tests added/passed
- Blockers encountered
- Questions for Okeito
- Next steps

See `reports/example-morning-report.md` for expected output format.

## Safety Rules & Limits
From `config.json`:
- Explicit approval required for:
  - `git_push_to_main`
  - `destructive_db_ops`
  - `paid_api_calls`
- Auto-commit branch prefix: `nightowl/`

Operational limits:
- No destructive operations without approval.
- No direct main-branch pushes.
- Preserve logs/artifacts for review.
- Prioritize reproducible test evidence in every report.

## First Queued Task
Ready in:
- `tasks/pending/2026-03-23-enhance-leadgen-browser-scraper.md`

This task upgrades scraper resilience (retry backoff, full error screenshots, randomized delays, and end-to-end test script).
