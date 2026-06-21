from __future__ import annotations

import json
import random
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from playwright.sync_api import BrowserContext, Page, TimeoutError, sync_playwright

try:
    from playwright_stealth import stealth_sync
except Exception:  # pragma: no cover
    stealth_sync = None


@dataclass
class Listing:
    title: str
    price: Optional[float]
    price_raw: str
    location: str
    seller_name: str
    seller_info: str
    description: str
    image_urls: List[str]
    listing_date: str
    category: str
    url: str


class FacebookMarketplaceScraper:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.fb_cfg = config.get("facebook", {})
        self.scraper_cfg = config.get("scraper", {})
        self.output_cfg = config.get("output", {})
        self.cookies_path = Path(self.fb_cfg.get("cookies_path", "data/fb_cookies.json"))
        self.cookies_path.parent.mkdir(parents=True, exist_ok=True)

    def _random_delay(self, base: float = 1.0, jitter: float = 1.5) -> None:
        time.sleep(base + random.random() * jitter)

    def _build_search_url(self, keyword: str, location: str) -> str:
        distance = self.scraper_cfg.get("distance_km", 40)
        min_price = self.scraper_cfg.get("min_price")
        max_price = self.scraper_cfg.get("max_price")

        params = [f"query={quote_plus(keyword)}", f"exact=false", f"deliveryMethod=local_pick_up", f"radius={distance}"]
        if min_price is not None:
            params.append(f"minPrice={int(min_price)}")
        if max_price is not None:
            params.append(f"maxPrice={int(max_price)}")
        if location:
            params.append(f"location={quote_plus(location)}")

        return f"https://www.facebook.com/marketplace/search/?{'&'.join(params)}"

    def _new_context(self, playwright):
        browser = playwright.chromium.launch(
            headless=self.scraper_cfg.get("headless", False),
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1366, "height": 900},
            user_agent=self.scraper_cfg.get(
                "user_agent",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            ),
            locale="en-US",
            timezone_id="Australia/Melbourne",
        )

        if self.cookies_path.exists():
            with open(self.cookies_path, "r", encoding="utf-8") as f:
                context.add_cookies(json.load(f))

        return browser, context

    def _save_cookies(self, context: BrowserContext) -> None:
        with open(self.cookies_path, "w", encoding="utf-8") as f:
            json.dump(context.cookies(), f, indent=2)

    def _is_logged_in(self, page: Page) -> bool:
        page.goto("https://www.facebook.com/marketplace", wait_until="domcontentloaded")
        self._random_delay(1.0, 1.0)
        return "login" not in page.url.lower()

    def _check_captcha(self, page: Page) -> bool:
        body = page.content().lower()
        signals = ["captcha", "checkpoint", "security check", "suspicious activity"]
        return any(sig in body for sig in signals)

    def login(self, context: BrowserContext) -> None:
        page = context.new_page()
        if stealth_sync:
            stealth_sync(page)

        if self._is_logged_in(page):
            print("[login] Session cookie valid; login skipped.")
            return

        email = self.fb_cfg.get("email")
        password = self.fb_cfg.get("password")
        if not email or not password:
            raise ValueError("Missing Facebook credentials. Set facebook.email/password in env or config.")

        page.goto("https://www.facebook.com/login", wait_until="domcontentloaded")
        page.fill("input[name='email']", email)
        self._random_delay(0.5, 0.6)
        page.fill("input[name='pass']", password)
        self._random_delay(0.5, 0.6)
        page.click("button[name='login']")

        try:
            page.wait_for_url(re.compile(r"facebook\.com/(?!login)"), timeout=20000)
        except TimeoutError:
            if self._check_captcha(page):
                raise RuntimeError("CAPTCHA/checkpoint detected. Solve manually and retry.")
            print("[login] Potential 2FA/checkpoint. Complete flow in opened browser within 90s...")
            page.wait_for_timeout(90000)

        if self._check_captcha(page):
            raise RuntimeError("CAPTCHA/checkpoint detected after login.")

        self._save_cookies(context)
        print("[login] Logged in and cookies saved.")

    @staticmethod
    def _parse_price(price_text: str) -> Optional[float]:
        if not price_text:
            return None
        txt = price_text.lower().replace(",", "")
        if any(x in txt for x in ["free", "swap", "trade"]):
            return 0.0
        m = re.search(r"(\d+(?:\.\d+)?)", txt)
        return float(m.group(1)) if m else None

    def _extract_listing_cards(self, page: Page) -> List[Dict[str, str]]:
        js = """
        () => {
          const cards = [...document.querySelectorAll('a[href*="/marketplace/item/"]')];
          const out = [];
          for (const c of cards) {
            const url = c.href;
            const title = c.querySelector('span')?.innerText || '';
            const text = c.innerText || '';
            const lines = text.split('\n').filter(Boolean);
            const priceRaw = lines.find(l => /^\\$|free|swap|trade/i.test(l)) || '';
            const location = lines.length > 1 ? lines[lines.length - 1] : '';
            out.push({url, title, priceRaw, location});
          }
          const dedup = new Map();
          out.forEach(i => dedup.set(i.url, i));
          return [...dedup.values()];
        }
        """
        return page.evaluate(js)

    def _extract_listing_details(self, context: BrowserContext, url: str, category: str = "") -> Dict[str, Any]:
        page = context.new_page()
        if stealth_sync:
            stealth_sync(page)
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        self._random_delay(1.0, 1.2)

        if self._check_captcha(page):
            raise RuntimeError("CAPTCHA/checkpoint detected while reading listing details.")

        js = """
        () => {
          const textBlocks = [...document.querySelectorAll('div,span,h1,h2')]
            .map(el => el.innerText?.trim())
            .filter(Boolean);

          const title = document.querySelector('h1')?.innerText?.trim() || '';
          const priceRaw = textBlocks.find(t => /^\\$\\s?\\d|free|swap|trade/i.test(t)) || '';

          const descriptionNode = [...document.querySelectorAll('span,div')]
            .find(el => /condition|description/i.test(el.innerText || ''));
          const description = descriptionNode?.innerText?.trim() || '';

          const sellerLink = document.querySelector('a[href*="/profile.php"], a[href*="/marketplace/profile"]');
          const sellerName = sellerLink?.innerText?.trim() || '';
          const sellerInfo = sellerLink?.getAttribute('href') || '';

          const imgs = [...document.querySelectorAll('img')]
            .map(i => i.src)
            .filter(src => src && src.includes('scontent'))
            .slice(0, 8);

          const listingDate = textBlocks.find(t => /listed|ago|day|hour|minute|week/i.test(t)) || '';
          const location = textBlocks.find(t => /,\\s?[A-Za-z]{2,}/.test(t)) || '';

          return {title, priceRaw, description, sellerName, sellerInfo, imageUrls: imgs, listingDate, location};
        }
        """
        data = page.evaluate(js)
        page.close()
        data["category"] = category
        data["url"] = url
        return data

    def search(self, keyword: str, location: str, max_listings: int = 20, category: str = "") -> List[Listing]:
        with sync_playwright() as p:
            browser, context = self._new_context(p)
            try:
                self.login(context)
                page = context.new_page()
                if stealth_sync:
                    stealth_sync(page)

                search_url = self._build_search_url(keyword, location)
                page.goto(search_url, wait_until="domcontentloaded")
                self._random_delay(1.5, 1.0)

                seen = {}
                max_scrolls = self.scraper_cfg.get("max_scrolls", 20)
                for _ in range(max_scrolls):
                    if self._check_captcha(page):
                        raise RuntimeError("CAPTCHA/checkpoint detected during search.")
                    cards = self._extract_listing_cards(page)
                    for c in cards:
                        seen[c["url"]] = c
                    if len(seen) >= max_listings:
                        break
                    page.mouse.wheel(0, random.randint(1800, 2600))
                    self._random_delay(0.8, 1.2)

                results: List[Listing] = []
                for item in list(seen.values())[:max_listings]:
                    try:
                        details = self._extract_listing_details(context, item["url"], category=category)
                    except Exception as e:
                        print(f"[warn] Failed listing details {item['url']}: {e}")
                        details = {
                            "title": item.get("title", ""),
                            "priceRaw": item.get("priceRaw", ""),
                            "location": item.get("location", ""),
                            "sellerName": "",
                            "sellerInfo": "",
                            "description": "",
                            "imageUrls": [],
                            "listingDate": "",
                            "category": category,
                            "url": item["url"],
                        }

                    price_raw = details.get("priceRaw", "")
                    results.append(
                        Listing(
                            title=details.get("title", "").strip(),
                            price=self._parse_price(price_raw),
                            price_raw=price_raw,
                            location=details.get("location", "").strip(),
                            seller_name=details.get("sellerName", "").strip(),
                            seller_info=details.get("sellerInfo", "").strip(),
                            description=details.get("description", "").strip(),
                            image_urls=details.get("imageUrls", []),
                            listing_date=details.get("listingDate", "").strip(),
                            category=details.get("category", category),
                            url=details.get("url", item["url"]),
                        )
                    )
                    self._random_delay(0.6, 0.9)

                self._save_cookies(context)
                return results
            finally:
                browser.close()

    def save_results(self, listings: List[Listing], out_dir: str = "output", base_name: str = "marketplace_results") -> Dict[str, str]:
        import csv

        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        json_path = out_path / f"{base_name}.json"
        csv_path = out_path / f"{base_name}.csv"

        payload = [asdict(item) for item in listings]
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(payload[0].keys()) if payload else [
                "title", "price", "price_raw", "location", "seller_name", "seller_info", "description", "image_urls", "listing_date", "category", "url"
            ])
            writer.writeheader()
            for row in payload:
                row = dict(row)
                row["image_urls"] = "|".join(row.get("image_urls", []))
                writer.writerow(row)

        return {"json": str(json_path), "csv": str(csv_path)}
