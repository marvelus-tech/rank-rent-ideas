# revealjs-deck — Apple-Quality Slide Deck Generator

Generate beautiful, Apple-inspired reveal.js HTML presentations from structured data.

## What It Does

Transforms a simple JSON/YAML data file into a fully-designed reveal.js HTML slide deck with:
- Clean typography (Inter font)
- Apple color palette (#1D1D1F, #F5F5F7, #0071E3, #34C759, #FF9500, #FF3B30)
- Card-based layouts with generous whitespace
- Responsive 16:9 presentation format
- Keyboard navigation (arrow keys, space)

## Installation

```bash
cd ~/.openclaw/workspace/skills/revealjs-deck
pip install -r requirements.txt
```

## Usage

### 1. Prepare Your Data (JSON)

```json
{
  "title": "Lead Generation Report",
  "kicker": "Marvelus Intelligence",
  "subtitle": "Automated pipeline results from Victoria, Australia",
  "date": "Wednesday, 27 May 2026",
  "category": "Landscapers",
  
  "metrics": [
    {"value": "10", "label": "Total Leads", "color": "dark"},
    {"value": "7", "label": "New Leads", "color": "green"},
    {"value": "3", "label": "Hot (75+)", "color": "red"},
    {"value": "4", "label": "Warm (50-74)", "color": "orange"}
  ],
  
  "leads": [
    {
      "name": "GreenScape Pro Melbourne",
      "description": "Residential & commercial landscaping · No website · Phone verified",
      "score": "92",
      "priority": "Call Today",
      "priority_color": "red"
    }
  ],
  
  "big_number": {
    "value": "47%",
    "label": "of extracted leads have no website",
    "sublabel": "Immediate AI service opportunity"
  },
  
  "actions": [
    {
      "title": "1. Contact GreenScape Pro Melbourne",
      "description": "Highest score (92). No website. Direct phone outreach recommended.",
      "badge": "Today",
      "badge_color": "red"
    }
  ],
  
  "categories": [
    {"name": "Plumbers", "count": "12 leads · 8 new", "fill": "85%"},
    {"name": "Electricians", "count": "9 leads · 5 new", "fill": "72%"}
  ]
}
```

### 2. Generate The Deck

```bash
python3 scripts/generate.py data/input.json output/deck.html
```

### 3. View It

```bash
open output/deck.html
```

Or serve it:
```bash
cd output && python3 -m http.server 8765
# open http://localhost:8765/deck.html
```

## Data Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✓ | Main presentation title |
| `kicker` | string | ✓ | Small uppercase label above title |
| `subtitle` | string | ✓ | Description below title |
| `date` | string | ✓ | Date/category line |
| `metrics` | array | ✓ | 4 metric cards (value, label, color) |
| `leads` | array | | Top leads with score/priority |
| `big_number` | object | | Centered stat slide |
| `actions` | array | | Recommended next steps |
| `categories` | array | | Category breakdown bars |

## Colors

Use these color keys in your data:
- `dark` → #1D1D1F
- `blue` → #0071E3
- `green` → #34C759
- `orange` → #FF9500
- `red` → #FF3B30
- `gray` → #86868B

## Slide Types Auto-Generated

1. **Title slide** — Dark gradient background, kicker, title, subtitle
2. **Metrics slide** — 4 white cards in a grid
3. **Leads slide** — Lead cards with score + priority badge
4. **Categories slide** — Progress bars with labels
5. **Big number slide** — Centered dramatic stat
6. **Actions slide** — Action cards with urgency badges

## Integration with Cron Jobs

Pipe your agent output directly:
```bash
cd ~/.openclaw/workspace/leadgen && python3 src/generate-report.py | \
  python3 ~/.openclaw/workspace/skills/revealjs-deck/scripts/generate.py - deck.html
```

## Customization

Edit `templates/apple-theme.css` to adjust:
- Color palette
- Font sizes
- Card border-radius
- Spacing

## Dependencies

- Python 3.8+
- Jinja2 (for templating)

## Files

```
skills/revealjs-deck/
├── SKILL.md
├── requirements.txt
├── scripts/
│   └── generate.py
└── templates/
    ├── apple-theme.css
    └── deck-template.html
```
