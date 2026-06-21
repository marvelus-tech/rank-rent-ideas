#!/usr/bin/env python3
"""
Phase 4: Opportunity Ranker
Ranks opportunities by weighted score: pain × feasibility × market × competitive gap.
"""

import argparse
import json
from typing import List, Dict, Any

class OpportunityRanker:
    def __init__(self, weights: str):
        # Parse weights string: "pain:0.3,feasibility:0.25,market_size:0.25,competitive_gap:0.2"
        self.weights = {}
        for pair in weights.split(","):
            key, value = pair.split(":")
            self.weights[key.strip()] = float(value.strip())
    
    def rank(self, opportunities: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """Rank opportunities by weighted score."""
        scored = []
        
        for opp in opportunities:
            score = self._calculate_score(opp)
            scored.append({
                **opp,
                "final_score": score,
                "score_breakdown": {
                    "pain": opp.get("pain_score", 0) * self.weights["pain"],
                    "feasibility": opp.get("total_score", 0) * self.weights["feasibility"],
                    "market_size": opp.get("market_size", 0) * self.weights["market_size"],
                    "competitive_gap": opp.get("competitive_score", 0) * self.weights["competitive_gap"]
                }
            })
        
        # Sort by final score
        ranked = sorted(scored, key=lambda x: x["final_score"], reverse=True)
        
        return ranked[:top_n]
    
    def _calculate_score(self, opp: Dict[str, Any]) -> float:
        """Calculate weighted opportunity score."""
        pain = opp.get("pain_score", 0) * self.weights.get("pain", 0.3)
        feasibility = opp.get("total_score", 0) * self.weights.get("feasibility", 0.25)
        market_size = opp.get("market_size", 0) * self.weights.get("market_size", 0.25)
        competitive_gap = opp.get("competitive_score", 0) * self.weights.get("competitive_gap", 0.2)
        
        return pain + feasibility + market_size + competitive_gap

def main():
    parser = argparse.ArgumentParser(description="Rank opportunities by score")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--weights", default="pain:0.3,feasibility:0.25,market_size:0.25,competitive_gap:0.2", help="Scoring weights")
    parser.add_argument("--top-n", type=int, default=10, help="Top N opportunities")
    parser.add_argument("--output", required=True, help="Output JSON file")
    
    args = parser.parse_args()
    
    with open(args.input) as f:
        opportunities = json.load(f)
    
    ranker = OpportunityRanker(args.weights)
    top = ranker.rank(opportunities, args.top_n)
    
    with open(args.output, 'w') as f:
        json.dump(top, f, indent=2)
    
    print(f"✅ Ranked top {len(top)} opportunities")
    print(f"📁 Saved to: {args.output}")
    
    # Print summary
    for i, opp in enumerate(top[:5], 1):
        print(f"\n{i}. {opp['title'][:50]}...")
        print(f"   Score: {opp['final_score']:.2f}/10")
        print(f"   Pain: {opp['pain_score']:.1f} | Feasibility: {opp.get('total_score', 0):.1f}")
        print(f"   Gap: {opp.get('gap_type', 'unknown')} | Competitive: {opp.get('competitive_score', 0):.1f}")

if __name__ == "__main__":
    main()