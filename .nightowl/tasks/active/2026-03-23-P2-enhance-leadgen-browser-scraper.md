# Task: Enhance leadgen browser scraper resilience

## Project / Context
- Project path: `/Users/oktos/.openclaw/workspace/leadgen`
- Target file: `/Users/oktos/.openclaw/workspace/leadgen/src/browser_scraper.py`
- Context: Current scraper works but needs resilience and reliability upgrades for unattended overnight execution.

## Specific Requirements
- [ ] Add exponential backoff retry logic to relevant fragile browser operations:
  - 3 retries total
  - Starting delay: 2 seconds
  - Backoff sequence: 2s, 4s, 8s
- [ ] Capture screenshots on **all** errors (not only fatal errors), with clear filenames and timestamps.
- [ ] Add random delay between business detail extractions:
  - Range: 1–3 seconds
  - Applied consistently per item to reduce anti-bot patterns.
- [ ] Create an end-to-end test script to verify scraper workflow and error-handling path.

## Acceptance Criteria
- [ ] Retry behavior is implemented and observable in logs.
- [ ] On any exception path, a screenshot artifact is created.
- [ ] Randomized delay is present and bounded to 1–3 seconds.
- [ ] Test script can be run locally and returns pass/fail outcome.
- [ ] Morning report includes changed files, diffs, and test output.

## Priority
**P1** (High)

## Estimated Hours
**4–6 hours**

## Dependencies
- Python environment and scraper dependencies installed.
- Access to target pages used by scraper test flow.
- Writable output folder for screenshots/test artifacts.

## Notes for Night Owl
- Use branch prefix from config: `nightowl/`.
- Keep changes minimal, targeted, and safe for review.
- Do not push to main without explicit approval.
