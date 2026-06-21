#!/bin/zsh
# Memory System Validation Test
# Tests that Obsidian-based memory system is working correctly

echo "🔱 Penelopi Memory System Validation"
echo "======================================"
echo ""

FAILED=0
PASSED=0

# Test 1: Core files exist
echo "📁 Testing file existence..."
files=(
  "$HOME/Obsidian/Penelopi/README.md"
  "$HOME/Obsidian/Penelopi/WHO-I-AM.md"
  "$HOME/Obsidian/Penelopi/WHO-YOU-ARE.md"
  "$HOME/Obsidian/Penelopi/DECISIONS.md"
  "$HOME/Obsidian/Penelopi/MEMORY.md"
  "$HOME/Obsidian/Penelopi/AGENTS.md"
)

for file in "${files[@]}"; do
  if [[ -f "$file" ]]; then
    echo "  ✅ $(basename "$file")"
    ((PASSED++))
  else
    echo "  ❌ $(basename "$file") - MISSING"
    ((FAILED++))
  fi
done

# Test 2: Daily folder exists and has content
echo ""
echo "📅 Testing daily logs..."
if [[ -d "$HOME/Obsidian/Penelopi/Daily" ]]; then
  DAILY_COUNT=$(ls -1 "$HOME/Obsidian/Penelopi/Daily"/*.md 2>/dev/null | wc -l)
  if [[ $DAILY_COUNT -gt 0 ]]; then
    echo "  ✅ Daily folder exists with $DAILY_COUNT entries"
    ((PASSED++))
  else
    echo "  ⚠️  Daily folder exists but is empty"
    ((PASSED++))  # Not a failure, just empty
  fi
else
  echo "  ❌ Daily folder missing"
  ((FAILED++))
fi

# Test 3: Today's file is writable
echo ""
echo "📝 Testing write access..."
TODAY_FILE="$HOME/Obsidian/Penelopi/Daily/$(date +%Y-%m-%d).md"
if echo "# Test entry $(date)" >> "$TODAY_FILE" 2>/dev/null; then
  echo "  ✅ Can write to daily log"
  ((PASSED++))
else
  echo "  ❌ Cannot write to daily log"
  ((FAILED++))
fi

# Test 4: Workspace redirects are in place
echo ""
echo "🔄 Testing workspace redirects..."
if grep -q "Obsidian/Penelopi" "$HOME/.openclaw/workspace/AGENTS.md" 2>/dev/null; then
  echo "  ✅ AGENTS.md redirects to Obsidian"
  ((PASSED++))
else
  echo "  ❌ AGENTS.md doesn't redirect"
  ((FAILED++))
fi

# Test 5: File content is readable
echo ""
echo "📖 Testing content readability..."
if grep -q "Penelopi" "$HOME/Obsidian/Penelopi/WHO-I-AM.md" 2>/dev/null; then
  echo "  ✅ WHO-I-AM.md has content"
  ((PASSED++))
else
  echo "  ❌ WHO-I-AM.md unreadable or empty"
  ((FAILED++))
fi

if grep -q "Okeito" "$HOME/Obsidian/Penelopi/WHO-YOU-ARE.md" 2>/dev/null; then
  echo "  ✅ WHO-YOU-ARE.md has content"
  ((PASSED++))
else
  echo "  ❌ WHO-YOU-ARE.md unreadable or empty"
  ((FAILED++))
fi

# Summary
echo ""
echo "======================================"
TOTAL=$((PASSED + FAILED))
echo "Results: $PASSED passed, $FAILED failed out of $TOTAL tests"

if [[ $FAILED -eq 0 ]]; then
  echo "🎉 All tests passed! Memory system is operational."
  exit 0
else
  echo "⚠️  Some tests failed. Check output above."
  exit 1
fi
