# Codex Verbosity Fix

## Prompt file
`~/.openclaw/workspace/.codex-prompt.md` — concise output rules + bad/good examples.

## How to apply

### Option 1: Inject via task prefix (immediate, no config change)
Prepend to every Codex task string:

```js
const CODEX_RULES = `Read ~/.openclaw/workspace/.codex-prompt.md and follow its output rules strictly.\n\n`;
sessions_spawn({ model: "Codex", task: CODEX_RULES + yourTask });
```

### Option 2: Bake into skill/spawn wrapper
Any skill that spawns Codex should include in its task:

```
[Output rules: read ~/.openclaw/workspace/.codex-prompt.md]
```

### Option 3: Add to Subagent Context in workspace
Append to `~/.openclaw/workspace/AGENTS.md` or the injected subagent context block — but this affects ALL subagents, not just Codex.

## Recommended approach
Use Option 1 for targeted Codex spawns. Add a helper:

```js
function spawnCodex(task) {
  return sessions_spawn({
    model: "Codex",
    task: `Follow output rules in ~/.openclaw/workspace/.codex-prompt.md\n\n${task}`
  });
}
```
