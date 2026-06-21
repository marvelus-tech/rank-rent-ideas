#!/bin/bash
/**
 * find-builders-peekaboo.sh — Automate Zillow browsing with Peekaboo
 * 
 * This script uses Peekaboo to:
 * 1. Open Chrome to Zillow new construction search
 * 2. Capture screenshots of listings
 * 3. Extract ZPIDs from the page
 * 4. Save them for processing
 * 
 * Usage:
 *   ./find-builders-peekaboo.sh "Austin, TX"
 *   ./find-builders-peekaboo.sh "Austin, TX" --pages 3
 */

LOCATION="${1:-Austin, TX}"
PAGES="${2:-1}"
OUTPUT="zpids-peekaboo-$(echo "$LOCATION" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g').txt"

echo "🏗️  Zillow Builder Finder via Peekaboo"
echo "   Location: $LOCATION"
echo "   Pages: $PAGES"
echo ""

# Check if Peekaboo is available
if ! command -v peekaboo &> /dev/null; then
    echo "❌ Peekaboo not found. Install with:"
    echo "   brew install steipete/tap/peekaboo"
    exit 1
fi

# URL encode location
ENCODED_LOCATION=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$LOCATION'))" 2>/dev/null || echo "$LOCATION")

# Build Zillow URL
ZILLOW_URL="https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22${ENCODED_LOCATION}%22%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Atrue%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%7D%7D"

echo "🚀 Opening Chrome..."

# Launch Chrome
open -a "Google Chrome" "$ZILLOW_URL"

# Wait for page to load
sleep 8

echo "📸 Capturing screen..."
peekaboo image --mode screen --path /tmp/zillow-page-1.png

echo ""
echo "✅ Browser opened to Zillow new construction search"
echo ""
echo "📋 Manual steps needed:"
echo "   1. Browse the listings in Chrome"
echo "   2. Click on listings to see details"
echo "   3. Note ZPIDs from URLs (number before _zpid)"
echo "   4. Enter ZPIDs below (one per line, 'done' to finish)"
echo ""

# Collect ZPIDs manually
ZPIDS=()
echo "Enter ZPIDs:"
while true; do
    read -p "ZPID (or 'done'): " ZPID
    if [ "$ZPID" = "done" ]; then
        break
    fi
    if [[ "$ZPID" =~ ^[0-9]+$ ]]; then
        ZPIDS+=("$ZPID")
        echo "   ✓ Added: $ZPID (total: ${#ZPIDS[@]})"
    else
        echo "   ✗ Invalid ZPID, try again"
    fi
done

# Save to file
if [ ${#ZPIDS[@]} -gt 0 ]; then
    printf "%s\n" "${ZPIDS[@]}" > "$OUTPUT"
    echo ""
    echo "✅ Saved ${#ZPIDS[@]} ZPIDs to: $OUTPUT"
    echo ""
    echo "Next steps:"
    echo "   node scripts/find-builders-zpids.js $OUTPUT"
    echo "   node scripts/export-csv.js builders-*.json --output leads.csv"
else
    echo ""
    echo "⚠️  No ZPIDs collected"
fi
