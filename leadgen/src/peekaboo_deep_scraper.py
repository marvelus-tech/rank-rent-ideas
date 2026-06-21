#!/usr/bin/env python3
"""
Deep Peekaboo Scraper — Clicks into each business page to get website + full details.
Much slower than bulk mode (~30-60s per business) but gets complete data.

Usage:
    python3 peekaboo_deep_scraper.py "plumbers" "Victoria, Australia" --limit 5
"""

import argparse
import json
import re
import subprocess
import time
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path


class PeekabooDeepScraper:
    def __init__(self, limit: int = 5, delay: int = 15):
        self.limit = limit
        self.delay = delay
        self.browser_app = "Brave Browser"
        self.debug_dir = Path("data/debug/peekaboo")
        self.debug_dir.mkdir(parents=True, exist_ok=True)

    def _peek(self, *args: str) -> str:
        cmd = ["peekaboo"] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
            return result.stdout
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"[peekaboo error] {' '.join(args)}: {getattr(e, 'stderr', str(e))}", file=__import__('sys').stderr)
            return ""

    def _sleep(self, seconds: float | None = None) -> None:
        time.sleep(seconds or self.delay)

    def _focus_browser(self) -> None:
        self._peek("window", "focus", "--app", self.browser_app)
        self._sleep(1)

    def _read_clipboard(self) -> str:
        try:
            result = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
        except Exception:
            pass
        return ""

    def launch(self) -> None:
        print("[1/4] Launching Brave Browser → Google Maps...")
        self._peek("app", "quit", "--app", self.browser_app)
        self._sleep(3)
        self._peek("app", "launch", self.browser_app, "--open", "https://maps.google.com")
        self._sleep(10)
        self._focus_browser()

    def search(self, category: str, location: str) -> None:
        query = f"{category} in {location}"
        print(f"[2/4] Searching: '{query}'...")
        self._focus_browser()
        self._peek("hotkey", "--keys", "cmd,l", "--app", self.browser_app, "--no-auto-focus")
        self._sleep(1)
        encoded_query = query.replace(" ", "+")
        url = f"https://www.google.com/maps/search/{encoded_query}"
        self._peek("type", url, "--app", self.browser_app, "--clear", "--no-auto-focus")
        self._sleep(1)
        self._peek("press", "return", "--app", self.browser_app, "--no-auto-focus")
        print("Waiting for results to load...")
        self._sleep(12)

    def _extract_via_js(self) -> dict | None:
        """Use JavaScript console to extract business details."""
        # Open console
        self._peek("press", "f12", "--app", self.browser_app, "--no-auto-focus")
        self._sleep(2)

        # Type JS to extract data
        js = """var data={};var h1=document.querySelector('h1');data.name=h1?h1.innerText:'';var auth=document.querySelector('a[data-item-id="authority"]');data.website=auth?auth.href:'';var addr=document.querySelector('button[data-item-id="address"]');data.address=addr?addr.innerText:'';var phoneBtn=document.querySelector('button[data-item-id^="phone:"]');data.phone=phoneBtn?phoneBtn.innerText:'';var rating=document.querySelector('span[role="img"][aria-label*="star"]');data.rating=rating?rating.getAttribute('aria-label'):'';var ta=document.createElement('textarea');ta.value=JSON.stringify(data);document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta);"""

        self._peek("type", js, "--app", self.browser_app, "--no-auto-focus")
        self._sleep(1)
        self._peek("press", "return", "--app", self.browser_app, "--no-auto-focus")
        self._sleep(2)

        # Close console
        self._peek("press", "f12", "--app", self.browser_app, "--no-auto-focus")
        self._sleep(1)

        # Read clipboard
        text = self._read_clipboard()
        if not text:
            return None

        # Parse JSON from clipboard
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return None

    def extract(self, category: str, location: str, query: str) -> list[dict]:
        print(f"[3/4] Deep extraction: clicking into each business...")
        leads = []

        for idx in range(self.limit):
            print(f"  → Business {idx + 1}/{self.limit}...")
            self._focus_browser()
            self._sleep(1)

            y_pos = 220 + (idx % 5) * 120
            if idx > 0 and idx % 5 == 0:
                self._peek("scroll", "--direction", "down", "--amount", "5",
                           "--app", self.browser_app, "--no-auto-focus")
                self._sleep(2)

            # Click result
            self._peek("click", "--coords", f"300,{y_pos}", "--app", self.browser_app, "--no-auto-focus")
            self._sleep(10)

            # Extract via JavaScript
            data = self._extract_via_js()

            if data and data.get("name"):
                # Parse rating from string like "4.9 stars"
                rating_str = data.get("rating", "")
                rating_match = re.search(r'(\d+\.\d+|\d+)', rating_str)
                rating = float(rating_match.group(1)) if rating_match else None

                lead = {
                    "source_query": query,
                    "category": category,
                    "location": location,
                    "name": data.get("name", "").strip(),
                    "address": data.get("address") or None,
                    "phone": data.get("phone") or None,
                    "website": data.get("website") or None,
                    "rating": rating,
                    "place_id": None,
                    "discovered_at": datetime.now(UTC).isoformat(),
                    "scraper": "peekaboo-deep",
                }
                leads.append(lead)
                print(f"    ✓ {lead['name']}")
                if lead.get("website"):
                    print(f"      🌐 {lead['website']}")
                if lead.get("phone"):
                    print(f"      ☎️ {lead['phone']}")
            else:
                print("    ✗ Failed to extract details")

            # Go back
            self._peek("press", "escape", "--app", self.browser_app, "--no-auto-focus")
            self._sleep(2)
            self._peek("press", "escape", "--app", self.browser_app, "--no-auto-focus")
            self._sleep(1)

        return leads

    def save(self, leads: list[dict]) -> None:
        print(f"[4/4] Saving {len(leads)} leads...")
        out_json = Path("data/processed/peekaboo_deep_leads.json")
        out_json.parent.mkdir(parents=True, exist_ok=True)

        existing = []
        if out_json.exists():
            try:
                existing = json.loads(out_json.read_text())
            except json.JSONDecodeError:
                existing = []

        seen = {(l.get("name"), l.get("website")) for l in existing}
        new_leads = []
        for lead in leads:
            key = (lead.get("name"), lead.get("website"))
            if key not in seen and lead.get("name"):
                seen.add(key)
                new_leads.append(lead)

        all_leads = existing + new_leads
        out_json.write_text(json.dumps(all_leads, indent=2, default=str), encoding="utf-8")

        # CSV
        out_csv = Path("data/processed/peekaboo_deep_leads.csv")
        import csv
        fieldnames = ["name", "address", "phone", "website", "rating", "category", "location", "discovered_at", "scraper"]
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for lead in all_leads:
                writer.writerow({k: lead.get(k, "") for k in fieldnames})

        print(f"  → Total: {len(all_leads)} (+{len(new_leads)} new)")

    def run(self, category: str, location: str) -> list[dict]:
        query = f"{category} in {location}"
        print(f"\n{'='*60}")
        print(f"Peekaboo DEEP Scraper (Website Extraction)")
        print(f"Query: {query}")
        print(f"Limit: {self.limit}")
        print(f"{'='*60}\n")

        leads = []
        try:
            self.launch()
            self.search(category, location)
            leads = self.extract(category, location, query)
            self.save(leads)
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._peek("app", "quit", "--app", self.browser_app)
            print(f"\n✅ Done! Extracted {len(leads)} leads with websites.\n")
        return leads


def main():
    parser = argparse.ArgumentParser(description="Peekaboo Deep Scraper — Gets website URLs")
    parser.add_argument("category", help="Business category")
    parser.add_argument("location", help="Location")
    parser.add_argument("--limit", type=int, default=5, help="Max leads (default: 5)")
    parser.add_argument("--delay", type=int, default=8, help="Delay seconds (default: 8)")
    args = parser.parse_args()

    scraper = PeekabooDeepScraper(limit=args.limit, delay=args.delay)
    scraper.run(args.category, args.location)


if __name__ == "__main__":
    main()
