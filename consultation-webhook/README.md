# Consultation webhook transcription

Uses **shared** whisper stack — do not install torch/whisperx here.

## Transcription options (pick one)

1. **Recommended:** `~/.openclaw/tools/whisper-env` (already installed)
2. **Minimal local venv:** `bash install-venv.sh` (faster-whisper only, ~100MB)
3. **API:** openai-whisper-api skill

## Reinstall minimal venv

```bash
cd ~/.openclaw/workspace/consultation-webhook
rm -rf venv
bash install-venv.sh
```

If pip fails on onnxruntime, use whisper-env instead:
```bash
~/.openclaw/tools/whisper-env/bin/python your_script.py
```
