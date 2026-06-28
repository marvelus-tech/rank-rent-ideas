from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .qualifier import recommend_for_outreach


def _notable_patterns(leads: list[dict[str, Any]]) -> list[str]:
    if not leads:
        return ["No new leads discovered today."]

    without_chatbot = sum(1 for l in leads if not bool(l.get("has_chatbot", False)))
    without_call = sum(1 for l in leads if not bool(l.get("has_click_to_call", False)))
    with_complete_contact = sum(1 for l in leads if bool(l.get("email")) and bool(l.get("phone")))
    high_rep = sum(
        1
        for l in leads
        if float(l.get("rating") or 0) >= 4.5 and int(l.get("reviews") or 0) >= 50
    )

    return [
        f"{without_chatbot}/{len(leads)} new leads have no chatbot.",
        f"{without_call}/{len(leads)} new leads have no click-to-call button.",
        f"{with_complete_contact}/{len(leads)} new leads have complete contact info (email + phone).",
        f"{high_rep}/{len(leads)} new leads have strong social proof (rating 4.5+ and 50+ reviews).",
    ]


def _format_lead_bullet(lead: dict[str, Any]) -> str:
    rec = "✅ Yes" if lead.get("recommended_for_outreach") else "⚪ Review"
    score = lead.get("priority_score", lead.get("lead_score", 0))
    email = lead.get("email") or "n/a"
    phone = lead.get("phone") or "n/a"
    missing = []
    if email == "n/a":
        missing.append("email")
    if phone == "n/a":
        missing.append("phone")
    missing_note = (
        f"  - Missing contact info: **{', '.join(missing)}** (flag for manual research)\n" if missing else ""
    )

    return (
        f"- **{lead.get('name', 'Unknown')}** ({lead.get('category', 'n/a')} — {lead.get('location', 'n/a')})\n"
        f"  - Score: **{score}** | Rating: **{lead.get('rating', 'n/a')}** | Reviews: **{lead.get('reviews', 'n/a')}**\n"
        f"  - No chatbot: **{not bool(lead.get('has_chatbot', False))}** | "
        f"No call button: **{not bool(lead.get('has_click_to_call', False))}**\n"
        f"  - Contact: Email **{email}** | Phone **{phone}** | Confidence **{lead.get('contact_confidence', 'low')}**\n"
        f"  - Recommended for outreach: **{rec}**\n"
        f"  - Website: {lead.get('website', 'n/a')}\n"
        f"{missing_note}"
        f"  - Action: {lead.get('action_suggestion', 'Call first, then follow with a short ROI-focused SMS/email.') }"
    )


def package_daily_findings(
    new_leads: list[dict[str, Any]],
    stats: dict[str, Any],
    max_review_leads: int = 15,
    output_dir: str = "output",
) -> dict[str, Any]:
    """
    Build a two-tier handoff package for Penelopi review.
    Outputs:
      - output/daily_for_review.md (Telegram-ready markdown)
      - output/daily_for_review.json (structured payload)
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    high_priority = [l for l in new_leads if str(l.get("priority", "")).lower() == "high"]

    recommended = recommend_for_outreach(high_priority)
    recommended_keys = {
        (l.get("dedupe_key") or f"{l.get('name','')}|{l.get('address','')}|{l.get('phone','')}") for l in recommended
    }

    ranked = sorted(
        high_priority,
        key=lambda x: float(x.get("priority_score", x.get("lead_score", 0)) or 0),
        reverse=True,
    )

    selected: list[dict[str, Any]] = []
    for lead in ranked:
        key = lead.get("dedupe_key") or f"{lead.get('name','')}|{lead.get('address','')}|{lead.get('phone','')}"
        tagged = dict(lead)
        tagged["recommended_for_outreach"] = key in recommended_keys
        if tagged["recommended_for_outreach"]:
            tagged.setdefault("action_suggestion", "Prioritize outreach with direct phone/email and ROI-focused opener.")
        else:
            tagged.setdefault("action_suggestion", "Manual review: verify fit and fill missing contact details before outreach.")
        selected.append(tagged)
        if len(selected) >= max_review_leads:
            break

    payload = {
        "date": date.today().isoformat(),
        "stats_summary": {
            "total_scanned": stats.get("total_scanned", 0),
            "new_leads": stats.get("new_leads", 0),
            "duplicates_skipped": stats.get("duplicates_skipped", 0),
            "high_priority_new": len(high_priority),
            "recommended_count": sum(1 for l in selected if l.get("recommended_for_outreach")),
        },
        "notable_patterns": _notable_patterns(high_priority),
        "leads_for_review": selected,
    }

    json_path = out_dir / "daily_for_review.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        f"# Daily Lead Review Packet — {payload['date']}",
        "",
        "## Quick Stats",
        f"- Total scanned: **{payload['stats_summary']['total_scanned']}**",
        f"- New leads: **{payload['stats_summary']['new_leads']}**",
        f"- Duplicates skipped: **{payload['stats_summary']['duplicates_skipped']}**",
        f"- High-priority new leads: **{payload['stats_summary']['high_priority_new']}**",
        f"- Recommended for outreach: **{payload['stats_summary']['recommended_count']}**",
        "",
        "## Notable Patterns",
    ]

    for pattern in payload["notable_patterns"]:
        lines.append(f"- {pattern}")

    lines += ["", "## Leads for Penelopi Review (max 15)", ""]

    if not selected:
        lines.append("- No high-priority leads to review today.")
    else:
        for lead in selected:
            lines.append(_format_lead_bullet(lead))
            lines.append("")

    md_path = out_dir / "daily_for_review.md"
    md_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

    return {
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "payload": payload,
    }
