#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [[ ! -d "venv" ]]; then
  echo "Missing venv at $PROJECT_DIR/venv"
  echo "Create it first with ./start.sh"
  exit 1
fi

source "venv/bin/activate"

if ! command -v huggingface-cli >/dev/null 2>&1; then
  echo "huggingface-cli not found in venv; installing huggingface_hub[cli]..."
  python -m pip install "huggingface_hub[cli]"
fi

WHISPER_MODEL="${WHISPERX_MODEL:-${FASTER_WHISPER_MODEL:-base}}"
LANG_CODE="${WHISPERX_LANGUAGE:-en}"
DIARIZATION_MODEL="${WHISPERX_DIARIZATION_MODEL:-pyannote/speaker-diarization-3.1}"

case "$WHISPER_MODEL" in
  tiny.en) FW_REPO="Systran/faster-whisper-tiny.en" ;;
  tiny) FW_REPO="Systran/faster-whisper-tiny" ;;
  base.en) FW_REPO="Systran/faster-whisper-base.en" ;;
  base) FW_REPO="Systran/faster-whisper-base" ;;
  small.en) FW_REPO="Systran/faster-whisper-small.en" ;;
  small) FW_REPO="Systran/faster-whisper-small" ;;
  medium.en) FW_REPO="Systran/faster-whisper-medium.en" ;;
  medium) FW_REPO="Systran/faster-whisper-medium" ;;
  large-v1) FW_REPO="Systran/faster-whisper-large-v1" ;;
  large-v2) FW_REPO="Systran/faster-whisper-large-v2" ;;
  large-v3|large) FW_REPO="Systran/faster-whisper-large-v3" ;;
  distil-large-v2) FW_REPO="Systran/faster-distil-whisper-large-v2" ;;
  distil-medium.en) FW_REPO="Systran/faster-distil-whisper-medium.en" ;;
  distil-small.en) FW_REPO="Systran/faster-distil-whisper-small.en" ;;
  distil-large-v3) FW_REPO="Systran/faster-distil-whisper-large-v3" ;;
  large-v3-turbo|turbo) FW_REPO="mobiuslabsgmbh/faster-whisper-large-v3-turbo" ;;
  */*) FW_REPO="$WHISPER_MODEL" ;;
  *)
    echo "Unknown Whisper model '$WHISPER_MODEL' (set WHISPERX_MODEL or FASTER_WHISPER_MODEL)."
    exit 1
    ;;
esac

echo "Preloading faster-whisper model: $FW_REPO"
huggingface-cli download "$FW_REPO" \
  --include "config.json" "preprocessor_config.json" "model.bin" "tokenizer.json" "vocabulary.*"

echo "Preloading WhisperX alignment model for language: $LANG_CODE"
python - <<'PY'
import os
import os.path
import torch
import torchaudio
import whisperx
from whisperx.alignment import (
    DEFAULT_ALIGN_MODELS_HF,
    DEFAULT_ALIGN_MODELS_TORCH,
    load_align_model,
)

lang = os.environ.get("WHISPERX_LANGUAGE", "en").strip()
explicit = os.environ.get("WHISPERX_ALIGN_MODEL", "").strip() or None
align_name = explicit or DEFAULT_ALIGN_MODELS_TORCH.get(lang) or DEFAULT_ALIGN_MODELS_HF.get(lang)
if not align_name:
    raise SystemExit(
        f"No default WhisperX align model for language={lang!r}. "
        "Set WHISPERX_ALIGN_MODEL to a valid wav2vec2 model."
    )
print(f"Alignment model: {align_name}")

try:
    load_align_model(language_code=lang, device="cpu", model_name=align_name)
except RuntimeError as exc:
    msg = str(exc).lower()
    if (
        align_name in torchaudio.pipelines.__all__
        and "pytorchstreamreader failed reading zip archive" in msg
    ):
        bundle = torchaudio.pipelines.__dict__[align_name]
        url = getattr(bundle, "_path", "")
        ckpt = os.path.join(torch.hub.get_dir(), "checkpoints", os.path.basename(url))
        if ckpt and os.path.exists(ckpt):
            print(f"Corrupt checkpoint detected, removing: {ckpt}")
            os.remove(ckpt)
        print("Retrying alignment model download...")
        load_align_model(language_code=lang, device="cpu", model_name=align_name)
    else:
        raise
print("Alignment model cached.")
PY

if [[ -n "${HF_TOKEN:-${HUGGINGFACE_HUB_TOKEN:-}}" ]]; then
  TOKEN="${HF_TOKEN:-${HUGGINGFACE_HUB_TOKEN:-}}"
  echo "Preloading diarization model: $DIARIZATION_MODEL"
  huggingface-cli download "$DIARIZATION_MODEL" --token "$TOKEN"
else
  echo "Skipping diarization preload (HF_TOKEN/HUGGINGFACE_HUB_TOKEN not set)."
fi

echo "Done. WhisperX assets are cached."
