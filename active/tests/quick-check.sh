#!/bin/zsh
# Quick Memory System Diagnostic
# One-line check: bash <(curl -s ...)
# Or run locally: ~/.openclaw/workspace/tests/quick-check.sh

echo "🔱 Penelopi Memory Check"
echo "========================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

check_file() {
  if [[ -f "$1" ]]; then
    echo "${GREEN}✓${NC} $2"
    return 0
  else
    echo "${RED}✗${NC} $2 - MISSING"
    ((ERRORS++))
    return 1
  fi
}

check_file "$HOME/Obsidian/Penelopi/WHO-I-AM.md" "Identity"
check_file "$HOME/Obsidian/Penelopi/WHO-YOU-ARE.md" "User Profile"
check_file "$HOME/Obsidian/Penelopi/DECISIONS.md" "Decisions"
check_file "$HOME/Obsidian/Penelopi/MEMORY.md" "Long-term Memory"

TODAY=$(date +%Y-%m-%d)
if [[ -f "$HOME/Obsidian/Penelopi/Daily/$TODAY.md" ]]; then
  echo "${GREEN}✓${NC} Today's Log ($TODAY)"
else
  echo "${YELLOW}⚠${NC} Today's Log ($TODAY) - Will create on first write"
fi

echo ""
if [[ $ERRORS -eq 0 ]]; then
  echo "${GREEN}✅ Memory system healthy${NC}"
  echo "   Run full test: ~/.openclaw/workspace/tests/validate-memory-system.sh"
else
  echo "${RED}❌ Issues detected${NC}"
  echo "   Check CONFIDENCE-REPORT.md for troubleshooting"
fi
