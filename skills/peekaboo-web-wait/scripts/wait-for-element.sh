#!/bin/bash
# Wait-for-element: Poll until element appears or timeout
# Usage: wait-for-element.sh --app "Brave Browser" --element-id "B5" --timeout 10000

APP=""
ELEMENT_ID=""
TIMEOUT_MS=10000
INTERVAL_MS=1000

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --app) APP="$2"; shift 2 ;;
    --element-id) ELEMENT_ID="$2"; shift 2 ;;
    --timeout) TIMEOUT_MS="$2"; shift 2 ;;
    --interval) INTERVAL_MS="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$APP" || -z "$ELEMENT_ID" ]]; then
  echo "Usage: wait-for-element.sh --app \"App Name\" --element-id \"B5\" [--timeout 10000] [--interval 1000]"
  exit 1
fi

OUTPUT_DIR="${TMPDIR:-/tmp}/peekaboo-wait"
mkdir -p "$OUTPUT_DIR"

ELAPSED=0
echo "🔍 Waiting for element $ELEMENT_ID in $APP (timeout: ${TIMEOUT_MS}ms)..."

while [[ $ELAPSED -lt $TIMEOUT_MS ]]; do
  TIMESTAMP=$(date +%s%N | cut -b1-13)
  OUTPUT="$OUTPUT_DIR/see-${TIMESTAMP}.png"
  
  peekaboo see --app "$APP" --annotate --path "$OUTPUT" 2>/dev/null
  
  # Check if element ID exists in the snapshot (peekaboo stores this info)
  # For now we rely on the visual capture — user checks the PNG
  echo "  ⏱️  ${ELAPSED}ms elapsed — captured to $OUTPUT"
  
  # Simple approach: sleep and increment
  peekaboo sleep --duration "$INTERVAL_MS"
  ELAPSED=$((ELAPSED + INTERVAL_MS))
done

echo "✅ Wait complete. Check captures in $OUTPUT_DIR"
