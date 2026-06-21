#!/bin/bash
# setup-remotion-sizzle.sh — One-command setup for Remotion webapp sizzle template
# Usage: ./setup-remotion-sizzle.sh [project-name]
# Or from anywhere: bash /path/to/setup-remotion-sizzle.sh my-video

set -e

PROJECT_NAME="${1:-my-sizzle-video}"
TEMPLATE_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$(pwd)/$PROJECT_NAME"

echo "🎬 Remotion Sizzle Template Setup"
echo "================================="
echo "Project name: $PROJECT_NAME"
echo "Target dir: $TARGET_DIR"
echo ""

# Step 1: Check if project already exists
if [ -d "$TARGET_DIR" ]; then
  echo "⚠️  Directory '$PROJECT_NAME' already exists."
  read -p "Delete and recreate? (y/N): " CONFIRM
  if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
    rm -rf "$TARGET_DIR"
  else
    echo "❌ Aborting. Choose a different name or delete the directory manually."
    exit 1
  fi
fi

# Step 2: Create Remotion project
echo "📦 Step 1/6: Creating Remotion project with create-video..."
npx create-video@latest "$PROJECT_NAME" --template="" --no-eslint --no-install || true

# Fallback if create-video didn't work or we need to init in existing dir
if [ ! -d "$TARGET_DIR" ]; then
  mkdir -p "$TARGET_DIR"
  cd "$TARGET_DIR"
  npm init -y
  npm install react react-dom remotion @remotion/cli @remotion/transitions
  npm install -D @types/react @types/react-dom typescript tailwindcss postcss autoprefixer
else
  cd "$TARGET_DIR"
fi

# Step 3: Install dependencies
echo "📦 Step 2/6: Installing dependencies..."
npm install react react-dom remotion @remotion/cli @remotion/transitions
npm install -D typescript @types/react @types/react-dom tailwindcss postcss autoprefixer

# Step 4: Copy template files
echo "📁 Step 3/6: Copying template files..."
if [ -d "$TEMPLATE_DIR/src" ]; then
  mkdir -p src/components src/hooks
  cp -r "$TEMPLATE_DIR/src/"* src/ 2>/dev/null || true
else
  echo "⚠️  Template source not found at $TEMPLATE_DIR/src"
  echo "   Using files from workspace..."
  WORKSPACE_TEMPLATE="$HOME/.openclaw/workspace/remotion-starter-template"
  if [ -d "$WORKSPACE_TEMPLATE/src" ]; then
    mkdir -p src/components src/hooks
    cp -r "$WORKSPACE_TEMPLATE/src/"* src/
  else
    echo "❌ Template files not found. Please ensure remotion-starter-template exists."
    exit 1
  fi
fi

# Step 5: Create Tailwind config
echo "🎨 Step 4/6: Configuring Tailwind CSS..."
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
EOF

# Step 6: Create PostCSS config
cat > postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
EOF

# Step 7: Ensure src/index.css has Tailwind directives
echo "📝 Step 5/6: Setting up CSS..."
mkdir -p src
cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF

# Step 8: Create package.json scripts if missing
echo "🔧 Step 6/6: Finalizing setup..."
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
pkg.scripts = pkg.scripts || {};
pkg.scripts.dev = pkg.scripts.dev || 'remotion studio src/index.ts';
pkg.scripts.build = pkg.scripts.build || 'remotion render src/index.ts WebAppShowcase out/video.mp4';
pkg.scripts.buildVertical = pkg.scripts.buildVertical || 'remotion render src/index.ts WebAppVertical out/video-vertical.mp4';
pkg.scripts.still = pkg.scripts.still || 'remotion still src/index.ts WebAppShowcase --frame=150 out/poster.png';
fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));
"

echo ""
echo "✅ Setup complete!"
echo "=================="
echo ""
echo "📂 Project: $TARGET_DIR"
echo ""
echo "🚀 Quick start:"
echo "   cd $PROJECT_NAME"
echo "   npm run dev"
echo ""
echo "🎬 Build video:"
echo "   npm run build         # 1920×1080 (YouTube)"
echo "   npm run buildVertical # 1080×1920 (TikTok/Reels)"
echo "   npm run still         # Export poster frame"
echo ""
echo "🎨 Customize:"
echo "   Edit src/Master.tsx to change showcased apps"
echo "   Edit src/Root.tsx to change composition presets"
echo ""
