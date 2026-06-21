# Cody — Pre-Loaded Skills & Templates

## How It Works

### 1. Pre-Loaded Skills (Auto-Injected)

When Cody spawns, his task prompt automatically includes:

```
## LOADED DESIGN SKILLS

### Skill 1: penelopi-web-design
[Full content of ~/.openclaw/workspace/skills/penelopi-web-design/SKILL.md]

### Skill 2: elite-frontend-design  
[Full content of ~/.openclaw/workspace/skills/elite-frontend-design/design-bible.md]

### Skill 3: frontend-design-ultimate
[Full content of ~/.openclaw/workspace/skills/frontend-design-ultimate/SKILL.md]

### Skill 4: hyperframes
[Key video composition patterns]

### Skill 5: remotion-video
[MP4 generation workflows]
```

**Result:** Cody doesn't waste tokens reading skills. He already knows:
- Anti-AI-slop rules (no Inter, no generic gradients)
- Typography pairings that work
- Animation patterns that convert
- Color hierarchies that feel premium
- Mobile-first breakpoints

### 2. Template Library (Clone & Customize)

Instead of "build a presentation from scratch," Cody clones a proven template:

```bash
# Template structure
templates/
├── corporate-luxury/          # Navy + Gold, Playfair + Jakarta
│   ├── src/
│   │   ├── components/
│   │   │   ├── sections/
│   │   │   │   ├── Hero.tsx
│   │   │   │   ├── Problem.tsx
│   │   │   │   ├── Features.tsx
│   │   │   │   ├── ROI.tsx
│   │   │   │   ├── Testimonials.tsx
│   │   │   │   └── CTA.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   └── Footer.tsx
│   │   │   └── ui/
│   │   ├── config/site.ts     # Content only — edit this
│   │   ├── styles/globals.css
│   │   └── App.tsx
│   ├── package.json
│   ├── tailwind.config.ts
│   └── vite.config.ts
│
├── tech-modern/               # Purple + Cyan, Clash + General
├── organic-natural/           # Forest + Sand, Cormorant + Instrument
├── brutalist/                 # Black + Neon, monospace
└── editorial-magazine/        # Strong grid, dramatic headlines
```

**Usage:**
```bash
# Cody clones template, swaps content
cp -r templates/corporate-luxury presentations/2026-06-11-ai-work-output/
# Then edits config/site.ts with new content
# Keeps all design system, animations, layout intact
```

### 3. Accumulated Learning (Persistent Memory)

Cody writes learnings to `~/Obsidian/Penelopi/Cody-Learnings.md` after each project:

```markdown
## 2026-06-11 — AI Work Output Presentation
- Palette: Navy + Gold worked well for B2B audience
- Layout: Asymmetric hero got positive reaction
- Animation: Staggered reveal at 0.1s intervals felt smooth
- Fix: Added more whitespace between sections (mobile felt cramped)
- Next: Try horizontal scroll for the 10 sites section
```

**Result:** Over time, Cody knows:
- "For corporate clients, always start with Navy + Gold"
- "Staggered reveal converts 23% better than fade-in"
- "Mobile needs 16px minimum font, always"

## Comparison: Before vs After

| Aspect | Before (Ad-hoc) | After (Cody) |
|--------|----------------|--------------|
| **Setup** | Read skills each time (2-3 min) | Pre-loaded, instant start |
| **Design decisions** | Rebuild from scratch | Clone proven template |
| **Consistency** | Inconsistent quality | Same high standard every time |
| **Learning** | None | Accumulated in Cody-Learnings.md |
| **Token cost** | High (reads skills + builds) | Low (clones template + swaps content) |
| **Speed** | 5-8 minutes | 2-3 minutes |
| **Output** | Sometimes misses anti-slop rules | Never misses, rules are muscle memory |

## What You Get

**For you:**
- Say "Build me a deck on X" → Cody delivers in 2-3 minutes
- Every presentation looks like it came from the same premium studio
- No more "this looks AI-generated" feedback

**For Cody:**
- Starts with full context, no cold start
- Templates handle 80% of work, only customizes content
- Learns from each project, gets better over time

## Current Templates Available

1. **Corporate Luxury** — B2B, consulting, financial services
2. **Tech Modern** — SaaS, AI products, startups
3. **Organic Natural** — Wellness, sustainability, lifestyle

**Next templates to build:**
- Brutalist (tech audiences)
- Editorial Magazine (content-heavy)
- Soft Pastel (consumer products)

## How to Request

**Simple:**
```
"Cody, build me a presentation on [topic]"
```

**With direction:**
```
"Cody, corporate deck on AI automation for law firms, use the luxury template"
```

**With content:**
```
"Cody, turn this transcript into a website: [paste content]"
```
