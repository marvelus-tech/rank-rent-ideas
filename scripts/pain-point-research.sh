#!/bin/bash
# Pain Point Research Pipeline — Systematic Approach
# Phase 1: Reddit Mining → Phase 2: ClawHub Audit → Phase 3: Opportunity Ranking

set -euo pipefail

WORKSPACE="$HOME/.openclaw/workspace"
ARCHIVE="$WORKSPACE/archive"
RESEARCH_DIR="$ARCHIVE/pain-point-research"
DATE=$(date +%Y-%m-%d)

echo "🔍 Phase 1: Mining Reddit for Pain Points"
python3 "$WORKSPACE/scripts/phase1-reddit-miner.py" \
  --subreddits "webscraping,Automate,VideoEditing,ContentCreation,LocalLLaMA,ClaudeAI,Entrepreneur,SmallBusiness, SaaS, startups" \
  --keywords "frustrating,annoying,pain,broken,waste time,manual,tedious,error,failed,can't,impossible,hate, wish there was, someone should build, no tool does" \
  --pain-threshold 7.0 \
  --output "$RESEARCH_DIR/raw-pain-points.json"

echo "📊 Phase 2: Analyzing Skill Feasibility"
python3 "$WORKSPACE/scripts/phase2-skill-analyzer.py" \
  --input "$RESEARCH_DIR/raw-pain-points.json" \
  --criteria-file "$WORKSPACE/config/skill-criteria.json" \
  --output "$RESEARCH_DIR/feasible-opportunities.json"

echo "🔎 Phase 3: ClawHub Competitive Audit"
python3 "$WORKSPACE/scripts/phase3-clawhub-audit.py" \
  --input "$RESEARCH_DIR/feasible-opportunities.json" \
  --clawhub-api "https://clawhub.openclaw.ai/api/v1/skills" \
  --output "$RESEARCH_DIR/gap-analysis.json"

echo "🏆 Phase 4: Ranking & Selection"
python3 "$WORKSPACE/scripts/phase4-opportunity-ranker.py" \
  --input "$RESEARCH_DIR/gap-analysis.json" \
  --weights "pain:0.3,feasibility:0.25,market_size:0.25,competitive_gap:0.2" \
  --top-n 10 \
  --output "$RESEARCH_DIR/top-opportunities.json"

echo "🎨 Phase 5: Generating Report"
python3 "$WORKSPACE/scripts/phase5-report-generator.py" \
  --input "$RESEARCH_DIR/top-opportunities.json" \
  --template "$WORKSPACE/templates/pain-report-template.html" \
  --output "$ARCHIVE/pain-point-research.html"

echo "✅ Pipeline Complete — Next: Monday 9:00 AM AEDT"
