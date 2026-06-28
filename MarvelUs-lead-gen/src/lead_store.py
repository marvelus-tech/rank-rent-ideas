from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


class LeadStore:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.records: list[dict[str, Any]] = []
        self.by_key: dict[str, dict[str, Any]] = {}

    def load(self) -> None:
        if not self.db_path.exists():
            self.records = []
            self.by_key = {}
            return

        self.records = json.loads(self.db_path.read_text(encoding="utf-8"))
        self.by_key = {}
        for record in self.records:
            key = record.get("dedupe_key") or self.build_dedupe_key(
                record.get("name"), record.get("address"), record.get("phone")
            )
            record["dedupe_key"] = key
            self._ensure_schema(record)
            self.by_key[key] = record

    def save(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.write_text(json.dumps(self.records, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def build_dedupe_key(name: str | None, address: str | None, phone: str | None) -> str:
        normalized = "|".join(
            [
                LeadStore._normalize(name),
                LeadStore._normalize(address),
                LeadStore._normalize(phone),
            ]
        )
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize(value: str | None) -> str:
        return " ".join((value or "").strip().lower().split())

    def filter_new_leads(self, scanned_records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
        today = date.today().isoformat()
        new_records: list[dict[str, Any]] = []
        seen_run: set[str] = set()

        total_scanned = len(scanned_records)
        duplicates_skipped = 0

        for record in scanned_records:
            key = self.build_dedupe_key(record.get("name"), record.get("address"), record.get("phone"))
            record["dedupe_key"] = key

            if key in self.by_key:
                duplicates_skipped += 1
                self._touch_seen(self.by_key[key], today, record.get("source_query"))
                continue

            if key in seen_run:
                duplicates_skipped += 1
                continue

            seen_run.add(key)
            new_record = dict(record)
            new_record["first_seen_date"] = today
            new_record["last_seen_date"] = today
            new_record["scan_history"] = [today]
            new_record["status_changes"] = []
            new_record["duplicate_of"] = None
            self._ensure_schema(new_record)
            new_records.append(new_record)

        return new_records, {
            "total_scanned": total_scanned,
            "new_leads": len(new_records),
            "duplicates_skipped": duplicates_skipped,
        }

    def add_new_records(self, analyzed_records: list[dict[str, Any]]) -> None:
        for record in analyzed_records:
            key = record.get("dedupe_key") or self.build_dedupe_key(
                record.get("name"), record.get("address"), record.get("phone")
            )
            record["dedupe_key"] = key
            self._ensure_schema(record)
            self.records.append(record)
            self.by_key[key] = record

    def stage_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in self.records:
            stage = str(record.get("pipeline_stage", "cold") or "cold")
            counts[stage] = counts.get(stage, 0) + 1
        return counts

    def _touch_seen(self, existing: dict[str, Any], today: str, source_query: str | None) -> None:
        existing["last_seen_date"] = today
        history = existing.get("scan_history") or []
        if today not in history:
            history.append(today)
        existing["scan_history"] = history
        if source_query:
            existing["source_query"] = source_query
        self._ensure_schema(existing)

    @staticmethod
    def _ensure_schema(record: dict[str, Any]) -> None:
        # Core fields
        record.setdefault("first_seen_date", record.get("discovered_at", "")[:10])
        record.setdefault("last_seen_date", record.get("discovered_at", "")[:10])
        record.setdefault("source_query", "")
        record.setdefault("scan_history", [])
        record.setdefault("status_changes", [])
        record.setdefault("duplicate_of", None)
        record.setdefault("phone", None)
        record.setdefault("email", None)
        record.setdefault("emails_found", [])
        record.setdefault("contact_page_url", None)
        record.setdefault("social_links", {"facebook": None, "linkedin": None, "instagram": None})
        record.setdefault("contact_confidence", "low")
        record.setdefault("owner_email_detected", False)
        record.setdefault("has_complete_contact_info", False)

        # Phase 1: SEO signals (fault-tolerant defaults)
        record.setdefault("seo_health_score", 0)
        record.setdefault("seo_signals", {
            "seo_health_score": 0,
            "has_meta_description": False,
            "title_quality": "unknown",
            "has_schema_markup": False,
            "heading_structure": {"h1_count": 0},
            "alt_text_coverage": 0.0,
        })

        # Phase 2: Multi-dimensional scoring (full-service)
        record.setdefault("ai_voice_fit_score", 0)
        record.setdefault("web_seo_fit_score", 0)
        record.setdefault("reputation_fit_score", 0)
        record.setdefault("booking_conversion_fit_score", 0)
        record.setdefault("overall_help_score", 0)
        record.setdefault("is_multi_opportunity", False)
        record.setdefault("strong_dimensions", [])
        record.setdefault("recommended_primary_service", "AI Voice")
        record.setdefault("top_recommended_services", ["AI Voice"])  # Phase 4: array for multi-service

        # Phase 7: Outreach drafts
        record.setdefault("outreach_sms", "")
        record.setdefault("outreach_email_subject", "")
        record.setdefault("outreach_email_body", "")
        record.setdefault("outreach_recommended_key", "")
        record.setdefault("outreach_is_multi", False)
