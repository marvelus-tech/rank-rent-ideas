---
name: consultation-processor
description: Process consultation recordings - transcribe audio, generate structured meeting notes, and draft a professional follow-up email. Trigger when user mentions "consultation", "meeting notes", or attaches audio and asks for notes/email.
metadata:
  openclaw:
    emoji: 📋
    requires:
      anyBins: ["whisper", "whisper-transcribe"]
---

# Consultation Processor Skill

## When to activate
- User attaches an audio file (.webm, .mp3, .m4a, .wav, .ogg) AND mentions "consultation", "client meeting", "record", "notes", "email", "transcribe", or similar.
- User says "process this consultation" or "process this recording"
- User asks for "meeting notes" from an audio file
- User wants "email draft" from a consultation recording
- **Consultation Recorder pipeline:** Whisper has already produced a transcript; a handoff file under `~/.openclaw/workspace/.consultation-signal/email-handoff/` needs a follow-up email draft from the agent (see below).

## Recorder email handoff (after Whisper, before the UI finishes)

The watcher **always** writes a request file when transcription completes:

- Path: `~/.openclaw/workspace/.consultation-signal/email-handoff/<job-stem>.request.json`
- Fields include: `transcript`, `clientName`, `jobFile` (absolute path to the job JSON).

If the operator set **`OPENCLAW_EMAIL_WAIT_SECONDS`** > 0 on the watcher, it **polls** for a reply file **with the same stem**:

- Write: `~/.openclaw/workspace/.consultation-signal/email-handoff/<job-stem>.reply.json`
- Shape: `{ "version": 1, "email": "<full email body including Subject: line>" }`
- Write **atomically** (write temp, then rename) so the watcher does not read a half-written file.

**Your job when this file appears:** Read the consultation-processor skill (email section), use **only** `transcript` from the request—no invention. Draft a professional follow-up email, then write `reply.json` as above. The watcher then continues: saves the note, marks the job `done`, and the **UI** shows transcript + that email.

If you are **not** using the wait window, the watcher still writes `*.request.json` for reference; the job completes with a **template** email unless a sync **`EMAIL_DRAFT_HOOK`** produced the draft.

## Step-by-step workflow

### 1. Receive the audio file
- Accept the attached audio file
- Confirm it's a consultation recording (proceed regardless - the skill works for any meeting)

### 2. Transcribe the audio
- Use `whisper-transcribe` or direct `whisper` command
- Transcribe to text with timestamps
- Save the full transcript as `consultation-transcript-[timestamp].md`

### 3. Generate structured meeting notes
From the transcript, extract and organize:

**Key Discussion Points:**
- Main topics covered
- Client's stated goals/problems
- Your recommendations/advice

**Action Items:**
- What needs to be done
- Who is responsible (if mentioned)
- Deadlines (if mentioned)

**Decisions Made:**
- Agreements reached
- Next steps confirmed

**Open Questions/Follow-ups:**
- Items to research
- Questions to answer later
- Resources to send

### 4. Draft a professional follow-up email
Include:
- **Subject line:** Professional and specific (e.g., "Follow-up: [Topic] Consultation - [Date]")
- **Greeting:** Personalized
- **Opening:** Thank them for the consultation
- **Summary:** Brief recap of key discussion points
- **Action items:** Clear bullet list of who does what
- **Next steps:** What happens next and when
- **Call to action:** Specific ask or confirmation needed
- **Closing:** Professional sign-off

### 5. Save outputs
Save files to current workspace or specified folder:
- `consultation-transcript-YYYY-MM-DD-HHMM.md`
- `consultation-notes-YYYY-MM-DD-HHMM.md`
- `consultation-email-YYYY-MM-DD-HHMM.md`

### 6. Reply to user
Summarize what was processed:
- Duration of recording
- Key topics identified
- Number of action items
- Location of saved files
- Ask: "Want me to send the email, tweak anything, or store in a specific folder?"

## Style Guidelines

- **Be concise:** Bullet points over paragraphs
- **Professional tone:** Client-friendly language
- **Action-oriented:** Clear next steps
- **No hallucination:** Stick strictly to what was said in the transcript
- **Customize:** Use user's preferred tone if known from memory

## Example Usage

**User:** "Process this consultation recording"
**Action:** 
1. Transcribe audio
2. Generate notes
3. Draft email
4. Save all three files
5. Reply with summary

**User:** "I need meeting notes from this call"
**Action:** Same workflow, focus on notes format

**User:** "Draft a follow-up email for this client meeting"
**Action:** Same workflow, focus on email quality

## Output Format

### Meeting Notes Structure
```markdown
# Consultation Notes - [Client Name] - [Date]

## Overview
- **Date:** [date]
- **Duration:** [length]
- **Recording:** [filename]

## Key Discussion Points
1. [Point 1]
2. [Point 2]
...

## Action Items
- [ ] [Action] - Owner: [name] - Due: [date]
...

## Decisions Made
- [Decision 1]
...

## Follow-ups Needed
- [Item 1]
...

## Next Steps
1. [Step 1]
2. [Step 2]
```

### Email Draft Structure
```markdown
Subject: Follow-up: [Topic] Consultation - [Date]

Dear [Client Name],

Thank you for taking the time to meet with me today. I enjoyed our conversation about [topic].

**Key points we discussed:**
- [Point 1]
- [Point 2]

**Action items:**
- [Item 1]
- [Item 2]

**Next steps:**
[Clear description of what happens next]

Please let me know if you have any questions or if there's anything else you'd like to discuss.

Best regards,
[Your name]
```

## Notes
- Works with any audio format Whisper supports
- First transcription may take time if model needs downloading
- For long recordings (30+ min), consider using `small` or `medium` Whisper model for better accuracy
- Can be extended later to auto-send emails, create calendar events, etc.
