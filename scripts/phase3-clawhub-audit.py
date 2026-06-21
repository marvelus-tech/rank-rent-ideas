#!/usr/bin/env python3
"""
Phase 3: ClawHub Competitive Audit
Checks existing skills on ClawHub to find gaps and improvement opportunities.
"""

import argparse
import json
import requests
from typing import List, Dict, Any

class ClawHubAuditor:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.existing_skills = self._fetch_skills()
    
    def _fetch_skills(self) -> List[Dict[str, Any]]:
        """Fetch all skills from ClawHub."""
        try:
            response = requests.get(f"{self.api_url}/skills")
            return response.json().get("skills", [])
        except Exception as e:
            print(f"⚠️ Could not fetch ClawHub skills: {e}")
            return []
    
    def audit(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Audit each opportunity against existing skills."""
        audited = []
        
        for opp in opportunities:
            gap_analysis = self._analyze_gap(opp)
            audited.append({
                **opp,
                **gap_analysis,
                "competitive_score": self._calculate_competitive_score(gap_analysis)
            })
        
        return sorted(audited, key=lambda x: x["competitive_score"], reverse=True)
    
    def _analyze_gap(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive gap for an opportunity."""
        # Search for similar skills
        similar = self._find_similar_skills(opportunity)
        
        if not similar:
            return {
                "existing_skills": [],
                "gap_type": "greenfield",  # No competition
                "gap_score": 10.0,
                "improvement_areas": []
            }
        
        # Analyze gaps in existing skills
        best_similar = similar[0]
        improvement_areas = self._identify_improvements(best_similar, opportunity)
        
        return {
            "existing_skills": similar,
            "gap_type": "improvement",  # Can improve existing
            "gap_score": self._calculate_gap_score(best_similar, improvement_areas),
            "improvement_areas": improvement_areas
        }
    
    def _find_similar_skills(self, opportunity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find skills similar to this opportunity."""
        # Simple keyword matching (would be more sophisticated in production)
        keywords = set(opportunity.get("keywords_found", []))
        similar = []
        
        for skill in self.existing_skills:
            skill_keywords = set(skill.get("keywords", []))
            overlap = keywords & skill_keywords
            if len(overlap) > 0:
                similar.append({
                    **skill,
                    "overlap_score": len(overlap) / len(keywords)
                })
        
        return sorted(similar, key=lambda x: x["overlap_score"], reverse=True)[:3]
    
    def _identify_improvements(self, existing_skill: Dict[str, Any], opportunity: Dict[str, Any]) -> List[str]:
        """Identify how we could improve upon existing skill."""
        improvements = []
        
        # Check for common improvement areas
        text = f"{opportunity['title']} {opportunity['content']}".lower()
        
        if "better" in text or "improve" in text:
            improvements.append("better UX")
        if "faster" in text or "slow" in text:
            improvements.append("faster execution")
        if "cheaper" in text or "expensive" in text:
            improvements.append("lower price")
        if "more" in text or "integration" in text:
            improvements.append("more integrations")
        if "error" in text or "bug" in text or "break" in text:
            improvements.append("better error handling")
        if "custom" in text or "configure" in text:
            improvements.append("more customization")
        
        return improvements if improvements else ["better UX", "lower price"]
    
    def _calculate_gap_score(self, existing_skill: Dict[str, Any], improvements: List[str]) -> float:
        """Calculate gap score (0-10)."""
        # More improvements = bigger gap = better opportunity
        base_score = 5.0
        improvement_bonus = len(improvements) * 1.0
        return min(base_score + improvement_bonus, 10)
    
    def _calculate_competitive_score(self, gap_analysis: Dict[str, Any]) -> float:
        """Calculate competitive opportunity score."""
        if gap_analysis["gap_type"] == "greenfield":
            return 10.0  # No competition = best opportunity
        else:
            return gap_analysis["gap_score"]

def main():
    parser = argparse.ArgumentParser(description="Audit ClawHub for competitive gaps")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--clawhub-api", required=True, help="ClawHub API URL")
    parser.add_argument("--output", required=True, help="Output JSON file")
    
    args = parser.parse_args()
    
    with open(args.input) as f:
        opportunities = json.load(f)
    
    auditor = ClawHubAuditor(args.clawhub_api)
    audited = auditor.audit(opportunities)
    
    with open(args.output, 'w') as f:
        json.dump(audited, f, indent=2)
    
    print(f"✅ Audited {len(audited)} opportunities against ClawHub")
    print(f"📁 Saved to: {args.output}")

if __name__ == "__main__":
    main()