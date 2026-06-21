---
name: remotion-video
description: Generate polished, Apple-quality Remotion MP4 videos from structured JSON ideas and data. Viral-optimized durations and platform formats.
metadata:
  tags: remotion, video, motion-design, automation, mp4, viral, social-media
---

## What this skill does

This skill turns a video concept + JSON data into a professional, scroll-stopping Remotion composition and renders an MP4.

- **Project root:** `~/.openclaw/workspace/remotion-studio/`
- **Skill root:** `~/.openclaw/workspace/skills/remotion-video/`
- **Output renders:** `~/.openclaw/workspace/remotion-studio/output/`

## Viral Duration Presets

Choose durations based on platform and goal. These are backed by completion-rate data and algorithm preferences:

| Preset | Duration | Best For | Why It Works |
|--------|----------|----------|--------------|
| `hook` | 5s | TikTok/Reels ultra-short | 95%+ completion rate. Algorithms reward 100% watches. |
| `snippet` | 7s | Twitter/X, Instagram Stories | Micro-content. Highest share-to-view ratio. |
| `flash` | 10s | Quick announcements, alerts | Punchy. One scene + one stat. |
| `short` | **15s** | **TikTok/Reels sweet spot** | Optimal for algorithmic boost. Most engaging short-form length. |
| `standard` | 30s | YouTube Shorts (max) | Full narrative with hook → body → CTA. |
| `story` | 45s | LinkedIn, Instagram carousel-to-video | Professional storytelling. Time for context + data + action. |
| `deep` | 60s | YouTube, LinkedIn long-form | Deep dive. Best for educational/explanatory content. |

**Default:** `standard` (30 seconds)

**Recommendation:**
- **Sales/promo content:** Use `short` (15s) or `standard` (30s)
- **Data reports:** Use `standard` (30s) or `story` (45s)
- **Quick announcements:** Use `hook` (5s) or `flash` (10s)
- **LinkedIn/Twitter:** Use `snippet` (7s) or `story` (45s)

## Platform Format Presets

| Format | Dimensions | Aspect | Platforms |
|--------|-----------|--------|-----------|
| `short` | 1080×1920 | 9:16 | **TikTok, Instagram Reels, YouTube Shorts** |
| `vertical` | 1080×1920 | 9:16 | Mobile-first vertical |
| `square` | 1080×1080 | 1:1 | Instagram Feed, Twitter/X, Facebook |
| `landscape` | 1920×1080 | 16:9 | YouTube main, LinkedIn, Twitter/X landscape |
| `widescreen` | 1920×1080 | 16:9 | Desktop-first presentations |

**Default:** `short` (1080×1920 portrait)

## JSON Schema Reference

### Top-level shape

```json
{
  "id": "string-kebab-or-date-id",
  "template": "lead-report | data-story | announcement | 3d-promo",
  "durationInSeconds": "short",
  "format": "short",
  "props": { }
}
```

### Duration specification

```json
{
  "durationInSeconds": "short"
}
```

Can be:
- **String preset:** `hook`, `snippet`, `flash`, `short`, `standard`, `story`, `deep`
- **Number:** Any integer (e.g., `22` for exactly 22 seconds)

### Format specification

```json
{
  "format": "short"
}
```

Options: `short`, `vertical`, `square`, `landscape`, `widescreen`

### `3d-promo` props (NEW — Pro 3D)

Production-ready 3D promotional video with cinematic motion design.

```json
{
  "kicker": "LUSTRE · SKIN",
  "title": "Skincare that truly understands you",
  "benefit": "Personalized skin wellness",
  "cta": "Start Your Journey",
  "imageUrl": "screenshot.png",
  "durationInSeconds": 15,
  "logoText": "LUSTRE"
}
```

**Pro techniques included:**

| Technique | Effect |
|-----------|--------|
| **Glowing Logo Intro** | Text fades in with intensifying glow (0-2s) |
| **Light Streak Transitions** | Horizontal/vertical sweep lines between scenes |
| **Floating 3D Cards** | Screenshot on beveled card with reflective surface |
| **Cinematic Camera** | Push-in + orbit with overshoot and settling |
| **Ambient Particles** | Minimal dust motes for depth |
| **Animated Gradient BG** | Shader-based slow-moving gradient |
| **Hover Tilt** | Cards tilt slightly based on time (parallax feel) |
| **Pulsing CTA** | Button breathes with glow layers |
| **Overshoot + Settle** | Text scales past 1.0 then settles back |
| **Anticipation** | Elements appear slightly before expected |
| **Sound Markers** | Comments indicate where music/sfx would hit |

### `lead-report` props

```json
{
  "title": "Lead Generation Report",
  "kicker": "Marvelus Intelligence",
  "date": "May 27, 2026",
  "durationInSeconds": 15,
  "metrics": [{"label": "Qualified Leads", "value": 48, "suffix": "%"}],
  "leads": [{"name": "Jane", "company": "Acme", "score": 94, "priority": "Critical"}],
  "bigNumber": {"value": "37%", "label": "Higher close rate"},
  "actions": [{"title": "Do X", "detail": "Why", "urgency": "High"}]
}
```

### `data-story` props

```json
{
  "title": "Revenue Mix Story",
  "kicker": "Quarterly Strategy",
  "subtitle": "What changed",
  "points": [{"label": "Referrals", "value": 42, "color": "#0071E3"}]
}
```

### `announcement` props

```json
{
  "kicker": "Product Update",
  "title": "AI Follow-Ups, Now in Real Time",
  "benefit": "Never lose high-intent leads",
  "cta": "Turn it on today"
}
```

## URL-Based Video Generation (NEW)

Turn any website into a promotional video automatically.

### 1) Fetch a website → extract content → generate JSON

```bash
python3 ~/.openclaw/workspace/skills/remotion-video/scripts/fetch-url.py \
  https://remotion.dev \
  --template announcement \
  --duration short \
  --format short \
  --screenshot /tmp/screenshot.png \
  /tmp/video-data.json
```

What it does:
1. Opens the website in a headless browser
2. Takes a full-page screenshot
3. Extracts: title, headlines, description, stats/numbers, CTAs, images
4. Builds a JSON file ready for video generation

Options:
- `--template` — `announcement`, `lead-report`, `data-story`
- `--duration` — Any viral preset or number of seconds
- `--format` — Platform format
- `--screenshot` — Save screenshot path

### 2) One-command URL → Video pipeline

```bash
python3 ~/.openclaw/workspace/skills/remotion-video/scripts/web-to-video.py \
  https://remotion.dev \
  --template announcement \
  --duration short \
  --format short
```

This runs the complete pipeline:
1. **Fetch** — Screenshot + content extraction
2. **Generate** — Create Remotion composition
3. **Render** — Output MP4

Output: `~/.openclaw/workspace/remotion-studio/output/web-[domain]-[template].mp4`

### 3) URL-based workflow examples

**TikTok/Reels promo from a product page:**

```bash
python3 ~/.openclaw/workspace/skills/remotion-video/scripts/web-to-video.py \
  https://yourproduct.com \
  --template announcement \
  --duration short \
  --format short
```

**LinkedIn story from a blog post:**

```bash
python3 ~/.openclaw/workspace/skills/remotion-video/scripts/web-to-video.py \
  https://yourblog.com/article \
  --template data-story \
  --duration story \
  --format landscape
```

**Twitter/X flash from a landing page:**

```bash
python3 ~/.openclaw/workspace/skills/remotion-video/scripts/web-to-video.py \
  https://yoursite.com \
  --template announcement \
  --duration snippet \
  --format square
```

**Generate only, preview in Remotion Studio:**

```bash
python3 ~/.openclaw/workspace/skills/remotion-video/scripts/web-to-video.py \
  https://yoursite.com \
  --no-render

# Then preview
npx remotion studio
```

### 4) Content extraction details

The fetch script automatically extracts:

| Data | Source | Used In |
|------|--------|---------|
| **Title** | `document.title` | Video title |
| **Description** | Meta description / og:description | Benefit/subtitle text |
| **Headlines** | `<h1>`, `<h2>` tags | Title options, data points |
| **Stats** | Percentages, dollar amounts, multiples | Metrics, data-story points |
| **CTAs** | Button/link text with action verbs | Call-to-action text |
| **Images** | `<img>` src attributes | Asset references |
| **Screenshot** | Full-page render | Reference / manual use |

### 5) Using the screenshot

Screenshots are saved to `remotion-studio/output/screenshots/` by default.

You can use them for:
- **Manual review** — Check what the bot "saw"
- **Asset inclusion** — Reference in custom templates
- **Thumbnail** — Use as video thumbnail for social platforms

```bash
# Screenshot only, no video
python3 ~/.openclaw/workspace/skills/remotion-video/scripts/fetch-url.py \
  https://example.com \
  --screenshot /tmp/screenshot.png
```

## How to use (JSON input)

### 1) Generate a composition from JSON

```bash
python3 ~/.openclaw/workspace/skills/remotion-video/scripts/generate.py \
  ~/.openclaw/workspace/skills/remotion-video/examples/sample-lead-report.json
```

This will:
1. Create a composition file in `remotion-studio/src/compositions/`
2. Register it in `remotion-studio/src/Root.tsx` with correct dimensions
3. Print the new file path and specs

### 2) Render to MP4

```bash
~/.openclaw/workspace/skills/remotion-video/scripts/render.sh lead-report
# or a generated id, e.g.
~/.openclaw/workspace/skills/remotion-video/scripts/render.sh lead-report-2026-05-27
```

Optional output filename:

```bash
~/.openclaw/workspace/skills/remotion-video/scripts/render.sh lead-report custom-output.mp4
```

### 3) Viral Workflow Example

**15-second TikTok/Reels lead report:**

```json
{
  "id": "lead-daily-15s",
  "template": "lead-report",
  "durationInSeconds": "short",
  "format": "short",
  "props": {
    "title": "Today's Leads",
    "kicker": "Marvelus",
    "date": "May 27, 2026",
    "durationInSeconds": 15,
    "metrics": [
      {"label": "New Leads", "value": 7},
      {"label": "Hot", "value": 3},
      {"label": "Worth", "value": 45, "suffix": "K"}
    ],
    "leads": [
      {"name": "GreenScape", "company": "Melbourne", "score": 92, "priority": "Critical"}
    ],
    "bigNumber": {"value": "47%", "label": "No website = AI opportunity"},
    "actions": [{"title": "Call them now", "detail": "92 score, no website", "urgency": "High"}]
  }
}
```

```bash
python3 ~/.openclaw/workspace/skills/remotion-video/scripts/generate.py input.json
~/.openclaw/workspace/skills/remotion-video/scripts/render.sh lead-daily-15s
```

**7-second Twitter/X flash update:**

```json
{
  "id": "flash-update",
  "template": "announcement",
  "durationInSeconds": "snippet",
  "format": "square",
  "props": {
    "kicker": "Breaking",
    "title": "3 Hot Leads Today",
    "benefit": "All scored 90+",
    "cta": "Check Telegram"
  }
}
```

### 4) Batch render multiple durations

```bash
# Generate same content in 3 viral lengths
for duration in hook short standard; do
  cat > /tmp/lead-${duration}.json << EOF
{
  "id": "lead-${duration}",
  "template": "lead-report",
  "durationInSeconds": "${duration}",
  "format": "short",
  "props": { ... }
}
EOF
  python3 ~/.openclaw/workspace/skills/remotion-video/scripts/generate.py /tmp/lead-${duration}.json
  ~/.openclaw/workspace/skills/remotion-video/scripts/render.sh lead-${duration}
done
```

## Render + Deliver Pipeline

### Automatic Telegram Fix (NEW)

Every render now automatically produces **two files**:

1. **Raw** — High quality for editing/re-uploading
2. **Telegram-safe** — Guaranteed to play in Telegram

The render script (`render.sh`) now auto-detects and fixes:
- `yuvj420p` → `yuv420p` pixel format conversion
- `High` profile → `Baseline` profile
- Adds `faststart` for streaming

### Manual validation

```bash
# Check if any video is Telegram-ready
python3 ~/.openclaw/workspace/skills/remotion-video/scripts/validate-telegram.py video.mp4

# Fix an incompatible video
~/.openclaw/workspace/skills/remotion-video/scripts/telegram-fix.sh video.mp4 output.mp4
```

### Why Telegram fails (technical)

| Issue | Cause | Fix |
|-------|-------|-----|
| `yuvj420p` | Full-range color (Remotion default) | Convert to `yuv420p` with `-color_range tv` |
| `High` profile | Advanced H.264 features | Use `Baseline` profile |
| No `faststart` | Moov atom at end of file | Add `-movflags +faststart` |
| Missing audio | Silent video | Add AAC audio track |

### Complete render command

```bash
~/.openclaw/workspace/skills/remotion-video/scripts/render.sh composition-id

# Outputs:
#   output/composition-id.mp4        (raw)
#   output/composition-id-telegram.mp4 (guaranteed compatible)
```

## Scene Timing Breakdown

LeadReportVideo auto-scales scene durations proportionally based on total duration:

| Scene | % of Duration | 15s | 30s | 60s |
|-------|--------------|-----|-----|-----|
| Title/Intro | 18% | 2.7s | 5.4s | 10.8s |
| Metrics | 18% | 2.7s | 5.4s | 10.8s |
| Leads | 20% | 3.0s | 6.0s | 12.0s |
| Big Number | 13% | 1.9s | 3.9s | 7.8s |
| Actions | 18% | 2.7s | 5.4s | 10.8s |
| Outro | 13% | 1.9s | 3.9s | 7.8s |

Minimum total duration: **5 seconds** (150 frames)

## Add a custom template

1. Create a new template component in `remotion-studio/src/compositions/`.
2. Support `durationInSeconds` prop for dynamic scaling.
3. Export prop type + default props from that file.
4. Add a `<Composition />` entry in `src/Root.tsx`.
5. Extend `TEMPLATE_MAP` in `scripts/generate.py` with:
   - template key
   - component name
   - props type name
6. Provide JSON payload using the new `template` string.

## Integration notes

- **revealjs-deck skill**: use deck JSON/outline as input source for `announcement` or `data-story` props.
- **lead scraper workflows**: feed scraped lead metrics directly into `lead-report` JSON and batch-render daily recaps in multiple durations.
- **website-to-video workflow**: use `fetch-url.py` or `web-to-video.py` to turn any webpage into a promotional video with auto-extracted content.
- **Social media posting**: combine with xurl skill for Twitter/X, or manually upload to TikTok/Instagram/LinkedIn.
- **Screenshot pipeline**: screenshots are auto-saved alongside videos for reference/thumbnails.

## Viral Best Practices

1. **First 1-2 seconds** are critical — hook with the kicker or strongest stat
2. **15 seconds** is the algorithmic sweet spot for TikTok/Reels
3. **7 seconds** gets highest completion and share rates on Twitter/X
4. **Under 30 seconds** = YouTube Shorts eligible (separate algorithm boost)
5. **1:1 square** format performs best on Twitter/X feed and Instagram feed
6. **9:16 portrait** is required for TikTok/Reels/Shorts native upload
7. Render multiple durations/formats from the same data for A/B testing

## Troubleshooting

- If fonts fail, run `npm install` in `remotion-studio` to ensure `@remotion/google-fonts` is installed.
- If render fails due to browser issues, run `npx remotion browser ensure`.
- Use `npm run compositions` to inspect available composition IDs.
- For very short durations (`hook` 5s), scenes compress aggressively — keep props minimal (1 metric, 1 lead max).
