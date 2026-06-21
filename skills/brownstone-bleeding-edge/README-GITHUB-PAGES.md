# Brownstone Bleeding Edge → GitHub Pages Publishing

This replaces Telegram delivery with static publishing to a GitHub Pages repo.

## What changed

- `scripts/check-and-process.sh`
  - Keeps existing fetch + TTS flow
  - Replaces Telegram send step with `publish-to-github.sh`
  - Marks article as processed only after successful publish

- `scripts/publish-to-github.sh` (new)
  - Clones/pulls GitHub Pages repo (or uses local repo)
  - Copies MP3 to `audio/<slug>.mp3`
  - Maintains `articles.json`
  - Regenerates `index.html` (dark, mobile responsive, newest-first, HTML5 audio players)
  - Commits + pushes

## Required repo setup

1. Create GitHub repo (if not already):
   - Suggested: `brownstone-audio`
   - Owner: `marvelus-tech`
2. Enable GitHub Pages in repo settings:
   - Deploy from branch: `main` (root)
3. Ensure this machine can push:
   - `git` auth via SSH key or GitHub token credential helper

## Runtime config (optional env vars)

- `PAGES_REPO_URL` (default: `https://github.com/marvelus-tech/brownstone-audio.git`)
- `PAGES_REPO_DIR` (default: `skills/brownstone-bleeding-edge/brownstone-audio-site`)
- `PAGES_BRANCH` (default: `main`)
- `PAGES_AUTO_PUSH` (default: `1`)
- `PAGES_LOCAL_ONLY` (default: `0`; set `1` for local-only testing)

## Local test (no remote push)

```bash
ffmpeg -y -f lavfi -i "sine=frequency=880:duration=1" -q:a 9 -acodec libmp3lame ./work/dummy.mp3

PAGES_LOCAL_ONLY=1 \
PAGES_AUTO_PUSH=0 \
PAGES_REPO_DIR=./work/test-site \
./scripts/publish-to-github.sh ./work/dummy.mp3 "Test Article" "Jun 10, 2026" "test-article" "https://example.com/test-article"
```

Then open `./work/test-site/index.html`.

## Production run

```bash
./scripts/check-and-process.sh
```

If new articles are found, audio + `index.html` + `articles.json` will be committed and pushed to the Pages repo.
