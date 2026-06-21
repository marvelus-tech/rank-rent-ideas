#!/bin/bash
# Prune ephemeral files under ~/.openclaw (destructive with --enforce)
# Usage: bash scripts/prune-ephemeral.sh [--dry-run] [--enforce]
# Default: dry-run (preview only)

set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
WORKSPACE="${WORKSPACE:-$OPENCLAW_HOME/workspace}"
DRY_RUN=true
if [[ "${1:-}" == "--enforce" ]] || [[ "${2:-}" == "--enforce" ]]; then
  DRY_RUN=false
fi

REMOVED=0
FREED_KB=0

print_summary() {
  local removed="$1" freed_kb="2"
  local size
  size=$(awk -v k="$freed_kb" 'BEGIN { if (k>=1048576) printf "%.1fG", k/1048576; else if (k>=1024) printf "%.0fM", k/1024; else printf "%dK", k }')
  if [ "$DRY_RUN" = true ]; then
    echo "🧹 *Storage Cleanup* (dry-run)\n\n📊 $removed paths would be pruned (~$size)"
  else
    echo "🧹 *Storage Cleanup*\n\n✅ Pruned $removed paths (~$size)"
  fi
}

maybe_remove() {
  local path="$1"
  [ -e "$path" ] || return 0

  local kb
  kb=$(du -sk "$path" 2>/dev/null | awk '{print $1}')
  kb=${kb:-0}

  if [ "$DRY_RUN" = false ]; then
    rm -rf "$path"
  fi
  REMOVED=$((REMOVED + 1))
  FREED_KB=$((FREED_KB + kb))
}

prune_older_than() {
  local dir="$1" days="$2"
  [ -d "$dir" ] || return 0
  while IFS= read -r -d '' item; do
    maybe_remove "$item"
  done < <(find "$dir" -mindepth 1 -maxdepth 1 -mtime +"$days" -print0 2>/dev/null)
}

# tmp/ — 7 day TTL
prune_older_than "$OPENCLAW_HOME/tmp" 7

# scratch/ — 14 day TTL
prune_older_than "$WORKSPACE/scratch" 14

# Caches (always safe)
while IFS= read -r -d '' d; do
  maybe_remove "$d"
done < <(find "$OPENCLAW_HOME" -type d -name __pycache__ -print0 2>/dev/null)

while IFS= read -r -d '' d; do
  maybe_remove "$d"
done < <(find "$OPENCLAW_HOME" -path '*/node_modules/.cache' -type d -print0 2>/dev/null)

# Leadgen debug dumps
if [ -d "$WORKSPACE/leadgen/data/debug" ]; then
  while IFS= read -r -d '' f; do
    maybe_remove "$f"
  done < <(find "$WORKSPACE/leadgen/data/debug" -type f -mtime +3 -print0 2>/dev/null)
fi

# Brownstone published audio (keep state JSON)
BROWNSTONE_WORK="$WORKSPACE/skills/brownstone-bleeding-edge/work"
if [ -d "$BROWNSTONE_WORK" ]; then
  while IFS= read -r -d '' f; do
    maybe_remove "$f"
  done < <(find "$BROWNSTONE_WORK" -type f \( -name '*.mp3' -o -name '*.aiff' \) -mtime +7 -print0 2>/dev/null)
fi

print_summary "$REMOVED" "$FREED_KB"
