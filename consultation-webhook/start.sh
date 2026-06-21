#!/bin/bash
# Start Consultation Webhook Server

cd /Users/oktos/.openclaw/workspace/consultation-webhook

# Local secrets for WhisperX / Hugging Face (optional). Copy from .env.example.
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "🎙️  Starting Consultation Webhook Server + transcription worker..."
echo "📡 Endpoint: http://localhost:5678/webhook/consultation"
echo "📁 Files saved to: ~/Obsidian/Consultations/Incoming"
echo ""
echo "To expose with ngrok (in another terminal):"
echo "  ngrok http 5678"
echo ""
echo "Optional: OpenClaw email handoff after Whisper (polls for email-handoff/<job>.reply.json):"
echo "  export OPENCLAW_EMAIL_WAIT_SECONDS=180"
echo ""

# Fail before starting watcher: if Flask can't bind, the script exits and the EXIT trap kills the watcher (SIGTERM).
if lsof -nP -iTCP:5678 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "ERROR: Port 5678 is already in use. Another webhook server is probably still running."
  echo "  See what holds it:  lsof -nP -iTCP:5678 -sTCP:LISTEN"
  echo "  Stop it (example):  kill \$(lsof -nP -t -iTCP:5678 -sTCP:LISTEN)"
  echo "  Then run ./start.sh again."
  exit 1
fi

# Transcription worker (Whisper) — required for /webhook/status to reach "done"
python3 watcher.py &
WATCHER_PID=$!
trap 'kill "$WATCHER_PID" 2>/dev/null' EXIT INT TERM

sleep 0.4
if ! kill -0 "$WATCHER_PID" 2>/dev/null; then
  echo ""
  echo "ERROR: watcher exited immediately (usually: another watcher already holds the lock)."
  echo "  tail -40 /Users/oktos/.openclaw/workspace/.consultation-signal/watcher.log"
  echo "  If stale: kill the old watcher or remove the lock and retry."
  exit 1
fi

python3 server.py
