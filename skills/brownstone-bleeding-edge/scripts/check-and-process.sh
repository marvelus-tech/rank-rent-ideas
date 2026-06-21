#!/bin/bash
# Main orchestration script for Brownstone Bleeding Edge monitor
# Workflow: fetch new articles, generate TTS, publish audio to GitHub Pages, update state.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$SCRIPT_DIR/../state"
WORK_DIR="$SCRIPT_DIR/../work"
STATE_FILE="$STATE_DIR/processed-articles.json"

# Check for virtual environment, fall back to system Python
if [ -f "$SCRIPT_DIR/../.venv/bin/activate" ]; then
  source "$SCRIPT_DIR/../.venv/bin/activate"
fi

mkdir -p "$STATE_DIR" "$WORK_DIR"

if [ ! -f "$STATE_FILE" ]; then
  echo '{"articles": []}' > "$STATE_FILE"
fi

echo "=== Brownstone Bleeding Edge Monitor ==="
echo "Fetching articles from brownstoneresearch.com..."

if ! python3 "$SCRIPT_DIR/fetch-articles.py" > "$WORK_DIR/all-articles.json"; then
  echo "Direct fetch failed (likely 403)."
  exit 1
fi

ARTICLE_COUNT=$(jq '. | length' "$WORK_DIR/all-articles.json")
echo "Found $ARTICLE_COUNT articles on the page"

python3 "$SCRIPT_DIR/state-manager.py" new "$WORK_DIR/all-articles.json" > "$WORK_DIR/new-articles.json"
NEW_COUNT=$(jq '. | length' "$WORK_DIR/new-articles.json")
echo "New articles to process: $NEW_COUNT"

if [ "$NEW_COUNT" -eq 0 ]; then
  echo "No new articles. Exiting."
  exit 0
fi

PUBLISHED_COUNT=0
FAILED_COUNT=0

while IFS= read -r article; do
  url=$(echo "$article" | jq -r '.url')
  slug=$(echo "$article" | jq -r '.slug')
  title=$(echo "$article" | jq -r '.title')

  echo ""
  echo "Processing: $title"
  echo "URL: $url"

  echo "  Fetching content..."
  if ! python3 "$SCRIPT_DIR/fetch-article-content.py" "$url" > "$WORK_DIR/article-${slug}.json"; then
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

  cat > "$WORK_DIR/tts-text-${slug}.txt" <<EOF
${FULL_TITLE}

${ARTICLE_DATE}

${CONTENT}
EOF

  echo "  Generating TTS audio..."
  AUDIO_FILE="$WORK_DIR/audio-${slug}.mp3"

  if ! python3 "$SCRIPT_DIR/generate-tts.py" "$WORK_DIR/tts-text-${slug}.txt" "$AUDIO_FILE"; then
    echo "  ✗ Failed to generate TTS"
    FAILED_COUNT=$((FAILED_COUNT + 1))
    continue
  fi

  echo "  Audio generated: $AUDIO_FILE"
  echo "  Publishing to GitHub Pages..."

  if "$SCRIPT_DIR/publish-to-github.sh" "$AUDIO_FILE" "$FULL_TITLE" "$ARTICLE_DATE" "$slug" "$url"; then
    python3 "$SCRIPT_DIR/state-manager.py" add "$WORK_DIR/article-${slug}.json" >/dev/null
    echo "  ✓ Published + marked as processed"
    PUBLISHED_COUNT=$((PUBLISHED_COUNT + 1))
  else
    echo "  ✗ Failed to publish"
    FAILED_COUNT=$((FAILED_COUNT + 1))
  fi

  sleep 2
done < <(jq -c '.[]' "$WORK_DIR/new-articles.json")

echo "=== Done ==="
echo "Published: $PUBLISHED_COUNT | Failed: $FAILED_COUNT"
