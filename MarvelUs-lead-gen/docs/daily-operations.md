# Daily Operations Runbook

## What the Daily Script Does

Command:

```bash
python main.py run --config config/config.yaml --mode browser
```

Step-by-step:
1. Loads config and existing lead database (`leads_db.json`).
2. Runs **browser mode** Google Maps discovery (`--mode browser`, no API cost).
3. Applies a hard daily limit (`limits.daily_lead_limit`, default 10) on **new non-duplicate leads**.
4. Uses round-robin scan state (`data/scan_state.json`) to rotate categories/locations daily.
5. Prioritizes high-value categories first (HVAC, plumbing, law firms, dental), then continues through the full list.
6. Builds dedupe key from `name + address + phone`.
7. Separates **new leads** from previously seen leads.
8. Updates existing leads' `last_seen_date` and `scan_history` when re-seen.
9. Analyzes only new leads (website + scoring).
10. Appends new analyzed leads into persistent DB.
11. Writes master outputs:
   - `leads_master.csv`
   - `leads_master.json`
   - daily delta (`daily_delta.csv`, only NEW leads)
   - `output/daily_complete.csv` (all NEW leads for DB ingestion/checkpoint)
12. Generates markdown daily report with:
   - total scanned
   - new leads
   - duplicates skipped
   - pipeline stage counts
13. Generates Penelopi handoff packet:
   - `output/daily_for_review.md` (Telegram-ready review brief)
   - `output/daily_for_review.json` (structured payload)
   - includes `recommended_for_outreach` flag and caps review list to max 15
14. Renders HTML dashboard.

## How to Interpret the Daily Report

Key metrics:
- **Total leads scanned**: raw scan volume (discovery throughput)
- **New leads found**: actual pipeline growth
- **Duplicates skipped**: re-scan overlap and market saturation signal
- **Pipeline stage counts**: current funnel distribution

Quick read:
- High duplicates + low new leads = zone/category saturation → expand grid ring or switch category tier.
- High new leads + low follow-up movement = outreach bottleneck.
- Rising contacted/interested with flat proposal/closed = qualification/messaging issue.

## Manual Review: When and How

Review daily delta manually when:
- `new leads >= 20` in a run
- New high-priority leads appear
- Duplicate rate jumps >60%

Manual review checklist:
1. Validate top scored leads (website quality + Google profile quality).
2. Confirm phone number and website are usable.
3. Remove obvious false positives (directories, aggregators).
4. Add outreach notes and initial sequence status.

## Follow-up Cadence Recommendations

Suggested default cadence:
- **Day 0:** Initial contact (phone + email if available)
- **Day 3:** Follow-up #1 (value proposition + missed-call angle)
- **Day 7:** Follow-up #2 (social proof/case style)
- **Day 14:** Breakup follow-up (final check-in)

Escalate priority if:
- business has strong reviews but weak digital response tooling
- high-ticket services and call-dependent operations

Deprioritize if:
- no direct phone path
- duplicated/invalid listing data
- out-of-service area

## Two-Tier Handoff Flow (Scraper → Penelopi → Okeito)

```text
Daily Cron Run
   ↓
Scraper + Analyzer + Scoring
   ↓
output/daily_complete.csv  (all new leads, database-grade)
output/daily_for_review.md (high-priority shortlist + recommendations)
   ↓
Penelopi evaluation gate (rubric + manual sanity checks)
   ↓
Curated, high-probability outreach list to Okeito
```

## What Penelopi Evaluates Daily

Penelopi reviews the packet using `docs/evaluation-rubric.md`:
- Must-surface: no chatbot AND no call button
- Reputation strength: rating 4.5+ and 50+ reviews
- Category/intent fit for AI voice + chat
- Business legitimacy (not spam/broken web presence)

Penelopi filters out:
- sophisticated existing chatbot implementations
- chain/franchise operators
- very low-signal listings (<5 reviews)
- broken/non-existent websites

## Review SLA

- **Penelopi review target:** within **24 hours** of each daily cron run
- If no qualified leads pass the gate, report "no action today" instead of forcing low-quality leads

## Responsible Outreach & Compliance

- Only contact businesses using lawful, transparent, and respectful outreach.
- Honor any "do not contact" request immediately and record it in your CRM/list hygiene process.
- For Australia, follow the **Spam Act 2003** (consent, sender identification, unsubscribe).
- For U.S. outreach, follow **CAN-SPAM** requirements (clear identity, no deceptive headers/subjects, easy opt-out).
- When contact information is missing or uncertain, flag for manual research instead of guessing.
