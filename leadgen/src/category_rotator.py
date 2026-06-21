#!/usr/bin/env python3
"""
Category rotator for Peekaboo scraper.
Picks the next category from a JSON list, avoiding cafes/restaurants.
"""

import json
from pathlib import Path

CONFIG_PATH = Path("config/peekaboo_categories.json")


def get_next_category() -> str:
    """Return the next category in rotation."""
    config = json.loads(CONFIG_PATH.read_text())
    cats = config["categories"]
    idx = config.get("current_index", 0) % len(cats)
    category = cats[idx]
    # Advance index
    config["current_index"] = (idx + 1) % len(cats)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    return category


def get_config() -> dict:
    """Return full config."""
    return json.loads(CONFIG_PATH.read_text())


if __name__ == "__main__":
    cat = get_next_category()
    print(cat)
