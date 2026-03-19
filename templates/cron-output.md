# Cron Job Output Template

**Every cron job that produces output MUST use this format. If nothing to report, output only: "Ran. Nothing to report."**

```
## [Job Name] — [Timestamp]

### What Happened
[Concise bullet list]

### Why It Matters
[One line — skip if nothing actionable]

### What's Next
[Action items, or "None"]

### Confidence: [0-100]

### Evidence
[File paths, outputs, links]
```

## Rules
- If nothing happened: "Ran. Nothing to report." — not silence
- Never dump raw logs — summarize with evidence
- "No output" and "nothing to report" are different signals
