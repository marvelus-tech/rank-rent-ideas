#!/bin/bash
# One-time storage cleanup (2026-06-13). Re-run only with Okeito approval.
# Documents what the junkyard purge did. See DECISIONS.md + disk-audit.sh for ongoing hygiene.

set -euo pipefail
echo "This script was already executed on 2026-06-13."
echo "Use instead:"
echo "  bash scripts/prune-ephemeral.sh --dry-run"
echo "  bash scripts/disk-audit.sh"
echo ""
echo "Archived stale projects → workspace/archive/"
echo "Removed: consultation-webhook/venv, .venv-youtube-extract, npm lossless-claw duplicate,"
echo "  presentation/template node_modules, remotion cache/output, brownstone audio, tmp/, debug/"
