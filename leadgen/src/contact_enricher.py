"""Contact enrichment module — extracts emails, phones, socials from business websites."""
from __future__ import annotations

import json
import re
import time
import random
from urllib.parse import urljoin, urlparse
from pathlib import Path
from typing import Any

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)
PHONE_RE = re.compile(
    r"(?:\+|\b00)[\d\s\-\(\)]{7,20}\b|\b(?:0[\d\s\-\(\)]{8,15})\b",
    re.IGNORECASE,
)
SOCIAL_PATTERNS = {
    "facebook": re.compile(r"https?://(?:www\.)?facebook\.com/[^\s\"<>]+", re.IGNORECASE),
    "instagram": re.compile(r"https?://(?:www\.)?instagram\.com/[^\s\"<>]+", re.IGNORECASE),
    "linkedin": re.compile(r"https?://(?:www\.)?linkedin\.com/(?:company|in)/[^\s\"<>]+", re.IGNORECASE),
    "twitter": re.compile(r"https?://(?:www\.)?(?:twitter|x)\.com/[^\s\"<>]+", re.IGNORECASE),
    "youtube": re.compile(r"https?://(?:www\.)?youtube\.com/(?:channel|c|user|@)[^\s\"<>]+", re.IGNORECASE),
}

CONTACT_PATHS = ["/contact", "/contact-us", "/about", "/about-us", "/get-in-touch"]


def _extract_from_text(text: str) -> dict[str, Any]:
    """Extract emails and phones from raw text."""
    emails = list(set(EMAIL_RE.findall(text)))
    phones = list(set(PHONE_RE.findall(text)))
    return {
        "emails": emails,
        "phones": phones,
    }


def _extract_socials(text: str) -> dict[str, str | None]:
    """Extract social media links from raw text."""
    result: dict[str, str | None] = {}
    for platform, pattern in SOCIAL_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            # Take first match, strip trailing comma/slash noise
            first = matches[0].rstrip(",")
            result[platform] = first
        else:
            result[platform] = None
    return result


def _is_contact_page(url: str) -> bool:
    """Check if URL looks like a contact page."""
    lowered = url.lower()
    return any(lowered.endswith(p) for p in CONTACT_PATHS) or "/contact" in lowered


def _normalize_email(email: str) -> str:
    """Clean up extracted email."""
    email = email.strip().rstrip(".").rstrip(",")
    # Remove common obfuscation
    email = email.replace("[at]", "@").replace("(at)", "@").replace(" at ", "@")
    return email


def _clean_phones(phones: list[str]) -> list[str]:
    """Deduplicate and clean phone numbers."""
    seen: set[str] = set()
    cleaned: list[str] = []
    for p in phones:
        normalized = re.sub(r"[^\d+]", "", p)
        if normalized not in seen and len(normalized) >= 8:
            seen.add(normalized)
            cleaned.append(p.strip())
    return cleaned


def _score_contact_confidence(
    emails: list[str],
    phones: list[str],
    has_contact_page: bool,
) -> str:
    """Score how complete the contact info is."""
    score = 0
    if emails:
        score += 40
    if len(emails) >= 2:
        score += 10
    if phones:
        score += 30
    if has_contact_page:
        score += 20

    if score >= 80:
        return "high"
    if score >= 50:
        return "medium"
    if score >= 20:
        return "low"
    return "none"


class ContactEnricher:
    """Enrich leads with contact info scraped from their websites."""

    def __init__(
        self,
        headless: bool = True,
        slow_mo: int = 500,
        timeout_ms: int = 8000,
        delay_seconds: int = 2,
        max_lead_seconds: int = 25,
    ):
        self.headless = headless
        self.slow_mo = slow_mo
        self.timeout_ms = timeout_ms
        self.delay_seconds = delay_seconds
        self.max_lead_seconds = max_lead_seconds
        self.debug_dir = Path("data/debug/contact_enrich")
        self.debug_dir.mkdir(parents=True, exist_ok=True)

    def enrich_lead(self, lead: dict[str, Any]) -> dict[str, Any]:
        """Enrich a single lead with contact info from its website."""
        website = lead.get("website")
        if not website:
            lead["email"] = None
            lead["emails_found"] = []
            lead["contact_page_url"] = None
            lead["social_links"] = {k: None for k in SOCIAL_PATTERNS}
            lead["contact_confidence"] = "none"
            lead["has_complete_contact_info"] = False
            return lead

        result = self._scrape_website(website)

        # Merge with existing Maps phone if we didn't find one on site
        maps_phone = lead.get("phone")
        all_phones = result["phones"]
        if maps_phone and maps_phone not in all_phones:
            all_phones.append(maps_phone)

        emails = [_normalize_email(e) for e in result["emails"]]
        emails = [e for e in emails if ".jpg" not in e.lower() and ".png" not in e.lower()]

        lead["email"] = emails[0] if emails else None
        lead["emails_found"] = emails
        lead["phones_found"] = _clean_phones(all_phones)
        lead["contact_page_url"] = result.get("contact_page_url")
        lead["social_links"] = result["socials"]
        lead["contact_confidence"] = _score_contact_confidence(
            emails, all_phones, bool(result.get("contact_page_url"))
        )
        lead["has_complete_contact_info"] = bool(emails and all_phones)
        lead["website_scraped_at"] = result.get("scraped_at")
        lead["website_scrape_success"] = result.get("success", False)

        return lead

    def _scrape_website(self, url: str) -> dict[str, Any]:
        """Scrape a single website for contact info (fast version)."""
        if not HAS_PLAYWRIGHT:
            return {"emails": [], "phones": [], "socials": {}, "success": False, "error": "playwright not installed"}

        start_time = time.time()
        result: dict[str, Any] = {
            "emails": [],
            "phones": [],
            "socials": {},
            "contact_page_url": None,
            "success": False,
            "scraped_at": None,
            "error": None,
        }

        if not url.startswith("http"):
            url = "https://" + url
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo,
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                )
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/123.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 800},
                )
                page = context.new_page()

                # Step 1: Visit homepage (fast, no extra sleep)
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                    homepage_text = page.content()
                except Exception as e:
                    result["error"] = f"homepage failed: {e}"
                    browser.close()
                    return result

                homepage_extracts = _extract_from_text(homepage_text)
                homepage_socials = _extract_socials(homepage_text)

                result["emails"].extend(homepage_extracts["emails"])
                result["phones"].extend(homepage_extracts["phones"])
                result["socials"] = homepage_socials

                # Step 2: Try ONE contact page only (fastest path)
                contact_url = None
                for path in ["/contact", "/contact-us", "/about"]:
                    if time.time() - start_time > self.max_lead_seconds:
                        break
                    candidate = urljoin(base_url, path)
                    try:
                        page.goto(candidate, wait_until="domcontentloaded", timeout=self.timeout_ms // 2)
                        contact_text = page.content()
                        if contact_text and len(contact_text) > 500:
                            contact_extracts = _extract_from_text(contact_text)
                            result["emails"].extend(contact_extracts["emails"])
                            result["phones"].extend(contact_extracts["phones"])
                            contact_socials = _extract_socials(contact_text)
                            for k, v in contact_socials.items():
                                if v and not result["socials"].get(k):
                                    result["socials"][k] = v
                            contact_url = candidate
                            break
                    except Exception:
                        continue

                result["contact_page_url"] = contact_url
                result["success"] = True
                result["scraped_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                browser.close()

        except Exception as e:
            result["error"] = str(e)

        result["emails"] = list(set(result["emails"]))
        result["phones"] = list(set(result["phones"]))
        result["scrape_duration_seconds"] = round(time.time() - start_time, 2)
        return result

    def enrich_leads(self, leads: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Enrich multiple leads."""
        enriched = []
        for i, lead in enumerate(leads):
            print(f"  [{i+1}/{len(leads)}] Enriching: {lead.get('name', 'Unknown')}...")
            enriched.append(self.enrich_lead(lead))
        return enriched


def enrich_leads_file(
    input_path: str | Path,
    output_path: str | Path | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Enrich leads from a JSON file and save results."""
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return []

    leads = []
    try:
        leads = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"Invalid JSON in {input_path}")
        return []

    if not isinstance(leads, list):
        print("Expected JSON array of leads")
        return []

    if limit:
        leads = leads[:limit]

    print(f"Enriching {len(leads)} leads...")
    enricher = ContactEnricher()
    enriched = enricher.enrich_leads(leads)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(enriched, indent=2, default=str), encoding="utf-8")
        print(f"Saved enriched leads to: {out}")

    return enriched


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enrich leads with contact info from websites")
    parser.add_argument("input", help="Input JSON file with leads")
    parser.add_argument("--output", "-o", help="Output JSON file (default: input-enriched.json)")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of leads to enrich")
    args = parser.parse_args()

    output = args.output or str(Path(args.input).with_suffix("")) + "-enriched.json"
    enrich_leads_file(args.input, output, limit=args.limit)
