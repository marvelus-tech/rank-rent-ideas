from __future__ import annotations

from dataclasses import asdict
from statistics import median
from typing import Any, Dict, List


class PriceAnalyzer:
    """Simple pricing engine for underpriced listing detection."""

    def __init__(self, config: Dict[str, Any]):
        analyzer_cfg = config.get("analyzer", {})
        self.default_discount_threshold = float(analyzer_cfg.get("default_discount_threshold", 0.30))
        self.min_profit = float(analyzer_cfg.get("min_profit", 50.0))
        self.category_rules = analyzer_cfg.get("category_rules", {})
        self.manual_market_values = analyzer_cfg.get("manual_market_values", {})

    def estimate_market_value(self, listing: Dict[str, Any], peers: List[Dict[str, Any]]) -> float | None:
        category = (listing.get("category") or "default").lower()
        title = (listing.get("title") or "").lower()

        # Highest priority: manual value by exact title phrase.
        for phrase, value in self.manual_market_values.items():
            if phrase.lower() in title:
                return float(value)

        # Category rule with optional fallback.
        cat_rule = self.category_rules.get(category, {})
        if cat_rule.get("fixed_market_value"):
            return float(cat_rule["fixed_market_value"])

        # Use peer median from same category or all peers.
        peer_prices = [p.get("price") for p in peers if isinstance(p.get("price"), (int, float)) and p.get("price") > 0]
        if peer_prices:
            return float(median(peer_prices))

        if cat_rule.get("fallback_market_value"):
            return float(cat_rule["fallback_market_value"])

        return None

    def analyze(self, listings: List[Any]) -> List[Dict[str, Any]]:
        # Normalize dataclass or dict input
        normalized = [asdict(l) if hasattr(l, "__dataclass_fields__") else dict(l) for l in listings]

        output: List[Dict[str, Any]] = []
        for i, item in enumerate(normalized):
            price = item.get("price")
            if not isinstance(price, (int, float)):
                price = None

            category = (item.get("category") or "default").lower()
            cat_rule = self.category_rules.get(category, {})
            threshold = float(cat_rule.get("discount_threshold", self.default_discount_threshold))

            peers = [x for j, x in enumerate(normalized) if j != i and (x.get("category") or "default").lower() == category]
            market_value = self.estimate_market_value(item, peers)

            discount_ratio = None
            expected_profit = None
            opportunity = False

            if market_value and price is not None and market_value > 0:
                discount_ratio = max(0.0, (market_value - price) / market_value)
                expected_profit = market_value - price
                opportunity = discount_ratio >= threshold and expected_profit >= self.min_profit

            enriched = {
                **item,
                "market_value_estimate": market_value,
                "discount_ratio": discount_ratio,
                "expected_profit": expected_profit,
                "is_opportunity": opportunity,
                "discount_threshold": threshold,
            }
            output.append(enriched)

        return output

    @staticmethod
    def top_opportunities(analyzed: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        ops = [x for x in analyzed if x.get("is_opportunity")]
        ops.sort(key=lambda x: (x.get("expected_profit") or 0, x.get("discount_ratio") or 0), reverse=True)
        return ops[:limit]
