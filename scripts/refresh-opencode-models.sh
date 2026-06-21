#!/usr/bin/env bash
# Refresh OpenCode Zen model list from the live API into openclaw.json.
# Run after OpenCode adds/renames models, or if Codex/Flash subagents fail with "Unknown model".
set -euo pipefail

AUTH="${HOME}/.openclaw/agents/main/agent/auth-profiles.json"
KEY=$(python3 -c "import json; print(json.load(open('${AUTH}'))['profiles']['opencode:default']['key'])")

curl -sf -H "Authorization: Bearer ${KEY}" https://opencode.ai/zen/v1/models -o /tmp/opencode-models.json

python3 <<'PY'
import json, subprocess

data = json.load(open("/tmp/opencode-models.json"))
CODEX = {
    "gpt-5.3-codex", "gpt-5.3-codex-spark", "gpt-5-codex",
    "gpt-5.5", "gpt-5.5-pro", "gpt-5.4-mini", "gpt-5.4-nano",
}
models = []
for item in data["data"]:
    mid = item["id"]
    reasoning = (
        mid in CODEX
        or mid.startswith("claude-")
        or mid.startswith("deepseek-")
        or mid.startswith("glm-")
        or mid.startswith("grok-")
    )
    models.append({
        "id": mid,
        "name": mid.replace("-", " ").title(),
        "reasoning": reasoning,
        "input": ["text"],
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        "contextWindow": 195000,
        "maxTokens": 8192,
        "api": "openai-completions",
    })

patch = {
    "models": {
        "providers": {
            "opencode": {
                "baseUrl": "https://opencode.ai/zen/v1",
                "api": "openai-completions",
                "models": models,
            }
        }
    }
}
json.dump(patch, open("/tmp/opencode-patch.json", "w"), indent=2)
print(f"Prepared {len(models)} models")
PY

openclaw config patch --file /tmp/opencode-patch.json
echo "Done. Restart gateway: openclaw gateway restart (or restart the LaunchAgent)"
