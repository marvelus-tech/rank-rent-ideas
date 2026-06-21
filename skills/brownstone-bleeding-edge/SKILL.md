## Concise Output Rule

All scripts and subagent outputs must be **concise and token-efficient**. No verbose progress logs, no step-by-step narration, no unnecessary detail. Output only:

- **Success**: One-line confirmation with key result (e.g., "3 articles found, 1 new")
- **Failure**: One-line error + fix suggestion
- **Data**: Minimal structured output (JSON, list, or summary)

**Bad**: "I am now fetching the page... Parsing HTML... Found 3 articles... Checking state... 1 new article detected..."
**Good**: "3 articles found, 1 new: 'Article Title'"

Subagents spawned for this skill must include: `Be concise. One-line summaries only. No verbose narration.`

---

This skill monitors the Brownstone Research "Bleeding Edge" newsletter, detects new articles, converts them to TTS audio, and sends them to Telegram.

## Workflow

1. **Fetch the Bleeding Edge page** and extract article list
2. **Compare against state** to find new articles
3. **Fetch each new article** and extract content
4. **Generate TTS audio** from article content
5. **Send audio to Telegram**
6. **Update state** with processed articles

## Quick Start

Run the main script to check for new articles:

```bash
~/.openclaw/workspace/skills/brownstone-bleeding-edge/scripts/check-and-process.sh
```

## State Management

Articles are tracked in:
- `~/.openclaw/workspace/skills/brownstone-bleeding-edge/state/processed-articles.json`

Format:
```json
{
  "articles": [
    {
      "url": "https://www.brownstoneresearch.com/bleeding-edge/article-slug/",
      "title": "Article Title",
      "date": "Apr 15, 2026",
      "processed_at": "2026-04-16T07:14:00Z"
    }
  ]
}
```

## Configuration

Create `~/.openclaw/workspace/skills/brownstone-bleeding-edge/.env` (gitignored under `workspace/` — never commit tokens):

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=<from @BotFather>
TELEGRAM_CHAT_ID=<your numeric chat id>

# TTS Configuration (optional - uses system default if not set)
# TTS_VOICE=nova
# TTS_MODEL=tts-1-hd
```

`scripts/send-telegram.py` loads this `.env` automatically via `python-dotenv`.

## Scripts

### Main Entry Point
- `scripts/check-and-process.sh` - Full workflow: check, fetch, TTS, send, update state

### Component Scripts
- `scripts/fetch-articles.py` - Extract article list from Bleeding Edge page
- `scripts/fetch-article-content.py` - Extract full article content from URL
- `scripts/generate-tts.py` - Convert article text to audio file
- `scripts/send-telegram.py` - Send audio file to Telegram chat
- `scripts/update-state.py` - Update processed articles state

## Manual Usage

Process a specific article:
```bash
python3 ~/.openclaw/workspace/skills/brownstone-bleeding-edge/scripts/fetch-article-content.py "https://www.brownstoneresearch.com/bleeding-edge/article-slug/"
```

Generate TTS from text file:
```bash
python3 ~/.openclaw/workspace/skills/brownstone-bleeding-edge/scripts/generate-tts.py /path/to/article.txt /path/to/output.mp3
```

Send audio to Telegram:
```bash
python3 ~/.openclaw/workspace/skills/brownstone-bleeding-edge/scripts/send-telegram.py /path/to/audio.mp3 "Article Title"
```

## Article Structure

The Bleeding Edge page contains:
- Article links with format: `https://www.brownstoneresearch.com/bleeding-edge/{slug}/`
- Article titles in `### [Title](url)` format
- Publication dates in `Apr 15, 2026` format
- Excerpt/summary text

## Dependencies

- Python 3.8+
- Required packages: requests, beautifulsoup4, python-dotenv
- OpenClaw TTS capability (sag/elevenlabs)
- curl (for Telegram API)

## Installation

```bash
# Install Python dependencies
pip3 install requests beautifulsoup4 python-dotenv

# Create state directory
mkdir -p ~/.openclaw/workspace/skills/brownstone-bleeding-edge/state

# Create initial state file
echo '{"articles": []}' > ~/.openclaw/workspace/skills/brownstone-bleeding-edge/state/processed-articles.json
```
