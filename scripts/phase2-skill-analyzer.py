#!/usr/bin/env python3
"""
Phase 2: Skill Feasibility Analyzer
Validates pain points against skill criteria to determine which can be built.
"""

import argparse
import json
from typing import List, Dict, Any

class SkillAnalyzer:
    def __init__(self, criteria_file: str):
        with open(criteria_file) as f:
            self.criteria = json.load(f)["skill_criteria"]
    
    def analyze(self, pain_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze each pain point for skill feasibility."""
        feasible = []
        
        for point in pain_points:
            analysis = self._analyze_point(point)
            if analysis["feasible"]:
                feasible.append({
                    **point,
                    **analysis,
                    "opportunity_score": self._calculate_opportunity_score(analysis)
                })
        
        return sorted(feasible, key=lambda x: x["opportunity_score"], reverse=True)
    
    def _analyze_point(self, point: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single pain point against criteria."""
        # This would use LLM or heuristics to score each criterion
        # For now, using placeholder logic
        
        analysis = {
            "can_be_automated": self._score_automation(point),
            "has_clear_input_output": self._score_clarity(point),
            "api_available": self._score_api_availability(point),
            "market_size": self._score_market_size(point),
            "price_point": self._score_price_point(point),
            "build_time": self._score_build_time(point),
        }
        
        # Weighted average
        total_score = sum(
            score * self.criteria[criterion]["weight"]
            for criterion, score in analysis.items()
        )
        
        analysis["feasible"] = total_score >= 6.0
        analysis["total_score"] = total_score
        
        return analysis
    
    def _score_automation(self, point: Dict[str, Any]) -> float:
        """Score if this can be automated (0-10)."""
        text = f"{point['title']} {point['content']}".lower()
        
        # Check for automation indicators
        auto_indicators = [
            "automatically", "auto", "script", "bot", "workflow",
            "every day", "every week", "repeatedly", "constantly"
        ]
        
        score = 5.0  # Base score
        for indicator in auto_indicators:
            if indicator in text:
                score += 1.5
        
        return min(score, 10)
    
    def _score_clarity(self, point: Dict[str, Any]) -> float:
        """Score if inputs/outputs are clear (0-10)."""
        text = f"{point['title']} {point['content']}".lower()
        
        # Check for clear input/output indicators
        clarity_indicators = [
            "input", "output", "data", "file", "url", "text",
            "image", "video", "csv", "json", "api"
        ]
        
        score = 5.0
        for indicator in clarity_indicators:
            if indicator in text:
                score += 1.0
        
        return min(score, 10)
    
    def _score_api_availability(self, point: Dict[str, Any]) -> float:
        """Score API availability (0-10)."""
        # Would check if relevant APIs exist
        # For now, assume 7/10 for most modern problems
        return 7.0
    
    def _score_market_size(self, point: Dict[str, Any]) -> float:
        """Score market size based on engagement (0-10)."""
        upvotes = point.get("upvotes", 0)
        comments = point.get("comments", 0)
        
        # Engagement score
        if upvotes > 500:
            return 9.0
        elif upvotes > 100:
            return 7.0
        elif upvotes > 50:
            return 6.0
        else:
            return 5.0
    
    def _score_price_point(self, point: Dict[str, Any]) -> float:
        """Score if this can be priced well (0-10)."""
        text = f"{point['title']} {point['content']}".lower()
        
        # B2B indicators = higher price tolerance
        b2b_indicators = [
            "team", "company", "business", "enterprise",
            "agency", "developer", "professional"
        ]
        
        score = 6.0
        for indicator in b2b_indicators:
            if indicator in text:
                score += 1.5
        
        return min(score, 10)
    
    def _score_build_time(self, point: Dict[str, Any]) -> float:
        """Score if MVP can be built quickly (0-10)."""
        text = f"{point['title']} {point['content']}".lower()
        
        # Complexity indicators (lower = faster build)
        complex_indicators = [
            "integration", "platform", "marketplace",
            "infrastructure", "database", "real-time"
        ]
        
        score = 8.0  # Assume most agent skills are quick
        for indicator in complex_indicators:
            if indicator in text:
                score -= 1.5
        
        return max(score, 3.0)
    
    def _calculate_opportunity_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall opportunity score."""
        return (
            analysis["can_be_automated"] * 0.3 +
            analysis["has_clear_input_output"] * 0.25 +
            analysis["api_available"] * 0.15 +
            analysis["market_size"] * 0.2 +
            analysis["price_point"] * 0.1
        )

def main():
    parser = argparse.ArgumentParser(description="Analyze skill feasibility")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--criteria-file", required=True, help="Criteria JSON file")
    parser.add_argument("--output", required=True, help="Output JSON file")
    
    args = parser.parse_args()
    
    with open(args.input) as f:
        pain_points = json.load(f)
    
    analyzer = SkillAnalyzer(args.criteria_file)
    feasible = analyzer.analyze(pain_points)
    
    with open(args.output, 'w') as f:
        json.dump(feasible, f, indent=2)
    
    print(f"✅ {len(feasible)}/{len(pain_points)} pain points are feasible as skills")
    print(f"📁 Saved to: {args.output}")

if __name__ == "__main__":
    main()