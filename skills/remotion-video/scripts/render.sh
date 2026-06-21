#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <composition-id> [output-name.mp4]"
  exit 1
fi

COMPOSITION_ID="$1"
OUTPUT_NAME="${2:-${COMPOSITION_ID}.mp4}"

STUDIO_DIR="/Users/oktos/.openclaw/workspace/remotion-studio"
OUTPUT_DIR="${STUDIO_DIR}/output"
mkdir -p "$OUTPUT_DIR"

cd "$STUDIO_DIR"

# Render with settings that maximize Telegram compatibility
npx remotion render "$COMPOSITION_ID" "${OUTPUT_DIR}/${OUTPUT_NAME}" \
  --codec=h264 \
  --crf=22 \
  --pixel-format=yuv420p \
  --audio-codec=aac \
  --concurrency=1

echo "Rendered: ${OUTPUT_DIR}/${OUTPUT_NAME}"

# Auto-fix for Telegram compatibility
TELEGRAM_NAME="${OUTPUT_NAME%.mp4}-telegram.mp4"
echo "🔧 Ensuring Telegram compatibility..."

# Check if pixel format is correct
PIX_FMT=$(ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt -of default=noprint_wrappers=1:nokey=1 "${OUTPUT_DIR}/${OUTPUT_NAME}" 2>/dev/null || echo "unknown")

if [[ "$PIX_FMT" != "yuv420p" ]]; then
  echo "   Detected $PIX_FMT — converting to yuv420p..."
  ffmpeg -y -i "${OUTPUT_DIR}/${OUTPUT_NAME}" \
    -c:v libx264 \
    -profile:v baseline \
    -level 3.0 \
    -pix_fmt yuv420p \
    -crf 23 \
    -preset fast \
    -movflags +faststart \
    -c:a aac \
    -b:a 128k \
    "${OUTPUT_DIR}/${TELEGRAM_NAME}" 2>/dev/null
  echo "✅ Telegram-ready: ${OUTPUT_DIR}/${TELEGRAM_NAME}"
else
  # Already yuv420p, just ensure faststart and copy
  ffmpeg -y -i "${OUTPUT_DIR}/${OUTPUT_NAME}" \
    -c:v copy \
    -c:a copy \
    -movflags +faststart \
    "${OUTPUT_DIR}/${TELEGRAM_NAME}" 2>/dev/null
  echo "✅ Already compatible: ${OUTPUT_DIR}/${TELEGRAM_NAME}"
fi

echo "Done!"
echo "  Raw: ${OUTPUT_DIR}/${OUTPUT_NAME}"
echo "  Telegram: ${OUTPUT_DIR}/${TELEGRAM_NAME}"
