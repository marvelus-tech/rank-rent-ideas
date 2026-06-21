#!/usr/bin/env bash
# Telegram Video Compatibility Fixer
# Run this after ANY render to guarantee Telegram playback

set -euo pipefail

VIDEO="${1:?Usage: $0 <video.mp4> [output.mp4]}"
OUTPUT="${2:-${VIDEO%.mp4}-telegram.mp4}"

echo "🔍 Checking: $VIDEO"

# Detect pixel format
PIX_FMT=$(ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt -of default=noprint_wrappers=1:nokey=1 "$VIDEO" 2>/dev/null || echo "unknown")

echo "   Pixel format: $PIX_FMT"

# If it's already yuv420p and baseline, just copy
if [[ "$PIX_FMT" == "yuv420p" ]]; then
    PROFILE=$(ffprobe -v error -select_streams v:0 -show_entries stream=profile -of default=noprint_wrappers=1:nokey=1 "$VIDEO" 2>/dev/null || echo "unknown")
    if [[ "$PROFILE" == "Constrained Baseline" ]] || [[ "$PROFILE" == "Baseline" ]]; then
        echo "✅ Already Telegram-compatible, copying..."
        cp "$VIDEO" "$OUTPUT"
        echo "✓ Output: $OUTPUT"
        exit 0
    fi
fi

# Re-encode with Telegram-safe settings
# CRITICAL: yuvj420p -> yuv420p requires explicit color range conversion
echo "🔄 Re-encoding for Telegram compatibility..."

ffmpeg -y -i "$VIDEO" \
    -c:v libx264 \
    -profile:v baseline \
    -level 3.0 \
    -pix_fmt yuv420p \
    -color_range tv \
    -colorspace bt709 \
    -color_trc bt709 \
    -color_primaries bt709 \
    -crf 23 \
    -preset fast \
    -movflags +faststart \
    -c:a aac \
    -b:a 128k \
    -ar 48000 \
    "$OUTPUT" 2>/dev/null

# Validate output
if [ -f "$OUTPUT" ]; then
    OUT_PIX=$(ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt -of default=noprint_wrappers=1:nokey=1 "$OUTPUT" 2>/dev/null)
    OUT_SIZE=$(du -h "$OUTPUT" | cut -f1)
    echo "✅ Fixed! Pixel format: $OUT_PIX | Size: $OUT_SIZE"
    echo "✓ Output: $OUTPUT"
else
    echo "❌ Failed to create output"
    exit 1
fi
