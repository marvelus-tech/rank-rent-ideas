#!/bin/bash
# Standalone Brownstone Bleeding Edge monitor — no AI needed
# This script runs directly from cron and handles everything:
# fetch, TTS, publish to GitHub Pages, notify Telegram

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$SCRIPT_DIR/../state"
WORK_DIR="$SCRIPT_DIR/../work"
LOG_DIR="$SCRIPT_DIR/../logs"
STATE_FILE="$STATE_DIR/processed-articles.json"
ENV_FILE="$SCRIPT_DIR/../.env"

# Load env vars
if [ -f "$ENV_FILE" ]; then
  export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

mkdir -p "$STATE_DIR" "$WORK_DIR" "$LOG_DIR"

LOG_FILE="$LOG_DIR/run-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

if [ ! -f "$STATE_FILE" ]; then
  echo '{"articles": []}' > "$STATE_FILE"
fi

echo "=== Brownstone Bleeding Edge Monitor ==="
echo "Started: $(date)"
echo "Fetching articles..."

# Check for virtual environment
if [ -f "$SCRIPT_DIR/../.venv/bin/activate" ]; then
  source "$SCRIPT_DIR/../.venv/bin/activate"
fi

# Fetch articles
if ! python3 "$SCRIPT_DIR/fetch-articles.py" > "$WORK_DIR/all-articles.json" 2>&1; then
  echo "ERROR: Failed to fetch articles"
  # Try to notify about failure
  if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      -d "text=⚠️ Brownstone monitor: Failed to fetch articles" > /dev/null || true
  fi
  exit 1
fi

ARTICLE_COUNT=$(jq '. | length' "$WORK_DIR/all-articles.json")
echo "Found $ARTICLE_COUNT articles on the page"

# Check for new articles
python3 "$SCRIPT_DIR/state-manager.py" new "$WORK_DIR/all-articles.json" > "$WORK_DIR/new-articles.json"
NEW_COUNT=$(jq '. | length' "$WORK_DIR/new-articles.json")
echo "New articles to process: $NEW_COUNT"

if [ "$NEW_COUNT" -eq 0 ]; then
  echo "No new articles. Exiting."
  exit 0
fi

PUBLISHED_COUNT=0
FAILED_COUNT=0
NOTIFICATIONS=""

while IFS= read -r article; do
  url=$(echo "$article" | jq -r '.url')
  slug=$(echo "$article" | jq -r '.slug')
  title=$(echo "$article" | jq -r '.title')

  echo ""
  echo "Processing: $title"
  echo "URL: $url"

  # Fetch content
  echo "  Fetching content..."
  if ! python3 "$SCRIPT_DIR/fetch-article-content.py" "$url" > "$WORK_DIR/article-${slug}.json" 2>&1; then
    echo "  ✗ Failed to fetch article content"
    FAILED_COUNT=$((FAILED_COUNT + 1))
    continue
  fi

  CONTENT=$(jq -r '.content' "$WORK_DIR/article-${slug}.json")
  if [ -z "$CONTENT" ] || [ "$CONTENT" = "null" ]; then
    echo "  ✗ No content found. Skipping."
    FAILED_COUNT=$((FAILED_COUNT + 1))
    continue
  fi

  WORD_COUNT=$(jq -r '.word_count' "$WORK_DIR/article-${slug}.json")
  echo "  Content: $WORD_COUNT words"

  FULL_TITLE=$(jq -r '.title' "$WORK_DIR/article-${slug}.json")
  ARTICLE_DATE=$(jq -r '.date' "$WORK_DIR/article-${slug}.json")

  # Prepare TTS text
  cat > "$WORK_DIR/tts-text-${slug}.txt" <<EOF
${FULL_TITLE}

${ARTICLE_DATE}

${CONTENT}
EOF

  # Generate TTS
  echo "  Generating TTS audio..."
  AUDIO_FILE="$WORK_DIR/audio-${slug}.mp3"

  if ! python3 "$SCRIPT_DIR/generate-tts.py" "$WORK_DIR/tts-text-${slug}.txt" "$AUDIO_FILE" > /dev/null 2>&1; then
    echo "  ✗ Failed to generate TTS"
    FAILED_COUNT=$((FAILED_COUNT + 1))
    continue
  fi

  echo "  Audio generated: $AUDIO_FILE"
  echo "  Publishing to GitHub Pages..."

  # Publish
  if "$SCRIPT_DIR/publish-to-github.sh" "$AUDIO_FILE" "$FULL_TITLE" "$ARTICLE_DATE" "$slug" "$url" > /dev/null 2>&1; then
    python3 "$SCRIPT_DIR/state-manager.py" add "$WORK_DIR/article-${slug}.json" > /dev/null
    echo "  ✓ Published + marked as processed"
    PUBLISHED_COUNT=$((PUBLISHED_COUNT + 1))

    # Build notification
    NOTIFICATIONS="${NOTIFICATIONS}🎧 ${FULL_TITLE}\n📅 ${ARTICLE_DATE}\n🔗 ${url}\n\n"
  else
    echo "  ✗ Failed to publish"
    FAILED_COUNT=$((FAILED_COUNT + 1))
  fi

  sleep 2
done < <(jq -c '.[]' "$WORK_DIR/new-articles.json")

echo "=== Done ==="
echo "Published: $PUBLISHED_COUNT | Failed: $FAILED_COUNT"
echo "Finished: $(date)"

# Send Telegram notification if we published anything
if [ "$PUBLISHED_COUNT" -gt 0 ] && [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
  MESSAGE="📰 Brownstone Audio Update\n\n${NOTIFICATIONS}🌐 https://marvelus-tech.github.io/brownstone-audio/"

  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${MESSAGE}" \
    -d "parse_mode=HTML" > /dev/null || true
fi

# Cleanup old work files (keep last 7 days)
find "$WORK_DIR" -type f -mtime +7 -delete 2>/dev/null || true
find "$LOG_DIR" -type f -mtime +30 -delete 2>/dev/null || true

exit 0
