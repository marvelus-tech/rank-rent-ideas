import sys
import json
import os
from datetime import datetime

def load_state(path):
    if not os.path.exists(path):
        return {"articles": []}
    with open(path, 'r') as f:
        return json.load(f)

def save_state(path, state):
    with open(path, 'w') as f:
        json.dump(state, f, indent=2)

def main():
    if len(sys.argv) < 3:
        print("Usage: state-manager.py <new|add> <file>")
        sys.exit(1)

    cmd = sys.argv[1]
    file_path = sys.argv[2]
    state_file = os.path.expanduser("~/.openclaw/workspace/skills/brownstone-bleeding-edge/state/processed-articles.json")
    state = load_state(state_file)
    processed_urls = {a['url'] for a in state['articles']}

    if cmd == "new":
        with open(file_path, 'r') as f:
            all_articles = json.load(f)
        new_articles = [a for a in all_articles if a['url'] not in processed_urls]
        print(json.dumps(new_articles))
    
    elif cmd == "add":
        with open(file_path, 'r') as f:
            article = json.load(f)
        if article['url'] not in processed_urls:
            article['processed_at'] = datetime.utcnow().isoformat() + "Z"
            state['articles'].append(article)
            save_state(state_file, state)

if __name__ == "__main__":
    main()
