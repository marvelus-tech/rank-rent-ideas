# Consultation Recorder MVP

## Quick Start (2 minutes)

### 1. Run the Recorder Locally
```bash
cd /Users/oktos/.openclaw/workspace/consultation-recorder
python3 -m http.server 8080
# Or just open index.html directly in browser
```

### 1b. Run the Webhook Backend (required for stop → upload → **done**)
In a separate terminal — use `start.sh` so **both** the HTTP server and the **transcription worker** run (otherwise the UI stays on “Processing…” forever):

```bash
cd /Users/oktos/.openclaw/workspace/consultation-webhook
./start.sh
```

(`server.py` only saves files; `watcher.py` runs Whisper and updates status to `done`.)

**Stuck on “In queue” / step 1:** The UI means the job is `pending` until `watcher.py` picks it. Common causes:

1. **Worker not running** — You only started `python3 server.py` or `start.sh` failed the watcher (e.g. “Watcher already running”). Use `./start.sh` and confirm you did **not** get the watcher error. Check `tail -40 ~/.openclaw/workspace/.consultation-signal/watcher.log`.
2. **One job blocking the queue** — Jobs are processed **one at a time**, **oldest first** (FIFO). If an older job is stuck in `processing` (e.g. Whisper hung at 0% CPU), nothing after it runs. Fix: stop the watcher, set that job’s JSON under `.consultation-signal/jobs/` to `"status": "error"` with an `"error"` message (or delete test jobs you do not need), then restart `./start.sh`.
3. **Large backlog** — Many pending uploads ahead of yours; wait or remove old `*.json` job files you no longer need (only for throwaway test data).

### 2. Expose with ngrok (for client demo)
```bash
# Install ngrok if needed: brew install ngrok
ngrok http 5678
```

You'll get a public URL like: `https://abc123.ngrok.io`

Open the recorder using that backend URL:

- Local: `http://localhost:8080?api=http://127.0.0.1:5678`
- Shareable: `http://localhost:8080?api=https://abc123.ngrok.io`

**Share the full recorder link** (including the `?api=...`) with your client.

### 3. Full pipeline (what happens after “Stop”)

1. **Upload** — Audio and job metadata go to the webhook; the watcher queues work.
2. **Whisper** — The watcher transcribes audio; the **transcript** is the source of truth from here on.
3. **Email draft handoff** — Right after transcription, the watcher writes  
   `~/.openclaw/workspace/.consultation-signal/email-handoff/<job-stem>.request.json`  
   with `transcript`, `clientName`, and `jobFile`. That is the moment to involve **OpenClaw**: the agent reads that file and (when you use the wait window below) writes `<job-stem>.reply.json` with the drafted email. This step only improves the **draft email**; everything else (queue → transcribe → save note → show results in the UI) stays the same.
4. **Continue** — The watcher saves the Obsidian note, sets the job to `done`, and the **UI** loads transcript + email (the browser may still run light formatting on the email text).

**Optional:** You can still say to the OpenClaw agent *“Process this consultation”* for a **full** pass (transcribe in the workspace, notes files, etc.). That is separate from this **recorder** pipeline, which already transcribed on the server.

---

## Files Created

| File | Purpose |
|------|---------|
| `index.html` | Recording webpage (single file, works offline) |
| `SKILL.md` | OpenClaw skill for processing (`workspace/skills/consultation-processor/`) |

---

## How It Works (at a glance)

```
Client records → Upload → Whisper (transcript)
                              │
                              ▼
              Handoff: email-handoff/<stem>.request.json
              (OpenClaw writes .reply.json when wait is enabled)
                              │
                              ▼
              Save note → Job done → UI shows transcript + email
```

---

## Demo Script for Client

**"Here's a simple tool for our consultations:"**

1. **Show the ngrok link** (works on phone or computer)
2. **Hit Record** - do a 30-second test
3. **Stop** — upload runs; processing steps advance on screen
4. **Show the result screen** — transcript and follow-up email (after the worker finishes)

**Client sees:** Recording in the browser, then transcript + draft email in the same UI when processing completes.

---

## What's Included

**Recording Page:**
- Works on any device (mobile/desktop)
- No install required
- Records high-quality audio
- Shows live timer
- Download as .webm (Whisper-compatible)

**Backend processing:**
- Full transcription (local Whisper / faster-whisper)
- Email draft via handoff + template fallback (see `consultation-webhook` README)
- Obsidian note updated when configured

---

## Next Steps (Future Enhancements)

- [ ] Auto-upload to cloud storage (Supabase/S3)
- [ ] Client portal to view past recordings
- [ ] Integration with CRM (HubSpot, etc.)
- [ ] Calendar booking + recording in one link

---

## Troubleshooting

**"Microphone not working"**
- Client needs to allow browser mic permissions
- Works best in Chrome/Edge/Safari

**"File won't download"**
- Check browser download settings
- File is .webm format (works everywhere)

**"Transcription is slow"**
- First run downloads AI model (~74MB)
- Subsequent transcriptions are faster on the same machine

---

## Cost

- **Recording tool:** FREE (just HTML/JS)
- **ngrok tunnel:** FREE tier (or $5/mo for reserved URL)
- **Transcription:** FREE (local Whisper, no API costs)
- **OpenClaw (when you use the agent for email handoff):** usage depends on your model settings

**Total MVP cost: $0** (using free tiers)

---

Ready to demo.
