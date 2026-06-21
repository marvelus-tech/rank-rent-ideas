from __future__ import annotations

from datetime import date
from pathlib import Path


def write_daily_report(all_df, new_df, stats: dict, stage_counts: dict[str, int], output_dir: str):
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    report_path = out_dir / f"daily_report_{today}.md"

    if new_df is None or new_df.empty:
        high_priority = new_df
    else:
        high_priority = new_df[new_df["priority"] == "high"]

    lines = [
        f"# Leadgen Daily Report — {today}",
        "",
        f"- Total leads scanned: **{stats.get('total_scanned', 0)}**",
        f"- New leads found: **{stats.get('new_leads', 0)}**",
        f"- Duplicates skipped: **{stats.get('duplicates_skipped', 0)}**",
        f"- Total leads in database: **{len(all_df) if all_df is not None else 0}**",
        "",
        "## Pipeline Stage Counts",
        "",
    ]

    if stage_counts:
        for stage, count in sorted(stage_counts.items()):
            lines.append(f"- {stage}: **{count}**")
    else:
        lines.append("- No leads in pipeline yet")

    lines += ["", "## Top New High-Priority Leads (Daily Delta)", ""]

    if high_priority is None or high_priority.empty:
        lines.append("- No new high-priority leads today")
    else:
        for _, row in high_priority.sort_values("lead_score", ascending=False).head(20).iterrows():
            email = row.get('email', '') or 'n/a'
            phone = row.get('phone', '') or 'n/a'
            missing = []
            if email == 'n/a':
                missing.append('email')
            if phone == 'n/a':
                missing.append('phone')
            missing_note = f" | Missing contact: {', '.join(missing)} (manual research)" if missing else ""
            lines.append(
                f"- **{row.get('name', '')}** ({row.get('category', '')}, {row.get('location', '')}) | "
                f"Score: {row.get('lead_score', 0)} | Rating: {row.get('rating', 'n/a')} | "
                f"Reviews: {row.get('reviews', 'n/a')} | Email: {email} | Phone: {phone} | Website: {row.get('website', '')}{missing_note}"
            )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return str(report_path)
