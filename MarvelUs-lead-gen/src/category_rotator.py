#!/usr/bin/env python3
"""
Category rotator for Peekaboo scraper.
Picks the next category from a JSON list, avoiding cafes/restaurants.
"""

import json
from pathlib import Path

CONFIG_PATH = Path("config/peekaboo_categories.json")


def get_next_category(full_service_bias: bool = False) -> str:
    """
    Phase 3: Return next category.
    When full_service_bias=True, strongly prefer categories known to produce
    multi-opportunity leads (AI Voice + SEO + Reputation + Booking).
    """
    config = json.loads(CONFIG_PATH.read_text())
    cats = config["categories"]

    if full_service_bias:
        # Phase 3 full-service priority order (curated for multi-service potential)
        fs_order = [
            "med spa", "beauty clinic", "skin clinic",
            "plumbers", "electricians", "hvac", "roofers",
            "dental clinic", "chiropractic", "physiotherapists",
            "lawyers", "accountants", "cleaning services",
            "pest control", "locksmiths", "builders", "landscapers"
        ]
        # Reorder cats to put full-service ones first, preserving relative order
        prioritized = []
        seen = set()
        for p in fs_order:
            for c in cats:
                if c.lower() == p.lower() and c not in seen:
                    prioritized.append(c)
                    seen.add(c)
        for c in cats:
            if c not in seen:
                prioritized.append(c)
        cats = prioritized

    idx = config.get("current_index", 0) % len(cats)
    category = cats[idx]
    config["current_index"] = (idx + 1) % len(cats)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    return category


def get_config() -> dict:
    """Return full config."""
    return json.loads(CONFIG_PATH.read_text())


if __name__ == "__main__":
    cat = get_next_category()
    print(cat)
