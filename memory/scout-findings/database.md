# Scout Findings Database
**Purpose:** Prevent duplicate reports across daily scout runs. Scout checks this file before reporting.

---

## Tracked Tokens

### 2026-03-20 — First Run
| Token | Ticker | Market Cap | First Seen | Status |
|-------|--------|-----------|------------|--------|
| SolCard | SOLC | $5-15M | 2026-03-20 | Known baseline |
| Meteora | MET | $60-90M | 2026-03-20 | Tracking |
| Kamino | KMNO | $80-110M | 2026-03-20 | Tracking |

---

## Duplicate Prevention Rules

**For each new scout run:**
1. Check token name/ticker against this database
2. If already tracked: Skip or update price/market cap only
3. If new: Add to report with full details
4. Update "Last Checked" date for all tracked tokens

**Reporting criteria:**
- **New token:** Full report (confidence ≥60)
- **Existing token:** Only report if market cap moved >20% or new mechanic announced
- **Stale token:** Remove if no activity for 30 days

---

## Scout Instructions
Before adding any token to your daily report, check:
- Is it in the Tracked Tokens table above?
- If yes → Skip (unless significant change)
- If no → Add full details and append to this file

**Goal:** Each daily report contains only NEW findings.
