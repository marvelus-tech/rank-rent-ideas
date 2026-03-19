#!/bin/bash
# Inventory Script — What actually exists on disk
# Anti-hallucination tool: grounds the agent in reality
# Run: bash scripts/inventory.sh

set -euo pipefail
WORKSPACE="/Users/oktos/.openclaw/workspace"

echo "========================================="
echo "  WORKSPACE INVENTORY"
echo "  Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "========================================="

echo ""
echo "📁 Core Files:"
for f in SOUL.md IDENTITY.md USER.md AGENTS.md MEMORY.md decisions.md SYSTEM_HARDENING.md HEARTBEAT.md TOOLS.md OWNERSHIP.md; do
    if [ -f "$WORKSPACE/$f" ]; then
        SIZE=$(wc -c < "$WORKSPACE/$f" | tr -d ' ')
        MOD=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$WORKSPACE/$f" 2>/dev/null || stat -c "%y" "$WORKSPACE/$f" | cut -d. -f1)
        echo "  ✅ $f (${SIZE}b, modified: $MOD)"
    else
        echo "  ❌ $f — MISSING"
    fi
done

echo ""
echo "📝 Daily Logs:"
LOG_COUNT=$(ls "$WORKSPACE/memory/"*.md 2>/dev/null | wc -l | tr -d ' ')
echo "  Total: $LOG_COUNT"
ls -1 "$WORKSPACE/memory/"*.md 2>/dev/null | while read f; do
    NAME=$(basename "$f")
    SIZE=$(wc -c < "$f" | tr -d ' ')
    echo "  - $NAME (${SIZE}b)"
done

echo ""
echo "🔧 Scripts:"
SCRIPT_COUNT=$(ls "$WORKSPACE/scripts/"* 2>/dev/null | wc -l | tr -d ' ')
echo "  Total: $SCRIPT_COUNT"
ls -1 "$WORKSPACE/scripts/"* 2>/dev/null | while read f; do
    echo "  - $(basename "$f")"
done

echo ""
echo "📋 Templates:"
TEMPLATE_COUNT=$(ls "$WORKSPACE/templates/"* 2>/dev/null | wc -l | tr -d ' ')
echo "  Total: $TEMPLATE_COUNT"
ls -1 "$WORKSPACE/templates/"* 2>/dev/null | while read f; do
    echo "  - $(basename "$f")"
done

echo ""
echo "🎯 Skills:"
SKILL_COUNT=$(find "$WORKSPACE/skills" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
echo "  Total: $SKILL_COUNT"
find "$WORKSPACE/skills" -name "SKILL.md" 2>/dev/null | while read f; do
    DIR=$(dirname "$f")
    echo "  - $(basename "$DIR")"
done

echo ""
echo "📦 Git Repos in Workspace:"
find "$WORKSPACE" -maxdepth 3 -name ".git" -type d 2>/dev/null | while read f; do
    echo "  - $(dirname "$f")"
done

echo ""
echo "⏰ Cron Jobs: (use 'cron list' tool for details)"

echo ""
echo "========================================="
