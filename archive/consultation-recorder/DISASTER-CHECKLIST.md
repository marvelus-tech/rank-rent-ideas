# Disaster Checklist (Consultation Recorder)

Pin this file in the repo root. If your machine dies, do this:

## 1) Restore project

- Get this folder back: `/Users/oktos/.openclaw/workspace/consultation-recorder`
- Confirm `index.html` exists

## 2) Install basics

Run:

```bash
python3 --version
```

If ngrok is needed for public links:

```bash
brew install ngrok
```

## 3) Start locally (one command)

From repo root:

```bash
./run.sh
```

Open:

- `http://localhost:8080`

## 4) Start public demo link (one command)

```bash
./run.sh --public
```

- Copy the HTTPS URL from ngrok and send to client

## 5) If something breaks fast

- `python3` missing -> install Python 3
- `ngrok` missing -> `brew install ngrok`
- `index.html` missing -> restore file from backup/repo
- Port busy -> run with another port:

```bash
PORT=8081 ./run.sh
```

## 6) Prevent future pain (30-second habit)

- Keep `index.html` in GitHub
- Optional: enable GitHub Pages for permanent frontend URL
- After edits, push changes or copy `index.html` to cloud backup
