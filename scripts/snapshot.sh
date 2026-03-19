#!/bin/bash
# Snapshot Script — Save current state before any config change
# Run: bash scripts/snapshot.sh [optional label]
# Snapshots stored in .snapshots/ with timestamp

set -euo pipefail
WORKSPACE="/Users/oktos/.openclaw/workspace"
LABEL="${1:-manual}"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
SNAP_DIR="$WORKSPACE/.snapshots/${TIMESTAMP}-${LABEL}"

mkdir -p "$SNAP_DIR"

# Copy all config-like files
for f in SOUL.md IDENTITY.md USER.md AGENTS.md MEMORY.md decisions.md SYSTEM_HARDENING.md HEARTBEAT.md TOOLS.md OWNERSHIP.md; do
    if [ -f "$WORKSPACE/$f" ]; then
        cp "$WORKSPACE/$f" "$SNAP_DIR/"
    fi
done

# Copy memory dir
if [ -d "$WORKSPACE/memory" ]; then
    cp -r "$WORKSPACE/memory" "$SNAP_DIR/"
fi

# Copy scripts
if [ -d "$WORKSPACE/scripts" ]; then
    cp -r "$WORKSPACE/scripts" "$SNAP_DIR/"
fi

# Record git state if available
if [ -d "$WORKSPACE/.git" ]; then
    cd "$WORKSPACE"
    git log -1 --format="commit: %H%nauthor: %an%ndate: %ai%nsubject: %s" > "$SNAP_DIR/git-state.txt"
    git diff --stat >> "$SNAP_DIR/git-state.txt" 2>/dev/null || true
fi

echo "✅ Snapshot saved to: $SNAP_DIR"
echo "   Files: $(find "$SNAP_DIR" -type f | wc -l | tr -d ' ')"
echo "   Size: $(du -sh "$SNAP_DIR" | cut -f1)"
