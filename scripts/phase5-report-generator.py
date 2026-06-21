#!/usr/bin/env python3
"""
Phase 5: Report Generator
Generates the final HTML report from ranked opportunities.
"""

import argparse
import json
from datetime import datetime
from typing import List, Dict, Any

class ReportGenerator:
    def __init__(self, template_file: str):
        with open(template_file) as f:
            self.template = f.read()
    
    def generate(self, opportunities: List[Dict[str, Any]]) -> str:
        """Generate HTML report from opportunities."""
        # Extract featured (top 1) and regular cards (rest)
        featured = opportunities[0] if opportunities else None
        cards = opportunities[1:4] if len(opportunities) > 1 else []
        
        # Generate HTML
        html = self.template
        html = html.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))
        html = html.replace("{{FEATURED}}", self._generate_featured(featured))
        html = html.replace("{{CARDS}}", self._generate_cards(cards))
        html = html.replace("{{STATS}}", self._generate_stats(opportunities))
        
        return html
    
    def _generate_featured(self, opp: Dict[str, Any]) -> str:
        """Generate featured opportunity HTML."""
        if not opp:
            return ""
        
        return f"""
        <div class="featured" id="featured-card" onclick="toggleFeatured()">
            <div class="copy-btn" onclick="event.stopPropagation(); copyCard('featured')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            </div>
            <div class="collapse-icon" onclick="event.stopPropagation(); toggleFeatured()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6"/></svg>
            </div>
            <div class="featured-tag">Quick Win</div>
            <div class="featured-content">
                <h2>{self._escape(opp['title'])}</h2>
                <p>{self._escape(opp['content'][:200])}...</p>
                <div class="featured-metrics">
                    <div class="featured-metric"><span class="featured-metric-value">{opp['pain_score']:.1f}</span><span class="featured-metric-label">Pain</span></div>
                    <div class="featured-metric"><span class="featured-metric-value">{opp.get('total_score', 0):.1f}</span><span class="featured-metric-label">Feasibility</span></div>
                    <div class="featured-metric"><span class="featured-metric-value">{opp.get('competitive_score', 0):.1f}</span><span class="featured-metric-label">Competitive Gap</span></div>
                </div>
            </div>
        </div>
        """
    
    def _generate_cards(self, opportunities: List[Dict[str, Any]]) -> str:
        """Generate opportunity cards HTML."""
        cards_html = []
        for i, opp in enumerate(opportunities, 1):
            cards_html.append(f"""
            <article class="card" id="card-{i}" onclick="toggleCard('card-{i}')">
                <div class="copy-btn" onclick="event.stopPropagation(); copyCard('card-{i}')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                </div>
                <div class="collapse-icon" onclick="event.stopPropagation(); toggleCard('card-{i}')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6"/></svg>
                </div>
                <div class="card-header">
                    <div class="card-title-wrap">
                        <h3 class="card-title">{self._escape(opp['title'])}</h3>
                    </div>
                </div>
                <div class="card-badges">
                    <span class="badge badge-pain">Pain {opp['pain_score']:.1f}</span>
                    <span class="badge badge-feas">Feasibility {opp.get('total_score', 0):.1f}</span>
                    <span class="badge badge-conf-high">Gap {opp.get('competitive_score', 0):.1f}</span>
                </div>
                <div class="card-content">
                    <div class="field">
                        <span class="field-label">Pain Severity <span class="tooltip" data-tip="How much users suffer (10 = excruciating)">ⓘ</span></span>
                        <span class="field-value">{self._escape(opp['content'][:150])}...</span>
                        <div class="progress-bar"><div class="progress-fill pain" style="--progress: {opp['pain_score']*10}%"></div></div>
                    </div>
                    <div class="field">
                        <span class="field-label">Target Customer <span class="tooltip" data-tip="Who would buy this">ⓘ</span></span>
                        <span class="field-value">{self._escape(opp.get('target', 'TBD'))}</span>
                    </div>
                    <div class="field">
                        <span class="field-label">Market Evidence <span class="tooltip" data-tip="Proof this pain exists">ⓘ</span></span>
                        <span class="field-value">{self._escape(opp.get('evidence', 'Reddit research'))}</span>
                    </div>
                    <div class="field">
                        <span class="field-label">Current Solutions <span class="tooltip" data-tip="What's already on the market">ⓘ</span></span>
                        <span class="field-value">{self._escape(opp.get('existing_skills', 'None found')[:100])}</span>
                    </div>
                    <div class="field">
                        <span class="field-label">Skill Description <span class="tooltip" data-tip="What the agent skill would do">ⓘ</span></span>
                        <span class="field-value">{self._escape(opp.get('skill_description', 'Auto-generated workflow'))}</span>
                    </div>
                    <div class="field">
                        <span class="field-label">Suggested Price <span class="tooltip" data-tip="What you could charge">ⓘ</span></span>
                        <span class="field-value">{self._escape(opp.get('price', '$29-99/mo'))}</span>
                    </div>
                </div>
            </article>
            """)
        
        return "\n".join(cards_html)
    
    def _generate_stats(self, opportunities: List[Dict[str, Any]]) -> str:
        """Generate stats bar HTML."""
        avg_pain = sum(o['pain_score'] for o in opportunities) / len(opportunities) if opportunities else 0
        avg_feas = sum(o.get('total_score', 0) for o in opportunities) / len(opportunities) if opportunities else 0
        
        return f"""
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-value">{len(opportunities)}</div>
                <div class="stat-label">Opportunities</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{avg_pain:.1f}</div>
                <div class="stat-label">Avg Pain Score</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{avg_feas:.1f}</div>
                <div class="stat-label">Avg Feasibility</div>
            </div>
        </div>
        """
    
    def _escape(self, text: str) -> str:
        """Escape HTML special characters."""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def main():
    parser = argparse.ArgumentParser(description="Generate HTML report")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--template", required=True, help="Template HTML file")
    parser.add_argument("--output", required=True, help="Output HTML file")
    
    args = parser.parse_args()
    
    with open(args.input) as f:
        opportunities = json.load(f)
    
    generator = ReportGenerator(args.template)
    html = generator.generate(opportunities)
    
    with open(args.output, 'w') as f:
        f.write(html)
    
    print(f"✅ Generated report with {len(opportunities)} opportunities")
    print(f"📁 Saved to: {args.output}")

if __name__ == "__main__":
    main()