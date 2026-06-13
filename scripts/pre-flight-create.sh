#!/bin/bash
# Pre-flight gate before creating venvs, node projects, or top-level dirs
# Usage: bash scripts/pre-flight-create.sh <type> <name> [extra args]
# Types: python | node | presentation | repo | dir
# Exit 0 = allowed, 1 = blocked (message on stderr)

set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
TYPE="${1:-}"
NAME="${2:-}"

fail() {
  echo "PRE-FLIGHT BLOCKED: $1" >&2
  echo "See ~/Obsidian/Penelopi/DECISIONS.md → Storage & Workspace Hygiene" >&2
  exit 1
}

warn() {
  echo "PRE-FLIGHT WARN: $1" >&2
}

if [ -z "$TYPE" ] || [ -z "$NAME" ]; then
  echo "Usage: bash scripts/pre-flight-create.sh <python|node|presentation|repo|dir> <name>" >&2
  exit 1
fi

count_venvs() {
  find "$OPENCLAW_HOME" \( -type d -name venv -o -type d -name .venv -o -type d -name '.venv-*' \) 2>/dev/null | wc -l | tr -d ' '
}

count_node_modules() {
  find "$OPENCLAW_HOME" -type d -name node_modules 2>/dev/null | wc -l | tr -d ' '
}

case "$TYPE" in
  dir)
    if [[ "$NAME" != scratch/* && "$NAME" != active/* && "$NAME" != archive/* ]]; then
      fail "No new top-level workspace folder '$NAME'. Use scratch/$NAME, active/$NAME, or get Okeito approval."
    fi
    ;;
  presentation)
    fail "Presentations must be single HTML. Copy presentations/2026-06-12-claude-for-business/index.html — do not scaffold Vite/npm for '$NAME'."
    ;;
  repo)
    fail "No nested git repos in workspace. Put '$NAME' in ~/Projects/ or use the workspace monorepo."
    ;;
  python)
    VENV_COUNT=$(count_venvs)
    if [ "$VENV_COUNT" -ge 2 ] && [ ! -d "$WORKSPACE/.venv" ]; then
      warn "Already $VENV_COUNT venvs under ~/.openclaw. Prefer workspace/.venv before creating another for '$NAME'."
    fi
    if [ -f "$WORKSPACE/$NAME/requirements.txt" ]; then
      if grep -qiE 'torch|whisperx|tensorflow|onnxruntime' "$WORKSPACE/$NAME/requirements.txt" 2>/dev/null; then
        fail "requirements.txt for '$NAME' lists forbidden ML packages. Use tools/whisper-env or faster-whisper only."
      fi
    fi
    REQ="${3:-}"
    if echo "$REQ" | grep -qiE 'torch|whisperx|tensorflow|onnxruntime'; then
      fail "Requested package is forbidden without Okeito approval: $REQ"
    fi
    ;;
  node)
    NM_COUNT=$(count_node_modules)
    if [ "$NM_COUNT" -ge 3 ]; then
      warn "Already $NM_COUNT node_modules trees. Prefer a shared workspace install before npm init for '$NAME'."
    fi
    if [[ "$NAME" == presentations/* ]]; then
      fail "No node_modules in presentations/. Use the HTML template instead."
    fi
    ;;
  *)
    fail "Unknown type '$TYPE'. Use: python | node | presentation | repo | dir"
    ;;
esac

echo "PRE-FLIGHT OK: $TYPE '$NAME'"
exit 0
