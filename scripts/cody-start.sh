#!/bin/bash
# Cody Quick-Start Script
# Clones a template, swaps content, builds production-ready output

set -e

TEMPLATE=$1
TOPIC=$2
OUTPUT_DIR=$3

if [ -z "$TEMPLATE" ] || [ -z "$TOPIC" ]; then
    echo "Usage: cody-start <template> <topic> [output-dir]"
    echo ""
    echo "Templates:"
    echo "  corporate-luxury    Navy + Gold, Playfair + Jakarta"
    echo "  tech-modern         Purple + Cyan, Clash + General"
    echo "  organic-natural     Forest + Sand, Cormorant + Instrument"
    echo "  brutalist           Black + Neon, monospace"
    echo "  hyperframes-video   HTML video composition base"
    echo "  remotion-sizzle     React video sizzle reel"
    echo ""
    echo "Example:"
    echo "  cody-start corporate-luxury \"AI Automation\""
    exit 1
fi

# Default output dir
if [ -z "$OUTPUT_DIR" ]; then
    OUTPUT_DIR="$HOME/.openclaw/workspace/presentations/$(date +%Y-%m-%d)-$(echo $TOPIC | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"
fi

TEMPLATE_DIR="$HOME/.openclaw/workspace/templates/$TEMPLATE"

if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "❌ Template '$TEMPLATE' not found"
    exit 1
fi

echo "🎨 Cody: Cloning $TEMPLATE template..."
mkdir -p "$OUTPUT_DIR"
cp -r "$TEMPLATE_DIR"/* "$OUTPUT_DIR/"

# Update package.json name
cd "$OUTPUT_DIR"
if [ -f "package.json" ]; then
    sed -i '' "s/\"name\": \".*\"/\"name\": \"$(echo $TOPIC | tr ' ' '-' | tr '[:upper:]' '[:lower:]')\"/" package.json 2>/dev/null || true
fi

# Update config/site.ts if it exists
if [ -f "src/config/site.ts" ]; then
    echo "📝 Updating content in config/site.ts..."
    # Title
    sed -i '' "s/AI Work Output/$TOPIC/" src/config/site.ts 2>/dev/null || true
    # Tagline
    sed -i '' "s/The Future of Knowledge Work/$TOPIC/" src/config/site.ts 2>/dev/null || true
fi

echo "✅ Cody ready at: $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "  cd $OUTPUT_DIR"
echo "  npm install"
echo "  npm run dev"
echo ""
echo "Edit src/config/site.ts to customize content"
