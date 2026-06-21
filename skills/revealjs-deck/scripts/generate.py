#!/usr/bin/env python3
"""
revealjs-deck — Apple-Quality Slide Deck Generator
Takes structured JSON data and outputs a reveal.js HTML presentation.

Usage:
    python3 generate.py input.json output.html
    cat data.json | python3 generate.py - output.html
    python3 generate.py input.json  # writes to input.html
"""

import json
import sys
import argparse
from pathlib import Path

# Use jinja2 if available, otherwise simple string templating
try:
    from jinja2 import Template
    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False
    print("Warning: jinja2 not found. Using basic templating.", file=sys.stderr)

# Apple Design System
COLORS = {
    "bg": "#F5F5F7",
    "dark": "#1D1D1F",
    "gray": "#86868B",
    "blue": "#0071E3",
    "green": "#34C759",
    "orange": "#FF9500",
    "red": "#FF3B30",
    "white": "#FFFFFF",
}

CSS_TEMPLATE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --apple-bg: {{ colors.bg }};
    --apple-dark: {{ colors.dark }};
    --apple-gray: {{ colors.gray }};
    --apple-blue: {{ colors.blue }};
    --apple-green: {{ colors.green }};
    --apple-orange: {{ colors.orange }};
    --apple-red: {{ colors.red }};
}

.reveal {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--apple-bg);
}

.reveal .slides { text-align: left; }
.reveal .slides section {
    padding: 60px;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Title Slide */
.title-slide {
    background: linear-gradient(135deg, {{ colors.dark }} 0%, #434344 100%);
}
.title-slide * { color: white !important; }
.title-slide .kicker {
    font-size: 18px;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: {{ colors.blue }} !important;
    margin-bottom: 24px;
}
.title-slide h1 {
    font-size: 72px;
    font-weight: 700;
    line-height: 1.05;
    letter-spacing: -0.02em;
    margin-bottom: 24px;
    max-width: 800px;
}
.title-slide .subtitle {
    font-size: 28px;
    font-weight: 400;
    color: {{ colors.gray }} !important;
    max-width: 600px;
    line-height: 1.4;
}
.title-slide .meta {
    margin-top: 60px;
    font-size: 16px;
    font-weight: 500;
    color: {{ colors.gray }} !important;
    letter-spacing: 0.05em;
}

/* Content Slides */
.content-slide h2 {
    font-size: 48px;
    font-weight: 700;
    color: {{ colors.dark }};
    letter-spacing: -0.02em;
    margin-bottom: 8px;
    line-height: 1.1;
}
.content-slide .section-label {
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: {{ colors.blue }};
    margin-bottom: 24px;
}
.content-slide .lead {
    font-size: 24px;
    font-weight: 400;
    color: {{ colors.gray }};
    line-height: 1.5;
    max-width: 700px;
    margin-bottom: 48px;
}

/* Metrics Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    margin-top: 40px;
}
.metric-card {
    background: white;
    border-radius: 20px;
    padding: 32px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}
.metric-value {
    font-size: 48px;
    font-weight: 700;
    color: {{ colors.dark }};
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 8px;
}
.metric-value.green { color: {{ colors.green }}; }
.metric-value.red { color: {{ colors.red }}; }
.metric-value.orange { color: {{ colors.orange }}; }
.metric-value.blue { color: {{ colors.blue }}; }
.metric-label {
    font-size: 15px;
    font-weight: 500;
    color: {{ colors.gray }};
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Lead Cards */
.lead-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-top: 32px;
}
.lead-card {
    background: white;
    border-radius: 16px;
    padding: 28px 32px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.03);
    display: grid;
    grid-template-columns: 1fr auto auto;
    align-items: center;
    gap: 24px;
}
.lead-info h3 {
    font-size: 22px;
    font-weight: 600;
    color: {{ colors.dark }};
    margin-bottom: 6px;
}
.lead-info p {
    font-size: 15px;
    color: {{ colors.gray }};
    margin: 0;
}
.lead-score { text-align: center; }
.lead-score .score {
    font-size: 36px;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1;
}
.lead-score .score.red { color: {{ colors.red }}; }
.lead-score .score.orange { color: {{ colors.orange }}; }
.lead-score .score.gray { color: {{ colors.gray }}; }
.lead-score .label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {{ colors.gray }};
    margin-top: 4px;
}
.priority-badge {
    background: {{ colors.dark }};
    color: white;
    padding: 8px 16px;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.priority-badge.red { background: {{ colors.red }}; }
.priority-badge.orange { background: {{ colors.orange }}; }
.priority-badge.green { background: {{ colors.green }}; }

/* Big Number */
.big-number {
    font-size: 180px;
    font-weight: 700;
    color: {{ colors.dark }};
    letter-spacing: -0.05em;
    line-height: 0.9;
}
.big-number-label {
    font-size: 32px;
    font-weight: 500;
    color: {{ colors.gray }};
    margin-top: 24px;
}

/* Categories */
.category-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 40px;
}
.category-card {
    background: white;
    border-radius: 16px;
    padding: 28px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.03);
}
.category-card .name {
    font-size: 20px;
    font-weight: 600;
    color: {{ colors.dark }};
    margin-bottom: 12px;
}
.category-card .count {
    font-size: 14px;
    color: {{ colors.gray }};
}
.category-card .bar {
    height: 4px;
    background: {{ colors.bg }};
    border-radius: 2px;
    margin-top: 16px;
    overflow: hidden;
}
.category-card .bar-fill {
    height: 100%;
    border-radius: 2px;
    background: {{ colors.blue }};
}

/* Footer */
.slide-footer {
    position: absolute;
    bottom: 40px;
    left: 60px;
    font-size: 13px;
    font-weight: 500;
    color: {{ colors.gray }};
    letter-spacing: 0.05em;
}
.nav-hint {
    position: absolute;
    bottom: 40px;
    right: 60px;
    font-size: 13px;
    color: {{ colors.gray }};
    opacity: 0.6;
}
""".strip()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.title }} — {{ data.kicker }}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.min.css">
    <style>
        {{ css }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">

            <!-- SLIDE 1: Title -->
            <section class="title-slide">
                <div class="kicker">{{ data.kicker }}</div>
                <h1>{{ data.title }}</h1>
                <div class="subtitle">{{ data.subtitle }}</div>
                <div class="meta">{{ data.date }}{% if data.category %} · Category: {{ data.category }}{% endif %}</div>
            </section>

            <!-- SLIDE 2: Metrics -->
            <section class="content-slide">
                <div class="section-label">Executive Summary</div>
                <h2>Pipeline Performance</h2>
                <p class="lead">{{ data.metrics_lead | default("Key metrics from today's pipeline run.") }}</p>
                <div class="metrics-grid">
                    {% for metric in data.metrics %}
                    <div class="metric-card">
                        <div class="metric-value {{ metric.color }}">{{ metric.value }}</div>
                        <div class="metric-label">{{ metric.label }}</div>
                    </div>
                    {% endfor %}
                </div>
                <div class="slide-footer">{{ data.kicker }}</div>
                <div class="nav-hint">→</div>
            </section>

            {% if data.leads %}
            <!-- SLIDE 3: Top Leads -->
            <section class="content-slide">
                <div class="section-label">Priority Targets</div>
                <h2>Top {{ data.leads | length }} Leads</h2>
                <p class="lead">Highest-scoring businesses with identifiable gaps in digital presence and customer engagement.</p>
                <div class="lead-list">
                    {% for lead in data.leads %}
                    <div class="lead-card">
                        <div class="lead-info">
                            <h3>{{ lead.name }}</h3>
                            <p>{{ lead.description }}</p>
                        </div>
                        <div class="lead-score">
                            <div class="score {{ lead.score_color | default('red') }}">{{ lead.score }}</div>
                            <div class="label">Score</div>
                        </div>
                        <div class="priority-badge {{ lead.priority_color | default('red') }}">{{ lead.priority }}</div>
                    </div>
                    {% endfor %}
                </div>
                <div class="slide-footer">{{ data.kicker }}</div>
                <div class="nav-hint">→</div>
            </section>
            {% endif %}

            {% if data.categories %}
            <!-- SLIDE 4: Categories -->
            <section class="content-slide">
                <div class="section-label">Rotation Coverage</div>
                <h2>Category Performance</h2>
                <p class="lead">Pipeline coverage across all tracked business categories.</p>
                <div class="category-grid">
                    {% for cat in data.categories %}
                    <div class="category-card">
                        <div class="name">{{ cat.name }}</div>
                        <div class="count">{{ cat.count }}</div>
                        <div class="bar"><div class="bar-fill" style="width: {{ cat.fill }}"></div></div>
                    </div>
                    {% endfor %}
                </div>
                <div class="slide-footer">{{ data.kicker }}</div>
                <div class="nav-hint">→</div>
            </section>
            {% endif %}

            {% if data.big_number %}
            <!-- SLIDE 5: Big Number -->
            <section class="content-slide" style="align-items: center; text-align: center;">
                <div class="big-number">{{ data.big_number.value }}</div>
                <div class="big-number-label">{{ data.big_number.label }}<br>{{ data.big_number.sublabel }}</div>
                <div style="margin-top: 48px; font-size: 18px; color: var(--apple-gray); max-width: 500px; line-height: 1.6;">
                    {{ data.big_number.description | default("") }}
                </div>
                <div class="slide-footer" style="left: 50%; transform: translateX(-50%);">{{ data.kicker }}</div>
            </section>
            {% endif %}

            {% if data.actions %}
            <!-- SLIDE 6: Actions -->
            <section class="content-slide">
                <div class="section-label">Recommended Actions</div>
                <h2>Next Steps</h2>
                <p class="lead">Priority-ranked actions based on pipeline results.</p>
                <div class="lead-list">
                    {% for action in data.actions %}
                    <div class="lead-card">
                        <div class="lead-info">
                            <h3>{{ action.title }}</h3>
                            <p>{{ action.description }}</p>
                        </div>
                        <div class="priority-badge {{ action.badge_color | default('gray') }}">{{ action.badge }}</div>
                    </div>
                    {% endfor %}
                </div>
                <div class="slide-footer">{{ data.kicker }}</div>
            </section>
            {% endif %}

        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.min.js"></script>
    <script>
        Reveal.initialize({
            hash: true,
            slideNumber: false,
            controls: true,
            progress: false,
            center: false,
            transition: 'fade',
            backgroundTransition: 'fade',
            width: 1280,
            height: 720,
            margin: 0
        });
    </script>
</body>
</html>
""".strip()

def render(data: dict) -> str:
    """Render the HTML deck from structured data."""
    # First render CSS with colors
    css_template = Template(CSS_TEMPLATE)
    rendered_css = css_template.render(colors=COLORS)
    
    # Then render HTML with data and rendered CSS
    html_template = Template(HTML_TEMPLATE)
    return html_template.render(data=data, colors=COLORS, css=rendered_css)

def load_data(source: str) -> dict:
    """Load JSON data from file or stdin."""
    if source == "-":
        return json.load(sys.stdin)
    path = Path(source)
    if not path.exists():
        print(f"Error: File not found: {source}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r") as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Generate Apple-quality reveal.js decks from JSON data")
    parser.add_argument("input", help="Input JSON file (or - for stdin)")
    parser.add_argument("output", nargs="?", help="Output HTML file (default: input filename with .html)")
    args = parser.parse_args()
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(args.input).with_suffix(".html")
    
    # Load data
    data = load_data(args.input)
    
    # Render HTML
    html = render(data)
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✓ Deck generated: {output_path.absolute()}")
    print(f"  Slides: {data.get('title', 'Untitled')}")
    print(f"  Open with: open {output_path}")

if __name__ == "__main__":
    main()
