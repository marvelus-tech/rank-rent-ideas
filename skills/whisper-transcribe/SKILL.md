# SKILL.md - whisper-transcribe

## Name
whisper-transcribe

## Description
Transcribe audio/video files to text using OpenAI Whisper running locally. Use when the user wants to convert speech to text, transcribe audio, extract subtitles from video, or create transcripts from podcasts/recordings. Runs 100% locally - no API keys, no cloud, no costs.

## Quick Start

```bash
# Transcribe an audio file
whisper-transcribe audio.mp3

# Transcribe with specific model (tiny/base/small/medium/large)
whisper-transcribe audio.mp3 --model small

# Transcribe video and output as SRT subtitles
whisper-transcribe video.mp4 --format srt

# Transcribe with language auto-detection
whisper-transcribe audio.mp3 --language auto

# Transcribe and save to specific directory
whisper-transcribe audio.mp3 --output /path/to/transcripts/
```

## How It Works

1. **Local Processing** - Whisper runs entirely on your machine
2. **No API Costs** - Free to use, no usage limits
3. **Privacy First** - Audio never leaves your computer
4. **Multiple Formats** - Supports MP3, WAV, M4A, MP4, MOV, etc.

## Usage Examples

### Basic Transcription
```bash
whisper-transcribe podcast.mp3
```
Outputs: `podcast.txt`, `podcast.json` (with timestamps)

### Create Subtitles
```bash
whisper-transcribe video.mp4 --format srt
```
Outputs: `video.srt` (subtitle file)

### Different Model Sizes
- `tiny` - Fastest, least accurate (~39MB)
- `base` - Fast, good accuracy (~74MB) ← DEFAULT
- `small` - Balanced (~244MB)
- `medium` - Slower, better accuracy (~769MB)
- `large` - Slowest, best accuracy (~1550MB)

```bash
whisper-transcribe audio.mp3 --model small
```

### Language Options
```bash
# Auto-detect language (default)
whisper-transcribe audio.mp3 --language auto

# Specify language
whisper-transcribe audio.mp3 --language en
whisper-transcribe audio.mp3 --language es
```

## Installation

```bash
# Via Homebrew (recommended on macOS)
brew install openai-whisper

# Or via pip (requires Python 3.7-3.11, not 3.14)
pip install openai-whisper
```

## Output Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| text | .txt | Plain transcript |
| json | .json | Full data with timestamps |
| srt | .srt | Video subtitles |
| vtt | .vtt | Web video subtitles |
| tsv | .tsv | Spreadsheet import |

## Common Tasks

**Transcribe a podcast episode:**
```bash
whisper-transcribe episode.mp3 --model small --format txt
```

**Create subtitles for a video:**
```bash
whisper-transcribe video.mp4 --format srt
```

**Process multiple files:**
```bash
for file in *.mp3; do whisper-transcribe "$file"; done
```

**High accuracy (slower):**
```bash
whisper-transcribe important.mp3 --model medium
```

## Troubleshooting

**"Command not found"**
- Make sure `/usr/local/bin` is in your PATH
- Try: `export PATH="/usr/local/bin:$PATH"`

**First run is slow**
- Whisper downloads the AI model on first use
- Model is cached at `~/.cache/whisper/`

**Out of memory**
- Use smaller model: `--model tiny` or `--model base`

**Poor transcription quality**
- Try larger model: `--model medium` or `--model large`
- Ensure audio is clear, minimal background noise

## Skill Script

The skill script wraps the `whisper` CLI with sensible defaults:
- Base model (good balance of speed/accuracy)
- Auto language detection
- Outputs to workspace directory
- Generates both text and JSON outputs

## Notes

- First transcription downloads the model (~74MB for base)
- GPU acceleration available if you have CUDA (not on Mac)
- Mac uses CPU but is still reasonably fast
- For batch processing, use the `tiny` or `base` model
