from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s().-]*)?(?:\(?\d{2,4}\)?[\s().-]*){2,4}\d{2,4}(?!\d)")

CONTACT_HINTS = ("contact", "about", "get in touch", "reach us")
SOCIAL_PATTERNS = {
    "facebook": ("facebook.com", "fb.com"),
    "linkedin": ("linkedin.com",),
    "instagram": ("instagram.com",),
}

GENERIC_EMAIL_PREFIXES = {
    "info",
    "contact",
    "support",
    "hello",
    "admin",
    "sales",
    "team",
    "office",
    "enquiries",
    "noreply",
    "no-reply",
}


class ContactExtractor:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def extract_from_maps_listing(self, listing: dict[str, Any]) -> str | None:
        return self._normalize_phone(str(listing.get("phone") or ""))

    def extract_from_website(self, website_url: str | None, maps_phone: str | None = None) -> dict[str, Any]:
        result = {
            "phone": self._normalize_phone(maps_phone or ""),
            "email": None,
            "emails_found": [],
            "contact_page_url": None,
            "social_links": {"facebook": None, "linkedin": None, "instagram": None},
            "contact_confidence": "low",
            "owner_email_detected": False,
            "has_complete_contact_info": False,
        }
        if not website_url:
            return result

        pages = self._candidate_pages(website_url)
        visited: set[str] = set()
        all_emails: set[str] = set()
        all_phones: set[str] = set(filter(None, [result["phone"]]))
        contact_page_url = None
        social_links = result["social_links"].copy()

        for page_url in pages:
            if page_url in visited:
                continue
            visited.add(page_url)
            html = self._fetch(page_url)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(" ", strip=True)
            normalized_text = self._deobfuscate(text)

            all_emails.update(self._extract_emails(normalized_text))
            all_phones.update(self._extract_phones(normalized_text))

            found_contact_page = self._find_contact_page(soup, page_url)
            if found_contact_page and not contact_page_url:
                contact_page_url = found_contact_page

            for key in social_links.keys():
                if social_links[key]:
                    continue
                social_links[key] = self._find_social(soup, key)

        prioritized_emails = sorted(all_emails, key=self._email_priority_key)
        primary_email = prioritized_emails[0] if prioritized_emails else None
        primary_phone = self._select_best_phone(all_phones)

        owner_email_detected = bool(primary_email and self._is_owner_like_email(primary_email))

        result.update(
            {
                "phone": primary_phone,
                "email": primary_email,
                "emails_found": prioritized_emails,
                "contact_page_url": contact_page_url,
                "social_links": social_links,
                "owner_email_detected": owner_email_detected,
                "has_complete_contact_info": bool(primary_email and primary_phone),
            }
        )
        result["contact_confidence"] = self._confidence(result)
        return result

    def _candidate_pages(self, website_url: str) -> list[str]:
        clean = website_url.strip()
        base = clean.rstrip("/")
        pages = [base, f"{base}/contact", f"{base}/about"]
        return pages

    def _fetch(self, url: str) -> str | None:
        try:
            resp = requests.get(url, timeout=self.timeout, headers=self.headers)
            if resp.status_code >= 400:
                return None
            return resp.text
        except Exception:  # noqa: BLE001
            return None

    def _deobfuscate(self, text: str) -> str:
        cleaned = text
        cleaned = re.sub(r"\s+\[at\]\s+|\s+\(at\)\s+|\s+at\s+", "@", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+\[dot\]\s+|\s+\(dot\)\s+|\s+dot\s+", ".", cleaned, flags=re.IGNORECASE)
        return cleaned

    def _extract_emails(self, text: str) -> set[str]:
        emails = {e.lower() for e in EMAIL_RE.findall(text)}
        filtered = {e for e in emails if not e.endswith((".png", ".jpg", ".jpeg", ".webp", ".svg"))}
        return filtered

    def _extract_phones(self, text: str) -> set[str]:
        phones: set[str] = set()
        for raw in PHONE_RE.findall(text):
            p = self._normalize_phone(raw)
            if p:
                phones.add(p)
        return phones

    def _normalize_phone(self, phone: str) -> str | None:
        digits = re.sub(r"\D", "", phone or "")
        if len(digits) < 8 or len(digits) > 15:
            return None
        if digits.startswith("00"):
            digits = digits[2:]
        if digits.startswith("61") and len(digits) == 11:
            return f"+{digits}"
        if len(digits) == 10 and digits.startswith("0"):
            return digits
        if phone.strip().startswith("+"):
            return f"+{digits}"
        return digits

    def _select_best_phone(self, phones: set[str]) -> str | None:
        if not phones:
            return None
        return sorted(phones, key=lambda p: (0 if p.startswith("+") else 1, -len(p)))[0]

    def _find_contact_page(self, soup: BeautifulSoup, current_url: str) -> str | None:
        for a in soup.select("a[href]"):
            href = (a.get("href") or "").strip()
            text = (a.get_text(" ", strip=True) or "").lower()
            if any(h in text for h in CONTACT_HINTS) or any(h in href.lower() for h in ("contact", "about")):
                absolute = urljoin(current_url, href)
                parsed = urlparse(absolute)
                if parsed.scheme in {"http", "https"}:
                    return absolute
        return None

    def _find_social(self, soup: BeautifulSoup, network: str) -> str | None:
        patterns = SOCIAL_PATTERNS.get(network, ())
        for a in soup.select("a[href]"):
            href = (a.get("href") or "").strip()
            if any(p in href for p in patterns):
                return href
        return None

    def _email_priority_key(self, email: str) -> tuple[int, int, str]:
        local = email.split("@", 1)[0].lower()
        ownerish = self._is_owner_like_email(email)
        generic = local in GENERIC_EMAIL_PREFIXES
        return (0 if ownerish else 1, 1 if generic else 0, email)

    def _is_owner_like_email(self, email: str) -> bool:
        local = email.split("@", 1)[0].lower()
        if local in GENERIC_EMAIL_PREFIXES:
            return False
        if any(token in local for token in ("owner", "founder", "director", "ceo", "principal")):
            return True
        return bool(re.match(r"^[a-z]+([._-][a-z]+)?$", local))

    def _confidence(self, result: dict[str, Any]) -> str:
        if result.get("email") and result.get("phone"):
            return "high"
        if result.get("email") or result.get("phone") or result.get("contact_page_url"):
            return "medium"
        return "low"
