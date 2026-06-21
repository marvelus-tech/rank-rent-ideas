#!/bin/bash
# Auto-Escalation Script — Detect repeated corrections and flag for script enforcement
# Run: bash scripts/auto-escalate.sh
#
# Scans decisions.md for patterns that appear more than once.
# If the same correction was given 2+ times, it needs a mechanical gate, not another doc line.
#
# Output: escalation report with recommended actions

set -euo pipefail
WORKSPACE="/Users/oktos/.openclaw/workspace"
DECISIONS="$WORKSPACE/decisions.md"
ESCALATION_LOG="$WORKSPACE/escalations.md"
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ ! -f "$DECISIONS" ]; then
    echo "❌ decisions.md not found at $DECISIONS"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AUTO-ESCALATION CHECK"
echo "  Timestamp: $NOW"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Extract decision lines (lines starting with - that have dates)
DECISION_LINES=$(grep -E '^\s*-\s*[0-9]{4}-[0-9]{2}-[0-9]{2}' "$DECISIONS" 2>/dev/null || true)

if [ -z "$DECISION_LINES" ]; then
    echo "  No dated decisions found. Nothing to check."
    exit 0
fi

TOTAL=$(echo "$DECISION_LINES" | wc -l | tr -d ' ')
echo "  Total decisions found: $TOTAL"
echo ""

# Normalize decisions: strip dates, lowercase, remove extra whitespace
# Then find duplicates or near-duplicates
NORMALIZED=$(echo "$DECISION_LINES" | sed 's/^[^:]*:[[:space:]]*//' | tr '[:upper:]' '[:lower:]' | sed 's/[[:space:]]\+/ /g' | sort)

# Find exact duplicates
EXACT_DUPES=$(echo "$NORMALIZED" | uniq -d)

# Find decisions with similar keywords (more than 3 shared significant words)
ESCALATION_NEEDED=0

if [ -n "$EXACT_DUPES" ]; then
    echo "  🚨 EXACT DUPLICATE CORRECTIONS FOUND:"
    echo "  These corrections were given multiple times — they MUST become scripts."
    echo ""
    echo "$EXACT_DUPES" | while read line; do
        COUNT=$(echo "$NORMALIZED" | grep -cF "$line" || true)
        echo "  ❌ Repeated $COUNT times: \"$line\""
    done
    echo ""
    ESCALATION_NEEDED=1
else
    echo "  ✅ No exact duplicate corrections found."
    echo ""
fi

# Keyword frequency analysis — find recurring themes
echo "  📊 Keyword Frequency (potential recurring themes):"
echo ""
KEYWORDS=$(echo "$NORMALIZED" | tr ' ' '\n' | awk 'length >= 5' | sort | uniq -c | sort -rn | head -10)
echo "$KEYWORDS" | while read count word; do
    if [ "$count" -gt 2 ]; then
        echo "  ⚠️  \"$word\" appears $count times across decisions"
        ESCALATION_NEEDED=1
    else
        echo "  ✅ \"$word\" ($count)"
    fi
done

echo ""

# Check for known anti-patterns: decisions that reference the same topic
echo "  🔍 Topic Clustering:"
echo ""

# Group by first significant noun/verb
TOPICS=$(echo "$NORMALIZED" | sed 's/^[^a-z]*//' | cut -d' ' -f1-3 | sort | uniq -c | sort -rn | head -5)
echo "$TOPICS" | while read count phrase; do
    if [ "$count" -gt 1 ]; then
        echo "  ⚠️  Topic repeated $count times: \"$phrase\""
    else
        echo "  ✅ \"$phrase\" ($count)"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$ESCALATION_NEEDED" -gt 0 ]; then
    echo "  ⚠️  ESCALATION RECOMMENDED"
    echo "  Some corrections are being repeated."
    echo "  Action: Convert repeated corrections into enforcement scripts."
    echo ""
    echo "  The article's data:"
    echo "    - Rules as documentation: ~48% compliance"
    echo "    - Rules as scripts: ~100% compliance"
    echo ""
    echo "  Every repeated correction is a script you haven't written yet."
else
    echo "  ✅ No escalation needed. All corrections appear unique."
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Append to escalation log if issues found
if [ "$ESCALATION_NEEDED" -gt 0 ]; then
    if [ ! -f "$ESCALATION_LOG" ]; then
        echo "# Escalation Log" > "$ESCALATION_LOG"
        echo "**Purpose:** Track corrections that were repeated and need script enforcement." >> "$ESCALATION_LOG"
        echo "" >> "$ESCALATION_LOG"
        echo "---" >> "$ESCALATION_LOG"
        echo "" >> "$ESCALATION_LOG"
    fi
    echo "## $NOW" >> "$ESCALATION_LOG"
    echo "Escalation check found repeated patterns. Review decisions.md and convert to scripts." >> "$ESCALATION_LOG"
    echo "" >> "$ESCALATION_LOG"
    echo "  📝 Escalation log updated: $ESCALATION_LOG"
fi
