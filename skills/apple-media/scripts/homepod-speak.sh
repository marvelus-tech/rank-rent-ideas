#!/bin/bash
# HomePod TTS - Text to Speech on HomePod
# Usage: homepod-speak.sh "Your message here"

export PATH="$PATH:$HOME/.local/bin"

HOMEPOD_NAME="Living Room"
MESSAGE="${1:-Hello}"
TEMP_AIFF="/tmp/homepod_speak_$(date +%s).aiff"
TEMP_WAV="/tmp/homepod_speak_$(date +%s).wav"

# Generate speech as AIFF
say "$MESSAGE" -o "$TEMP_AIFF"

# Convert AIFF to WAV using afconvert (macOS built-in)
afconvert "$TEMP_AIFF" "$TEMP_WAV" -f WAVE -d LEI16

# Stream to HomePod
atvremote -n "$HOMEPOD_NAME" stream_file="$TEMP_WAV"

# Cleanup
rm -f "$TEMP_AIFF" "$TEMP_WAV"
