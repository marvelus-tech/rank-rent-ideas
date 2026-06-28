"""Intelligence Scorer — evaluates leads for AI service need."""
from __future__ import annotations

import re
import json
from typing import Any

# Thresholds
LOW_REVIEWS_THRESHOLD = 50  # Under this = reputation management opportunity
HIGH_REVIEWS_THRESHOLD = 200  # Over this = good social proof

# Service business types (high need for AI voice/chat)
HIGH_NEED_CATEGORIES = [
    "plumber", "plumbing", "electrician", "electrical",
    "hvac", "ac repair", "air conditioning", "heating",
    "locksmith", "garage door", "pest control",
    "cleaning", "cleaner", "carpet cleaning",
    "auto repair", "mechanic", "towing",
    "dentist", "dental", "chiropractor", "med spa",
    "law firm", "lawyer", "attorney",
    "roofing", "roof",
    "landscaping", "landscaper", "tree service",
    "moving", "removalist", "storage",
    "appliance repair", "handyman",
]

# Website tech signals that indicate they DON'T need us (already sophisticated)
ANTI_SIGNALS = [
    "chatbot", "live chat", "chat widget", "drift", "intercom",
    "zendesk", "freshdesk", "hubspot chat",
    "book now", "schedule online", "online booking",
    "ai assistant", "virtual assistant",
]


def _has_call_button(html: str) -> bool:
    """Check if website has a click-to-call button or tel: link."""
    if not html:
        return False
    html_lower = html.lower()
    # tel: links
    if 'href="tel:' in html_lower or "href='tel:" in html_lower:
        return True
    # Click to call buttons
    call_patterns = [
        r"call\s*(now|today|us)",
        r"click\s*to\s*call",
        r"call\s*button",
        r"phone\s*icon",
        r"call\s*\d",
    ]
    for pattern in call_patterns:
        if re.search(pattern, html_lower):
            return True
    return False


def _has_chat_widget(html: str) -> bool:
    """Check if website has a chat widget or chatbot."""
    if not html:
        return False
    html_lower = html.lower()
    chat_signals = [
        "chatwidget", "chat-widget", "livechat", "live-chat",
        "intercom", "drift", "zendesk", "freshdesk",
        "tawk.to", "tidio", "crisp", "hubspot",
        "chatbot", "ai assistant", "virtual assistant",
        "window.__lc", "livechat_", "zopim",
    ]
    return any(signal in html_lower for signal in chat_signals)


def _has_booking_system(html: str) -> bool:
    """Check if website has online booking/appointment system."""
    if not html:
        return False
    html_lower = html.lower()
    booking_signals = [
        "book now", "schedule appointment", "online booking",
        "appointment", "reservation", "booking system",
        "calendly", "square appointments", "acuity",
        "setmore", "simplybook", "timely",
    ]
    return any(signal in html_lower for signal in booking_signals)


def _check_seo_signals(html: str, url: str) -> dict[str, Any]:
    """Check basic SEO signals on the page."""
    if not html:
        return {"seo_score": 0, "has_title": False, "has_meta_desc": False, "has_h1": False}
    
    html_lower = html.lower()
    
    # Title tag
    has_title = bool(re.search(r"<title>[^<]+</title>", html, re.IGNORECASE))
    title_text = ""
    title_match = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    if title_match:
        title_text = title_match.group(1).strip()
    
    # Meta description
    has_meta_desc = bool(re.search(r'<meta[^>]*name=["\']description["\'][^>]*>', html, re.IGNORECASE))
    
    # H1 tag
    has_h1 = bool(re.search(r"<h1[^>]*>[^<]+</h1>", html, re.IGNORECASE))
    
    # Multiple H1s (bad SEO)
    h1_count = len(re.findall(r"<h1[^>]*>[^<]+</h1>", html, re.IGNORECASE))
    
    # Schema.org markup
    has_schema = "schema.org" in html_lower or "application/ld+json" in html_lower
    
    # Image alt tags (rough check)
    images = re.findall(r"<img[^>]*>", html, re.IGNORECASE)
    images_with_alt = sum(1 for img in images if "alt=" in img.lower())
    alt_ratio = images_with_alt / len(images) if images else 1.0
    
    # Mobile viewport
    has_viewport = bool(re.search(r'<meta[^>]*name=["\']viewport["\'][^>]*>', html, re.IGNORECASE))
    
    # Score 0-100
    score = 0
    if has_title: score += 20
    if has_meta_desc: score += 20
    if has_h1 and h1_count == 1: score += 20
    if has_schema: score += 15
    if alt_ratio > 0.5: score += 15
    if has_viewport: score += 10
    
    return {
        "seo_score": score,
        "has_title": has_title,
        "title_text": title_text,
        "has_meta_desc": has_meta_desc,
        "has_h1": has_h1,
        "h1_count": h1_count,
        "has_schema_markup": has_schema,
        "images_total": len(images),
        "images_with_alt": images_with_alt,
        "has_viewport": has_viewport,
    }


def _check_review_opportunity(reviews: int | None) -> dict[str, Any]:
    """Evaluate if business needs reputation management."""
    if reviews is None:
        return {
            "review_count": 0,
            "needs_reputation_mgmt": True,
            "review_urgency": "high",
            "review_signal": "no_reviews_found",
        }
    
    if reviews < 10:
        return {
            "review_count": reviews,
            "needs_reputation_mgmt": True,
            "review_urgency": "critical",
            "review_signal": "very_few_reviews",
        }
    elif reviews < LOW_REVIEWS_THRESHOLD:
        return {
            "review_count": reviews,
            "needs_reputation_mgmt": True,
            "review_urgency": "high",
            "review_signal": "low_review_count",
        }
    elif reviews < HIGH_REVIEWS_THRESHOLD:
        return {
            "review_count": reviews,
            "needs_reputation_mgmt": False,
            "review_urgency": "medium",
            "review_signal": "moderate_reviews",
        }
    else:
        return {
            "review_count": reviews,
            "needs_reputation_mgmt": False,
            "review_urgency": "low",
            "review_signal": "good_reviews",
        }


def _is_service_business(category: str) -> bool:
    """Check if category is a high-need service business."""
    cat_lower = category.lower()
    return any(need in cat_lower for need in HIGH_NEED_CATEGORIES)


def score_lead_intelligence(lead: dict[str, Any], website_html: str | None = None) -> dict[str, Any]:
    """
    Score a lead for AI service need.
    
    Returns enrichment dict with:
    - ai_service_score (0-100)
    - priority (cold | warm | hot)
    - signals (dict of what we found)
    - opportunities (list of services they likely need)
    """
    
    category = lead.get("category", "")
    reviews = lead.get("reviews")
    website = lead.get("website")
    website_missing = lead.get("website_missing", False)
    
    signals = {}
    score = 0
    opportunities = []
    
    # === WEBSITE PRESENCE (40 points) ===
    if website_missing or not website:
        score += 40
        signals["no_website"] = True
        opportunities.append("website_building")
        opportunities.append("google_business_profile")
    else:
        signals["no_website"] = False
        # Check for call button
        has_call = _has_call_button(website_html)
        signals["has_call_button"] = has_call
        if not has_call:
            score += 15
            opportunities.append("click_to_call")
        
        # Check for chat widget
        has_chat = _has_chat_widget(website_html)
        signals["has_chat_widget"] = has_chat
        if not has_chat:
            score += 20
            opportunities.append("ai_chatbot")
        
        # Check for booking system
        has_booking = _has_booking_system(website_html)
        signals["has_booking_system"] = has_booking
        if not has_booking:
            score += 10
            opportunities.append("online_booking")
    
    # === SEO HEALTH (25 points) ===
    seo_data = _check_seo_signals(website_html, website or "")
    signals["seo"] = seo_data
    
    if website and not website_missing:
        if seo_data["seo_score"] < 40:
            score += 25
            opportunities.append("seo_optimization")
            signals["poor_seo"] = True
        elif seo_data["seo_score"] < 60:
            score += 15
            opportunities.append("seo_improvement")
            signals["poor_seo"] = False
        else:
            signals["poor_seo"] = False
    else:
        # No website = max SEO need
        score += 25
        opportunities.append("seo_optimization")
        signals["poor_seo"] = True
    
    # === REVIEWS / REPUTATION (20 points) ===
    review_data = _check_review_opportunity(reviews)
    signals["reviews"] = review_data
    
    if review_data["needs_reputation_mgmt"]:
        score += 20
        opportunities.append("reputation_management")
    
    # === BUSINESS TYPE (15 points) ===
    if _is_service_business(category):
        score += 15
        signals["service_business"] = True
    else:
        signals["service_business"] = False
    
    # === RATING SIGNAL ===
    rating = lead.get("rating")
    if rating is not None:
        if rating < 3.5:
            score += 5
            opportunities.append("review_recovery")
            signals["poor_rating"] = True
        else:
            signals["poor_rating"] = False
    
    # === PRIORITY ===
    if score >= 75:
        priority = "hot"
    elif score >= 50:
        priority = "warm"
    elif score >= 25:
        priority = "cold"
    else:
        priority = "cold"
    
    # === SUMMARY ===
    return {
        "ai_service_score": min(score, 100),
        "priority": priority,
        "opportunities": list(set(opportunities)),
        "signals": signals,
        "needs_ai_voice": signals.get("has_chat_widget") is False or website_missing,
        "needs_web_presence": website_missing or signals.get("poor_seo", False),
        "needs_reputation_mgmt": review_data["needs_reputation_mgmt"],
        "needs_call_button": not signals.get("has_call_button", True) and not website_missing,
    }


def enrich_with_intelligence(leads: list[dict[str, Any]], website_htmls: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Enrich leads with intelligence scoring."""
    enriched = []
    for lead in leads:
        website = lead.get("website")
        html = None
        if website_htmls and website:
            html = website_htmls.get(website)
        
        intel = score_lead_intelligence(lead, html)
        lead.update(intel)
        enriched.append(lead)
    return enriched


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Score leads for AI service need")
    parser.add_argument("input", help="Input JSON file with enriched leads")
    parser.add_argument("--output", "-o", help="Output JSON file")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"File not found: {input_path}")
        exit(1)
    
    leads = json.loads(input_path.read_text(encoding="utf-8"))
    scored = enrich_with_intelligence(leads)
    
    output = args.output or str(input_path.with_suffix("")) + "-scored.json"
    out_path = Path(output)
    out_path.write_text(json.dumps(scored, indent=2, default=str), encoding="utf-8")
    print(f"Scored {len(scored)} leads → {out_path}")
    
    # Print summary
    hot = sum(1 for l in scored if l.get("priority") == "hot")
    warm = sum(1 for l in scored if l.get("priority") == "warm")
    cold = sum(1 for l in scored if l.get("priority") == "cold")
    print(f"\nPriority breakdown:")
    print(f"  🔥 Hot:   {hot}")
    print(f"  🌡️ Warm:  {warm}")
    print(f"  ❄️ Cold:  {cold}")
