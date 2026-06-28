from __future__ import annotations

GENERIC_PREFIXES = {
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


def _is_direct_owner_email(email: str | None) -> bool:
    if not email or "@" not in email:
        return False
    local = email.split("@", 1)[0].lower()
    if local in GENERIC_PREFIXES:
        return False
    if any(t in local for t in ("owner", "founder", "director", "ceo", "principal")):
        return True
    return any(sep in local for sep in (".", "_", "-")) or local.isalpha()


def score_lead(row: dict, scoring_cfg: dict) -> dict:
    w = scoring_cfg["weights"]
    t = scoring_cfg["thresholds"]

    score = 0
    reasons: list[str] = []

    if not row.get("has_chatbot", False):
        score += w["no_chatbot"]
        reasons.append("No chatbot")

    if not row.get("has_click_to_call", False):
        score += w["no_click_to_call"]
        reasons.append("No click-to-call")

    if not row.get("has_booking", False):
        score += w["no_booking"]
        reasons.append("No booking flow")

    tech_score = int(row.get("tech_sophistication_score", 0) or 0)
    if tech_score < 45:
        score += w["low_tech_sophistication"]
        reasons.append("Low-tech website")

    rating = row.get("rating") or 0
    reviews = row.get("reviews") or 0
    if rating >= t["high_rating"] and reviews >= t["high_reviews"]:
        score += w["high_rating_and_reviews"]
        reasons.append("Strong reputation")

    email = row.get("email")
    phone = row.get("phone")
    if email:
        score += 15
        reasons.append("Email found (+15)")
    if phone:
        score += 10
        reasons.append("Phone found (+10)")
    if _is_direct_owner_email(email) or bool(row.get("owner_email_detected")):
        score += 10
        reasons.append("Direct owner-like email (+10)")

    has_complete_contact_info = bool(email and phone)
    if has_complete_contact_info:
        score += 5
        reasons.append("Complete contact info (+5)")

    if score >= 70:
        priority = "high"
    elif score >= 45 or (has_complete_contact_info and score >= 40):
        priority = "medium"
    else:
        priority = "low"

    return {
        "lead_score": score,
        "priority": priority,
        "score_reasons": " | ".join(reasons),
        "has_complete_contact_info": has_complete_contact_info,
    }
