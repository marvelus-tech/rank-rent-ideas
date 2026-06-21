import json
import os
import sys
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.openclaw/workspace/skills/brownstone-bleeding-edge/state/processed-articles.json")

def add_article(url, title, date, slug):
    if not os.path.exists(STATE_FILE):
        state = {"articles": []}
    else:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    
    # Avoid duplicates
    if any(a['url'] == url for a in state['articles']):
        return False
        
    state['articles'].append({
        "url": url,
        "title": title,
        "date": date,
        "slug": slug,
        "processed_at": datetime.utcnow().isoformat() + "Z"
    })
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    return True

if __name__ == "__main__":
    if len(sys.argv) == 5:
        url, title, date, slug = sys.argv[1:5]
        if add_article(url, title, date, slug):
            print(f"Added {title}")
