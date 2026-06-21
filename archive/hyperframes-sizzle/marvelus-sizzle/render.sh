#!/bin/bash
# Render the HyperFrames sizzle video
# Usage: ./render.sh [output_filename]

OUTPUT="${1:-marvelus-sizzle.mp4}"
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🎬 Rendering HyperFrames sizzle video..."
echo "   Source: $DIR/index.html"
echo "   Output: $DIR/$OUTPUT"

# Check if hyperframes CLI is available
if ! command -v npx &> /dev/null; then
    echo "❌ npx not found. Install Node.js first."
    exit 1
fi

# Install hyperframes if needed
echo "📦 Checking HyperFrames CLI..."
npx hyperframes --version &> /dev/null || npx hyperframes@latest --version &> /dev/null

cd "$DIR"

# Render the video
echo "🔨 Rendering..."
npx hyperframes render --input index.html --output "$OUTPUT" --non-interactive

if [ $? -eq 0 ]; then
    echo "✅ Render complete: $DIR/$OUTPUT"
    ls -lh "$DIR/$OUTPUT"
else
    echo "❌ Render failed. Check HyperFrames is installed."
    echo "   Try: npm install -g hyperframes"
    exit 1
fi
