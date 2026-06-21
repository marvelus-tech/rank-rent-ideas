#!/usr/bin/env python3
"""
Send audio file to Telegram chat.
"""
import sys
import os
import requests
from pathlib import Path

from dotenv import load_dotenv

# Load skill-root .env when running from cron or any cwd
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def send_audio_to_telegram(audio_path, caption, bot_token=None, chat_id=None):
    """Send audio file to Telegram."""
    
    # Load from env or args
    bot_token = bot_token or os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = chat_id or os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set", file=sys.stderr)
        sys.exit(1)
    
    url = f"https://api.telegram.org/bot{bot_token}/sendAudio"
    
    with open(audio_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        data = {
            'chat_id': chat_id,
            'caption': caption[:1024] if caption else '',  # Telegram caption limit
            'title': caption[:255] if caption else 'Article Audio'
        }
        
        try:
            response = requests.post(url, files=files, data=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                print(f"Successfully sent: {caption[:50]}...")
                return True
            else:
                print(f"Telegram API error: {result}", file=sys.stderr)
                return False
        
        except Exception as e:
            print(f"Error sending to Telegram: {e}", file=sys.stderr)
            return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: send-telegram.py <audio-path> <caption>", file=sys.stderr)
        sys.exit(1)
    
    audio_path = sys.argv[1]
    caption = sys.argv[2]
    
    success = send_audio_to_telegram(audio_path, caption)
    sys.exit(0 if success else 1)
