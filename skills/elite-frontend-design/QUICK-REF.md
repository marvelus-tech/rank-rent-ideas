## 🎨 DESIGN BIBLE QUICK REFERENCE

> **For:** Every Codex web design task  
> **Standard:** Award-winning (Awwwards / Land-Book / MotionSites tier)  
> **File:** `~/.openclaw/workspace/skills/elite-frontend-design/design-bible.md`

---

### MANDATORY PREFACE FOR EVERY TASK

When spawning Codex for web design, ALWAYS include:

```
## Design Standards (MANDATORY)

Before writing any code, read:
~/.openclaw/workspace/skills/elite-frontend-design/design-bible.md

You MUST follow all specifications in the Design Bible.
Failure = instant rejection. No exceptions.
```

---

### THE 15 NON-NEGOTIABLES

| # | Rule | Violation |
|---|------|-----------|
| 1 | Mobile-first, never desktop-only | Instant rejection |
| 2 | Dark mode default for premium/SaaS | Looks cheap without |
| 3 | Max 2 font families per page | Typography chaos |
| 4 | Every element has a purpose | No decorative orphans |
| 5 | 60fps animations or none | Janky = amateur |
| 6 | Contrast ≥ 4.5:1 body, ≥ 3:1 large | Accessibility fail |
| 7 | Load time < 3s on 4G | User bounce |
| 8 | No generic stock imagery | AI-generated vibe |
| 9 | Consistent 8px spacing scale | Visual rhythm destroyed |
| 10 | Hero value in 3 seconds | Failed conversion |
| 11 | CTAs visually dominant | Lost conversions |
| 12 | Max 3 primary actions per viewport | Decision paralysis |
| 13 | Scroll depth > 60% before footer | Engagement fail |
| 14 | Micro-interactions on everything | Feels dead |
| 15 | Glassmorphism only with purpose | 2020 called |

---

### ANTI-AI-GENERATED CHECKLIST

**NEVER do these (instant cheap look):**
- ❌ Generic purple-to-blue gradients
- ❌ border-radius: 9999px on everything
- ❌ Centered text > 65ch wide
- ❌ Stock photos with perfect smiles
- ❌ Default Tailwind colors unmodified
- ❌ Shadow abuse (arbitrary values)
- ❌ No hover states
- ❌ Missing focus rings
- ❌ "Welcome to our website" text
- ❌ "Click here" link text

---

### TYPOGRAPHY AT A GLANCE

```css
/* Hero: 76-192px, tight leading, -0.03em tracking */
/* H1: 49-112px, snug leading, -0.01em tracking */
/* H2: 39-80px, normal leading, -0.01em tracking */
/* H3: 20-28px, normal leading, 0.01em tracking */
/* Body: 16-20px, relaxed leading, 0.01em tracking, max 65ch */
/* Caption: 10-11px, wide tracking, 0.1em, uppercase */
```

**Font Pairings:**
- Premium/SaaS: Inter + Space Grotesk
- Creative/Agency: Clash Display + Satoshi
- Luxury: Cormorant Garamond + Montserrat
- Fintech: Geist + Geist Mono

---

### COLOR PALETTES (Pick One)

**Midnight Premium (SaaS/Fintech):**
```css
--bg-primary: #0a0a0f; --bg-secondary: #12121a; --bg-tertiary: #1a1a25;
--text-primary: #fafafa; --text-secondary: #a1a1aa; --text-tertiary: #52525b;
--accent-primary: #6366f1; --accent-secondary: #8b5cf6; --accent-tertiary: #ec4899;
```

**Warm Editorial (Agency/Creative):**
```css
--bg-primary: #faf9f6; --bg-secondary: #f5f0e8; --bg-tertiary: #ede8e0;
--text-primary: #1a1a1a; --text-secondary: #6b6b6b; --text-tertiary: #a3a3a3;
--accent-primary: #d97706; --accent-secondary: #b45309; --accent-tertiary: #f59e0b;
```

**Cybernetic (Web3/Tech):**
```css
--bg-primary: #050505; --bg-secondary: #0a0a0a; --bg-tertiary: #111111;
--text-primary: #00ff88; --text-secondary: #00cc6a; --text-tertiary: #008844;
--accent-primary: #00ff88; --accent-secondary: #00ccff; --accent-tertiary: #ff0066;
```

---

### SPACING SCALE

```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-4: 1rem;     /* 16px */
--space-6: 2rem;     /* 32px */
--space-8: 3rem;     /* 48px */
--space-10: 4rem;    /* 64px */
--space-16: 8rem;    /* 128px */
--space-24: 16rem;   /* 256px */
```

**Section padding:** 128px vertical (space-16)  
**Hero padding:** 256px top, 128px bottom (space-24, space-16)  
**Card padding:** 24px (space-6)  
**Component gap:** 16px (space-4)

---

### ANIMATION ESSENTIALS

**Easing Curves:**
```css
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);      /* Primary */
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);     /* Secondary */
--ease-elastic: cubic-bezier(0.68, -0.55, 0.265, 1.55); /* Playful */
```

**Performance Rules:**
- ✅ Animate ONLY: transform, opacity
- ❌ NEVER animate: width, height, top, left, margin, padding
- ✅ Use will-change sparingly, remove after
- ✅ Respect prefers-reduced-motion

**GSAP ScrollTrigger Pattern:**
```javascript
gsap.from(el, {
  y: 50, opacity: 0, duration: 0.8,
  ease: 'power3.out',
  scrollTrigger: { trigger: el, start: 'top 85%' }
});
```

---

### COMPONENT SNIPPETS

**Primary Button:**
```css
.btn-primary {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 16px 24px; background: var(--accent-primary);
  color: white; font-weight: 600; border-radius: 12px;
  transition: all 0.3s var(--ease-out-expo);
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px -10px var(--accent-primary);
}
```

**Card:**
```css
.card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: 16px; padding: 24px;
  transition: all 0.4s var(--ease-out-expo);
}
.card:hover {
  transform: translateY(-4px);
  border-color: var(--accent-primary);
}
```

**Glass Card:**
```css
.card-glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px; padding: 48px;
}
```

---

### QUALITY CHECKLIST (Before Shipping)

**Visual:**
- [ ] 2 font families max
- [ ] clamp() type scale
- [ ] No text > 65ch (body) or 25ch (headings)
- [ ] Contrast ≥ 4.5:1
- [ ] No generic gradients
- [ ] Shadows follow elevation system
- [ ] Border radius intentional
- [ ] Images optimized (WebP) with alt text

**Layout:**
- [ ] Mobile-first (320px, 768px, 1440px)
- [ ] 8px spacing scale
- [ ] No horizontal scroll
- [ ] Touch targets ≥ 44px

**Animation:**
- [ ] 60fps (transform/opacity only)
- [ ] Reduced motion respected
- [ ] Hover states on ALL interactives
- [ ] Loading states for async

**Interaction:**
- [ ] Focus rings visible
- [ ] Tab navigation logical
- [ ] Form validation clear
- [ ] No broken links

**Content:**
- [ ] Hero value in 3 seconds
- [ ] One clear CTA per section
- [ ] No placeholder text
- [ ] No generic stock photos
- [ ] No "Click here" / "Welcome"

**Performance:**
- [ ] Page weight < 1MB
- [ ] Images lazy-loaded below fold
- [ ] Fonts preloaded if critical
- [ ] Core Web Vitals passing

---

### QUICK SPAWNING TEMPLATE

```
sessions_spawn({
  model: "Codex",
  task: `
## Design Standards (MANDATORY)
Before writing any code, read:
~/.openclaw/workspace/skills/elite-frontend-design/design-bible.md

## Task
[Your specific task here]

## Requirements
- Follow ALL Design Bible specifications
- Use [Palette A/B/C] color system
- Implement GSAP scroll animations
- Verify Quality Checklist before completion
- Include screenshots of final result
`,
  taskName: "web-design-task"
})
```

---

*Last updated: 2026-06-10*  
*Full specifications: `~/.openclaw/workspace/skills/elite-frontend-design/design-bible.md`*