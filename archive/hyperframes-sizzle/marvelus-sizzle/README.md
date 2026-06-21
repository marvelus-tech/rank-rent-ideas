# HyperFrames Sizzle Video — Marvelus.cc

## What This Is

A production-ready **HyperFrames sizzle video composition** built from all the research on startup promo videos. Uses plain HTML + CSS + GSAP — no build step, no React, no bundler. Just `index.html` that plays in the browser and renders to MP4 via headless Chrome + FFmpeg.

## The Formula (5 Scenes, 40 Seconds)

| Scene | Duration | What Happens | Technique |
|-------|----------|--------------|-----------|
| **1. Search Query** | 0-6s | Types "AI voice agent for small business" into Google-style search bar | Character-by-character typewriter with blinking cursor |
| **2. Browser Reveal** | 6-14s | Browser window slides up, URL types out, app content appears | Chrome mockup with traffic lights, staggered card reveals |
| **3. Feature Showcase** | 14-24s | "How it works" with numbered steps + phone mockup chat | Split-frame layout, chat bubble stagger, 3D phone tilt |
| **4. Stats Counter** | 24-32s | Big numbers animate up: 50K+ calls, 0% missed, 3x ROI | Counter animation with gradient text |
| **5. CTA Outro** | 32-40s | Bold headline + "Start Free Trial" button with glow pulse | Elastic button entrance, ambient pulse, fade to black |

## How to Use

### Preview in Browser (Instant)
```bash
cd ~/.openclaw/workspace/hyperframes-sizzle/marvelus-sizzle
npx hyperframes preview
# Opens browser at http://localhost:3000
```

### Render to MP4
```bash
# Using the render script
./render.sh

# Or manually
npx hyperframes render --input index.html --output marvelus-sizzle.mp4 --non-interactive
```

### Customize for Your Brand

The composition supports **variables** — edit these at the top of `index.html`:

```html
<html
  data-composition-variables='[
    {"id":"brandName","type":"string","label":"Brand Name","default":"Marvelus"},
    {"id":"tagline","type":"string","label":"Tagline","default":"AI Voice Agents for Small Business"},
    {"id":"accentColor","type":"color","label":"Accent Color","default":"#06b6d4"},
    {"id":"bgColor","type":"color","label":"Background","default":"#0a0e1a"},
    {"id":"searchQuery","type":"string","label":"Search Query","default":"AI voice agent for small business"}
  ]'
>
```

Or override at render time:
```bash
npx hyperframes render --variables '{"brandName":"Nolostsales","accentColor":"#22c55e"}' --output nolostsales.mp4
```

## Architecture

```
marvelus-sizzle/
├── index.html          # Full composition (HTML + CSS + GSAP timeline)
├── render.sh           # One-command render script
└── README.md           # This file
```

**No dependencies.** Everything is inline — fonts load from Google Fonts CDN, GSAP from CDN. The only requirement is HyperFrames CLI for rendering.

## Key Techniques Used

| Technique | Implementation | File |
|-----------|---------------|------|
| **Typewriter effect** | `gsap.set()` per character with 80ms delay | `index.html` |
| **Cursor blink** | `gsap.to()` opacity yoyo loop | `index.html` |
| **Browser mockup** | CSS border + traffic light dots + URL bar | `index.html` |
| **Card stagger** | `gsap.fromTo()` with stagger property | `index.html` |
| **Number counter** | `gsap.to()` object property + onUpdate | `index.html` |
| **Button glow pulse** | `gsap.to()` boxShadow yoyo | `index.html` |
| **Scene transitions** | Visibility toggle + data-start/duration | `index.html` |
| **Background texture** | Radial gradients + noise SVG + grid lines | `index.html` |

## HyperFrames Rules Followed

- ✅ **Layout Before Animation** — Static CSS positions first, then animate
- ✅ **fromTo() everywhere** — Deterministic state at every timeline position
- ✅ **No exit animations** — Scenes stay visible, transitions handle handoff
- ✅ **Final scene fade** — Only exit allowed on last scene
- ✅ **Background texture** — Radial glows + noise + grid (never flat color)
- ✅ **8-10 elements per scene** — Filled frame, never empty
- ✅ **Video sizes** — Headlines 72-120px, body 24-42px
- ✅ **Ambient motion** — Button pulse, cursor blink attach to timeline
- ✅ **Two focal points** — Eye always has somewhere to travel
- ✅ **8 visual presets** — Swiss Pulse color palette, clean typography

## Next Steps

1. **Preview it** — `npx hyperframes preview` to see it in browser
2. **Customize copy** — Edit text in the HTML directly
3. **Change colors** — Update CSS variables or use `--variables` flag
4. **Render it** — `./render.sh` to generate MP4
5. **A/B test** — Duplicate, change search query/headline, render both

## For Nolostsales.cc

Quick rebrand:
- Change `accentColor` to `#22c55e` (green)
- Change `brandName` to `Nolostsales`
- Change `searchQuery` to `recover lost sales with AI`
- Change headline to "Stop losing sales to missed calls"

Everything else stays the same — the template is product-agnostic.
