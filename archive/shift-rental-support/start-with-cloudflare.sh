#!/usr/bin/env bash
# Start SHIFT Rental Support Server with Cloudflare Tunnel (quick public URL)

set -euo pipefail
cd "$(dirname "$0")"

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Check if port 3000 is already in use
if lsof -nP -iTCP:3000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "ERROR: Port 3000 is already in use."
  echo "  See what holds it:  lsof -nP -iTCP:3000 -sTCP:LISTEN"
  echo "  Stop it (example):  kill $(lsof -nP -t -iTCP:3000 -sTCP:LISTEN)"
  exit 1
fi

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "⚠️  cloudflared not found. Install it:"
    echo "   brew install cloudflare/cloudflare/cloudflared"
    echo ""
    echo "Starting server locally only (no public URL)..."
    echo "📡 Local: http://localhost:3000"
    echo "💬 Support chat: http://localhost:3000/support"
    npm start
    exit 0
fi

# Start the Node.js server in the background
echo "🚗 Starting SHIFT Rental Support Server..."
npm start &
SERVER_PID=$!

# Wait for server to be ready
sleep 2

# Start Cloudflare Tunnel
echo "🌐 Starting Cloudflare Tunnel (creating public URL)..."
echo ""
cloudflared tunnel --url http://localhost:3000 &
CF_PID=$!

# Trap to kill both processes on exit
trap 'kill "$SERVER_PID" "$CF_PID" 2>/dev/null' EXIT INT TERM

echo ""
echo "✅ SHIFT Rental Support is running!"
echo ""
echo "📡 Local:     http://localhost:3000"
echo "💬 Support:   http://localhost:3000/support"
echo ""
echo "🌍 Public URL will appear above (look for 'https://*.trycloudflare.com')"
echo ""
echo "Press Ctrl+C to stop both server and tunnel"
echo ""

# Keep script running
wait
