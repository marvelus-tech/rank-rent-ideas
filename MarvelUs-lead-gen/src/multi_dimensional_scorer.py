"""
Phase 2: Multi-Dimensional Scoring for Full-Service Agency

SpaceX-grade implementation:
- Deterministic, config-driven
- Graceful defaults
- Clear separation of concerns
- Returns structured sub-scores + overall + opportunity flags
- Backward compatible with legacy single-score path

Dimensions:
- AI Voice / Receptionist fit
- Web / SEO Presence fit (uses Phase 1 seo_health_score)
- Reputation Management fit
- Booking / Conversion fit
"""

from __future__ import annotations
from typing import Any

DEFAULT_WEIGHTS = {
    "ai_voice": 30,
    "web_seo": 25,
    "reputation": 20,
    "booking": 15,
    "contact_completeness": 10,
}

DEFAULT_THRESHOLDS = {
    "high": 75,
    "medium": 50,
    "multi_opportunity_min": 65,
    "min_dimensions_for_multi": 2,
}


def _clamp(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _calculate_ai_voice_fit(row: dict[str, Any], weights: dict) -> int:
    """AI receptionist / voice fit."""
    score = 0

    if not row.get("has_chatbot", False):
        score += 35
    if not row.get("has_click_to_call", False):
        score += 25
    if not row.get("has_booking", False):
        score += 20

    tech = int(row.get("tech_sophistication_score") or 0)
    if tech < 45:
        score += 20

    # Bonus for service businesses that take phone calls
    if row.get("category") in ["plumbers", "electricians", "hvac", "roofers", "med spa", "dental clinic"]:
        score += 10

    return _clamp(score * (weights.get("ai_voice", 30) / 100))


def _calculate_web_seo_fit(row: dict[str, Any], weights: dict) -> int:
    """Web presence + SEO opportunity (Phase 1 signals)."""
    score = 0

    seo_health = int(row.get("seo_health_score") or 0)
    tech = int(row.get("tech_sophistication_score") or 0)

    # Low SEO health = high opportunity
    if seo_health < 40:
        score += 50
    elif seo_health < 60:
        score += 35
    else:
        score += 10

    if tech < 50:
        score += 30

    # No website is massive opportunity
    if not row.get("website"):
        score += 20

    # On-page signals from Phase 1
    seo = row.get("seo_signals", {}) or {}
    if not seo.get("has_meta_description"):
        score += 10
    if seo.get("title_quality") in ("too_short", "too_long"):
        score += 8

    return _clamp(score * (weights.get("web_seo", 25) / 100))


def _calculate_reputation_fit(row: dict[str, Any], weights: dict) -> int:
    """Reputation management opportunity."""
    score = 0

    rating = float(row.get("rating") or 0)
    reviews_raw = row.get("reviews") or 0
    try:
        reviews = int(reviews_raw)
    except (ValueError, TypeError):
        reviews = 0

    if rating < 4.0:
        score += 40
    elif rating < 4.5:
        score += 25

    if reviews < 20:
        score += 30
    elif reviews < 50:
        score += 15

    # Low review count + decent rating still means opportunity to build proof
    if 4.0 <= rating < 4.8 and reviews < 30:
        score += 10

    return _clamp(score * (weights.get("reputation", 20) / 100))


def _calculate_booking_fit(row: dict[str, Any], weights: dict) -> int:
    """Booking and conversion opportunity."""
    score = 0

    if not row.get("has_booking", False):
        score += 50

    if not row.get("has_click_to_call", False):
        score += 25

    # Service categories that benefit from online booking
    cat = (row.get("category") or "").lower()
    if any(x in cat for x in ["spa", "dental", "clinic", "chiro", "physio", "beauty"]):
        score += 15

    return _clamp(score * (weights.get("booking", 15) / 100))


def _calculate_contact_bonus(row: dict[str, Any], weights: dict) -> int:
    """Bonus for having contact info (makes outreach easier)."""
    score = 0
    if row.get("email"):
        score += 50
    if row.get("phone"):
        score += 30
    if row.get("has_complete_contact_info"):
        score += 20
    return _clamp(score * (weights.get("contact_completeness", 10) / 100))


def score_lead_multi(row: dict[str, Any], config: dict | None = None) -> dict[str, Any]:
    """
    Phase 2 multi-dimensional scorer.

    Returns rich structure while preserving legacy fields for compatibility.
    """
    if config is None:
        config = {}

    multi_cfg = config.get("multi_scoring", {})
    weights = {**DEFAULT_WEIGHTS, **multi_cfg.get("weights", {})}
    thresholds = {**DEFAULT_THRESHOLDS, **multi_cfg.get("thresholds", {})}

    # Calculate dimensions
    ai_voice = _calculate_ai_voice_fit(row, weights)
    web_seo = _calculate_web_seo_fit(row, weights)
    reputation = _calculate_reputation_fit(row, weights)
    booking = _calculate_booking_fit(row, weights)
    contact = _calculate_contact_bonus(row, weights)

    # Weighted overall (0-100)
    overall = _clamp(
        (ai_voice * weights["ai_voice"] +
         web_seo * weights["web_seo"] +
         reputation * weights["reputation"] +
         booking * weights["booking"] +
         contact * weights["contact_completeness"]) / 100
    )

    # Determine which dimensions are strong opportunities
    dimensions = {
        "ai_voice": ai_voice,
        "web_seo": web_seo,
        "reputation": reputation,
        "booking": booking,
    }

    strong_dimensions = [k for k, v in dimensions.items() if v >= thresholds["multi_opportunity_min"]]
    is_multi = len(strong_dimensions) >= thresholds["min_dimensions_for_multi"]

    # Recommended primary service
    max_dim = max(dimensions, key=dimensions.get)
    primary_map = {
        "ai_voice": "AI Voice",
        "web_seo": "SEO / Web Presence",
        "reputation": "Reputation Management",
        "booking": "Online Booking",
    }
    recommended = primary_map.get(max_dim, "AI Voice")

    if is_multi:
        recommended = "Full Stack"

    # Legacy compatibility fields (map overall to old lead_score style)
    if overall >= thresholds["high"]:
        priority = "high"
    elif overall >= thresholds["medium"]:
        priority = "medium"
    else:
        priority = "low"

    reasons = []
    if ai_voice > 60:
        reasons.append("Strong AI voice opportunity")
    if web_seo > 60:
        reasons.append("Weak digital presence / SEO")
    if reputation > 50:
        reasons.append("Reputation building needed")
    if booking > 55:
        reasons.append("No booking system")

    return {
        # New Phase 2 fields
        "ai_voice_fit_score": ai_voice,
        "web_seo_fit_score": web_seo,
        "reputation_fit_score": reputation,
        "booking_conversion_fit_score": booking,
        "overall_help_score": overall,
        "is_multi_opportunity": is_multi,
        "strong_dimensions": strong_dimensions,
        "recommended_primary_service": recommended,

        # Legacy compatibility (so existing dashboard / reports don't break)
        "lead_score": overall,
        "priority": priority,
        "score_reasons": " | ".join(reasons) if reasons else "Standard opportunity",
        "has_complete_contact_info": bool(row.get("has_complete_contact_info")),
    }


# Legacy wrapper for backward compatibility when multi-dimensional is disabled
def score_lead_legacy(row: dict[str, Any], scoring_cfg: dict) -> dict[str, Any]:
    """Original single-score logic (kept for reference and fallback)."""
    from .scoring import score_lead as original_score_lead
    return original_score_lead(row, scoring_cfg)