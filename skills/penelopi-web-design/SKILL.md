---
name: penelopi-web-design
description: >
  Supreme frontend design skill for creating distinctive, production-grade web interfaces.
  Use for ANY website, landing page, dashboard, web app, marketing site, portfolio, or frontend component.
  Enforces anti-AI-slop aesthetics, performance-first engineering, accessibility compliance,
  and conversion-optimized UX. Generates React/Next.js, Vue, or HTML/CSS/JS output.
  Now includes 22 curated brand DESIGN.md files (Vercel, Linear, Stripe, Apple, etc.) for instant brand-aligned aesthetics.
  Triggers on all web design, frontend development, UI creation, or site building tasks.
metadata:
  openclaw:
    emoji: "🎨"
    requires:
      bins: ["node", "npm"]
  tags: [web-design, frontend, ui, react, nextjs, tailwind, shadcn, accessibility, performance]
---

# Penelopi Web Design — Supreme Frontend Skill

Create distinctive, production-grade web interfaces that avoid generic "AI slop" aesthetics. Ship real working code with exceptional attention to design craft, performance engineering, accessibility compliance, and conversion-optimized UX.

## When to Use

**ALWAYS trigger this skill when:**
- Building any website, landing page, or web application
- Creating React/Vue/HTML components, dashboards, or forms
- Designing marketing sites, portfolios, SaaS products, or e-commerce
- Refactoring or restyling existing web interfaces
- Any task containing: website, landing page, web app, frontend, UI, design, page, site, component

## Design Thinking (Mandatory First Step)

Before writing ANY code, commit to a **BOLD aesthetic direction**. Answer these questions:

1. **Purpose**: What problem does this solve? Who uses it? What's the desired action?
2. **Tone**: Pick ONE extreme and commit fully:
   - **Brutally Minimal** — Sparse, monochrome, massive typography, raw edges
   - **Maximalist Chaos** — Layered, dense, overlapping, controlled disorder
   - **Retro-Futuristic** — Neon, geometric, CRT aesthetics, scanlines
   - **Organic/Natural** — Soft curves, earth tones, hand-drawn, flowing
   - **Luxury/Refined** — Subtle animations, premium typography, restrained palette
   - **Editorial/Magazine** — Strong grid, dramatic headlines, whitespace as hero
   - **Brutalist/Raw** — Exposed structure, harsh contrasts, anti-design
   - **Art Deco/Geometric** — Gold accents, symmetry, ornate patterns
   - **Soft/Pastel** — Rounded, gentle gradients, friendly, approachable
   - **Industrial/Utilitarian** — Functional, monospace, data-dense, terminal-like
   - **Cyberpunk/Dark Mode** — Dark bg, neon accents, high contrast, terminal aesthetic
3. **Brand Design System** (Optional but powerful): Does the user want a specific brand aesthetic?
   - Check `references/design-systems/` for curated DESIGN.md files from real brands
   - If the prompt mentions a brand name (e.g., "like Linear", "in the style of Stripe"), load the matching DESIGN.md and apply its tokens
   - If no brand match, fall back to the anti-AI-slop rules below
4. **Differentiation**: What's the ONE thing someone will screenshot and remember?
5. **Conversion**: What's the primary CTA? Is it visible above the fold? Is the funnel clear?

**CRITICAL**: Timid middle-ground designs fail. Bold maximalism and refined minimalism BOTH work. Intentionality > intensity.

## Brand Design System Library

The `references/design-systems/` directory contains **22 curated DESIGN.md files** extracted from real-world brand websites. These are ready-to-use design tokens, color palettes, typography rules, and component styles.

### How to Use

When a prompt mentions a brand or aesthetic:
> "Build a SaaS landing page **in the style of Linear**"  
> "Make it look like **Stripe's developer docs**"  
> "I want that **retro Nintendo 2001** vibe"

1. **Auto-detect** the brand keyword in the prompt
2. **Load** the matching DESIGN.md from `references/design-systems/{category}/{brand}.md`
3. **Apply** its tokens to the generated `site.ts` and `globals.css`
4. **Fall back** to anti-AI-slop rules if no brand match

### Available Design Systems

| Category | Brands | Best For |
|----------|--------|----------|
| **AI & Dev Tools** | `vercel`, `linear`, `raycast`, `supabase`, `cursor`, `warp`, `framer` | Developer platforms, SaaS, dashboards, CLI tools |
| **Fintech** | `stripe`, `wise`, `revolut`, `coinbase` | Payment apps, banking, crypto, financial dashboards |
| **Consumer** | `apple`, `nike`, `spotify`, `airbnb`, `notion` | Lifestyle apps, retail, media, productivity |
| **Automotive** | `bmw`, `ferrari`, `lamborghini`, `tesla` | Luxury brands, high-performance products |
| **Retro** | `dell-1996`, `nintendo-2001` | Nostalgic campaigns, vintage aesthetics, Y2K revival |

### DESIGN.md Structure

Each file follows the Google Stitch DESIGN.md specification with:
- **Visual Theme & Atmosphere** — Mood, density, design philosophy
- **Color Palette & Roles** — Semantic names + hex + functional roles
- **Typography Rules** — Font families, full hierarchy table
- **Component Stylings** — Buttons, cards, inputs, navigation with states
- **Layout Principles** — Spacing scale, grid, whitespace philosophy
- **Depth & Elevation** — Shadow system, surface hierarchy
- **Do's and Don'ts** — Design guardrails and anti-patterns
- **Responsive Behavior** — Breakpoints, touch targets, collapsing strategy
- **Agent Prompt Guide** — Quick color reference, ready-to-use prompts

### Quick Reference: Brand Keywords

Use these keywords in prompts for auto-detection:

```
vercel, linear, raycast, supabase, cursor, warp, framer,
stripe, wise, revolut, coinbase,
apple, nike, spotify, airbnb, notion,
bmw, ferrari, lamborghini, tesla,
dell-1996, nintendo-2001, retro, y2k, vintage
```

### Example: Applying a Brand Design System

**User prompt**: "Build a developer dashboard in the style of Raycast"

**What the skill does**:
1. Detects "raycast" → loads `references/design-systems/ai-devtools/raycast.md`
2. Extracts tokens:
   - Canvas: `#07080a` (near-black)
   - Surface ladder: `#0d0d0d` → `#101111` → `#121212`
   - Typography: Inter with `ss03` stylistic set
   - Hairline borders: `#242728`
   - Accent colors: blue `#57c1ff`, red `#ff6161`, green `#59d499`, yellow `#ffc533`
3. Generates `globals.css` with CSS variables mapped to DESIGN.md tokens
4. Generates `site.ts` with Raycast-style component configurations
5. Builds components using the extracted spacing, radius, and shadow rules

### Fallback Behavior

If no brand keyword is detected:
- Use the **Anti-AI-Slop Doctrine** (see below)
- Apply the **Typography System** and **Color Theory** rules
- Generate a distinctive custom aesthetic from scratch

---

## The Anti-AI-Slop Doctrine (Non-Negotiable)

### BANNED — Never Use

| Category | Banned | Why |
|----------|--------|-----|
| **Fonts** | Inter, Roboto, Arial, Helvetica, Open Sans, Segoe UI, system-ui, sans-serif default | These are the #1 signal of AI-generated design. Every generic SaaS uses them. |
| **Colors** | Purple/blue gradient on white; evenly distributed 5+ color palettes; gray backgrounds that say "I gave up" | The cardinal sin of AI slop. No visual hierarchy, no emotion. |
| **Layout** | Centered hero + 3-column features + CTA; perfect symmetry everywhere; predictable card grids | Template thinking. No tension, no interest, no memorability. |
| **Motion** | Generic fade-in on every element; no orchestration; 1s+ sluggish transitions | Scattered micro-interactions create fatigue. One orchestrated moment creates delight. |
| **Backgrounds** | Solid white (#ffffff); solid light gray (#f5f5f5); subtle gradient as "bold" choice | Atmosphere and depth signal intention. Solids signal apathy. |

### REQUIRED — Always Include

- **Distinctive typography** with pairing strategy (display + body + mono)
- **Dominant + sharp accent** color hierarchy (60-30-10 rule)
- **Atmospheric background** (gradient mesh, noise texture, pattern, layered transparencies)
- **Asymmetric or intentional layout** (overlap, diagonal, grid-breaking, generous negative space)
- **Orchestrated motion** (staggered page load, scroll-triggered reveals, surprising hover states)
- **Clear conversion path** (CTA hierarchy, social proof placement, trust signals)

## Typography System

See **[references/typography-system.md](references/typography-system.md)** for the complete type scale, pairing strategies, and loading patterns.

**Quick Rules:**
- Display font: Bold personality (Clash Display, Cabinet Grotesk, Playfair Display, Cormorant Garamond)
- Body font: Refined readability (Plus Jakarta Sans, General Sans, Instrument Sans, Source Sans 3)
- Mono font: Technical credibility (JetBrains Mono, DM Mono, IBM Plex Mono)
- Size jumps: Minimum 3x ratio (e.g., 16px body → 48px heading)
- Weight contrast: Use extremes (100 vs 900, 300 vs 700)
- Load via Google Fonts `<link>` or `@import` — NEVER rely on system fonts

## Color Theory

See **[references/color-theory.md](references/color-theory.md)** for palette generation, dark mode, and contrast rules.

**Quick Rules:**
- 60% dominant (background), 30% secondary (cards/sections), 10% accent (CTAs/highlights)
- Commit to dark OR light. Gray middle-grounds signal uncertainty.
- Use CSS variables for everything: `--bg-primary`, `--bg-secondary`, `--accent`, `--text-primary`, `--text-muted`
- CTA buttons must pop dramatically against their container
- Test contrast: WCAG AA minimum (4.5:1 text, 3:1 UI components)

## Motion & Animation

See **[references/motion-patterns.md](references/motion-patterns.md)** for orchestration strategies, performance-safe animation, and reduced-motion support.

**Quick Rules:**
- **One orchestrated page load** > scattered micro-interactions everywhere
- Stagger hero elements: badge (0.1s), title (0.2s), subtitle (0.3s), CTA (0.4s)
- Durations: 200-400ms (snappy). Never exceed 600ms for UI feedback.
- Use `transform` and `opacity` only for animations (GPU-accelerated)
- NEVER animate `width`, `height`, `top`, `left`, `margin`, `padding` — these trigger layout thrashing
- Always respect `prefers-reduced-motion`
- Use Intersection Observer for scroll-triggered reveals (not scroll event listeners)

## Layout & Spatial Composition

See **[references/layout-patterns.md](references/layout-patterns.md)** for grid systems, asymmetric compositions, and section patterns.

**Quick Rules:**
- Asymmetry with purpose. Overlap elements. Break the grid.
- Diagonal flow, off-center heroes, staggered card heights
- Generous negative space OR controlled density — pick one, commit fully
- Every section needs a focal point. No section should look like a template.
- Use CSS Grid for 2D layouts, Flexbox for 1D layouts
- Container queries for component-level responsiveness where appropriate

## Mobile-First Patterns

See **[references/mobile-patterns.md](references/mobile-patterns.md)** for responsive breakpoints, touch targets, and mobile-specific UX.

**Quick Rules:**
- Design mobile FIRST, then enhance for desktop
- All grids collapse to single column below 768px
- Forms stack vertically on mobile (never side-by-side)
- Touch targets minimum 44x44px (Apple HIG) / 48x48px (Material)
- Font-size on inputs must be 16px+ to prevent iOS zoom
- Navigation becomes sheet/drawer on mobile (not horizontal scroll)
- Hero switches from grid to flex column; visual element often hidden on mobile
- Test on actual devices, not just Chrome DevTools

## Component Architecture

See **[references/component-patterns.md](references/component-patterns.md)** for shadcn/ui patterns, form handling, and state design.

**Quick Rules:**
- Use shadcn/ui as base (Button, Card, Badge, Accordion, Dialog, Tabs, Sheet, Input, Select)
- Extend variants rather than override — maintain design system consistency
- Form inputs, selects, textareas must be styled as a GROUP (never individually)
- Dropdown `<option>` elements need SOLID backgrounds (can't inherit backdrop-filter)
- Radio/checkbox need visible borders (especially transparent-border styles)
- Loading states and skeleton screens for async content
- Error states and empty states are part of the design (not afterthoughts)
- Consistent spacing scale: 4px base (4, 8, 12, 16, 24, 32, 48, 64, 96)

## Accessibility (WCAG 2.1 AA Minimum)

See **[references/accessibility-checklist.md](references/accessibility-checklist.md)** for full compliance checklist.

**Quick Rules:**
- Color contrast: 4.5:1 for normal text, 3:1 for large text/UI components
- Focus states must be VISIBLE (never remove outline without replacement)
- Semantic HTML: `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`, `<header>`
- Alt text for all images (decorative images: `alt=""`)
- Form labels associated with inputs (`<label for="id">` or `aria-labelledby`)
- Keyboard navigation works for all interactive elements
- ARIA labels for icon-only buttons
- Skip-to-content link for keyboard users

## Performance Engineering

See **[references/performance.md](references/performance.md)** for Core Web Vitals, image optimization, and bundle strategies.

**Quick Rules:**
- **LCP** (Largest Contentful Paint) < 2.5s — optimize hero image, use `fetchpriority="high"`
- **FID/INP** (Interaction to Next Paint) < 200ms — minimize JS on main thread, code-split
- **CLS** (Cumulative Layout Shift) < 0.1 — always size images with `width`/`height`, never inject content above existing content
- Images: WebP/AVIF with fallback, lazy load below-fold, `srcset` for responsive
- Fonts: `font-display: swap`, preload critical fonts, subset if possible
- CSS: Purge unused styles, critical CSS inline for above-fold
- JS: Code-split routes, defer non-critical scripts, use `IntersectionObserver` not scroll listeners
- Third-party scripts: Load async/defer, use Partytown for non-essential analytics

## SEO & Meta Essentials

Every page needs:
- `<title>` — unique, descriptive, under 60 chars, include primary keyword
- `<meta name="description">` — compelling, under 160 chars, include CTA
- `<meta name="viewport" content="width=device-width, initial-scale=1">`
- OpenGraph tags: `og:title`, `og:description`, `og:image` (1200x630), `og:type`, `og:url`
- Twitter Card tags: `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`
- Canonical URL: `<link rel="canonical" href="...">`
- Semantic heading hierarchy: ONE `<h1>` per page, logical `<h2>` → `<h3>` flow
- Structured data (JSON-LD) for: Organization, Product, FAQ, HowTo, LocalBusiness
- Favicon: SVG + PNG fallback, apple-touch-icon

## UX Writing & Microcopy

- Headlines: Benefit-driven, not feature-driven. "Write 10x faster" > "AI Writing Tool"
- CTAs: Action + outcome. "Start Free Trial" > "Submit". "Get My Report" > "Download"
- Error messages: What happened + how to fix it. Never blame the user.
- Empty states: Explain what's missing + how to add it. Include a relevant illustration.
- Loading text: Specific progress when possible. "Analyzing your data..." > "Loading..."
- Form labels: Sentence case. "Email address" not "Email Address"
- Microcopy around inputs: Contextual help, not placeholders as labels

## Build Stack (Default)

**Modern React Stack:**
- React 18 + TypeScript + Vite (static) or Next.js 14+ (SSR/SSG)
- Tailwind CSS for styling
- shadcn/ui for base components
- Framer Motion for orchestrated animations
- Lucide React for icons

**Alternative Stacks:**
- Vue 3 + Nuxt + Tailwind
- HTML/CSS/JS with Alpine.js for lightweight
- Astro for content-heavy sites

## Project Structure

```
my-site/
├── public/
│   ├── favicon.svg
│   ├── og-image.jpg
│   └── fonts/ (self-hosted if critical)
├── src/
│   ├── components/
│   │   ├── ui/          # shadcn/ui components
│   │   ├── layout/      # Header, Footer, Nav
│   │   ├── sections/    # Hero, Features, Pricing, FAQ, CTA
│   │   └── shared/      # Reusable primitives
│   ├── lib/
│   │   └── utils.ts     # cn() helper
│   ├── config/
│   │   └── site.ts      # All editable content
│   ├── styles/
│   │   └── globals.css   # CSS variables, keyframes
│   ├── hooks/
│   │   └── use-media-query.ts
│   └── types/
│       └── index.ts
├── index.html (or app/ for Next.js)
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## Site Config Pattern

Keep ALL editable content in one file:

```typescript
// config/site.ts
export const siteConfig = {
  name: "Product Name",
  tagline: "Compelling one-line benefit",
  description: "Meta description for SEO",
  url: "https://example.com",
  ogImage: "/og-image.jpg",
  
  // Optional: Brand design system reference
  // When a DESIGN.md is loaded, its tokens populate this section
  designSystem: {
    brand: "raycast",           // References design-systems/ai-devtools/raycast.md
    canvas: "#07080a",
    surface: "#0d0d0d",
    surfaceElevated: "#101111",
    primary: "#ffffff",
    accent: "#57c1ff",
    hairline: "#242728",
    typography: {
      display: "Inter",
      body: "Inter",
      mono: "JetBrains Mono",
    }
  },
  
  nav: { links: [...], cta: { label: "...", href: "..." } },
  hero: { badge: "...", title: "...", subtitle: "...", cta: {...}, stats: [...] },
  features: { title: "...", items: [...] },
  pricing: { plans: [...] },
  faq: { items: [...] },
  testimonials: { items: [...] },
  footer: { links: [...], social: [...] },
}
```

This separates content from code. Clients can edit text without touching components. When a DESIGN.md brand is loaded, the `designSystem` block is auto-populated with extracted tokens.

---

## Brand-Aware CSS Generation

When a DESIGN.md is applied, generate `globals.css` like this:

```css
@layer base {
  :root {
    /* Auto-populated from DESIGN.md tokens */
    --canvas: #07080a;
    --surface: #0d0d0d;
    --surface-elevated: #101111;
    --surface-card: #121212;
    --ink: #f4f4f6;
    --body: #cdcdcd;
    --mute: #9c9c9d;
    --hairline: #242728;
    --hairline-soft: rgba(255,255,255,0.08);
    --accent-blue: #57c1ff;
    --accent-red: #ff6161;
    --accent-green: #59d499;
    --accent-yellow: #ffc533;
    
    /* Typography */
    --font-display: "Inter", system-ui, sans-serif;
    --font-body: "Inter", system-ui, sans-serif;
    --font-mono: "JetBrains Mono", monospace;
  }
}
```

Map DESIGN.md `colors` and `typography` sections directly to CSS custom properties. Maintain the anti-AI-slop rules as guardrails even when using brand tokens.

---

## Pre-Ship Checklist

### Design Quality
- [ ] Typography is distinctive (no Inter/Roboto/Arial/system) — OR matches the loaded DESIGN.md font stack
- [ ] Color palette has clear dominant + accent (60-30-10) — OR follows the loaded DESIGN.md token hierarchy
- [ ] Background has atmosphere (not solid white/gray) — OR matches DESIGN.md canvas/surface system
- [ ] At least one unforgettable/memorable element
- [ ] Animations are orchestrated, not scattered
- [ ] Layout has intentional asymmetry or bold symmetry
- [ ] No template-y sections (generic hero + 3-col features + CTA)
- [ ] **If using a DESIGN.md**: All tokens are correctly mapped to CSS variables and component props

### Mobile
- [ ] Hero centers on mobile (not left-aligned with empty grid space)
- [ ] All grids collapse to single column below 768px
- [ ] Forms stack vertically
- [ ] Touch targets 48px minimum
- [ ] Font sizes 16px+ on inputs (prevent iOS zoom)
- [ ] Navigation uses sheet/drawer pattern
- [ ] Tested on actual mobile device or responsive mode

### Accessibility
- [ ] Color contrast meets WCAG AA (4.5:1 text, 3:1 UI)
- [ ] Focus states visible on ALL interactive elements
- [ ] Semantic HTML used correctly
- [ ] Alt text on all images
- [ ] Form labels present and associated
- [ ] Keyboard navigation works
- [ ] Skip-to-content link present
- [ ] `prefers-reduced-motion` respected

### Performance
- [ ] Images optimized (WebP/AVIF, lazy loaded, sized)
- [ ] Fonts use `font-display: swap`
- [ ] No layout shift (images have width/height)
- [ ] JS bundle reasonably sized (code-split if large)
- [ ] Core Web Vitals pass on PageSpeed Insights

### SEO
- [ ] Unique `<title>` and `<meta description>`
- [ ] OpenGraph image (1200x630) present
- [ ] Canonical URL set
- [ ] Semantic heading hierarchy (one H1)
- [ ] Structured data (JSON-LD) where relevant

### Conversion
- [ ] Primary CTA above the fold
- [ ] CTA color contrasts with surroundings
- [ ] Social proof visible (testimonials, logos, stats)
- [ ] Trust signals present (security badges, guarantees)
- [ ] Form friction minimized (only ask for essential info)
- [ ] Loading/error/empty states designed

## Output Requirements

Generate production-ready code that is:
- **Visually striking** — someone would screenshot it
- **Performance-engineered** — passes Core Web Vitals
- **Accessibility-compliant** — usable by everyone
- **Conversion-optimized** — drives the desired action
- **Mobile-perfect** — designed thumb-first
- **SEO-ready** — discoverable from day one
- **Maintainable** — clean component structure, content separated in config
- **Brand-consistent** — when a DESIGN.md is loaded, every token, spacing value, and component style aligns with the referenced brand

**Never ship prototype code.** Every output should be deployable with minimal changes.

## Remember

Claude is capable of extraordinary creative work. Don't hold back — commit to a direction, execute with precision, and ship something that feels designed, not generated.

The middle ground is where designs go to die. Pick an extreme. Push it. Make it unforgettable.

When a brand DESIGN.md is loaded, treat it as gospel — every color, font, spacing value, and shadow is intentional. The brand's design system IS the bold direction. Your job is to execute it flawlessly while maintaining the anti-AI-slop guardrails.
