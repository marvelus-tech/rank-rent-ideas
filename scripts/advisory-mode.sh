#!/bin/bash
# Advisory-Only Mode — Test new rules before enforcing them
# Run: bash scripts/advisory-mode.sh <rule-file>
#
# Checks proposed rules against existing config for conflicts, 
# duplicates, and impact. Outputs a report without changing anything.

WORKSPACE="/Users/oktos/.openclaw/workspace"
RULE_FILE="${1:-}"
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
REPORT_DIR="$WORKSPACE/advisory-reports"

if [ -z "$RULE_FILE" ] || [ ! -f "$RULE_FILE" ]; then
    echo "❌ Usage: bash scripts/advisory-mode.sh <rule-file>"
    echo "   Provide a file with proposed rules/changes."
    exit 1
fi

mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/advisory-$(date +%Y%m%d-%H%M%S).md"

cat > "$REPORT" <<EOF
# Advisory Mode Report
**Timestamp:** $NOW
**Proposed rules:** $RULE_FILE

## 1. Conflict Detection
EOF

CONFLICT_COUNT=0
CONFIG_FILES="AGENTS.md SOUL.md OWNERSHIP.md decisions.md"

for f in $CONFIG_FILES; do
    TARGET="$WORKSPACE/$f"
    if [ ! -f "$TARGET" ]; then continue; fi
    
    # Count overlapping significant words (5+ chars)
    OVERLAP_COUNT=0
    OVERLAP_WORDS=""
    
    for word in $(grep -oiE '[A-Za-z]{5,}' "$RULE_FILE" | sort -u | head -50); do
        if grep -qiw "$word" "$TARGET" 2>/dev/null; then
            OVERLAP_COUNT=$((OVERLAP_COUNT + 1))
            OVERLAP_WORDS="$OVERLAP_WORDS $word"
        fi
    done
    
    if [ "$OVERLAP_COUNT" -gt 5 ]; then
        echo "⚠️  **$f** — $OVERLAP_COUNT overlapping terms (sample: $(echo $OVERLAP_WORDS | tr ' ' '\n' | head -5 | tr '\n' ', '))" >> "$REPORT"
        CONFLICT_COUNT=$((CONFLICT_COUNT + 1))
    else
        echo "✅ **$f** — $OVERLAP_COUNT overlapping terms (low risk)" >> "$REPORT"
    fi
done

echo "" >> "$REPORT"
echo "## 2. Size Impact" >> "$REPORT"
echo "" >> "$REPORT"

RULE_LINES=$(wc -l < "$RULE_FILE" | tr -d ' ')
AGENTS_LINES=$(wc -l < "$WORKSPACE/AGENTS.md" | tr -d ' ')
echo "- Proposed file: $RULE_LINES lines" >> "$REPORT"
echo "- Current AGENTS.md: $AGENTS_LINES lines" >> "$REPORT"
echo "- Config files with overlaps: $CONFLICT_COUNT / $(echo $CONFIG_FILES | wc -w | tr -d ' ')" >> "$REPORT"

echo "" >> "$REPORT"
echo "## 3. Risk Assessment" >> "$REPORT"
echo "" >> "$REPORT"

if [ "$CONFLICT_COUNT" -gt 2 ]; then
    echo "### ⚠️  HIGH RISK" >> "$REPORT"
    echo "Multiple config files have significant overlap with proposed rules. Manual review of each overlap required before applying." >> "$REPORT"
elif [ "$CONFLICT_COUNT" -gt 0 ]; then
    echo "### 🟡 MODERATE RISK" >> "$REPORT"
    echo "Some overlaps detected. Review flagged files before applying." >> "$REPORT"
else
    echo "### ✅ LOW RISK" >> "$REPORT"
    echo "Minimal overlap with existing config. Safe to apply with standard review." >> "$REPORT"
fi

echo "" >> "$REPORT"
echo "---" >> "$REPORT"
echo "**Before applying:** Run \`bash scripts/snapshot.sh pre-rule-change\`" >> "$REPORT"

echo ""
echo "✅ Advisory report saved to: $REPORT"
echo ""
cat "$REPORT"
