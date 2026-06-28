from __future__ import annotations

from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path
import random
import re
import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


class CaptchaDetectedError(RuntimeError):
    """Raised when Google shows CAPTCHA or anti-bot challenge."""


class BrowserMapsScraper:
    """Google Maps scraper driven by a real browser (Playwright)."""

    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        headless: bool = True,
        slow_mo: int = 2000,
        max_results_per_search: int = 30,
        search_delay_seconds: int = 5,
        debug_dir: str = "data/debug/browser",
    ):
        self.headless = headless
        self.slow_mo = slow_mo
        self.max_results_per_search = min(max_results_per_search, 50)
        self.search_delay_seconds = search_delay_seconds
        self.debug_dir = Path(debug_dir)
        self.debug_dir.mkdir(parents=True, exist_ok=True)

    def search_businesses(self, category: str, location: str, limit: int | None = None) -> list[dict]:
        target_limit = min(limit or self.max_results_per_search, self.max_results_per_search)
        query = f"{category} in {location}"

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            )
            context = browser.new_context(
                user_agent=self.USER_AGENT,
                locale="en-AU",
                viewport={"width": 1440, "height": 960},
            )
            page = context.new_page()

            try:
                self._navigate_and_search(page, query)
                listing_links = self._collect_listing_links(page, target_limit)
                return self._extract_listings(page, listing_links, category, location, query, target_limit)
            except Exception as exc:  # noqa: BLE001
                self._save_artifacts(page, f"fatal_{self._safe_slug(query)}", exc)
                raise
            finally:
                context.close()
                browser.close()

    def _navigate_and_search(self, page, query: str) -> None:
        page.goto("https://www.google.com/maps", wait_until="domcontentloaded", timeout=60000)
        self._check_captcha(page, "initial_load")
        self._sleep_random()

        search_input = page.locator('input.UGojuc, input[id^="ucc-"]').first
        search_input.wait_for(state="visible", timeout=30000)
        search_input.fill(query)
        self._sleep_random()
        search_input.press("Enter")

        page.wait_for_selector('div[role="feed"], a.hfpxzc', timeout=45000)
        self._check_captcha(page, "after_search")
        self._sleep_random()

    def _collect_listing_links(self, page, limit: int) -> list[str]:
        feed = page.locator('div[role="feed"]').first

        links: list[str] = []
        seen: set[str] = set()
        stagnant_rounds = 0

        while len(links) < limit and stagnant_rounds < 6:
            self._check_captcha(page, "collect_links")

            cards = page.locator('a.hfpxzc')
            count = cards.count()
            for idx in range(count):
                href = cards.nth(idx).get_attribute("href")
                if href and href not in seen:
                    seen.add(href)
                    links.append(href)
                    if len(links) >= limit:
                        break

            before = len(links)
            if feed.count() > 0:
                feed.evaluate("el => { el.scrollTop = el.scrollHeight; }")
            else:
                page.mouse.wheel(0, 3500)

            self._sleep_random()

            cards_after = page.locator('a.hfpxzc').count()
            if len(links) == before and cards_after <= count:
                stagnant_rounds += 1
            else:
                stagnant_rounds = 0

        return links[:limit]

    def _extract_listings(
        self,
        page,
        listing_links: list[str],
        category: str,
        location: str,
        query: str,
        limit: int,
    ) -> list[dict]:
        leads: list[dict] = []

        for idx, href in enumerate(listing_links[:limit], start=1):
            self._check_captcha(page, f"listing_{idx}")

            try:
                page.goto(href, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_selector("h1.DUwDvf", timeout=25000)
                self._sleep_random()
                leads.append(self._extract_detail_fields(page, category, location, query, href))
            except Exception as exc:  # noqa: BLE001
                self._save_artifacts(page, f"extract_fail_{idx}_{self._safe_slug(query)}", exc)
                continue

        return leads

    def _extract_detail_fields(self, page, category: str, location: str, query: str, href: str) -> dict:
        name = self._safe_text(page, "h1.DUwDvf")
        address = self._safe_text(page, 'button[data-item-id="address"] .Io6YTe, button[data-item-id="address"]')
        phone = self._safe_text(page, 'button[data-item-id^="phone:"] .Io6YTe, button[data-item-id^="phone:"]')
        business_type = self._safe_text(page, "button.DkEaL")

        website = None
        website_locator = page.locator('a[data-item-id="authority"]')
        if website_locator.count() > 0:
            website = website_locator.first.get_attribute("href")

        return {
            "source_query": query,
            "category": category,
            "location": location,
            "name": name or "",
            "address": address,
            "phone": phone,
            "website": website,
            "website_missing": website is None,
            "rating": self._extract_rating(page),
            "reviews": self._extract_reviews(page),
            "place_id": self._extract_place_id(href),
            "discovered_at": datetime.now(UTC).isoformat(),
            "business_hours": self._extract_hours(page),
            "business_type": business_type,
            "maps_url": href,
        }

    def _extract_rating(self, page) -> float | None:
        text = self._safe_text(page, 'div.F7nice span[aria-hidden="true"]')
        if not text:
            text = self._safe_text(page, 'span[role="img"][aria-label*="star"]')
        if not text:
            return None
        m = re.search(r"(\d+[\.,]?\d*)", text)
        if not m:
            return None
        try:
            return float(m.group(1).replace(",", "."))
        except ValueError:
            return None

    def _extract_reviews(self, page) -> int | None:
        text = self._safe_text(page, "button.hh2c6")
        if not text:
            text = self._safe_text(page, 'button[aria-label*="reviews"]')
        if not text:
            return None
        m = re.search(r"([\d,\.]+)", text)
        if not m:
            return None
        raw = m.group(1).replace(",", "").replace(".", "")
        return int(raw) if raw.isdigit() else None

    def _extract_hours(self, page) -> str | None:
        hours = self._safe_text(page, 'table.eK4R0e')
        if hours:
            return re.sub(r"\s+", " ", hours).strip()
        quick = self._safe_text(page, 'div[aria-label*="Hours"]')
        return re.sub(r"\s+", " ", quick).strip() if quick else None

    def _check_captcha(self, page, stage: str) -> None:
        url = (page.url or "").lower()
        text = (page.content() or "").lower()
        triggered = any(
            signal in url or signal in text
            for signal in ["/sorry/", "recaptcha", "unusual traffic", "detected unusual traffic"]
        )
        if triggered:
            self._save_artifacts(page, f"captcha_{stage}", CaptchaDetectedError("captcha detected"))
            raise CaptchaDetectedError("Google CAPTCHA or bot detection page encountered")

    def _save_artifacts(self, page, name: str, error: Exception | None = None) -> None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = self._safe_slug(name)
        html_path = self.debug_dir / f"{stamp}_{safe_name}.html"
        screenshot_path = self.debug_dir / f"{stamp}_{safe_name}.png"
        err_path = self.debug_dir / f"{stamp}_{safe_name}.log"

        try:
            html_path.write_text(page.content(), encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass

        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
        except Exception:  # noqa: BLE001
            pass

        if error:
            err_path.write_text(repr(error), encoding="utf-8")

    def _sleep_random(self) -> None:
        low = max(3, self.search_delay_seconds - 2)
        high = max(low, self.search_delay_seconds + 2)
        time.sleep(random.uniform(low, high))

    @staticmethod
    def _safe_text(page, selector: str) -> str | None:
        loc = page.locator(selector)
        if loc.count() == 0:
            return None
        try:
            text = loc.first.inner_text(timeout=3000)
        except Exception:  # noqa: BLE001
            return None
        if not text:
            return None
        # Strip Google Maps UI artifacts (icons like , , etc.)
        text = re.sub(r"[\ue000-\uf8ff]", "", text)
        text = text.strip()
        return text if text else None

    @staticmethod
    def _extract_place_id(url: str | None) -> str | None:
        if not url:
            return None
        m = re.search(r"1s(0x[0-9a-fA-F:]+)", url)
        return m.group(1) if m else None

    @staticmethod
    def _safe_slug(value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_").lower()[:80]


def browser_search_with_retry(
    scraper: BrowserMapsScraper,
    category: str,
    location: str,
    max_retries: int = 3,
    backoff_seconds: int = 4,
) -> list[dict]:
    for attempt in range(max_retries):
        try:
            return scraper.search_businesses(category=category, location=location)
        except CaptchaDetectedError:
            raise
        except (PlaywrightTimeoutError, RuntimeError, ValueError) as exc:
            if attempt == max_retries - 1:
                raise
            sleep_time = backoff_seconds * (2**attempt)
            print(
                f"Browser scrape failed for {category} in {location} "
                f"(attempt {attempt + 1}/{max_retries}): {exc}. Retrying in {sleep_time}s..."
            )
            time.sleep(sleep_time)
    return []
