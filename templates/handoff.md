# Agent Handoff Template

**When passing work between agents/sub-agents, include ALL of these fields.**

```
## Handoff: [Task Name]
**From:** [Sending agent/session]
**To:** [Receiving agent/session]
**Dispatched:** [Timestamp]
**Priority:** [High/Medium/Low]

### Task
[Clear, single-scope description of what to do]

### Context
[What the receiving agent needs to know — don't assume shared context]

### Inputs
[Files, data, references needed]

### Expected Output
[What "done" looks like — specific deliverables]

### Return To
[Where results should go — file path, session, channel]

### Evidence Required
[What proof of completion is needed]
```

## Rules
- One task per handoff. No multi-problem bundles.
- If context is ambiguous, the handoff is bad. Rewrite it.
- Receiving agent must be able to execute with ONLY this handoff — no telepathy.
