---
name: youtube-extract
description: Extract transcripts, titles, descriptions, and metadata from YouTube videos using yt-dlp subtitle and metadata APIs (no browser automation). Use when the user asks to transcribe a YouTube video, analyze a YouTube video, get a video transcript, or summarize video content from a YouTube URL.
---

# youtube-extract

Extract transcript text and core metadata from a YouTube URL using **yt-dlp** for fast, reliable subtitle retrieval.

## Prerequisites

- Requires `yt-dlp` installed on the system (recommended via `pipx install yt-dlp`)

## Quick start

```bash
# Install Python dependency shim (optional but kept for environment consistency)
python3 -m pip install -r skills/youtube-extract/scripts/requirements.txt

# Extract to default JSON output path
python3 skills/youtube-extract/scripts/extract_youtube.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Extract with custom output path and retries
python3 skills/youtube-extract/scripts/extract_youtube.py \
  "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --output /tmp/youtube_extract.json \
  --retries 4
```

## Extraction workflow (yt-dlp)

1. Verify `yt-dlp` is available in PATH.
2. Fetch metadata with:
   - `yt-dlp --dump-json --skip-download "URL"`
3. Check available subtitles with:
   - `yt-dlp --list-subs "URL"`
4. Download auto-generated English subtitles as SRT with:
   - `yt-dlp --write-auto-subs --skip-download --sub-langs en --convert-subs srt -o "output" "URL"`
5. Parse the SRT file into clean transcript segments (`start`, `text`) and merged transcript text.
6. Save final JSON with metadata + transcript.

## Output format

The script writes JSON shaped like:

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "video_id": "...",
  "title": "...",
  "channel": "...",
  "description": "...",
  "duration_seconds": 0,
  "publish_date": null,
  "transcript": {
    "method": "yt_dlp_auto_subs|none",
    "language": "en",
    "text": "...",
    "segments": [{"start": 0.0, "text": "..."}]
  },
  "status": "ok|partial|error",
  "errors": []
}
```

## Failure modes

- **yt-dlp missing**: script returns `status=error` and includes install commands in `errors`.
- **No subtitles available**: metadata still returns, transcript may be empty with `status=partial`.
- **Video restricted/unavailable**: yt-dlp stderr is captured in `errors`.
- **Transient extraction failure**: automatic retries via `--retries`.
