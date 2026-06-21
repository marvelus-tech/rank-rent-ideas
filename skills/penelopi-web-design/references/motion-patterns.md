# Motion & Animation Patterns

## Core Principle

One orchestrated moment creates delight. Scattered micro-interactions create fatigue.

## Performance-First Rules

### ONLY Animate These Properties
These are GPU-accelerated and don't trigger layout recalculation:
- `transform` (translate, scale, rotate)
- `opacity`
- `filter` (blur, brightness — use sparingly)

### NEVER Animate These Properties
These trigger layout thrashing and jank:
- `width`, `height`, `top`, `left`, `right`, `bottom`
- `margin`, `padding`
- `border-width`
- `font-size`

### Timing Guidelines

| Animation Type | Duration | Easing |
|---------------|----------|--------|
| Micro-interaction (button hover) | 150-200ms | `ease-out` |
| UI feedback (toast, modal) | 200-300ms | `cubic-bezier(0.4, 0, 0.2, 1)` |
| Page transitions | 300-400ms | `cubic-bezier(0.4, 0, 0.2, 1)` |
| Hero orchestration | 400-600ms | `cubic-bezier(0.16, 1, 0.3, 1)` |
| Scroll reveals | 500-700ms | `cubic-bezier(0.4, 0, 0.2, 1)` |

**Rule**: Never exceed 600ms for UI animations. If it feels sluggish, it's wrong.

## Page Load Orchestration

### The Narrative Entrance
Elements should enter in a sequence that tells a story:

```css
/* Step 1: Badge appears ( establishes credibility ) */
.hero-badge   { animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both; }

/* Step 2: Title drops in ( the promise ) */
.hero-title   { animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.25s both; }

/* Step 3: Subtitle follows ( the detail ) */
.hero-subtitle{ animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.35s both; }

/* Step 4: CTA appears ( the action ) */
.hero-cta     { animation: fadeSlideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.45s both; }

/* Step 5: Social proof ( builds trust ) */
.hero-stats   { animation: fadeSlideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.55s both; }

/* Step 6: Visual element ( the payoff ) */
.hero-visual  { animation: fadeIn 0.8s ease-out 0.3s both; }

@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(30px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
```

### React Implementation (Framer Motion)
```tsx
import { motion } from "framer-motion";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 }
  }
};

const item = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } }
};

<motion.div variants={container} initial="hidden" animate="show">
  <motion.span variants={item} className="badge">Now in beta</motion.span>
  <motion.h1 variants={item}>Your words, supercharged</motion.h1>
  <motion.p variants={item}>Write 10x faster with AI...</motion.p>
  <motion.div variants={item}>
    <button>Get Started</button>
  </motion.div>
</motion.div>
```

## Scroll-Triggered Reveals

### Intersection Observer (Native)
```javascript
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target); // Animate once
      }
    });
  },
  { threshold: 0.1, rootMargin: "0px 0px -50px 0px" }
);

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
```

```css
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease-out, transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.reveal.animate-in {
  opacity: 1;
  transform: translateY(0);
}

/* Stagger children */
.reveal-grid .reveal:nth-child(1) { transition-delay: 0s; }
.reveal-grid .reveal:nth-child(2) { transition-delay: 0.1s; }
.reveal-grid .reveal:nth-child(3) { transition-delay: 0.2s; }
.reveal-grid .reveal:nth-child(4) { transition-delay: 0.3s; }
```

### Framer Motion (whileInView)
```tsx
<motion.div
  initial={{ opacity: 0, y: 40 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: "-100px" }}
  transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
>
  {/* Content */}
</motion.div>
```

## Hover States

### Button Hover
```css
.btn {
  position: relative;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}
.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(var(--accent-rgb), 0.25);
}
.btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(var(--accent-rgb), 0.2);
}
```

### Card Hover
```css
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}
.card:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 
    0 24px 48px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(var(--accent-rgb), 0.1);
  border-color: rgba(var(--accent-rgb), 0.2);
}
```

### Link Hover (Underline Animation)
```css
.link-animated {
  position: relative;
  text-decoration: none;
}
.link-animated::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--accent);
  transition: width 0.3s ease;
}
.link-animated:hover::after {
  width: 100%;
}
```

## Reduced Motion Support

**Always** respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

```tsx
// Framer Motion
const prefersReducedMotion = 
  typeof window !== 'undefined' && 
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

<motion.div
  initial={prefersReducedMotion ? false : { opacity: 0 }}
  animate={{ opacity: 1 }}
  // ...
/>
```

## Skeleton Loading States

```tsx
function SkeletonCard() {
  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="flex items-center gap-4">
        <div className="h-12 w-12 rounded-full bg-muted animate-pulse" />
        <div className="space-y-2">
          <div className="h-4 w-24 rounded bg-muted animate-pulse" />
          <div className="h-3 w-16 rounded bg-muted animate-pulse" />
        </div>
      </div>
      <div className="mt-4 space-y-2">
        <div className="h-3 w-full rounded bg-muted animate-pulse" />
        <div className="h-3 w-4/5 rounded bg-muted animate-pulse" />
      </div>
    </div>
  );
}
```

```css
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton-shimmer {
  background: linear-gradient(
    90deg,
    var(--bg-secondary) 0%,
    var(--bg-tertiary) 50%,
    var(--bg-secondary) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

## Page Transitions

### CSS-Only Fade
```css
.page-transition-enter {
  opacity: 0;
}
.page-transition-enter-active {
  opacity: 1;
  transition: opacity 0.3s ease;
}
.page-transition-exit {
  opacity: 1;
}
.page-transition-exit-active {
  opacity: 0;
  transition: opacity 0.3s ease;
}
```

### Framer Motion Page Transition
```tsx
import { AnimatePresence, motion } from "framer-motion";

<AnimatePresence mode="wait">
  <motion.div
    key={pathname}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ duration: 0.3 }}
  >
    {children}
  </motion.div>
</AnimatePresence>
```

## Common Easing Curves

```css
:root {
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

| Name | Value | Use Case |
|------|-------|----------|
| Expo Out | `cubic-bezier(0.16, 1, 0.3, 1)` | Primary entrance, hero elements |
| Quart Out | `cubic-bezier(0.25, 1, 0.5, 1)` | Subtle entrances, cards |
| Standard | `cubic-bezier(0.4, 0, 0.2, 1)` | General UI feedback |
| Spring | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Playful bouncy effects |

## Anti-Patterns

- ❌ Animating `width`/`height`/`top`/`left` — triggers layout thrashing
- ❌ No `prefers-reduced-motion` support — inaccessible
- ❌ Animating everything on the page — creates fatigue
- ❌ Transitions longer than 400ms for UI feedback — feels sluggish
- ❌ Scroll listeners instead of Intersection Observer — terrible performance
- ❌ `requestAnimationFrame` loops for simple CSS animations — over-engineering
- ❌ Parallax effects without performance consideration — causes jank
