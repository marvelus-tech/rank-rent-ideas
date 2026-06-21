from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .obsidian_tracker import get_tracker


class OpportunityAlerter:
    def __init__(self, config: Dict[str, Any]):
        alert_cfg = config.get("alerts", {})
        self.console_enabled = bool(alert_cfg.get("console", True))
        self.file_enabled = bool(alert_cfg.get("file_export", True))
        self.webhook_url = alert_cfg.get("webhook_url") or ""
        self.rate_limit_seconds = float(alert_cfg.get("rate_limit_seconds", 10))
        self._last_sent = 0.0
        self.output_path = Path(alert_cfg.get("alerts_file", "output/opportunities_alerts.json"))
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize Obsidian tracker for duplicate suppression
        vault_path = alert_cfg.get("obsidian_vault_path")
        self.tracker = get_tracker(vault_path)
        self.dedup_enabled = bool(alert_cfg.get("dedup_enabled", True))

    def _throttle(self):
        elapsed = time.time() - self._last_sent
        if elapsed < self.rate_limit_seconds:
            time.sleep(self.rate_limit_seconds - elapsed)
        self._last_sent = time.time()

    def _format(self, item: Dict[str, Any]) -> str:
        discount = item.get("discount_ratio")
        discount_str = f"{discount * 100:.1f}%" if isinstance(discount, (int, float)) else "N/A"
        profit = item.get("expected_profit")
        profit_str = f"${profit:.2f}" if isinstance(profit, (int, float)) else "N/A"
        return (
            f"[OPPORTUNITY] {item.get('title', 'Unknown')}\n"
            f"Price: {item.get('price_raw') or item.get('price')} | Market est: {item.get('market_value_estimate')}\n"
            f"Discount: {discount_str} | Expected profit: {profit_str}\n"
            f"Location: {item.get('location', '')}\n"
            f"URL: {item.get('url', '')}\n"
        )

    def filter_new_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out previously seen listings using Obsidian tracking."""
        if not self.dedup_enabled:
            return opportunities
            
        new_opps = []
        for opp in opportunities:
            url = opp.get("url", "")
            if not url:
                continue
                
            if self.tracker.has_seen(url):
                # Already tracked - check if price changed significantly
                print(f"[dedup] Skipping already-seen listing: {opp.get('title', 'Unknown')[:50]}...")
                continue
            else:
                new_opps.append(opp)
                
        stats = self.tracker.get_stats()
        print(f"[dedup] Filtered {len(opportunities)} -> {len(new_opps)} new (total tracked: {stats['total_tracked']})")
        return new_opps

    def send(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not opportunities:
            return {"sent": 0, "file": None, "new_listings": 0}

        # Filter out duplicates before alerting
        new_opportunities = self.filter_new_opportunities(opportunities)
        
        if not new_opportunities:
            print("[alert] No new opportunities after deduplication.")
            return {"sent": 0, "file": None, "new_listings": 0}

        sent = 0
        exports = []

        for item in new_opportunities:
            msg = self._format(item)

            if self.console_enabled:
                print(msg)

            if self.file_enabled:
                exports.append(item)

            if self.webhook_url:
                self._throttle()
                try:
                    requests.post(self.webhook_url, json={"text": msg, "listing": item}, timeout=15)
                except Exception as e:
                    print(f"[alert] webhook failed: {e}")

            # Mark as seen in Obsidian (whether alerted or not, we track it)
            if self.dedup_enabled:
                self.tracker.mark_seen(item)

            sent += 1

        if self.file_enabled:
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(exports, f, indent=2, ensure_ascii=False)

        return {
            "sent": sent, 
            "file": str(self.output_path) if self.file_enabled else None,
            "new_listings": len(new_opportunities)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get alerter statistics including tracking info."""
        return {
            "dedup_enabled": self.dedup_enabled,
            "tracker_stats": self.tracker.get_stats()
        }
