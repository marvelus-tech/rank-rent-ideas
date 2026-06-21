# Cody — Quick-Start Templates

## Available Templates

### Web Templates

**1. corporate-luxury**
- Palette: Navy (#0a1628) + Gold (#d4a853)
- Typography: Playfair Display + Plus Jakarta Sans
- Use: B2B, consulting, financial services, premium products
- Status: ✅ Ready (based on 2026-06-11 AI Work Output presentation)

**2. tech-modern**
- Palette: Deep Purple (#1a1a2e) + Electric Cyan (#00d4ff)
- Typography: Clash Display + General Sans
- Use: SaaS, AI/tech products, startups
- Status: 🔄 Building

**3. organic-natural**
- Palette: Forest (#1a3a2f) + Sand (#d4c5a9)
- Typography: Cormorant Garamond + Instrument Sans
- Use: Wellness, sustainability, lifestyle brands
- Status: 🔄 Building

**4. brutalist**
- Palette: Pure Black (#000000) + Neon Green (#39ff14)
- Typography: JetBrains Mono + Space Grotesk
- Use: Tech audiences, developers, anti-design statements
- Status: 🔄 Building

### Video Templates

**5. hyperframes-video**
- Base: HTML composition with GSAP timeline
- Use: Animated presentations, music-sync visuals, explainer videos
- Status: 🔄 Building

**6. remotion-sizzle**
- Base: React video with animated search fields, browser mockups
- Use: Product demos, app walkthroughs, sizzle reels
- Status: 🔄 Building

## How to Use

### Quick Start (Command Line)
```bash
# Clone template + customize
cody-start corporate-luxury "AI Automation for Law Firms"

# Output: ~/.openclaw/workspace/presentations/2026-06-11-ai-automation-for-law-firms/
```

### Manual Clone
```bash
# Copy template
cp -r ~/.openclaw/workspace/templates/corporate-luxury \
   ~/.openclaw/workspace/presentations/2026-06-11-my-topic/

# Edit content
cd ~/.openclaw/workspace/presentations/2026-06-11-my-topic/
nano src/config/site.ts

# Build
npm install
npm run build
```

### Via Cody Agent
```
"Cody, build me a corporate deck on AI automation using the luxury template"
```

## Template Structure

```
templates/corporate-luxury/
├── src/
│   ├── components/
│   │   ├── sections/      # Hero, Problem, Features, ROI, Testimonials, CTA
│   │   ├── layout/        # Header, Footer
│   │   └── ui/            # NoiseOverlay, buttons, cards
│   ├── config/
│   │   └── site.ts        # ALL EDITABLE CONTENT — edit this only
│   ├── styles/
│   │   └── globals.css    # CSS variables, animations
│   ├── lib/
│   │   └── utils.ts       # cn() helper
│   ├── hooks/
│   │   └── use-media-query.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx            # Main layout
│   └── main.tsx           # Entry point
├── public/
│   └── favicon.svg
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── README.md
```

## Customization Guide

### 1. Edit Content (config/site.ts)
```typescript
export const siteConfig = {
  name: "Your Company",
  tagline: "Your compelling headline",
  description: "Meta description for SEO",
  
  hero: {
    title: "Your Hero Title",
    subtitle: "Your value proposition",
    cta: { label: "Get Started", href: "#contact" },
    stats: [
      { value: "99%", label: "Success Rate" },
    ],
  },
  
  features: {
    items: [
      {
        icon: "Presentation",
        title: "Feature Name",
        description: "Feature description",
        useCase: "Ideal for: ...",
      },
    ],
  },
  
  // ... more sections
};
```

### 2. Change Colors (tailwind.config.ts)
```typescript
colors: {
  navy: { 950: "#0a1628", ... },
  gold: { 500: "#d4a853", ... },
}
```

### 3. Change Fonts (index.html)
```html
<link href="https://fonts.googleapis.com/css2?family=Your+Display+Font&family=Your+Body+Font" rel="stylesheet">
```

### 4. Add Sections
Copy any section from `src/components/sections/` and customize.

## Build & Deploy

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

**Deploy to:**
- Vercel: `vercel --prod`
- Netlify: Drag `dist/` folder to deploy
- GitHub Pages: Push `dist/` to `gh-pages` branch
- Any static host: Upload `dist/` contents

## Adding New Templates

1. Build a presentation that proves the aesthetic works
2. Copy to `templates/{template-name}/`
3. Remove all content-specific data (keep only structure)
4. Update this README with template details
5. Test with `cody-start {template-name} "Test Topic"`

## Template Checklist

Before marking a template as "Ready":
- [ ] Build passes: `npm run build` succeeds
- [ ] Mobile responsive: Test on actual device
- [ ] Content separated: All text in `config/site.ts`
- [ ] Anti-AI-slop: No Inter, no generic gradients, no template grids
- [ ] Performance: Passes Core Web Vitals
- [ ] Accessibility: WCAG AA minimum
- [ ] SEO: Meta tags, OpenGraph, canonical URL
- [ ] Unique element: One memorable design moment

## Current Status

| Template | Status | Used In Projects |
|----------|--------|------------------|
| corporate-luxury | ✅ Ready | 1 (AI Work Output) |
| tech-modern | 🔄 Building | 0 |
| organic-natural | 🔄 Building | 0 |
| brutalist | 🔄 Building | 0 |
| hyperframes-video | 🔄 Building | 0 |
| remotion-sizzle | 🔄 Building | 0 |

## Next Templates

- [ ] Editorial Magazine (strong grid, dramatic headlines)
- [ ] Soft Pastel (consumer products, friendly)
- [ ] Industrial/Utilitarian (data-heavy, functional)
- [ ] Cyberpunk/Dark (gaming, crypto, edgy)
- [ ] Art Deco (luxury, ornate, geometric)
