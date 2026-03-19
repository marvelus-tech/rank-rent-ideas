# Evidence Gate Checklist

**Purpose:** Before ANY task can be marked "done", this checklist MUST be completed. No exceptions. Copy this template into the task output.

---

## Template (copy for each task completion)

```
### Evidence Gate — [Task Name]
- [ ] **What changed:** List every file path modified
- [ ] **Why:** One-line rationale for each change
- [ ] **Commit:** Hash or "not applicable" (with reason)
- [ ] **Verification:** How was this verified? (ran script, tested manually, checked output, etc.)
- [ ] **Artifacts:** Screenshots, logs, or output snippets if applicable
- [ ] **State persisted:** Completion state written to tracking file BEFORE this report
```

## Rules
1. If ANY box is unchecked, the task is NOT done
2. "I checked and it works" is not verification — show the output
3. If there's no commit and there should be, explain why
4. This gate applies to sub-agents too — their completions must include evidence
