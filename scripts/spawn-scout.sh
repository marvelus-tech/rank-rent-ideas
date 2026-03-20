#!/bin/bash
# Manual Solana Scout — Run this to spawn the scout agent manually
# Usage: bash scripts/spawn-scout.sh

SESSION=$(openclaw sessions spawn \
  --runtime subagent \
  --mode run \
  --model Flash \
  --task "You are the Solana Scout agent. Read agents/solana-scout.md for your mission briefing. Find 3-5 Solana small-cap tokens (under $100M market cap) with hold-to-earn reward mechanics similar to solcard.cc. Use web search extensively. Report findings using templates/handoff.md format. Include for each token: name, ticker, market cap, description, reward mechanic, confidence score (0-100), and links. Return results to main session." \
  2>&1 | grep -oE 'session:[^"]+' | head -1)

echo "Scout spawned: $SESSION"
echo "Session will report back when complete."
