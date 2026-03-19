#!/bin/bash
# System Health Check — OpenClaw Workspace
# Produces structured JSON + human-readable summary
# Run: bash scripts/health-check.sh

set -euo pipefail

WORKSPACE="/Users/oktos/.openclaw/workspace"
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TODAY=$(date +"%Y-%m-%d")
YESTERDAY=$(date -v-1d +"%Y-%m-%d" 2>/dev/null || date -d "yesterday" +"%Y-%m-%d")

# Track scores
PASS=0
FAIL=0
WARN=0
CRITICAL_FAIL=0
DETAILS=""

check() {
    local name="$1" status="$2" detail="$3" critical="${4:-false}"
    if [ "$status" = "PASS" ]; then
        PASS=$((PASS + 1))
        DETAILS="${DETAILS}\n  ✅ ${name}: ${detail}"
    elif [ "$status" = "WARN" ]; then
        WARN=$((WARN + 1))
        DETAILS="${DETAILS}\n  ⚠️  ${name}: ${detail}"
    else
        FAIL=$((FAIL + 1))
        DETAILS="${DETAILS}\n  ❌ ${name}: ${detail}"
        if [ "$critical" = "true" ]; then
            CRITICAL_FAIL=$((CRITICAL_FAIL + 1))
        fi
    fi
}

# --- Core Files ---
for f in SOUL.md IDENTITY.md USER.md AGENTS.md decisions.md SYSTEM_HARDENING.md; do
    if [ -f "$WORKSPACE/$f" ]; then
        check "Core file: $f" "PASS" "exists"
    else
        check "Core file: $f" "FAIL" "MISSING" "true"
    fi
done

# --- Daily Logs ---
if [ -f "$WORKSPACE/memory/${TODAY}.md" ]; then
    check "Today's log" "PASS" "memory/${TODAY}.md exists"
else
    check "Today's log" "FAIL" "memory/${TODAY}.md MISSING — session has no context for today" "true"
fi

if [ -f "$WORKSPACE/memory/${YESTERDAY}.md" ]; then
    check "Yesterday's log" "PASS" "memory/${YESTERDAY}.md exists"
else
    check "Yesterday's log" "WARN" "memory/${YESTERDAY}.md missing"
fi

# --- Decisions Log Freshness ---
if [ -f "$WORKSPACE/decisions.md" ]; then
    DECISIONS_MOD=$(stat -f "%m" "$WORKSPACE/decisions.md" 2>/dev/null || stat -c "%Y" "$WORKSPACE/decisions.md")
    NOW_EPOCH=$(date +%s)
    AGE_HOURS=$(( (NOW_EPOCH - DECISIONS_MOD) / 3600 ))
    if [ "$AGE_HOURS" -gt 168 ]; then
        check "Decisions freshness" "WARN" "Last modified ${AGE_HOURS}h ago — review needed"
    else
        check "Decisions freshness" "PASS" "Modified ${AGE_HOURS}h ago"
    fi
fi

# --- MEMORY.md ---
if [ -f "$WORKSPACE/MEMORY.md" ]; then
    check "Long-term memory" "PASS" "MEMORY.md exists"
else
    check "Long-term memory" "WARN" "MEMORY.md missing — no long-term memory yet"
fi

# --- Git Status ---
if [ -d "$WORKSPACE/.git" ]; then
    cd "$WORKSPACE"
    DIRTY=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [ "$DIRTY" -eq 0 ]; then
        check "Git status" "PASS" "Clean working tree"
    else
        check "Git status" "WARN" "${DIRTY} uncommitted changes"
    fi
    LAST_COMMIT=$(git log -1 --format="%ar" 2>/dev/null || echo "unknown")
    check "Last commit" "PASS" "$LAST_COMMIT"
else
    check "Git repo" "FAIL" "Workspace not under version control" "true"
fi

# --- Duplicate Repos Check ---
DUPES=$(find "$WORKSPACE" -name ".git" -type d 2>/dev/null | wc -l | tr -d ' ')
if [ "$DUPES" -le 1 ]; then
    check "Repo duplicates" "PASS" "No duplicate repos found in workspace"
else
    check "Repo duplicates" "WARN" "${DUPES} .git directories found — check for duplicates"
fi

# --- Cron Jobs ---
# This is a placeholder — actual cron audit needs the cron tool
check "Cron audit" "WARN" "Manual review needed — run cron list"

# --- Hardening Progress ---
if [ -f "$WORKSPACE/SYSTEM_HARDENING.md" ]; then
    DONE_COUNT=$(grep -c "✅ DONE" "$WORKSPACE/SYSTEM_HARDENING.md" 2>/dev/null || echo 0)
    TODO_COUNT=$(grep -c "⬜ TODO" "$WORKSPACE/SYSTEM_HARDENING.md" 2>/dev/null || echo 0)
    PARTIAL_COUNT=$(grep -c "🟡 PARTIAL" "$WORKSPACE/SYSTEM_HARDENING.md" 2>/dev/null || echo 0)
    TOTAL=$((DONE_COUNT + TODO_COUNT + PARTIAL_COUNT))
    if [ "$TOTAL" -gt 0 ]; then
        PCT=$((DONE_COUNT * 100 / TOTAL))
        check "Hardening progress" "PASS" "${DONE_COUNT}/${TOTAL} complete (${PCT}%)"
    fi
fi

# --- Calculate Scores ---
TOTAL_CHECKS=$((PASS + FAIL + WARN))
if [ "$TOTAL_CHECKS" -eq 0 ]; then
    RAW_SCORE=0
else
    RAW_SCORE=$((PASS * 100 / TOTAL_CHECKS))
fi

# Integrity multiplier
if [ "$CRITICAL_FAIL" -gt 0 ]; then
    INTEGRITY="FAILING"
    MULTIPLIER="0.33"
    FINAL_SCORE=$(echo "$RAW_SCORE * 0.33" | bc -l | cut -d. -f1)
elif [ "$WARN" -gt 2 ]; then
    INTEGRITY="WARNING"
    MULTIPLIER="0.67"
    FINAL_SCORE=$(echo "$RAW_SCORE * 0.67" | bc -l | cut -d. -f1)
else
    INTEGRITY="HEALTHY"
    MULTIPLIER="1.0"
    FINAL_SCORE=$RAW_SCORE
fi

# Letter grade
if [ "$FINAL_SCORE" -ge 90 ]; then GRADE="A"
elif [ "$FINAL_SCORE" -ge 80 ]; then GRADE="B"
elif [ "$FINAL_SCORE" -ge 70 ]; then GRADE="C"
elif [ "$FINAL_SCORE" -ge 60 ]; then GRADE="D"
else GRADE="F"
fi

# --- Output ---
echo "========================================="
echo "  SYSTEM HEALTH CHECK"
echo "  Timestamp: $NOW"
echo "========================================="
echo ""
echo "  Grade: $GRADE ($FINAL_SCORE/100)"
echo "  Raw Score: $RAW_SCORE/100"
echo "  Integrity: $INTEGRITY (×$MULTIPLIER)"
echo ""
echo "  Checks: $PASS pass / $WARN warn / $FAIL fail"
echo "  Critical failures: $CRITICAL_FAIL"
echo ""
echo "  Details:"
echo -e "$DETAILS"
echo ""
echo "========================================="

# JSON output
cat <<EOF > "$WORKSPACE/health-report.json"
{
  "timestamp": "$NOW",
  "grade": "$GRADE",
  "score": $FINAL_SCORE,
  "rawScore": $RAW_SCORE,
  "integrity": "$INTEGRITY",
  "multiplier": $MULTIPLIER,
  "checks": {
    "pass": $PASS,
    "warn": $WARN,
    "fail": $FAIL,
    "criticalFail": $CRITICAL_FAIL
  }
}
EOF
echo "  JSON report saved to health-report.json"
