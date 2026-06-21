#!/bin/bash
# Pain Point Research Pipeline — Kimi K2 Enhanced
# Uses Kimi K2 subagent for reasoning-heavy phases

set -euo pipefail

WORKSPACE="$HOME/.openclaw/workspace"
ARCHIVE="$WORKSPACE/archive"
RESEARCH_DIR="$ARCHIVE/pain-point-research"
DATE=$(date +%Y-%m-%d)

echo "🤖 Phase 1: Kimi K2 Reddit Research"
# Spawn Kimi K2 to search Reddit and analyze pain points
openclaw sessions_spawn \
  --model "Kimi" \
  --task "Search Reddit for pain points in these subreddits: r/webscraping, r/Automate, r/VideoEditing, r/ContentCreation, r/LocalLLaMA, r/ClaudeAI, r/Entrepreneur, r/SmallBusiness, r/SaaS, r/startups. Look for keywords: frustrating, annoying, pain, broken, waste time, manual, tedious, error, failed, can't, impossible, hate, wish there was, someone should build, no tool does. For each pain point found, score it 1-10 on: pain severity, frequency of mentions, clarity of problem, solvability with AI agent. Return structured JSON with top 20 opportunities." \
  --output "$RESEARCH_DIR/kimi-research.json"

echo "🔍 Phase 2: Local Validation"
python3 "$WORKSPACE/scripts/phase2-skill-analyzer.py" \
  --input "$RESEARCH_DIR/kimi-research.json" \
  --criteria-file "$WORKSPACE/config/skill-criteria.json" \
  --output "$RESEARCH_DIR/feasible-opportunities.json"

echo "🤖 Phase 3: Kimi K2 ClawHub Audit"
# Spawn Kimi K2 to audit ClawHub and identify gaps
openclaw sessions_spawn \
  --model "Kimi" \
  --task "Check ClawHub (https://clawhub.openclaw.ai) for existing skills related to these opportunities. For each, identify: 1) If similar skill exists, 2) What's missing or could be improved, 3) Competitive gap score 1-10. Return structured JSON with gap analysis." \
  --input "$RESEARCH_DIR/feasible-opportunities.json" \
  --output "$RESEARCH_DIR/kimi-gap-analysis.json"

echo "📊 Phase 4: Merge & Rank"
python3 "$WORKSPACE/scripts/phase4-opportunity-ranker.py" \
  --input "$RESEARCH_DIR/kimi-gap-analysis.json" \
  --weights "pain:0.3,feasibility:0.25,market_size:0.25,competitive_gap:0.2" \
  --top-n 10 \
  --output "$RESEARCH_DIR/top-opportunities.json"

echo "🎨 Phase 5: Generate Report"
python3 "$WORKSPACE/scripts/phase5-report-generator.py" \
  --input "$RESEARCH_DIR/top-opportunities.json" \
  --template "$WORKSPACE/templates/pain-report-template.html" \
  --output "$ARCHIVE/pain-point-research.html"

echo "✅ Pipeline Complete — Next: Monday 9:00 AM AEDT"
