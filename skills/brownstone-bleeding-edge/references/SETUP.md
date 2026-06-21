# Setup Guide for Brownstone Bleeding Edge Monitor

## Prerequisites

1. Python 3.8+ with pip
2. Telegram Bot Token and Chat ID
3. OpenClaw TTS capability (sag/ElevenLabs) or macOS `say` command

## Installation

### Step 1: Install Python Dependencies

```bash
pip3 install requests beautifulsoup4 python-dotenv jq
```

### Step 2: Configure Telegram

1. Create a Telegram bot via @BotFather
2. Get your bot token
3. Get your chat ID (use @userinfobot or message @getidsbot)

Create the environment file:

```bash
cat > ~/.openclaw/workspace/skills/brownstone-bleeding-edge/.env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EOF
```

### Step 3: Test the Setup

Run a manual check:

```bash
~/.openclaw/workspace/skills/brownstone-bleeding-edge/scripts/check-and-process.sh
```

### Step 4: Set Up Cron Job

Edit your crontab:

```bash
crontab -e
```

Add a daily entry (runs at 4:30 PM ET - 30 min after Bleeding Edge publishes):

```cron
# Brownstone Bleeding Edge - daily at 4:30 PM ET / 6:30 AM AEST (next day)
30 16 * * * cd ~/.openclaw/workspace/skills/brownstone-bleeding-edge && ./scripts/check-and-process.sh >> ./logs/cron.log 2>&1

# Or for AEST timezone (runs at 6:30 AM):
30 6 * * * cd ~/.openclaw/workspace/skills/brownstone-bleeding-edge && ./scripts/check-and-process.sh >> ./logs/cron.log 2>&1
```

Create logs directory:

```bash
mkdir -p ~/.openclaw/workspace/skills/brownstone-bleeding-edge/logs
```

## File Structure

```
brownstone-bleeding-edge/
├── SKILL.md                              # This skill documentation
├── scripts/
│   ├── check-and-process.sh              # Main orchestration script
│   ├── fetch-articles.py                 # Fetch article list from page
│   ├── fetch-article-content.py          # Fetch individual article content
│   ├── generate-tts.py                   # Generate TTS audio
│   ├── send-telegram.py                  # Send audio to Telegram
│   └── state-manager.py                  # Manage processed articles state
├── state/
│   └── processed-articles.json           # Tracks which articles are done
├── work/                                 # Temporary work directory
├── logs/                                 # Cron execution logs
└── .env                                  # Telegram credentials (not committed)
```

## State Format

The `state/processed-articles.json` file tracks processed articles:

```json
{
  "articles": [
    {
      "url": "https://www.brownstoneresearch.com/bleeding-edge/article-slug/",
      "title": "Article Title",
      "date": "Apr 15, 2026",
      "slug": "article-slug",
      "processed_at": "2026-04-16T07:14:00Z"
    }
  ]
}
```

## Troubleshooting

### No articles found
- Check if the website structure changed
- Run `python3 scripts/fetch-articles.py` manually to debug

### TTS not working
- Check if `sag` is installed: `which sag`
- On macOS, `say` command should work as fallback
- Check TTS text file is created in work/ directory

### Telegram not sending
- Verify bot token and chat ID in .env
- Test manually: `curl https://api.telegram.org/bot<TOKEN>/getMe`
- Check bot has permission to send messages

### Cron not running
- Check logs: `tail -f ~/.openclaw/workspace/skills/brownstone-bleeding-edge/logs/cron.log`
- Ensure scripts are executable: `chmod +x scripts/*`
- Test command manually first

## Manual Operations

### Reset state (process all articles again)

```bash
echo '{"articles": []}' > ~/.openclaw/workspace/skills/brownstone-bleeding-edge/state/processed-articles.json
```

### Check current state

```bash
python3 ~/.openclaw/workspace/skills/brownstone-bleeding-edge/scripts/state-manager.py load
```

### Process specific article

```bash
# Fetch content
python3 scripts/fetch-article-content.py "https://www.brownstoneresearch.com/bleeding-edge/article-slug/" > article.json

# Generate TTS
jq -r '.content' article.json > article.txt
python3 scripts/generate-tts.py article.txt article.mp3

# Send to Telegram
python3 scripts/send-telegram.py article.mp3 "Article Title"
```
