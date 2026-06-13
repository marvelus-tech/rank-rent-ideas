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

log_action() {
  echo "$1"
}

maybe_remove() {
  local path="$1"
  local reason="$2"
  [ -e "$path" ] || return 0

  local kb
  kb=$(du -sk "$path" 2>/dev/null | awk '{print $1}')
  kb=${kb:-0}

  if [ "$DRY_RUN" = true ]; then
    log_action "[dry-run] would remove ($reason): $path ($(awk -v k="$kb" 'BEGIN { if (k>=1048576) printf "%.1fG", k/1048576; else if (k>=1024) printf "%.0fM", k/1024; else printf "%dK", k }'))"
  else
    rm -rf "$path"
    log_action "removed ($reason): $path"
  fi
  REMOVED=$((REMOVED + 1))
  FREED_KB=$((FREED_KB + kb))
}

prune_older_than() {
  local dir="$1" days="$2" reason="$3"
  [ -d "$dir" ] || return 0
  while IFS= read -r -d '' item; do
    maybe_remove "$item" "$reason"
  done < <(find "$dir" -mindepth 1 -maxdepth 1 -mtime +"$days" -print0 2>/dev/null)
}

echo "========================================="
echo "  PRUNE EPHEMERAL"
echo "  Mode: $([ "$DRY_RUN" = true ] && echo dry-run || echo ENFORCE)"
echo "  Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "========================================="

# tmp/ — 7 day TTL
prune_older_than "$OPENCLAW_HOME/tmp" 7 "tmp TTL"

# scratch/ — 14 day TTL
prune_older_than "$WORKSPACE/scratch" 14 "scratch TTL"

# Caches (always safe)
find "$OPENCLAW_HOME" -type d -name __pycache__ 2>/dev/null | while read -r d; do
  maybe_remove "$d" "__pycache__"
done

find "$OPENCLAW_HOME" -path '*/node_modules/.cache' -type d 2>/dev/null | while read -r d; do
  maybe_remove "$d" "webpack/node cache"
done

# Leadgen debug dumps
if [ -d "$WORKSPACE/leadgen/data/debug" ]; then
  find "$WORKSPACE/leadgen/data/debug" -type f -mtime +3 2>/dev/null | while read -r f; do
    maybe_remove "$f" "leadgen debug"
  done
fi

# Brownstone published audio (keep state JSON)
BROWNSTONE_WORK="$WORKSPACE/skills/brownstone-bleeding-edge/work"
if [ -d "$BROWNSTONE_WORK" ]; then
  find "$BROWNSTONE_WORK" -type f \( -name '*.mp3' -o -name '*.aiff' \) -mtime +7 2>/dev/null | while read -r f; do
    maybe_remove "$f" "brownstone audio TTL"
  done
fi

echo ""
if [ "$DRY_RUN" = true ]; then
  echo "Dry-run complete. $REMOVED paths would be affected (~$(awk -v k="$FREED_KB" 'BEGIN { if (k>=1048576) printf "%.1fG", k/1048576; else if (k>=1024) printf "%.0fM", k/1024; else printf "%dK", k }'))."
  echo "Run with --enforce to delete."
else
  echo "Pruned $REMOVED paths (~$(awk -v k="$FREED_KB" 'BEGIN { if (k>=1048576) printf "%.1fG", k/1048576; else if (k>=1024) printf "%.0fM", k/1024; else printf "%dK", k }'))."
fi
