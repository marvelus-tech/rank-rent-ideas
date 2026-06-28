#!/usr/bin/env python3
"""
Peekaboo-based Google Maps Lead Scraper
=========================================
Uses macOS UI automation (Peekaboo) to control Brave Browser
and scrape business leads from Google Maps.

Extraction method: Select all → copy → parse clipboard text
This captures ALL visible results in the left panel at once.

- No API keys needed (100% free)
- 10 leads per run (configurable)
- Slow but reliable
- Saves to MarvelUs-lead-gen JSON/CSV format

Usage:
    python3 peekaboo_scraper.py "coffee shops" "Melbourne, Australia"
    python3 peekaboo_scraper.py --category "plumbers" --location "Sydney" --limit 10
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path


class PeekabooMapsScraper:
    """Scrape Google Maps via Peekaboo + Brave Browser."""

    def __init__(self, limit: int = 10, delay: int = 12):
        self.limit = limit
        self.delay = delay
        self.leads: list[dict] = []
        self.debug_dir = Path("data/debug/peekaboo")
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        self.browser_app = "Brave Browser"

    # ------------------------------------------------------------------
    # Peekaboo wrappers
    # ------------------------------------------------------------------

    def _peek(self, *args: str, capture: bool = True) -> str:
        """Run a peekaboo CLI command."""
        cmd = ["peekaboo"] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"[peekaboo error] {' '.join(args)}: {e.stderr}", file=sys.stderr)
            return ""
        except subprocess.TimeoutExpired:
            print(f"[peekaboo timeout] {' '.join(args)}", file=sys.stderr)
            return ""

    def _sleep(self, seconds: float | None = None) -> None:
        """Human-ish pause."""
        time.sleep(seconds or self.delay)

    def _focus_browser(self) -> None:
        """Ensure Brave window is focused before interacting."""
        self._peek("window", "focus", "--app", self.browser_app)
        self._sleep(1)

    # ------------------------------------------------------------------
    # Browser lifecycle
    # ------------------------------------------------------------------

    def launch_maps(self) -> None:
        """Launch Brave Browser to Google Maps."""
        print("[1/4] Launching Brave Browser → Google Maps...")
        # First, ensure Brave isn't already running (clean state)
        self._peek("app", "quit", "--app", self.browser_app)
        self._sleep(3)
        self._peek("app", "launch", self.browser_app, "--open", "https://maps.google.com")
        self._sleep(10)
        self._focus_browser()

    def quit_brave(self) -> None:
        """Quit Brave Browser (ignore errors if already quit)."""
        print("[4/4] Quitting Brave Browser...")
        try:
            self._peek("app", "quit", "--app", self.browser_app)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, category: str, location: str) -> None:
        """Navigate to Google Maps search results."""
        query = f"{category} in {location}"
        print(f"[2/4] Searching: '{query}'...")

        self._focus_browser()

        # Use URL bar for direct navigation (most reliable)
        self._peek("hotkey", "--keys", "cmd,l", "--app", self.browser_app, "--no-auto-focus")
        self._sleep(1)

        encoded_query = query.replace(" ", "+")
        url = f"https://www.google.com/maps/search/{encoded_query}"
        self._peek("type", url, "--app", self.browser_app, "--clear", "--no-auto-focus")
        self._sleep(1)
        self._peek("press", "return", "--app", self.browser_app, "--no-auto-focus")
        
        # Wait for results to load (Google Maps is slow)
        print("Waiting for results to load...")
        self._sleep(12)

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    def extract_results(self, category: str, location: str, query: str) -> list[dict]:
        """Extract business listings from search results."""
        print(f"[3/4] Extracting leads...")
        leads: list[dict] = []

        self._focus_browser()

        # Click near top of page to focus content area
        # This ensures cmd+a selects page content including results list
        self._peek("click", "--coords", "300,150", "--app", self.browser_app, "--no-auto-focus")
        self._sleep(1)

        # Select all and copy to get accessible text content
        self._peek("hotkey", "--keys", "cmd,a", "--app", self.browser_app, "--no-auto-focus")
        self._sleep(0.5)
        self._peek("hotkey", "--keys", "cmd,c", "--app", self.browser_app, "--no-auto-focus")
        self._sleep(1)

        # Read clipboard
        clipboard_text = self._read_clipboard()
        
        if not clipboard_text:
            print("    ✗ Clipboard empty, no data extracted")
            return leads

        # Save raw clipboard for debugging
        debug_file = self.debug_dir / "last_clipboard.txt"
        debug_file.write_text(clipboard_text, encoding="utf-8")

        # Parse all businesses from clipboard
        leads = self._parse_all_businesses(clipboard_text, category, location, query)
        
        # Limit to requested number
        leads = leads[:self.limit]
        
        for lead in leads:
            print(f"    ✓ {lead['name']}")
            if lead.get("address"):
                print(f"      📍 {lead['address']}")

        return leads

    def _read_clipboard(self) -> str:
        """Read system clipboard text."""
        # Try pbpaste first (macOS native)
        try:
            result = subprocess.run(
                ["pbpaste"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
        except Exception:
            pass

        # Fallback to peekaboo clipboard
        try:
            result = subprocess.run(
                ["peekaboo", "clipboard", "--action", "get"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass

        return ""

    def _parse_all_businesses(self, text: str, category: str, location: str, query: str) -> list[dict]:
        """Parse all business listings from clipboard text."""
        leads: list[dict] = []
        
        # Split into lines and clean
        lines = [l.strip() for l in text.split('\n')]
        lines = [l for l in lines if l]  # Remove empty lines
        
        # Find business entry points
        # A business entry typically starts with a name line followed by a rating line
        i = 0
        while i < len(lines) - 1:
            # Look for rating pattern: "4.5(3,303)" OR "4.5(3,303) · A$1–20" (price is optional)
            rating_match = re.match(r'(\d+\.\d+|\d+)\s*\(([\d,]+)\)\s*(?:·\s*(.*))?', lines[i])
            
            if rating_match and i > 0:
                # Previous line is the business name
                name = lines[i - 1]
                
                # Skip if name looks like UI element or is too short
                if self._is_valid_name(name):
                    rating = float(rating_match.group(1))
                    reviews_str = rating_match.group(2).replace(',', '')
                    reviews = int(reviews_str) if reviews_str.isdigit() else None
                    price_info = rating_match.group(3)  # Could be price range or None
                    
                    # Next line should be category + address
                    category_address = lines[i + 1] if i + 1 < len(lines) else ""
                    cat, address = self._parse_category_address(category_address)
                    
                    # Description is next line (if not hours or quote)
                    description = None
                    if i + 2 < len(lines):
                        next_line = lines[i + 2]
                        if not next_line.startswith('"') and not re.match(r'Open|Closed|Opens|Closes|Website|Directions', next_line):
                            # If it doesn't have · it's likely a description
                            if ' · ' not in next_line and len(next_line) > 10:
                                description = next_line
                    
                    # Hours + phone extraction
                    hours = None
                    phone = None
                    for j in range(i + 2, min(i + 7, len(lines))):
                        line = lines[j]
                        # Skip website/directions icons
                        if line in ['Website', 'Directions', 'Share', 'Save']:
                            continue
                        # Skip review quotes
                        if line.startswith('"'):
                            continue
                        # Hours/phone line
                        if re.match(r'Open|Closed|Opens|Closes|Open 24 hours', line):
                            hours = line
                            # Extract phone if present: "Open 24 hours · +61 1300 100 977"
                            phone_match = re.search(r'·\s*([+\d\s()-]+\d)', line)
                            if phone_match:
                                phone = phone_match.group(1).strip()
                            break
                    
                    lead = {
                        "source_query": query,
                        "category": category,
                        "location": location,
                        "name": name,
                        "address": address,
                        "phone": phone,
                        "website": None,
                        "rating": rating,
                        "reviews": reviews,
                        "price_range": price_info,
                        "place_id": None,
                        "discovered_at": datetime.now(UTC).isoformat(),
                        "business_hours": hours,
                        "business_type": cat or category,
                        "description": description,
                        "scraper": "peekaboo",
                    }
                    leads.append(lead)
                
                # Move past this entry (skip at least 3 lines: name, rating, category/address)
                i += 3
            else:
                i += 1
        
        return leads

    @staticmethod
    def _is_valid_name(name: str) -> bool:
        """Check if a line looks like a business name."""
        if len(name) < 2 or len(name) > 80:
            return False
        # Skip common UI labels
        ui_labels = [
            "Ask Maps", "Saved", "Recents", "Get app", "Clear", "Done",
            "Price", "Rating", "Hours", "All filters", "Share",
            "Directions", "Save", "Nearby", "Send to phone",
            "All", "Latest", "Videos", "Menu", "Food & drink", "Vibe",
            "Overview", "Reviews", "About", "Reserve a table", "Order online",
        ]
        if name in ui_labels:
            return False
        # Skip lines that look like menu items (all lowercase common words)
        common_menu_items = ['coffee', 'espresso', 'cappuccino', 'latte', 'croissant', 
                            'cold brew coffee', 'iced coffee', 'tea', 'sandwich']
        if name.lower() in common_menu_items:
            return False
        return True

    @staticmethod
    def _parse_category_address(text: str) -> tuple[str | None, str | None]:
        """Parse category and address from a line like 'Coffee shop · 🕊 · 359 Little Bourke St'."""
        if not text:
            return None, None
        
        # Split by middle dot (·)
        parts = [p.strip() for p in text.split('·')]
        
        if len(parts) >= 3:
            # First part is category, last part is address
            category = parts[0]
            address = parts[-1]
            # Validate address contains street-like text
            if re.search(r'\d+\s+|St|Ave|Rd|Ln|Dr|Blvd|Way|Street|Avenue|Road', address, re.IGNORECASE):
                return category, address
            return category, None
        elif len(parts) == 2:
            # Could be category · address or just category · icon
            if re.search(r'\d+\s+|St|Ave|Rd|Ln|Dr|Blvd|Way|Street|Avenue|Road', parts[1], re.IGNORECASE):
                return parts[0], parts[1]
            return parts[0], None
        
        return None, None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_leads(self, leads: list[dict]) -> None:
        """Save leads to JSON and CSV."""
        print(f"[4/4] Saving {len(leads)} leads...")

        # JSON
        out_json = Path("data/processed/peekaboo_leads.json")
        out_json.parent.mkdir(parents=True, exist_ok=True)

        existing = []
        if out_json.exists():
            try:
                existing = json.loads(out_json.read_text())
            except json.JSONDecodeError:
                existing = []

        # Deduplicate by name+address
        seen = {(l.get("name"), l.get("address")) for l in existing}
        new_leads = []
        for lead in leads:
            key = (lead.get("name"), lead.get("address"))
            if key not in seen and lead.get("name"):
                seen.add(key)
                new_leads.append(lead)

        all_leads = existing + new_leads
        out_json.write_text(json.dumps(all_leads, indent=2, default=str), encoding="utf-8")

        # CSV
        out_csv = Path("data/processed/peekaboo_leads.csv")
        _write_csv(out_csv, all_leads)

        # Daily delta
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        delta_path = Path(f"data/reports/daily_delta_peekaboo_{today}.csv")
        delta_path.parent.mkdir(parents=True, exist_ok=True)
        _write_csv(delta_path, new_leads)

        print(f"  → Total leads: {len(all_leads)} (+{len(new_leads)} new)")
        print(f"  → JSON: {out_json}")
        print(f"  → CSV:  {out_csv}")
        print(f"  → Delta: {delta_path}")

    # ------------------------------------------------------------------
    # Main flow
    # ------------------------------------------------------------------

    def run(self, category: str, location: str) -> list[dict]:
        """Full scrape cycle."""
        query = f"{category} in {location}"
        print(f"\n{'='*60}")
        print(f"Peekaboo Maps Scraper")
        print(f"Query: {query}")
        print(f"Limit: {self.limit}")
        print(f"{'='*60}\n")

        leads = []
        try:
            self.launch_maps()
            self.search(category, location)
            leads = self.extract_results(category, location, query)
            self.save_leads(leads)
        except Exception as e:
            print(f"\n[ERROR] Scrape failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.quit_brave()
            print(f"\n✅ Done! Extracted {len(leads)} leads.\n")
        
        return leads


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _write_csv(path: Path, leads: list[dict]) -> None:
    import csv

    fieldnames = [
        "name", "address", "phone", "website", "website_missing", "email", "emails_found",
        "rating", "reviews", "price_range", "category", "location", "discovered_at", "scraper",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            writer.writerow({k: lead.get(k, "") for k in fieldnames})


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Peekaboo Google Maps Lead Scraper")
    parser.add_argument("category", help="Business category (e.g., 'coffee shops')")
    parser.add_argument("location", help="Location (e.g., 'Melbourne, Australia')")
    parser.add_argument("--limit", type=int, default=10, help="Max leads to extract (default: 10)")
    parser.add_argument("--delay", type=int, default=5, help="Seconds between actions (default: 5)")
    args = parser.parse_args()

    scraper = PeekabooMapsScraper(limit=args.limit, delay=args.delay)
    scraper.run(args.category, args.location)


if __name__ == "__main__":
    main()
