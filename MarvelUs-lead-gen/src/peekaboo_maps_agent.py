#!/usr/bin/env python3
"""
Peekaboo Maps Lead Agent — Vision-driven Google Maps scraper.

Manus-style autonomous agent for extracting business leads from Google Maps.
Uses the PeekabooAgent framework with full vision loop:
  OBSERVE → ANALYZE → PLAN → ACT → VERIFY → RECOVER

Features:
  - Vision-first: screenshots + analysis before every click
  - Element targeting: clicks by ID instead of blind coordinates
  - Multi-strategy extraction: vision → JS injection → clipboard fallback
  - Self-correcting: retries failed actions with alternates
  - Resumable: saves state, can continue after interruption
  - Deep extraction: clicks into each business for website, phone, etc.
  - Intelligence scoring: scores leads inline for AI service need

Usage:
    python3 peekaboo_maps_agent.py "plumbers" "Victoria, Australia" --limit 10
    python3 peekaboo_maps_agent.py --resume  # resume from last state
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import traceback
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path
from typing import Any

from peekaboo_agent import (
    PeekabooAgent,
    AgentState,
    AgentError,
    PhaseError,
    ScreenshotAnalysis,
    extract_json_from_text,
)

# Optional: import intelligence scorer
sys.path.insert(0, str(Path(__file__).parent))
try:
    from intelligence_scorer import score_lead_intelligence, enrich_with_intelligence
    HAS_INTELLIGENCE = True
except ImportError:
    HAS_INTELLIGENCE = False


# ------------------------------------------------------------------
# Maps Lead Agent
# ------------------------------------------------------------------

class MapsLeadAgent(PeekabooAgent):
    """
    Autonomous agent for scraping business leads from Google Maps.
    """

    def __init__(
        self,
        category: str,
        location: str,
        limit: int = 10,
        state_file: str = "data/agent_state.json",
        debug_dir: str = "data/debug/maps_agent",
        mode: str = "autonomous",
    ):
        super().__init__(
            task_name="maps_lead_scrape",
            state_file=state_file,
            debug_dir=debug_dir,
            mode=mode,
            max_retries=3,
            delay_base=3.0,
        )
        self.category = category
        self.location = location
        self.limit = limit
        self.query = f"{category} in {location}"
        self.leads: list[dict] = []
        self.extraction_strategies = [
            self._extract_via_vision,
            self._extract_via_js_console,
            self._extract_via_clipboard,
        ]

    # ------------------------------------------------------------------
    # Main orchestration
    # ------------------------------------------------------------------

    def run(self, resume: bool = False) -> list[dict]:
        """
        Execute the full maps scraping workflow.
        """
        print(f"\n{'='*60}")
        print(f"🗺️  Maps Lead Agent")
        print(f"   Query: {self.query}")
        print(f"   Limit: {self.limit}")
        print(f"   Mode:  {self.mode}")
        print(f"{'='*60}\n")

        # Check for resume
        if resume and self.state.is_resumable("extract"):
            print(f"[agent] Resuming from phase: {self.state.phase}")
            self.leads = self.state.get_data("leads", [])
            print(f"[agent] Recovered {len(self.leads)} leads from state")
        else:
            self.state.start_task("maps_lead_scrape", category=self.category, location=self.location, limit=self.limit)
            self.state.set_data("leads", [])

        try:
            # Phase 1: Initialize browser
            if self.state.phase in ("idle", "init"):
                self.run_phase("init", self._phase_init)

            # Phase 2: Search
            if self.state.phase in ("idle", "init", "search"):
                self.run_phase("search", self._phase_search)

            # Phase 3: Extract leads (with scrolling)
            if self.state.phase in ("idle", "init", "search", "extract"):
                self._phase_extract_loop()

            # Phase 4: Intelligence scoring
            if self.state.phase in ("idle", "init", "search", "extract", "score"):
                self.run_phase("score", self._phase_score)

            # Phase 5: Save results
            if self.state.phase in ("idle", "init", "search", "extract", "score", "save"):
                self.run_phase("save", self._phase_save)

            print(f"\n{'='*60}")
            print(f"✅ SUCCESS: Extracted {len(self.leads)} leads")
            print(f"{'='*60}\n")

        except AgentError as e:
            print(f"\n🔥 Agent failed: {e}")
            self.state.log_error("agent", str(e))
            # Save whatever we got
            self._save_leads(self.leads)
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            traceback.print_exc()
            self.state.log_error("agent", f"Unexpected: {type(e).__name__}: {e}")
            self._save_leads(self.leads)
        finally:
            self.quit_browser()
            self.print_report()

        return self.leads

    # ------------------------------------------------------------------
    # Phase: Initialize
    # ------------------------------------------------------------------

    def _phase_init(self, analysis: ScreenshotAnalysis) -> bool:
        """Launch Brave and navigate to Google Maps."""
        print("[init] Ensuring browser is running...")
        self.ensure_browser(url="https://maps.google.com")
        self.sleep(8)  # Maps is slow to load

        # Verify Maps loaded
        analysis = self.quick_observe("init_verify")
        if "map" not in analysis.detected_ui and "search" not in analysis.detected_ui:
            # Maybe still loading
            print("[init] Maps not fully loaded, waiting...")
            self.sleep(5)
            analysis = self.quick_observe("init_verify_2")

        # Check for auth walls or errors
        if "auth_required" in analysis.error_flags or "captcha" in analysis.error_flags:
            raise PhaseError("Google Maps requires authentication or captcha")

        print(f"[init] Maps loaded successfully")
        return True

    # ------------------------------------------------------------------
    # Phase: Search
    # ------------------------------------------------------------------

    def _phase_search(self, analysis: ScreenshotAnalysis) -> bool:
        """Enter search query and submit."""
        print(f"[search] Entering query: '{self.query}'")

        # Focus browser
        self._peek("window", "focus", "--app", self.browser_app)
        self.sleep(1)

        # Try to click search box via element ID first
        search_element = self._find_search_element(analysis)
        if search_element:
            print(f"[search] Clicking search box element {search_element}")
            self._peek("click", "--on", search_element, "--app", self.browser_app, "--no-auto-focus")
        else:
            # Fallback: use hotkey to focus URL bar and navigate directly
            print("[search] Using URL bar navigation...")
            self._peek("hotkey", "--keys", "cmd,l", "--app", self.browser_app, "--no-auto-focus")
            self.sleep(0.5)

        # Type query
        encoded_query = self.query.replace(" ", "+")
        url = f"https://www.google.com/maps/search/{encoded_query}"
        self._peek("type", url, "--app", self.browser_app, "--clear", "--no-auto-focus")
        self.sleep(0.5)
        self._peek("press", "return", "--app", self.browser_app, "--no-auto-focus")

        # Wait for results
        print("[search] Waiting for results...")
        self.sleep(10)

        return True

    def _find_search_element(self, analysis: ScreenshotAnalysis) -> str | None:
        """Find the search box element ID from analysis."""
        for eid, desc in analysis.element_map.items():
            desc_lower = desc.lower()
            if any(kw in desc_lower for kw in ["search", "query", "input", "find"]):
                return eid
        return None

    # ------------------------------------------------------------------
    # Phase: Extract Loop (with scrolling)
    # ------------------------------------------------------------------

    def _phase_extract_loop(self) -> None:
        """Extract leads from search results, scrolling to load more."""
        self.state.set_phase("extract")
        target_count = self.limit
        scroll_attempts = 0
        max_scrolls = 10
        no_new_count = 0
        max_no_new = 2

        while len(self.leads) < target_count and scroll_attempts < max_scrolls:
            # Extract from current visible results
            new_leads = self._extract_visible_results()

            if new_leads:
                print(f"[extract] Got {len(new_leads)} leads from current view")
                for lead in new_leads:
                    if not self._is_duplicate(lead):
                        self.leads.append(lead)
                        self.state.set_data("leads", self.leads)
                        print(f"  ✓ {lead.get('name')} (total: {len(self.leads)}/{target_count})")
                        if len(self.leads) >= target_count:
                            break
                no_new_count = 0
            else:
                no_new_count += 1
                print(f"[extract] No new leads found (no_new streak: {no_new_count})")
                if no_new_count >= max_no_new:
                    print("[extract] No new leads after multiple attempts, stopping.")
                    break

            # Scroll for more results
            if len(self.leads) < target_count:
                print("[extract] Scrolling for more results...")
                scroll_success = self._scroll_results()
                if not scroll_success:
                    print("[extract] Scroll didn't load more results, stopping.")
                    break
                scroll_attempts += 1
                self.sleep(2)

        print(f"[extract] Extraction complete: {len(self.leads)} leads total")

    def _is_duplicate(self, lead: dict) -> bool:
        """Check if lead already extracted (by name + address)."""
        name = lead.get("name", "").lower().strip()
        address = lead.get("address", "") or ""
        for existing in self.leads:
            if (existing.get("name", "").lower().strip() == name and
                (existing.get("address") or "") == address):
                return True
        return False

    def _extract_visible_results(self) -> list[dict]:
        """Extract all visible business results from the current view."""
        print("[extract] Analyzing current results view...")

        # Take screenshot and analyze
        analysis = self.quick_observe("results_view")

        # Find business listing elements
        listings = self._find_listing_elements(analysis)
        if not listings:
            print("[extract] No listing elements found in current view")
            # Try a different approach - look for text-based businesses
            return self._extract_from_text(analysis.raw_text)

        leads = []
        for idx, (element_id, desc) in enumerate(listings[:5]):  # Max 5 per view
            if len(self.leads) + len(leads) >= self.limit:
                break

            print(f"  [extract] Opening listing {idx+1}: {desc[:40]}...")

            try:
                lead = self._extract_listing_detail(element_id, desc)
                if lead and lead.get("name"):
                    leads.append(lead)
            except Exception as e:
                print(f"    ✗ Failed to extract: {e}")
                self.state.log_error("extract_detail", str(e), {"element": element_id, "desc": desc})
                continue

        return leads

    def _find_listing_elements(self, analysis: ScreenshotAnalysis) -> list[tuple[str, str]]:
        """Find business listing elements from screenshot analysis."""
        listings = []
        for eid, desc in analysis.element_map.items():
            desc_lower = desc.lower()
            # Look for business-related element descriptions
            if any(kw in desc_lower for kw in [
                "result", "listing", "business", "place", "card",
                "name", "title", "heading"
            ]):
                listings.append((eid, desc))
        return listings

    def _extract_from_text(self, text: str) -> list[dict]:
        """Fallback: extract business names from raw analysis text."""
        leads = []
        # Look for business name patterns
        patterns = [
            r'"([^"]{3,50})"\s*[-–—]\s*(?:\d+\.\d+\s*stars?|\d+\s*reviews?)',
            r'([A-Z][A-Za-z\s\&\']{3,40})\s*\n\s*(\d+\.\d+)\s*\((\d+)\)',
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                name = match.group(1).strip()
                if name and len(name) > 3:
                    leads.append({
                        "name": name,
                        "address": None,
                        "phone": None,
                        "website": None,
                        "rating": None,
                        "reviews": None,
                        "source": "text_fallback",
                        "category": self.category,
                        "location": self.location,
                        "discovered_at": datetime.now(UTC).isoformat(),
                        "scraper": "peekaboo-agent",
                    })
        return leads

    def _extract_listing_detail(self, element_id: str, desc: str) -> dict | None:
        """
        Click a listing, extract details from detail panel, then close.
        Uses multiple extraction strategies with fallback.
        """
        # Click the listing
        self._peek("click", "--on", element_id, "--app", self.browser_app, "--no-auto-focus")
        self.sleep(3)

        # Verify detail panel opened
        analysis = self.quick_observe("detail_panel")
        if "detail" not in str(analysis.detected_ui).lower() and "info" not in str(analysis.detected_ui).lower():
            print("    ⚠️ Detail panel didn't open, trying Escape + retry...")
            self.press_key("escape")
            self.sleep(0.5)
            self._peek("click", "--on", element_id, "--app", self.browser_app, "--no-auto-focus")
            self.sleep(3)
            analysis = self.quick_observe("detail_panel_retry")

        # Try extraction strategies in order
        lead = None
        for strategy in self.extraction_strategies:
            try:
                lead = strategy(analysis)
                if lead and lead.get("name"):
                    print(f"    ✓ Extracted via {strategy.__name__}")
                    break
            except Exception as e:
                print(f"    ✗ {strategy.__name__} failed: {e}")
                continue

        # Close detail panel
        self.press_key("escape")
        self.sleep(1)

        # Verify we're back to list
        post_analysis = self.quick_observe("back_to_list")
        if "detail" in str(post_analysis.detected_ui).lower():
            # Still in detail, try clicking outside
            self._peek("click", "--coords", "800,400", "--app", self.browser_app, "--no-auto-focus")
            self.sleep(1)

        if lead:
            lead["category"] = self.category
            lead["location"] = self.location
            lead["source_query"] = self.query
            lead["discovered_at"] = datetime.now(UTC).isoformat()
            lead["scraper"] = "peekaboo-agent"
            lead["extraction_method"] = strategy.__name__ if lead else "unknown"

        return lead

    # ------------------------------------------------------------------
    # Extraction Strategies
    # ------------------------------------------------------------------

    def _extract_via_vision(self, analysis: ScreenshotAnalysis) -> dict | None:
        """
        Primary strategy: Use Peekaboo's vision analysis to read detail panel.
        """
        # Re-analyze with specific prompt for business details
        detail_analysis = self._peek(
            "image",
            "--path", analysis.screenshot_path,
            "--analyze",
            "Extract all visible business information from this Google Maps detail panel. "
            "Provide: business name, full address, phone number, website URL, "
            "Google rating (out of 5), number of reviews, and opening hours. "
            "Format as a JSON object with keys: name, address, phone, website, rating, reviews, hours.",
            timeout=30,
        )

        if not detail_analysis:
            return None

        # Try to parse JSON from analysis
        data = extract_json_from_text(detail_analysis)
        if data and data.get("name"):
            return {
                "name": data.get("name", "").strip(),
                "address": data.get("address") or None,
                "phone": self._normalize_phone(data.get("phone")),
                "website": self._normalize_url(data.get("website")),
                "rating": self._safe_float(data.get("rating")),
                "reviews": self._safe_int(data.get("reviews")),
                "business_hours": data.get("hours") or None,
                "extraction_confidence": 0.8,
            }

        return None

    def _extract_via_js_console(self, analysis: ScreenshotAnalysis) -> dict | None:
        """
        Strategy 2: Use JavaScript console injection (from deep_scraper).
        More reliable for structured data but requires console access.
        """
        # Open console
        self._peek("press", "f12", "--app", self.browser_app, "--no-auto-focus")
        self.sleep(2)

        # JS extraction script
        js = (
            'var data={};'
            'var h1=document.querySelector(\'h1\');'
            'data.name=h1?h1.innerText:\'\';'
            'var auth=document.querySelector(\'a[data-item-id="authority"]\');'
            'data.website=auth?auth.href:\'\';'
            'var addr=document.querySelector(\'button[data-item-id="address"]\');'
            'data.address=addr?addr.innerText:\'\';'
            'var phoneBtn=document.querySelector(\'button[data-item-id^="phone:"]\');'
            'data.phone=phoneBtn?phoneBtn.innerText:\'\';'
            'var rating=document.querySelector(\'span[role="img"][aria-label*="star"]\');'
            'data.rating=rating?rating.getAttribute(\'aria-label\'):\'\';'
            'var reviews=document.querySelector(\'button[data-item-id^="oloc:"]\');'
            'data.reviews=reviews?reviews.innerText:\'\';'
            'var ta=document.createElement(\'textarea\');'
            'ta.value=JSON.stringify(data);'
            'document.body.appendChild(ta);'
            'ta.select();'
            'document.execCommand(\'copy\');'
            'document.body.removeChild(ta);'
        )

        self._peek("type", js, "--app", self.browser_app, "--no-auto-focus")
        self.sleep(0.5)
        self._peek("press", "return", "--app", self.browser_app, "--no-auto-focus")
        self.sleep(2)

        # Close console
        self._peek("press", "f12", "--app", self.browser_app, "--no-auto-focus")
        self.sleep(0.5)

        # Read clipboard
        text = self._pbpaste()
        if not text:
            return None

        data = extract_json_from_text(text)
        if not data or not data.get("name"):
            return None

        # Parse rating from "4.9 stars"
        rating_str = data.get("rating", "")
        rating_match = re.search(r'(\d+\.\d+|\d+)', rating_str)
        rating = float(rating_match.group(1)) if rating_match else None

        # Parse reviews
        reviews_str = data.get("reviews", "")
        reviews_match = re.search(r'(\d[\d,]*)', reviews_str)
        reviews = int(reviews_match.group(1).replace(",", "")) if reviews_match else None

        return {
            "name": data.get("name", "").strip(),
            "address": data.get("address") or None,
            "phone": self._normalize_phone(data.get("phone")),
            "website": self._normalize_url(data.get("website")),
            "rating": rating,
            "reviews": reviews,
            "extraction_confidence": 0.7,
        }

    def _extract_via_clipboard(self, analysis: ScreenshotAnalysis) -> dict | None:
        """
        Strategy 3: Select all in detail panel and copy to clipboard.
        Fallback when other methods fail.
        """
        # Click in detail panel area to focus
        self._peek("click", "--coords", "300,300", "--app", self.browser_app, "--no-auto-focus")
        self.sleep(0.5)

        # Select all and copy
        self.hotkey("cmd,a")
        self.sleep(0.3)
        self.hotkey("cmd,c")
        self.sleep(1)

        text = self._pbpaste()
        if not text:
            return None

        # Parse business info from clipboard text
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        name = None
        address = None
        phone = None
        website = None
        rating = None
        reviews = None

        # Name is usually the first substantial line
        for line in lines[:5]:
            if len(line) > 3 and not line.startswith(("Open", "Closed", "Website", "Directions")):
                name = line
                break

        # Look for rating pattern
        for line in lines:
            rating_match = re.match(r'(\d+\.\d+)\s*\(([\d,]+)\)', line)
            if rating_match:
                rating = float(rating_match.group(1))
                reviews = int(rating_match.group(2).replace(",", ""))
                break

        # Look for address (contains street keywords)
        for line in lines:
            if re.search(r'\d+\s+|St\b|Ave\b|Rd\b|Ln\b|Dr\b|Blvd|Way|Street|Avenue|Road', line, re.IGNORECASE):
                address = line
                break

        # Look for phone
        for line in lines:
            phone_match = re.search(r'[+(]?[\d\s()-]{8,}', line)
            if phone_match:
                phone = phone_match.group(0).strip()
                break

        # Look for website (URL pattern)
        for line in lines:
            url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+)', line)
            if url_match:
                website = url_match.group(1)
                break

        if not name:
            return None

        return {
            "name": name,
            "address": address,
            "phone": self._normalize_phone(phone),
            "website": self._normalize_url(website),
            "rating": rating,
            "reviews": reviews,
            "extraction_confidence": 0.5,
        }

    # ------------------------------------------------------------------
    # Scroll
    # ------------------------------------------------------------------

    def _scroll_results(self) -> bool:
        """Scroll the results panel to load more. Returns True if new content likely loaded."""
        # Take pre-scroll screenshot
        pre_analysis = self.quick_observe("pre_scroll")
        pre_text = pre_analysis.raw_text

        # Scroll in the results area (left panel)
        self._peek("scroll", "--direction", "down", "--amount", "5",
                   "--app", self.browser_app, "--no-auto-focus")
        self.sleep(2)

        # Take post-scroll screenshot
        post_analysis = self.quick_observe("post_scroll")
        post_text = post_analysis.raw_text

        # Heuristic: if text changed significantly, new content loaded
        if post_text != pre_text:
            print("  [scroll] New content detected")
            return True

        # Check if we hit the bottom ("You've reached the end" or similar)
        end_indicators = ["end of list", "no more results", "reached the end", "all results"]
        for indicator in end_indicators:
            if indicator in post_text.lower():
                print(f"  [scroll] Hit end: '{indicator}'")
                return False

        return post_text != pre_text

    # ------------------------------------------------------------------
    # Phase: Score
    # ------------------------------------------------------------------

    def _phase_score(self, analysis: ScreenshotAnalysis) -> list[dict]:
        """Score leads for AI service need."""
        print(f"[score] Scoring {len(self.leads)} leads...")

        if not HAS_INTELLIGENCE:
            print("  [score] Intelligence scorer not available, skipping")
            return self.leads

        # For each lead with a website, we'd ideally fetch the HTML
        # For now, score based on available data (no website = high score)
        website_htmls = {}

        scored = []
        for lead in self.leads:
            intel = score_lead_intelligence(lead, website_htmls.get(lead.get("website")))
            lead.update(intel)
            scored.append(lead)
            score = intel.get("ai_service_score", 0)
            priority = intel.get("priority", "cold")
            print(f"  {lead.get('name')}: {score} ({priority})")

        self.leads = scored
        self.state.set_data("leads", self.leads)
        return scored

    # ------------------------------------------------------------------
    # Phase: Save
    # ------------------------------------------------------------------

    def _phase_save(self, analysis: ScreenshotAnalysis) -> bool:
        """Save leads to JSON, CSV, and Obsidian."""
        print(f"[save] Saving {len(self.leads)} leads...")
        self._save_leads(self.leads)
        return True

    def _save_leads(self, leads: list[dict]) -> None:
        """Persist leads to multiple formats."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")

        # JSON
        out_json = Path("data/processed/maps_agent_leads.json")
        out_json.parent.mkdir(parents=True, exist_ok=True)

        existing = []
        if out_json.exists():
            try:
                existing = json.loads(out_json.read_text())
            except json.JSONDecodeError:
                existing = []

        # Deduplicate
        seen = {(l.get("name"), l.get("address")) for l in existing}
        new_leads = []
        for lead in leads:
            key = (lead.get("name"), lead.get("address"))
            if key not in seen and lead.get("name"):
                seen.add(key)
                new_leads.append(lead)

        all_leads = existing + new_leads
        out_json.write_text(json.dumps(all_leads, indent=2, default=str), encoding="utf-8")
        print(f"  → JSON: {out_json} ({len(all_leads)} total, +{len(new_leads)} new)")

        # CSV
        out_csv = Path("data/processed/maps_agent_leads.csv")
        fieldnames = [
            "name", "address", "phone", "website", "rating", "reviews",
            "category", "location", "ai_service_score", "priority",
            "opportunities", "discovered_at", "scraper", "extraction_method",
        ]
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for lead in all_leads:
                writer.writerow({k: lead.get(k, "") for k in fieldnames})
        print(f"  → CSV:  {out_csv}")

        # Daily delta CSV
        delta_path = Path(f"data/reports/daily_delta_agent_{date_str}.csv")
        delta_path.parent.mkdir(parents=True, exist_ok=True)
        with delta_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for lead in new_leads:
                writer.writerow({k: lead.get(k, "") for k in fieldnames})
        print(f"  → Delta: {delta_path}")

        # Obsidian vault
        self._save_to_obsidian(new_leads, date_str)

        # Update state
        self.state.set_data("saved_count", len(all_leads))
        self.state.set_data("new_count", len(new_leads))

    def _save_to_obsidian(self, leads: list[dict], date_str: str) -> None:
        """Save leads to Obsidian vault."""
        vault_path = Path.home() / "Obsidian" / "Penelopi" / "Leads"
        if not vault_path.exists():
            print(f"  [obsidian] Vault not found at {vault_path}, skipping")
            return

        vault_path.mkdir(parents=True, exist_ok=True)

        for lead in leads:
            name = lead.get("name", "Unknown").replace("/", "-").replace(":", "-")
            score = lead.get("ai_service_score", 0)
            priority = lead.get("priority", "cold")

            filename = f"{date_str}_{name}.md"
            filepath = vault_path / filename

            # Avoid overwriting
            if filepath.exists():
                filepath = vault_path / f"{date_str}_{name}_{datetime.now(UTC).strftime('%H%M%S')}.md"

            opportunities = lead.get("opportunities", [])
            opp_str = ", ".join(opportunities) if opportunities else "N/A"

            content = f"""# {lead.get('name', 'Unknown Business')}

**Date:** {date_str}  
**Category:** {lead.get('category', 'N/A')}  
**Location:** {lead.get('location', 'N/A')}  
**Source:** Maps Agent (Peekaboo)

## Contact
- **Address:** {lead.get('address') or 'N/A'}
- **Phone:** {lead.get('phone') or 'N/A'}
- **Website:** {lead.get('website') or 'N/A'}

## Google Maps Data
- **Rating:** {lead.get('rating', 'N/A')}
- **Reviews:** {lead.get('reviews', 'N/A')}
- **Hours:** {lead.get('business_hours') or 'N/A'}

## AI Service Score
- **Score:** {score}/100
- **Priority:** {priority}
- **Opportunities:** {opp_str}

## Signals
- No website: {lead.get('signals', {}).get('no_website', 'N/A')}
- Missing call button: {lead.get('signals', {}).get('has_call_button', 'N/A') == False}
- Missing chat widget: {lead.get('signals', {}).get('has_chat_widget', 'N/A') == False}
- Poor SEO: {lead.get('signals', {}).get('poor_seo', 'N/A')}
- Low reviews: {lead.get('signals', {}).get('reviews', {}).get('needs_reputation_mgmt', 'N/A')}

## Action
{lead.get('action_suggestion', 'Review and prioritize outreach.')}

## Raw Data
```json
{json.dumps(lead, indent=2, default=str)}
```
"""
            filepath.write_text(content, encoding="utf-8")
            print(f"    → Obsidian: {filepath.name}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_phone(phone: str | None) -> str | None:
        if not phone:
            return None
        phone = phone.strip()
        # Remove common prefixes
        phone = re.sub(r'^(Tel[:\s]*|Phone[:\s]*|Call[:\s]*)', '', phone, flags=re.IGNORECASE)
        if re.search(r'\d', phone):
            return phone
        return None

    @staticmethod
    def _normalize_url(url: str | None) -> str | None:
        if not url:
            return None
        url = url.strip()
        if url.startswith("http"):
            return url
        if url.startswith("www."):
            return f"https://{url}"
        return None

    @staticmethod
    def _safe_float(value) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _safe_int(value) -> int | None:
        try:
            return int(str(value).replace(",", "")) if value is not None else None
        except (TypeError, ValueError):
            return None


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Peekaboo Maps Lead Agent — Vision-driven scraper")
    parser.add_argument("category", nargs="?", help="Business category (e.g., 'plumbers')")
    parser.add_argument("location", nargs="?", help="Location (e.g., 'Victoria, Australia')")
    parser.add_argument("--limit", type=int, default=10, help="Max leads to extract")
    parser.add_argument("--resume", action="store_true", help="Resume from last state")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode (pauses on errors)")
    parser.add_argument("--state-file", default="data/agent_state.json", help="State file path")
    parser.add_argument("--debug-dir", default="data/debug/maps_agent", help="Debug screenshots directory")
    args = parser.parse_args()

    if not args.category or not args.location:
        if not args.resume:
            parser.print_help()
            sys.exit(1)
        # Resume mode: read category/location from state
        state = AgentState.load(args.state_file)
        if not state.data.get("category"):
            print("No previous state found. Provide category and location.")
            sys.exit(1)
        category = state.data["category"]
        location = state.data["location"]
        limit = state.data.get("limit", 10)
        print(f"[resume] Using saved query: {category} in {location}")
    else:
        category = args.category
        location = args.location
        limit = args.limit

    mode = "interactive" if args.interactive else "autonomous"

    agent = MapsLeadAgent(
        category=category,
        location=location,
        limit=limit,
        state_file=args.state_file,
        debug_dir=args.debug_dir,
        mode=mode,
    )

    leads = agent.run(resume=args.resume)

    print(f"\n{'='*60}")
    print(f"FINAL RESULT: {len(leads)} leads extracted")
    print(f"{'='*60}")

    if leads:
        hot = sum(1 for l in leads if l.get("priority") == "hot")
        warm = sum(1 for l in leads if l.get("priority") == "warm")
        print(f"\nPriority breakdown:")
        print(f"  🔥 Hot:   {hot}")
        print(f"  🌡️ Warm:  {warm}")
        print(f"  ❄️ Cold:  {len(leads) - hot - warm}")

    return leads


if __name__ == "__main__":
    main()
