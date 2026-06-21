#!/usr/bin/env bash
set -euo pipefail

# podcast-transcribe/scripts/transcribe.sh
# Download podcast audio from RSS feed and transcribe with Whisper

RSS_URL="${1:-}"
if [[ -z "$RSS_URL" ]]; then
    echo "Usage: $0 <rss-url> [episode-number]" >&2
    echo "  rss-url: The RSS feed URL of the podcast" >&2
    echo "  episode-number: Which episode to transcribe (1 = most recent, default: 1)" >&2
    exit 1
fi

EPISODE_NUM="${2:-1}"
WORK_DIR="${TMPDIR:-/tmp}/podcast-transcribe-$$"
mkdir -p "$WORK_DIR"

cleanup() {
    rm -rf "$WORK_DIR"
}
trap cleanup EXIT

# Check dependencies
for cmd in curl jq whisper; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "ERROR: $cmd not found. Install it first." >&2
        exit 1
    fi
done

echo "Fetching RSS feed: $RSS_URL"

# Download and parse RSS feed
RSS_XML=$(curl -s -L "$RSS_URL")
if [[ -z "$RSS_XML" ]]; then
    echo "ERROR: Failed to fetch RSS feed" >&2
    exit 1
fi

# Save RSS to temp file for parsing
echo "$RSS_XML" > "$WORK_DIR/feed.xml"

# Parse RSS to get episodes using Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is required for RSS parsing" >&2
    exit 1
fi

EPISODE_INFO=$(python3 - "$WORK_DIR/feed.xml" "$EPISODE_NUM" <<'PYEOF'
import sys
import xml.etree.ElementTree as ET
import json

rss_file = sys.argv[1]
episode_num = int(sys.argv[2])

try:
    tree = ET.parse(rss_file)
    root = tree.getroot()
    
    channel = root.find('channel') if root.tag == 'rss' else root
    
    if channel is None:
        print(json.dumps({"error": "Invalid RSS feed"}))
        sys.exit(1)
    
    title_elem = channel.find('title')
    podcast_title = title_elem.text if title_elem is not None else "Unknown Podcast"
    
    items = channel.findall('item')
    if len(items) == 0 and root.tag == 'rss':
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        items = root.findall('atom:entry', ns)
    
    total_episodes = len(items)
    
    if episode_num < 1 or episode_num > total_episodes:
        print(json.dumps({"error": f"Episode {episode_num} not found. Total episodes: {total_episodes}"}))
        sys.exit(1)
    
    item = items[episode_num - 1]
    
    episode_title = ""
    audio_url = ""
    pub_date = ""
    duration = ""
    
    title_elem = item.find('title')
    if title_elem is not None:
        episode_title = title_elem.text or ""
    
    enclosure = item.find('enclosure')
    if enclosure is not None:
        audio_url = enclosure.get('url', '')
    
    pub_date_elem = item.find('pubDate')
    if pub_date_elem is not None:
        pub_date = pub_date_elem.text or ""
    
    duration_elem = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}duration')
    if duration_elem is not None:
        duration = duration_elem.text or ""
    
    if not episode_title:
        title_elem = item.find('{http://www.w3.org/2005/Atom}title')
        if title_elem is not None:
            episode_title = title_elem.text or ""
    
    if not audio_url:
        link = item.find('{http://www.w3.org/2005/Atom}link')
        if link is not None and link.get('rel') == 'enclosure':
            audio_url = link.get('href', '')
    
    result = {
        "podcast_title": podcast_title,
        "episode_title": episode_title,
        "audio_url": audio_url,
        "pub_date": pub_date,
        "duration": duration,
        "episode_number": episode_num,
        "total_episodes": total_episodes
    }
    
    print(json.dumps(result))
    
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
PYEOF
)

# Parse the JSON result
if echo "$EPISODE_INFO" | jq -e '.error' >/dev/null 2>&1; then
    echo "ERROR: $(echo "$EPISODE_INFO" | jq -r '.error')" >&2
    exit 1
fi

PODCAST_TITLE=$(echo "$EPISODE_INFO" | jq -r '.podcast_title // "Unknown"')
EPISODE_TITLE=$(echo "$EPISODE_INFO" | jq -r '.episode_title // "Unknown"')
AUDIO_URL=$(echo "$EPISODE_INFO" | jq -r '.audio_url // empty')
PUB_DATE=$(echo "$EPISODE_INFO" | jq -r '.pub_date // "Unknown"')
DURATION=$(echo "$EPISODE_INFO" | jq -r '.duration // "Unknown"')
TOTAL_EPISODES=$(echo "$EPISODE_INFO" | jq -r '.total_episodes // 0')

echo ""
echo "========================================="
echo "Podcast: $PODCAST_TITLE"
echo "Episode: $EPISODE_TITLE"
echo "Date: $PUB_DATE"
echo "Duration: $DURATION"
echo "Episode $EPISODE_NUM of $TOTAL_EPISODES"
echo "========================================="
echo ""

if [[ -z "$AUDIO_URL" ]]; then
    echo "ERROR: Could not find audio URL for episode" >&2
    exit 1
fi

# Download the audio file
AUDIO_FILE="$WORK_DIR/episode.mp3"
echo "Downloading audio from: $AUDIO_URL"

curl -s -L -o "$AUDIO_FILE" "$AUDIO_URL" &
CURL_PID=$!

# Wait for download to start (check file size)
for i in {1..10}; do
    sleep 1
    if [[ -f "$AUDIO_FILE" ]]; then
        FILE_SIZE=$(stat -f%z "$AUDIO_FILE" 2> /dev/null || stat -c%s "$AUDIO_FILE" 2> /dev/null || echo 0)
        if [[ $FILE_SIZE -gt 0 ]]; then
            echo "Download started: $(($FILE_SIZE / 1024)) KB so far..."
            break
        fi
    fi
    echo "Waiting for download to start... ($i/10)"
done

# For testing, we can stop here after verifying download works
# Remove the exit 0 below to do full transcription
if [[ -n "${TEST_MODE:-}" ]]; then
    echo "TEST_MODE: Stopping after download verification"
    kill $CURL_PID 2>/dev/null || true
    exit 0
fi

# Wait for download to complete
wait $CURL_PID

if [[ ! -f "$AUDIO_FILE" || ! -s "$AUDIO_FILE" ]]; then
    echo "ERROR: Downloaded audio file is empty" >&2
    exit 1
fi

FILE_SIZE=$(stat -f%z "$AUDIO_FILE" 2> /dev/null || stat -c%s "$AUDIO_FILE" 2> /dev/null)
echo "Downloaded: $(($FILE_SIZE / 1024 / 1024)) MB"

# Run Whisper transcription
echo "Transcribing with Whisper (this may take a while)..."
OUTPUT_DIR="$WORK_DIR/transcript"
mkdir -p "$OUTPUT_DIR"

# Use the base model for speed, or medium for accuracy
WHISPER_MODEL="${WHISPER_MODEL:-medium}"

echo "Using Whisper model: $WHISPER_MODEL"

whisper "$AUDIO_FILE" \
    --model "$WHISPER_MODEL" \
    --language en \
    --output_format txt \
    --output_dir "$OUTPUT_DIR" \
    --verbose False

# Copy results to current directory
RESULT_DIR="./podcast-transcripts"
mkdir -p "$RESULT_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SAFE_TITLE=$(echo "$EPISODE_TITLE" | sed 's/[^a-zA-Z0-9]/_/g' | tr '[:upper:]' '[:lower:]' | cut -c1-50)
OUTPUT_PREFIX="${RESULT_DIR}/${TIMESTAMP}_${SAFE_TITLE}"

if [[ -f "$OUTPUT_DIR/$(basename "$AUDIO_FILE" .mp3).txt" ]]; then
    cp "$OUTPUT_DIR/$(basename "$AUDIO_FILE" .mp3).txt" "${OUTPUT_PREFIX}.txt"
fi
if [[ -f "$OUTPUT_DIR/$(basename "$AUDIO_FILE" .mp3).srt" ]]; then
    cp "$OUTPUT_DIR/$(basename "$AUDIO_FILE" .mp3).srt" "${OUTPUT_PREFIX}.srt"
fi
if [[ -f "$OUTPUT_DIR/$(basename "$AUDIO_FILE" .mp3).json" ]]; then
    cp "$OUTPUT_DIR/$(basename "$AUDIO_FILE" .mp3).json" "${OUTPUT_PREFIX}.json"
fi

echo ""
echo "========================================="
echo "TRANSCRIPTION COMPLETE"
echo "========================================="
echo "Files saved to: $RESULT_DIR/"
echo "  - ${TIMESTAMP}_${SAFE_TITLE}.txt"
echo ""

# Show a preview of the transcript
if [[ -f "${OUTPUT_PREFIX}.txt" ]]; then
    echo "Preview (first 500 chars):"
    head -c 500 "${OUTPUT_PREFIX}.txt"
    echo "..."
    echo ""
    echo "Full transcript: ${OUTPUT_PREFIX}.txt"
fi
