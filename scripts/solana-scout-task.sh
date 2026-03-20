#!/bin/bash
# Solana Scout — Daily Token Research Task
# This script documents what the scout agent should do.
# Actual execution happens via cron + sub-agent spawn.

set -euo pipefail

REPORT_FILE="$1"

cat > "$REPORT_FILE" << 'SCOUT_TEMPLATE'
## Handoff: Solana Token Scout — Daily Report
**From:** Solana Scout (sub-agent)
**To:** Penelopi (main session)
**Dispatched:** {{TIMESTAMP}}
**Priority:** Medium

### Task
Daily Solana small-cap hold-to-earn token research.

### Context
Searching for tokens under $100M market cap on Solana with reward mechanics similar to solcard.cc.

### Expected Output
3-5 qualified tokens with full details and evidence.

---

## Findings

{{#each tokens}}
### {{name}} (${{ticker}})
- **Market Cap:** {{marketCap}}
- **What it does:** {{description}}
- **Reward mechanic:** {{rewardMechanic}}
- **Why interesting:** {{whyInteresting}}
- **Links:** {{links}}
- **Confidence:** {{confidence}}/100

{{/each}}

{{#if noTokensFound}}
**Result:** No qualifying tokens found in today's scan.
**Note:** This is a valid outcome — quality over quantity.
{{/if}}

---

## Evidence Summary
- Tokens found: {{count}}
- Sources checked: Web search, X/Twitter mentions, Solana ecosystem trackers
- Search terms used: "Solana hold to earn", "Solana revenue share token", "Solana staking rewards small cap"

### Return To
Main session will review and surface high-confidence finds (≥70/100) to Okeito immediately.
Lower confidence finds aggregated in weekly digest unless explicitly interesting.
SCOUT_TEMPLATE

echo "Template ready: $REPORT_FILE"
