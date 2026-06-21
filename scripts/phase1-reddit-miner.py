#!/usr/bin/env python3
"""
Phase 1: Reddit Pain Point Miner
Scrapes Reddit for pain points and validates them against skill criteria.
"""

import argparse
import json
import re
from datetime import datetime
from typing import List, Dict, Any
import praw  # Reddit API

class RedditPainMiner:
    def __init__(self, subreddits: List[str], keywords: List[str], pain_threshold: float):
        self.subreddits = subreddits
        self.keywords = keywords
        self.pain_threshold = pain_threshold
        self.reddit = praw.Reddit(
            client_id="reddit_client_id",
            client_secret="reddit_client_secret",
            user_agent="PainPointResearch/1.0"
        )
    
    def mine_pain_points(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Mine Reddit for pain points."""
        pain_points = []
        
        for subreddit_name in self.subreddits:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Search for posts with pain keywords
            for post in subreddit.hot(limit=limit):
                pain_score = self._calculate_pain_score(post)
                if pain_score >= self.pain_threshold:
                    pain_point = {
                        "title": post.title,
                        "content": post.selftext,
                        "subreddit": subreddit_name,
                        "pain_score": pain_score,
                        "upvotes": post.score,
                        "comments": post.num_comments,
                        "url": f"https://reddit.com{post.permalink}",
                        "keywords_found": self._extract_keywords(post),
                        "timestamp": datetime.now().isoformat()
                    }
                    pain_points.append(pain_point)
        
        return sorted(pain_points, key=lambda x: x["pain_score"], reverse=True)
    
    def _calculate_pain_score(self, post) -> float:
        """Calculate pain score based on keywords, engagement, and sentiment."""
        score = 0.0
        
        # Keyword density (0-5)
        keyword_count = sum(1 for kw in self.keywords if kw.lower() in post.title.lower() or kw.lower() in post.selftext.lower())
        score += min(keyword_count * 0.5, 5)
        
        # Engagement (0-3)
        if post.score > 100:
            score += 3
        elif post.score > 50:
            score += 2
        elif post.score > 10:
            score += 1
        
        # Comment activity (0-2)
        if post.num_comments > 50:
            score += 2
        elif post.num_comments > 10:
            score += 1
        
        return min(score, 10)
    
    def _extract_keywords(self, post) -> List[str]:
        """Extract found keywords from post."""
        found = []
        text = f"{post.title} {post.selftext}".lower()
        for keyword in self.keywords:
            if keyword.lower() in text:
                found.append(keyword)
        return found

def main():
    parser = argparse.ArgumentParser(description="Mine Reddit for pain points")
    parser.add_argument("--subreddits", required=True, help="Comma-separated subreddit names")
    parser.add_argument("--keywords", required=True, help="Comma-separated keywords")
    parser.add_argument("--pain-threshold", type=float, default=7.0, help="Minimum pain score")
    parser.add_argument("--limit", type=int, default=100, help="Posts per subreddit")
    parser.add_argument("--output", required=True, help="Output JSON file")
    
    args = parser.parse_args()
    
    subreddits = [s.strip() for s in args.subreddits.split(",")]
    keywords = [k.strip() for k in args.keywords.split(",")]
    
    miner = RedditPainMiner(subreddits, keywords, args.pain_threshold)
    pain_points = miner.mine_pain_points(args.limit)
    
    with open(args.output, 'w') as f:
        json.dump(pain_points, f, indent=2)
    
    print(f"✅ Found {len(pain_points)} pain points (threshold: {args.pain_threshold})")
    print(f"📁 Saved to: {args.output}")

if __name__ == "__main__":
    main()