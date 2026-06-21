from __future__ import annotations

from typing import Any


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def _priority_score(lead: dict[str, Any]) -> float:
    # Backward-compatible aliases
    if lead.get("priority_score") is not None:
        return float(lead.get("priority_score") or 0)
    if lead.get("lead_score") is not None:
        return float(lead.get("lead_score") or 0)
    return 0.0


def recommend_for_outreach(leads: list[dict[str, Any]], min_score: float = 80) -> list[dict[str, Any]]:
    """
    Returns leads that satisfy the hard qualification rule:
    priority_score > 80 AND no_chatbot AND no_call_button.
    """
    recommended: list[dict[str, Any]] = []

    for lead in leads:
        score = _priority_score(lead)

        has_chatbot = _to_bool(lead.get("has_chatbot"))

        # Rule uses "no_call_button"; stored field is usually has_click_to_call.
        if "no_call_button" in lead:
            no_call_button = _to_bool(lead.get("no_call_button"))
        else:
            no_call_button = not _to_bool(lead.get("has_click_to_call"))

        if score > min_score and (not has_chatbot) and no_call_button:
            tagged = dict(lead)
            tagged["recommended_for_outreach"] = True
            recommended.append(tagged)

    return recommended
