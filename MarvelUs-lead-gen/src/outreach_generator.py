"""
Phase 7: Auto-Outreach Draft Generation

SpaceX-grade: deterministic, config-driven, personalized using Phase 1-5 intelligence.
Generates low-pressure, benefit-first SMS and Email drafts.

Tailored to:
- recommended_primary_service
- is_multi_opportunity
- strong_dimensions
- seo_health_score
- category / location
"""

from __future__ import annotations
from typing import Any

DEFAULT_OUTREACH_CONFIG = {
    "templates": {
        "sms": {
            "full_stack": "Hi {name_short}, I help {category} in {location} get more bookings with 24/7 AI receptionist + website/SEO + reputation. 10-min chat? [Your Name] Marvelus",
            "ai_voice": "Hi {name_short}, I help {category} in {location} stop missing calls with a natural AI receptionist that books 24/7. Quick 10-min look? [Your Name] Marvelus",
            "web_seo": "Hi {name_short}, Noticed your {category} in {location}. Many lose leads to weak website/SEO. We build high-converting sites + AI booking. 10-min chat? [Your Name] Marvelus",
            "reputation": "Hi {name_short}, I help {category} in {location} turn reviews into a growth engine with automated reputation + AI voice. Quick chat? [Your Name] Marvelus",
            "booking": "Hi {name_short}, Quick idea for {category} in {location}: Add simple online booking + AI receptionist so clients book 24/7. 10-min chat? [Your Name] Marvelus",
        },
        "email_subject": {
            "full_stack": "More bookings + better website for {name} in {location}",
            "ai_voice": "AI receptionist for {category} in {location} (24/7 booking)",
            "web_seo": "Website & SEO fix for your {category} in {location}",
            "reputation": "Turn reviews into leads for {name}",
            "booking": "Simple 24/7 booking system for {category}",
        },
        "email_body": {
            "full_stack": "Hi {name},\n\nI came across {name} while looking at strong {category} businesses in {location}.\n\nA lot of places like yours are losing enquiries because:\n- Calls go unanswered after hours\n- The website/SEO isn't capturing leads well (current health score suggests room to improve)\n- Reviews aren't being turned into new bookings\n\nWe've built a simple system that combines:\n• Natural AI voice receptionist (answers + books 24/7)\n• Website/SEO optimization\n• Automated reputation management\n• Smart online booking\n\nIt's already working for other Melbourne {category} businesses.\n\nWould you be open to a short 10-15 min call this week (or a 1-min demo video first)?\n\nNo pressure.\n\nBest,\n[Your Name]\nMarvelus\n[Phone]",
            "ai_voice": "Hi {name},\n\nI help {category} businesses in {location} get more bookings with a natural Australian AI receptionist that answers 24/7 and books clients straight into your calendar.\n\nWould you be open to a quick 10-min chat this week?\n\nBest,\n[Your Name]\nMarvelus",
            "web_seo": "Hi {name},\n\nI saw your {category} in {location}.\n\nMany businesses in your space lose potential clients because their website and SEO aren't optimized to convert visitors into bookings.\n\nWe specialize in high-converting sites + AI booking systems for service businesses.\n\nHappy to send a short audit or jump on a call.\n\nBest,\n[Your Name]\nMarvelus",
            "reputation": "Hi {name},\n\nI help {category} businesses turn Google reviews into a reliable source of new clients.\n\nCombined with AI voice, it compounds.\n\nOpen to a quick chat?\n\nBest,\n[Your Name]\nMarvelus",
            "booking": "Hi {name},\n\nQuick idea for {category} in {location}:\n\nAdd a simple system so clients can book (and your AI receptionist can confirm) 24/7.\n\nWorks with most calendars.\n\n10-min chat?\n\nBest,\n[Your Name]\nMarvelus",
        }
    },
    "max_sms_length": 160,
    "default_signoff": "[Your Name]\nMarvelus"
}


def _short_name(name: str) -> str:
    if not name:
        return "there"
    parts = name.split()
    return parts[0] if parts else "there"


def _get_recommended_key(recommended: str) -> str:
    rec = (recommended or "").lower()
    if "full" in rec:
        return "full_stack"
    if "voice" in rec or "ai" in rec:
        return "ai_voice"
    if "seo" in rec or "web" in rec:
        return "web_seo"
    if "reputation" in rec:
        return "reputation"
    if "booking" in rec:
        return "booking"
    return "ai_voice"


def generate_outreach_drafts(lead: dict[str, Any], config: dict | None = None) -> dict[str, str]:
    """
    Phase 7: Generate personalized SMS + Email drafts using rich scoring data.
    """
    if config is None:
        config = {}

    outreach_cfg = config.get("outreach", DEFAULT_OUTREACH_CONFIG)
    templates = outreach_cfg.get("templates", DEFAULT_OUTREACH_CONFIG["templates"])

    name = lead.get("name", "there")
    name_short = _short_name(name)
    category = lead.get("category", "your business")
    location = lead.get("location", "Melbourne")

    recommended = lead.get("recommended_primary_service", "AI Voice")
    key = _get_recommended_key(recommended)

    is_multi = lead.get("is_multi_opportunity", False)
    if is_multi:
        key = "full_stack"

    # SEO context
    seo_score = int(lead.get("seo_health_score", 50))
    seo_note = ""
    if seo_score < 50:
        seo_note = " (your current website/SEO health looks low)"

    # Build SMS
    sms_template = templates["sms"].get(key, templates["sms"]["ai_voice"])
    sms = sms_template.format(
        name_short=name_short,
        name=name,
        category=category,
        location=location,
    )
    if seo_note and key == "full_stack":
        sms = sms.replace("low)", f"low){seo_note}")

    # Build Email
    subject_template = templates["email_subject"].get(key, templates["email_subject"]["ai_voice"])
    subject = subject_template.format(name=name, category=category, location=location)

    body_template = templates["email_body"].get(key, templates["email_body"]["ai_voice"])
    body = body_template.format(
        name=name,
        category=category,
        location=location,
    )

    return {
        "outreach_sms": sms.strip(),
        "outreach_email_subject": subject.strip(),
        "outreach_email_body": body.strip(),
        "outreach_recommended_key": key,
        "outreach_is_multi": is_multi,
    }


def generate_daily_outreach_pack(leads: list[dict], config: dict | None = None) -> list[dict]:
    """Batch generate for a list of leads (used in reporting)."""
    return [ {**lead, **generate_outreach_drafts(lead, config)} for lead in leads ]