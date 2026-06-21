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

    def analyze(self, website_url: str | None, maps_phone: str | None = None) -> dict:
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

    @staticmethod
    def _empty_result(status: str) -> dict:
        return {
            "analysis_status": status,
            "has_chatbot": False,
            "has_click_to_call": False,
            "has_booking": False,
            "tech_sophistication_score": 0,
        }
