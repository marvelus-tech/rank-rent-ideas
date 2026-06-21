#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8080}"
PUBLIC=0

if [[ "${1:-}" == "--public" ]]; then
  PUBLIC=1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 not found."
  echo "Install it first, then rerun ./run.sh"
  exit 1
fi

if [[ ! -f "index.html" ]]; then
  echo "Error: index.html not found."
  echo "Run this from the repo root: /Users/oktos/.openclaw/workspace/consultation-recorder"
  exit 1
fi

echo "Starting local server..."
echo "Local URL: http://localhost:${PORT}"
echo "Press Ctrl+C to stop."
echo

if [[ "${PUBLIC}" -eq 1 ]]; then
  if ! command -v ngrok >/dev/null 2>&1; then
    echo "Error: ngrok not found."
    echo "Install with: brew install ngrok"
    exit 1
  fi

  python3 -m http.server "${PORT}" >/tmp/consultation-recorder-server.log 2>&1 &
  SERVER_PID=$!
  trap 'kill ${SERVER_PID} 2>/dev/null || true' EXIT

  sleep 1
  if ! kill -0 "${SERVER_PID}" >/dev/null 2>&1; then
    echo "Server failed to start. Check /tmp/consultation-recorder-server.log"
    exit 1
  fi

  echo "Opening public tunnel with ngrok..."
  echo "Share the HTTPS URL ngrok prints below."
  echo
  ngrok http "${PORT}"
else
  python3 -m http.server "${PORT}"
fi
