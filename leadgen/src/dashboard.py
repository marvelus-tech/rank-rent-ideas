from __future__ import annotations

from pathlib import Path
from jinja2 import Template

DASHBOARD_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset='utf-8'/>
  <title>Leadgen Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    .kpi { display:inline-block; margin-right: 24px; padding:12px; background:#f5f5f5; border-radius:8px; }
    table { border-collapse: collapse; width:100%; margin-top:16px; }
    th, td { border:1px solid #ddd; padding:8px; text-align:left; font-size:14px; }
    th { background:#222; color:#fff; }
  </style>
</head>
<body>
  <h1>Lead Pipeline Dashboard</h1>
  <div class='kpi'>Total Leads: <b>{{ total }}</b></div>
  <div class='kpi'>High Priority: <b>{{ high }}</b></div>
  <div class='kpi'>Due Follow-ups: <b>{{ due }}</b></div>

  <h2>Top Opportunities</h2>
  <table>
    <tr><th>Name</th><th>Category</th><th>Location</th><th>Score</th><th>Priority</th><th>Stage</th><th>Website</th></tr>
    {% for row in rows %}
    <tr>
      <td>{{ row.name }}</td>
      <td>{{ row.category }}</td>
      <td>{{ row.location }}</td>
      <td>{{ row.lead_score }}</td>
      <td>{{ row.priority }}</td>
      <td>{{ row.pipeline_stage }}</td>
      <td><a href="{{ row.website }}">link</a></td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""


def render_dashboard(df, due_df, output_path: str):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    html = Template(DASHBOARD_TEMPLATE).render(
        total=len(df),
        high=int((df["priority"] == "high").sum()) if "priority" in df.columns else 0,
        due=len(due_df),
        rows=df.sort_values("lead_score", ascending=False).head(50).fillna("").to_dict("records"),
    )
    output.write_text(html, encoding="utf-8")
    return str(output)
