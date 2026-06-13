#!/bin/bash
# Minimal venv for consultation-webhook (faster-whisper only — no torch)
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv venv
./venv/bin/pip install -U pip
./venv/bin/pip install -r requirements.txt
echo "Done. Venv size: $(du -sh venv | awk '{print $1}')"
