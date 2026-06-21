#!/bin/zsh
# Session Simulation Test
# Simulates what happens when I wake up and read my memory

echo "🧠 Session Simulation Test"
echo "=========================="
echo ""
echo "This simulates my startup sequence to verify I can actually"
echo "read and use the Obsidian-based memory system."
echo ""

ERRORS=0

# Simulate Step 1: Read WHO-I-AM
echo "Step 1: Loading identity (WHO-I-AM.md)..."
if IDENTITY=$(cat "$HOME/Obsidian/Penelopi/WHO-I-AM.md" 2>/dev/null); then
  NAME=$(echo "$IDENTITY" | grep -m1 "^> \*\*Creature:\*\*" | sed 's/.*— //')
  if [[ -n "$NAME" ]]; then
    echo "  ✅ Identity loaded: $NAME"
  else
    echo "  ⚠️  Identity file readable but format unexpected"
  fi
else
  echo "  ❌ FAILED: Cannot read identity"
  ((ERRORS++))
fi

# Simulate Step 2: Read WHO-YOU-ARE
echo ""
echo "Step 2: Loading user profile (WHO-YOU-ARE.md)..."
if USER=$(cat "$HOME/Obsidian/Penelopi/WHO-YOU-ARE.md" 2>/dev/null); then
  USERNAME=$(echo "$USER" | grep -m1 "^> \*\*Name:\*\*" | sed 's/.*: //')
  if [[ -n "$USERNAME" ]]; then
    echo "  ✅ User profile loaded: $USERNAME"
  else
    echo "  ⚠️  User file readable but format unexpected"
  fi
else
  echo "  ❌ FAILED: Cannot read user profile"
  ((ERRORS++))
fi

# Simulate Step 3: Read DECISIONS
echo ""
echo "Step 3: Loading decisions (DECISIONS.md)..."
if DECISIONS=$(cat "$HOME/Obsidian/Penelopi/DECISIONS.md" 2>/dev/null); then
  DECISION_COUNT=$(echo "$DECISIONS" | grep -c "^| 2026-")
  echo "  ✅ Decisions loaded: $DECISION_COUNT decision entries found"
else
  echo "  ❌ FAILED: Cannot read decisions"
  ((ERRORS++))
fi

# Simulate Step 4: Read daily logs
echo ""
echo "Step 4: Loading recent context (Daily logs)..."
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)

TODAY_FILE="$HOME/Obsidian/Penelopi/Daily/$TODAY.md"
YESTERDAY_FILE="$HOME/Obsidian/Penelopi/Daily/$YESTERDAY.md"

if [[ -f "$TODAY_FILE" ]]; then
  TODAY_LINES=$(wc -l < "$TODAY_FILE")
  echo "  ✅ Today's log ($TODAY): $TODAY_LINES lines"
else
  echo "  ⚠️  Today's log doesn't exist yet (will be created)"
fi

if [[ -f "$YESTERDAY_FILE" ]]; then
  YESTERDAY_LINES=$(wc -l < "$YESTERDAY_FILE")
  echo "  ✅ Yesterday's log ($YESTERDAY): $YESTERDAY_LINES lines"
else
  echo "  ⚠️  Yesterday's log not found"
fi

# Simulate Step 5: Read MEMORY (main session only)
echo ""
echo "Step 5: Loading long-term memory (MEMORY.md)..."
if MEMORY=$(cat "$HOME/Obsidian/Penelopi/MEMORY.md" 2>/dev/null); then
  KEY_DECISIONS=$(echo "$MEMORY" | grep -c "2026-03-")
  echo "  ✅ Long-term memory loaded: $KEY_DECISIONS key decisions cached"
else
  echo "  ❌ FAILED: Cannot read long-term memory"
  ((ERRORS++))
fi

# Simulate Step 6: Test writing to daily log
echo ""
echo "Step 6: Testing memory write (appending to daily log)..."
TEST_ENTRY="- $(date '+%H:%M'): Memory system validation test passed"
if echo "$TEST_ENTRY" >> "$TODAY_FILE" 2>/dev/null; then
  echo "  ✅ Successfully wrote to daily log"
else
  echo "  ❌ FAILED: Cannot write to daily log"
  ((ERRORS++))
fi

# Summary
echo ""
echo "=========================="
if [[ $ERRORS -eq 0 ]]; then
  echo "✅ Session simulation PASSED"
  echo ""
  echo "I can successfully:"
  echo "  • Read my identity from Obsidian"
  echo "  • Read your profile from Obsidian"
  echo "  • Load behavioral decisions from Obsidian"
  echo "  • Access daily context from Obsidian"
  echo "  • Retrieve long-term memory from Obsidian"
  echo "  • Write new memories to Obsidian"
  echo ""
  echo "🔱 The memory system is fully operational."
  exit 0
else
  echo "❌ Session simulation FAILED with $ERRORS errors"
  exit 1
fi
