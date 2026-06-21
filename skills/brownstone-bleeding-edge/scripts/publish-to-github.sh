#!/bin/bash
# Publish generated Brownstone audio to a GitHub Pages repo.
# Usage:
#   publish-to-github.sh <audio_file> <title> <date> <slug> <url>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

AUDIO_FILE="${1:-}"
TITLE="${2:-}"
ARTICLE_DATE="${3:-}"
SLUG="${4:-}"
ARTICLE_URL="${5:-}"

if [ -z "$AUDIO_FILE" ] || [ -z "$TITLE" ] || [ -z "$SLUG" ]; then
  echo "Usage: $(basename "$0") <audio_file> <title> <date> <slug> <url>" >&2
  exit 1
fi

if [ ! -f "$AUDIO_FILE" ]; then
  echo "Audio file not found: $AUDIO_FILE" >&2
  exit 1
fi

PAGES_REPO_URL="${PAGES_REPO_URL:-https://github.com/marvelus-tech/brownstone-audio.git}"
PAGES_REPO_DIR="${PAGES_REPO_DIR:-$SCRIPT_DIR/../brownstone-audio-site}"
PAGES_BRANCH="${PAGES_BRANCH:-main}"
PAGES_LOCAL_ONLY="${PAGES_LOCAL_ONLY:-0}"
PAGES_AUTO_PUSH="${PAGES_AUTO_PUSH:-1}"

AUDIO_DIR="$PAGES_REPO_DIR/audio"
METADATA_FILE="$PAGES_REPO_DIR/articles.json"
INDEX_FILE="$PAGES_REPO_DIR/index.html"

if [ ! -d "$PAGES_REPO_DIR/.git" ]; then
  if [ "$PAGES_LOCAL_ONLY" = "1" ]; then
    mkdir -p "$PAGES_REPO_DIR"
    if [ ! -d "$PAGES_REPO_DIR/.git" ]; then
      git -C "$PAGES_REPO_DIR" init >/dev/null 2>&1 || true
    fi
  else
    mkdir -p "$(dirname "$PAGES_REPO_DIR")"
    echo "Cloning $PAGES_REPO_URL into $PAGES_REPO_DIR"
    git clone "$PAGES_REPO_URL" "$PAGES_REPO_DIR"
  fi
else
  if [ "$PAGES_LOCAL_ONLY" != "1" ]; then
    git -C "$PAGES_REPO_DIR" fetch origin "$PAGES_BRANCH" || true
    git -C "$PAGES_REPO_DIR" checkout "$PAGES_BRANCH" || true
    git -C "$PAGES_REPO_DIR" pull --rebase origin "$PAGES_BRANCH" || true
  fi
fi

mkdir -p "$AUDIO_DIR"
DEST_AUDIO_REL="audio/${SLUG}.mp3"
DEST_AUDIO="$PAGES_REPO_DIR/$DEST_AUDIO_REL"
cp "$AUDIO_FILE" "$DEST_AUDIO"

python3 - "$METADATA_FILE" "$INDEX_FILE" "$TITLE" "$ARTICLE_DATE" "$SLUG" "$ARTICLE_URL" "$DEST_AUDIO_REL" <<'PY'
import json
import sys
from datetime import datetime
from html import escape
from pathlib import Path

metadata_file = Path(sys.argv[1])
index_file = Path(sys.argv[2])
title = sys.argv[3]
article_date = sys.argv[4]
slug = sys.argv[5]
article_url = sys.argv[6]
audio_path = sys.argv[7]

from datetime import timezone
now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

if metadata_file.exists():
    try:
        data = json.loads(metadata_file.read_text())
        if not isinstance(data, list):
            data = []
    except Exception:
        data = []
else:
    data = []

entry = {
    "title": title,
    "date": article_date,
    "slug": slug,
    "url": article_url,
    "audio": audio_path,
    "published_at": now_iso,
}

filtered = [x for x in data if x.get("slug") != slug and x.get("url") != article_url]
filtered.append(entry)

def parse_date(item):
    raw = (item.get("date") or "").strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt)
        except Exception:
            continue
    raw_pub = item.get("published_at")
    if raw_pub:
        try:
            return datetime.fromisoformat(raw_pub.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            pass
    return datetime.min

articles = sorted(filtered, key=parse_date, reverse=True)
metadata_file.write_text(json.dumps(articles, indent=2) + "\n")

cards = []
for item in articles:
    t = escape(item.get("title", "Untitled"))
    d = escape(item.get("date", "Unknown date"))
    u = item.get("url", "")
    a = escape(item.get("audio", ""), quote=True)
    link = f'<a class="src" href="{escape(u, quote=True)}" target="_blank" rel="noopener">Source ↗</a>' if u else ""
    cards.append(
        f'''<article class="card">\n'''
        f'''  <div class="meta">\n'''
        f'''    <h2>{t}</h2>\n'''
        f'''    <p>{d}</p>\n'''
        f'''    {link}\n'''
        f'''  </div>\n'''
        f'''  <audio controls preload="none" src="{a}"></audio>\n'''
        f'''</article>'''
    )

html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Brownstone Audio — Bleeding Edge</title>
  <style>
    :root {{
      --bg: #070b14;
      --panel: #111827;
      --border: #1f2a44;
      --text: #e6edf7;
      --muted: #94a3b8;
      --accent: #14f195;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
      background: radial-gradient(1200px 600px at 80% -20%, #1f2952 0%, transparent 60%), var(--bg);
      color: var(--text);
      min-height: 100vh;
    }}
    .wrap {{ max-width: 920px; margin: 0 auto; padding: 24px 16px 56px; }}
    h1 {{ margin: 0 0 8px; font-size: clamp(1.5rem, 2.4vw, 2rem); }}
    .sub {{ color: var(--muted); margin-bottom: 20px; }}
    .list {{ display: grid; gap: 12px; }}
    .card {{
      background: linear-gradient(180deg, rgba(17,24,39,0.92), rgba(13,18,32,0.92));
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      display: grid;
      gap: 10px;
    }}
    .meta h2 {{ margin: 0 0 4px; font-size: 1rem; line-height: 1.35; }}
    .meta p {{ margin: 0; color: var(--muted); font-size: .92rem; }}
    .src {{ color: var(--accent); text-decoration: none; font-size: .88rem; display: inline-block; margin-top: 6px; }}
    audio {{ width: 100%; }}
    footer {{ margin-top: 18px; color: var(--muted); font-size: .84rem; }}
    @media (min-width: 700px) {{
      .card {{ grid-template-columns: 1fr minmax(260px, 340px); align-items: center; }}
    }}
  </style>
</head>
<body>
  <main class=\"wrap\">
    <h1>Brownstone Audio — Bleeding Edge</h1>
    <p class=\"sub\">Latest article narrations, newest first.</p>
    <section class=\"list\">
      {''.join(cards) if cards else '<p>No audio articles yet.</p>'}
    </section>
    <footer>Auto-generated from the Brownstone monitor workflow.</footer>
  </main>
</body>
</html>
"""

index_file.write_text(html)
PY

if [ -d "$PAGES_REPO_DIR/.git" ]; then
  git -C "$PAGES_REPO_DIR" add "$DEST_AUDIO_REL" "articles.json" "index.html"
  if ! git -C "$PAGES_REPO_DIR" diff --cached --quiet; then
    git -C "$PAGES_REPO_DIR" commit -m "Add Brownstone audio: $TITLE"
    if [ "$PAGES_AUTO_PUSH" = "1" ] && [ "$PAGES_LOCAL_ONLY" != "1" ]; then
      git -C "$PAGES_REPO_DIR" push origin "$PAGES_BRANCH"
    fi
  fi
fi

echo "$INDEX_FILE"