from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
UTC = timezone.utc
import requests


@dataclass
class BusinessLead:
    source_query: str
    category: str
    location: str
    name: str
    address: str | None
    phone: str | None
    website: str | None
    rating: float | None
    reviews: int | None
    place_id: str | None
    discovered_at: str

    def to_dict(self) -> dict:
        return asdict(self)


class SerpApiMapsClient:
    def __init__(self, api_key: str, google_domain: str = "google.com", hl: str = "en"):
        self.api_key = api_key
        self.google_domain = google_domain
        self.hl = hl
        self.endpoint = "https://serpapi.com/search.json"

    def search_businesses(self, category: str, location: str, limit: int = 20) -> list[BusinessLead]:
        query = f"{category} in {location}"
        params = {
            "engine": "google_maps",
            "q": query,
            "google_domain": self.google_domain,
            "hl": self.hl,
            "api_key": self.api_key,
        }
        response = requests.get(self.endpoint, params=params, timeout=45)
        response.raise_for_status()
        payload = response.json()

        results = payload.get("local_results", [])[:limit]
        leads: list[BusinessLead] = []

        for item in results:
            leads.append(
                BusinessLead(
                    source_query=query,
                    category=category,
                    location=location,
                    name=item.get("title", ""),
                    address=item.get("address"),
                    phone=item.get("phone"),
                    website=item.get("website"),
                    rating=self._safe_float(item.get("rating")),
                    reviews=self._safe_int(item.get("reviews")),
                    place_id=item.get("place_id"),
                    discovered_at=datetime.now(UTC).isoformat(),
                )
            )
        return leads

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
