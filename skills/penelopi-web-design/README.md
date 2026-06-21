# Penelopi Web Design — Supreme Frontend Skill

## Created: 2026-05-29

### What This Is

A custom OpenClaw skill that synthesizes the best aspects of three researched frontend design skills (`frontend-design-ultimate`, `frontend-design-3`, `elite-frontend-design`) and adds critical missing dimensions. This is now the canonical skill for all web-based work in this workspace.

### Where It Lives

```
~/.openclaw/workspace/skills/penelopi-web-design/
├── SKILL.md                                    (main trigger — 16KB)
├── references/
│   ├── design-philosophy.md                     (anti-AI-slop manifesto)
│   ├── typography-system.md                     (font library + pairings)
│   ├── color-theory.md                          (palette strategies + dark mode)
│   ├── motion-patterns.md                       (orchestrated animation + performance)
│   ├── layout-patterns.md                       (grid, flex, asymmetry)
│   ├── mobile-patterns.md                       (thumb-first responsive)
│   ├── component-patterns.md                    (shadcn/ui + form patterns)
│   ├── accessibility-checklist.md               (WCAG 2.1 AA compliance)
│   └── performance.md                           (Core Web Vitals + optimization)
└── templates/
    └── site-config.ts                           (production-ready content config)
```

### What Makes It Superior

| Dimension | Original Skills | Penelopi Web Design |
|-----------|----------------|---------------------|
| **Anti-AI-slop** | ✓ (good) | ✓✓ (deeper + specific fixes) |
| **Typography** | ✓ (recommendations) | ✓✓ (full pairing matrix + loading strategy) |
| **Color** | ✓ (palettes) | ✓✓ (emotional palettes + IDE themes + dark mode) |
| **Motion** | ✓ (orchestration) | ✓✓ (performance-safe + reduced-motion) |
| **Mobile** | ✓ (patterns) | ✓✓ (real-world fixes + iOS-specific) |
| **Components** | ✓ (shadcn/ui) | ✓✓ (forms + validation + loading/error/empty states) |
| **Accessibility** | ✗ (implied) | ✓✓ (full WCAG AA checklist + ARIA patterns) |
| **Performance** | ✗ (missing) | ✓✓ (Core Web Vitals + image/font/JS optimization) |
| **SEO** | ✗ (missing) | ✓✓ (meta tags + OpenGraph + structured data) |
| **UX Writing** | ✗ (missing) | ✓✓ (microcopy + CTA optimization) |
| **Conversion** | ✗ (missing) | ✓✓ (funnel design + trust signals) |
| **Build workflow** | ✓ (Vite/Next.js) | ✓ (stack specified, content-config pattern) |

### Key Differentiators

1. **Design Thinking Framework** — Forces BOLD aesthetic direction before any code is written. 11 tone categories from Brutalist to Cyberpunk.

2. **Anti-Pattern Detection Scan** — Explicit checklist to catch and fix AI-slop before shipping (Inter font, purple gradients, centered layouts, etc.)

3. **Production-Ready Patterns** — Not just "make it look good" but:
   - Skeleton loading states
   - Form validation UX
   - Error/empty states
   - Focus trap in modals
   - Live ARIA regions

4. **Performance Engineering** — Core Web Vitals targets, image optimization, font loading strategy, code splitting, CSS purging.

5. **Conversion Optimization** — CTA hierarchy, social proof placement, trust signals, form friction minimization.

6. **Site Config Pattern** — All editable content in one TypeScript file. Clients edit text without touching components.

### How Subagents Use It

The skill auto-triggers on any web design task (keywords: website, landing page, web app, frontend, UI, design, page, site, component). When a subagent is spawned for coding/design work, OpenClaw loads this skill automatically from `~/.openclaw/workspace/skills/`.

### Next Steps

- [ ] Test with a real build: generate a Marvelus.cc or Nolostsales.cc landing page
- [ ] Verify skill loads correctly in a spawned subagent
- [ ] Iterate based on real-world output quality
