#!/bin/bash
#
# peekaboo-smart-capture.sh
# Smart wrapper for peekaboo that waits for page content to load
# before capturing screenshots. Solves the race condition where
# screenshots happen before DOM renders.
#
# Usage: peekaboo-smart-capture.sh [OPTIONS] <URL>
#
set -euo pipefail

# Default configuration
BROWSER="Brave Browser"
TIMEOUT=10000          # Max wait time in ms
POLL_INTERVAL=500      # Check every 500ms
STABILIZE_MS=1500      # Consider stable after 1.5s of no changes
INITIAL_WAIT=1000      # Initial delay before polling starts
OUTPUT="/tmp/peekaboo-smart-capture.png"
TEMP_DIR=$(mktemp -d)

# Cleanup on exit
trap "rm -rf $TEMP_DIR" EXIT

show_help() {
    cat << EOF
Peekaboo Smart Capture - Waits for page to load before screenshot

Usage: $0 [OPTIONS] <URL>

Options:
  -b, --browser <name>     Browser to use (default: "Brave Browser")
  -t, --timeout <ms>       Max wait time in ms (default: 10000)
  -p, --poll <ms>          Polling interval in ms (default: 500)
  -s, --stabilize <ms>     Stability threshold in ms (default: 1500)
  -i, --initial <ms>       Initial delay before polling (default: 1000)
  -o, --output <path>      Output file path (default: /tmp/peekaboo-smart-capture.png)
  -h, --help               Show this help

Examples:
  $0 https://example.com
  $0 -t 15000 -o ~/screenshot.png https://slow-site.com
  $0 -b Safari https://apple.com

How it works:
  1. Launches browser and navigates to URL
  2. Waits initial delay for first paint
  3. Polls every 500ms, capturing screenshots
  4. Compares consecutive screenshots (hash-based)
  5. When 3+ consecutive captures are identical, page is "stable"
  6. Saves the stable capture (or last capture on timeout)
EOF
}

# Parse arguments
URL=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--browser)
            BROWSER="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -p|--poll)
            POLL_INTERVAL="$2"
            shift 2
            ;;
        -s|--stabilize)
            STABILIZE_MS="$2"
            shift 2
            ;;
        -i|--initial)
            INITIAL_WAIT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            URL="$1"
            shift
            ;;
    esac
done

# Validate URL
if [[ -z "$URL" ]]; then
    echo "Error: URL is required"
    show_help
    exit 1
fi

# Validate browser
if ! command -v "$BROWSER" &> /dev/null; then
    # Try just checking if peekaboo knows about it
    if ! peekaboo list apps --json 2>/dev/null | grep -q "$BROWSER"; then
        echo "Warning: Browser '$BROWSER' may not be installed, proceeding anyway..."
    fi
fi

echo "🔍 Smart Capture: $URL"
echo "   Browser: $BROWSER"
echo "   Timeout: ${TIMEOUT}ms | Poll: ${POLL_INTERVAL}ms | Stabilize: ${STABILIZE_MS}ms"
echo ""

# Step 1: Launch browser
echo "📱 Launching browser..."
peekaboo app launch "$BROWSER" --open "$URL" 2>/dev/null || {
    echo "Error: Failed to launch browser"
    exit 1
}

# Give initial paint a moment
sleep 0.5

# Step 2: Wait for initial load (basic delay)
echo "⏳ Initial wait (${INITIAL_WAIT}ms)..."
sleep $(awk "BEGIN {print $INITIAL_WAIT/1000}")

# Step 3: Polling loop - capture until stable or timeout
echo "🔍 Polling for page stability..."

PREV_HASH=""
STABLE_COUNT=0
STABLE_NEEDED=$((STABILIZE_MS / POLL_INTERVAL))
ITERATIONS=$((TIMEOUT / POLL_INTERVAL))
BEST_CAPTURE=""

for ((i=0; i<ITERATIONS; i++)); do
    sleep $(awk "BEGIN {print $POLL_INTERVAL/1000}")
    
    # Capture current state
    TEMP_FILE="$TEMP_DIR/capture_$i.png"
    
    if ! peekaboo image --mode screen --path "$TEMP_FILE" 2>/dev/null; then
        echo "   Warning: Capture $i failed, retrying..."
        continue
    fi
    
    # Keep track of best (latest) capture
    BEST_CAPTURE="$TEMP_FILE"
    
    # Calculate simple hash of image
    if [[ -f "$TEMP_FILE" ]]; then
        # Use file size + md5 of first 4KB as content hash
        FILE_SIZE=$(stat -f%z "$TEMP_FILE" 2>/dev/null || stat -c%s "$TEMP_FILE" 2>/dev/null)
        
        if [[ $FILE_SIZE -lt 1000 ]]; then
            echo "   Frame $i: file too small (${FILE_SIZE}b), still loading..."
            PREV_HASH=""
            STABLE_COUNT=0
            continue
        fi
        
        CURRENT_HASH="${FILE_SIZE}_$(head -c 4096 "$TEMP_FILE" | md5 -q 2>/dev/null || head -c 4096 "$TEMP_FILE" | md5sum | cut -d' ' -f1)"
        
        if [[ "$CURRENT_HASH" == "$PREV_HASH" ]]; then
            ((STABLE_COUNT++))
            
            if [[ $((i % 2)) -eq 0 ]]; then
                echo "   Frame $i: stable ($STABLE_COUNT/$STABLE_NEEDED)"
            fi
            
            if [[ $STABLE_COUNT -ge $STABLE_NEEDED ]]; then
                TOTAL_MS=$((INITIAL_WAIT + (i * POLL_INTERVAL)))
                echo ""
                echo "✅ Page stabilized after ${TOTAL_MS}ms"
                cp "$TEMP_FILE" "$OUTPUT"
                break
            fi
        else
            if [[ $STABLE_COUNT -gt 0 ]]; then
                echo "   Frame $i: content changed, reset stability counter"
            else
                echo "   Frame $i: content loading..."
            fi
            STABLE_COUNT=0
        fi
        
        PREV_HASH="$CURRENT_HASH"
    fi
done

# If we never got stability, use the best (last) capture
if [[ ! -f "$OUTPUT" ]]; then
    echo ""
    echo "⚠️ Timeout reached, using last capture"
    if [[ -n "$BEST_CAPTURE" && -f "$BEST_CAPTURE" ]]; then
        cp "$BEST_CAPTURE" "$OUTPUT"
    else
        echo "❌ No captures found"
        exit 1
    fi
fi

# Final verification
FILE_SIZE=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null)
echo ""
echo "✅ Capture saved: $OUTPUT"
echo "   Size: $(du -h "$OUTPUT" 2>/dev/null | cut -f1 || echo "${FILE_SIZE}b")"

if [[ $FILE_SIZE -lt 10000 ]]; then
    echo "⚠️  Warning: Capture seems small - page may still be loading or blank"
    exit 2
fi

echo ""
echo "💡 Tip: If content is still missing, try:"
echo "   - Increasing --timeout (e.g., -t 20000 for 20s)"
echo "   - Checking if the site requires interaction to load"
echo "   - Using --stabilize 3000 for very slow-loading pages"
