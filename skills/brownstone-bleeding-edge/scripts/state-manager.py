#!/usr/bin/env python3
"""
Manage state of processed articles.
"""
import json
import sys
import os
from datetime import datetime, timezone

STATE_DIR = os.path.expanduser("~/.openclaw/workspace/skills/brownstone-bleeding-edge/state")
STATE_FILE = os.path.join(STATE_DIR, "processed-articles.json")

def load_state():
    """Load processed articles state."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"articles": []}

def save_state(state):
    """Save processed articles state."""
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def is_article_processed(url):
    """Check if article has been processed."""
    state = load_state()
    return any(a['url'] == url for a in state['articles'])

def mark_article_processed(article_data):
    """Mark article as processed."""
    state = load_state()
    
    article_record = {
        "url": article_data['url'],
        "title": article_data.get('title', ''),
        "date": article_data.get('date', ''),
        "slug": article_data.get('slug', ''),
        "processed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
    
    # Avoid duplicates
    if not any(a['url'] == article_record['url'] for a in state['articles']):
        state['articles'].append(article_record)
        save_state(state)
        return True
    return False

def get_new_articles(articles_list):
    """Filter to only new articles not yet processed."""
    return [a for a in articles_list if not is_article_processed(a['url'])]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: state-manager.py <command> [args]", file=sys.stderr)
        print("Commands: load, check <url>, add <json-file>, new <articles-json-file>", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "load":
        print(json.dumps(load_state(), indent=2))
    
    elif command == "check":
        if len(sys.argv) < 3:
            print("Usage: state-manager.py check <url>", file=sys.stderr)
            sys.exit(1)
        url = sys.argv[2]
        print("true" if is_article_processed(url) else "false")
    
    elif command == "add":
        if len(sys.argv) < 3:
            print("Usage: state-manager.py add <article-json-file>", file=sys.stderr)
            sys.exit(1)
        with open(sys.argv[2], 'r') as f:
            article = json.load(f)
        mark_article_processed(article)
        print("Added to state")
    
    elif command == "new":
        if len(sys.argv) < 3:
            print("Usage: state-manager.py new <articles-json-file>", file=sys.stderr)
            sys.exit(1)
        with open(sys.argv[2], 'r') as f:
            articles = json.load(f)
        new_articles = get_new_articles(articles)
        print(json.dumps(new_articles, indent=2))
    
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
