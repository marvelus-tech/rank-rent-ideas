#!/bin/bash
# OpenClaw TTS + Mac Speaker Test
# Usage: tts-speak.sh "Your message"

MESSAGE="${1:-Hello from OpenClaw}"
TEMP_FILE="/tmp/openclaw_tts_$(date +%s).mp3"

# Use Edge TTS (free, no API key)
edge-tts --voice "en-US-MichelleNeural" --text "$MESSAGE" --write-media "$TEMP_FILE"

# Play on Mac
afplay "$TEMP_FILE"

# Cleanup
rm -f "$TEMP_FILE"
