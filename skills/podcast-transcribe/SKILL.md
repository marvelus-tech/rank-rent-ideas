---
name: podcast-transcribe
description: Transcribe podcasts from any platform (Spotify, Apple Podcasts, YouTube, RSS) to text with timestamps. Takes a podcast URL, resolves it to the audio source, downloads the episode, and transcribes with Whisper. Use when the user wants to transcribe a podcast episode, get text from a podcast, extract podcast content, or create a transcript from Spotify/Apple/YouTube/RSS podcast URLs.
---

# Podcast Transcribe

Transcribe podcast episodes from any platform into text with timestamps using local Whisper.

## Supported Platforms

- **Spotify** — Resolves to RSS via metadata, downloads audio, transcribes
- **Apple Podcasts** — Uses iTunes API to find RSS feed, then transcribes
- **YouTube** — Delegates to `youtube-extract` skill or `yt-dlp` directly
- **RSS feeds** — Direct download and transcription
- **Any podcast with a public RSS feed** — Works regardless of discovery platform

## Requirements

- `curl` — HTTP requests
- `jq` — JSON parsing
- `python3` — RSS XML parsing
- `whisper` — Local transcription (install via `brew install openai-whisper`)
- `LISTENNOTES_API_KEY` — For Spotify/Apple podcast search (free tier: 10,000 requests/month)
  - Get key at: https://www.listennotes.com/api/
  - Set as env var: `export LISTENNOTES_API_KEY=your_key`
  - Or create `~/.podcast-transcribe/config` with: `LISTENNOTES_API_KEY=your_key`

## Scripts

### `scripts/resolve.sh`

Resolve a podcast URL to an RSS feed.

```bash
# Spotify episode
scripts/resolve.sh "https://open.spotify.com/episode/4rOoJ6Egrf8K2IrywzwOMk"

# Apple Podcasts
scripts/resolve.sh "https://podcasts.apple.com/us/podcast/id123456789"

# RSS feed (passes through)
scripts/resolve.sh "https://example.com/podcast/feed.xml"
```

Output:
```
Platform: spotify
Title: Podcast Name
RSS_URL: https://example.com/podcast/feed.xml
```

### `scripts/transcribe.sh`

Download and transcribe from an RSS feed.

```bash
# Transcribe most recent episode
scripts/transcribe.sh "https://example.com/podcast/feed.xml"

# Transcribe 5th most recent episode
scripts/transcribe.sh "https://example.com/podcast/feed.xml" 5

# Use a different whisper model (default: medium)
WHISPER_MODEL=base scripts/transcribe.sh "https://example.com/podcast/feed.xml"
```

Output files saved to `./podcast-transcripts/`:
- `.txt` — Plain text transcript
- `.srt` — Subtitle format with timestamps
- `.json` — Structured JSON with word-level timing

## Full Workflow

```bash
# 1. Resolve Spotify URL to RSS
RSS=$(scripts/resolve.sh "https://open.spotify.com/episode/XXXX" | grep RSS_URL | cut -d' ' -f2)

# 2. Transcribe
scripts/transcribe.sh "$RSS"
```

## Notes

- **Spotify-exclusive podcasts** (original content not available elsewhere) cannot be transcribed via RSS. The tool will report this.
- **Whisper model sizes**: `tiny`, `base`, `small`, `medium`, `large`. Default is `medium`. Use `base` for speed, `large` for accuracy.
- **Episode numbering**: `1` = most recent episode. Increase the number for older episodes.
- **No cloud API calls for transcription** — Whisper runs locally. Only ListenNotes API calls are external (for metadata resolution).
- For YouTube podcasts, use `youtube-extract` skill directly — it's faster and purpose-built.

## Limitations

- Requires podcast to have a public RSS feed (covers 90%+ of podcasts)
- Spotify-exclusive content (no external RSS) is not supported
- Transcription speed depends on local hardware (GPU significantly faster than CPU)
