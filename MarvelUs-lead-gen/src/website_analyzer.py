from __future__ import annotations

import re
import requests
from bs4 import BeautifulSoup

from .contact_extractor import ContactExtractor

CHATBOT_PATTERNS = [
    "intercom",
    "drift",
    "zendesk",
    "tawk.to",
    "livechat",
    "chatbot",
    "gorgias",
    "freshchat",
]
BOOKING_PATTERNS = [
    "book now",
    "schedule",
    "appointment",
    "calendly",
    "acuity",
    "mindbody",
    "squareup.com/appointments",
    "bookings",
]


class WebsiteAnalyzer:
    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.contact_extractor = ContactExtractor(timeout=min(timeout, 15))

    def analyze(self, website_url: str | None, maps_phone: str | None = None, config: dict | None = None) -> dict:
        contact_data = self.contact_extractor.extract_from_website(website_url, maps_phone=maps_phone)

        if not website_url:
            result = self._empty_result("no_website")
            result.update(contact_data)
            return result

        try:
            response = requests.get(website_url, timeout=self.timeout, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            html = response.text
        except Exception as exc:  # noqa: BLE001
            result = self._empty_result(f"fetch_error:{exc}")
            result.update(contact_data)
            return result

        soup = BeautifulSoup(html, "html.parser")
        text_blob = (soup.get_text(" ", strip=True) or "").lower()
        html_lower = html.lower()

        has_chatbot = any(p in html_lower for p in CHATBOT_PATTERNS)
        has_click_to_call = bool(soup.select('a[href^="tel:"]'))
        has_booking = any(p in html_lower or p in text_blob for p in BOOKING_PATTERNS)

        tech_score = self._tech_sophistication_score(html_lower, soup)

        result = {
            "analysis_status": "ok",
            "has_chatbot": has_chatbot,
            "has_click_to_call": has_click_to_call,
            "has_booking": has_booking,
            "tech_sophistication_score": tech_score,
        }

        # Phase 1: SEO signals (core foundation for full-service scoring)
        # Respect feature flag from config if provided
        seo_enabled = True
        if config:
            seo_enabled = config.get("features", {}).get("enable_full_seo_scoring", True)
            seo_enabled = seo_enabled and config.get("seo", {}).get("enabled", True)

        if seo_enabled:
            seo_signals = self._analyze_seo_signals(soup, html, website_url)
            result["seo_signals"] = seo_signals
            result["seo_health_score"] = seo_signals.get("seo_health_score", 0)
        else:
            result["seo_signals"] = self._empty_result("seo_disabled")["seo_signals"]
            result["seo_health_score"] = 0

        result.update(contact_data)
        return result

    def _tech_sophistication_score(self, html: str, soup: BeautifulSoup) -> int:
        score = 0

        if any(k in html for k in ["gtag(", "google-analytics", "segment.com", "hotjar"]):
            score += 20
        if any(k in html for k in ["react", "next.js", "vue", "nuxt", "webpack"]):
            score += 25
        if soup.find("meta", attrs={"name": "viewport"}):
            score += 15
        if len(soup.find_all("form")) > 0:
            score += 10
        if re.search(r"(book|schedule|appointment|contact)", soup.get_text(" ", strip=True), re.IGNORECASE):
            score += 10
        if any(k in html for k in ["hubspot", "mailchimp", "activecampaign", "klaviyo"]):
            score += 20

        return max(0, min(score, 100))

    def _analyze_seo_signals(self, soup: BeautifulSoup, html: str, url: str | None, config: dict | None = None) -> dict:
        """
        Phase 1: Real SEO signals extraction.
        Lightweight, fast, no external APIs. Returns structured data + seo_health_score (0-100).
        SpaceX-grade: always returns complete structure, graceful on bad HTML.
        """
        # Default weights (Phase 1 baseline)
        w = {
            "title": 25,
            "meta_description": 25,
            "schema": 15,
            "headings": 15,
            "alt_text": 5,
            "viewport": 5,
            "canonical": 5,
            "onpage_relevance": 5,
        }
        if config:
            w.update(config.get("seo", {}).get("weights", {}))

        signals = {
            "seo_health_score": 0,
            "has_meta_description": False,
            "meta_description_length": 0,
            "title": "",
            "title_length": 0,
            "title_quality": "unknown",
            "has_schema_markup": False,
            "heading_structure": {"h1_count": 0, "h2_count": 0, "has_multiple_h1": False},
            "alt_text_coverage": 0.0,
            "has_viewport_meta": False,
            "has_canonical": False,
            "onpage_score_breakdown": {},
        }

        if not soup:
            return signals

        # Title
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
            signals["title"] = title
            signals["title_length"] = len(title)

            if 30 <= len(title) <= 60:
                signals["title_quality"] = "good"
            elif len(title) < 30:
                signals["title_quality"] = "too_short"
            elif len(title) > 70:
                signals["title_quality"] = "too_long"
            else:
                signals["title_quality"] = "acceptable"

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            desc = meta_desc.get("content", "").strip()
            signals["has_meta_description"] = True
            signals["meta_description_length"] = len(desc)

        # Schema markup (JSON-LD or common microdata)
        schema_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
        if schema_scripts:
            signals["has_schema_markup"] = True
        else:
            if soup.find(attrs={"itemtype": True}) or soup.find(attrs={"itemprop": True}):
                signals["has_schema_markup"] = True

        # Heading structure
        h1s = soup.find_all("h1")
        h2s = soup.find_all("h2")
        signals["heading_structure"] = {
            "h1_count": len(h1s),
            "h2_count": len(h2s),
            "has_multiple_h1": len(h1s) > 1,
        }

        # Alt text coverage
        images = soup.find_all("img")
        if images:
            with_alt = sum(1 for img in images if img.get("alt") and img.get("alt").strip())
            signals["alt_text_coverage"] = round((with_alt / len(images)) * 100, 1)

        # Viewport meta (mobile friendly)
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if viewport and viewport.get("content"):
            signals["has_viewport_meta"] = True

        # Canonical
        canonical = soup.find("link", attrs={"rel": "canonical"})
        if canonical and canonical.get("href"):
            signals["has_canonical"] = True

        # On-page score breakdown (lightweight)
        onpage = {}
        title_lower = signals["title"].lower() if signals["title"] else ""
        onpage["title_has_business_keywords"] = any(kw in title_lower for kw in ["melbourne", "spa", "clinic", "plumber", "dentist", "roofer"])
        onpage["has_h1"] = signals["heading_structure"]["h1_count"] >= 1
        onpage["good_alt_coverage"] = signals["alt_text_coverage"] >= 70
        signals["onpage_score_breakdown"] = onpage

        # Compute final seo_health_score using configurable weights (Phase 1)
        score = 0
        if signals["title_length"] > 0:
            score += w["title"]
            if signals["title_quality"] in ("good", "acceptable"):
                score += 10  # quality bonus
        if signals["has_meta_description"]:
            score += w["meta_description"]
            if 80 <= signals["meta_description_length"] <= 160:
                score += 10
        if signals["has_schema_markup"]:
            score += w["schema"]
        if signals["heading_structure"]["h1_count"] >= 1:
            score += w["headings"]
            if not signals["heading_structure"]["has_multiple_h1"]:
                score += 5
        if signals["alt_text_coverage"] >= 50:
            score += w["alt_text"]
        if signals["has_viewport_meta"]:
            score += w["viewport"]
        if signals["has_canonical"]:
            score += w["canonical"]

        # On-page relevance bonus
        if onpage.get("title_has_business_keywords"):
            score += w["onpage_relevance"]
        if onpage.get("has_h1"):
            score += 5

        signals["seo_health_score"] = min(100, max(0, score))
        return signals

    @staticmethod
    def _empty_result(status: str) -> dict:
        # Fault-tolerant defaults for Phase 1 SEO + existing fields
        return {
            "analysis_status": status,
            "has_chatbot": False,
            "has_click_to_call": False,
            "has_booking": False,
            "tech_sophistication_score": 0,
            "seo_health_score": 0,
            "seo_signals": {
                "seo_health_score": 0,
                "has_meta_description": False,
                "meta_description_length": 0,
                "title": "",
                "title_length": 0,
                "title_quality": "unknown",
                "has_schema_markup": False,
                "heading_structure": {"h1_count": 0, "h2_count": 0, "has_multiple_h1": False},
                "alt_text_coverage": 0.0,
                "has_viewport_meta": False,
                "has_canonical": False,
                "onpage_score_breakdown": {},
            },
        }
