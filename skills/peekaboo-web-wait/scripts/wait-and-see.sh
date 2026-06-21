#!/bin/bash
# Wait-and-see: Basic wait then capture for web pages
# Usage: wait-and-see.sh "App Name" [sleep_ms]

APP="${1:-Brave Browser}"
SLEEP_MS="${2:-3000}"

OUTPUT_DIR="${TMPDIR:-/tmp}/peekaboo-wait"
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%s)
OUTPUT="$OUTPUT_DIR/see-${TIMESTAMP}.png"

echo "⏳ Waiting ${SLEEP_MS}ms for page to load..."
peekaboo sleep --duration "$SLEEP_MS"

echo "📸 Capturing annotated screenshot..."
peekaboo see --app "$APP" --annotate --path "$OUTPUT"

echo "✅ Saved to: $OUTPUT"
