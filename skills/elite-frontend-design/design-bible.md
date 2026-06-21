# 🎨 THE DESIGN BIBLE — Elite Frontend Design System

> **Version:** 1.0.0  
> **Purpose:** Mandatory reference for every Codex sub-agent producing web design  
> **Standard:** Award-winning caliber (Awwards, Land-Book, MotionSites tier)  
> **Rule:** NO webpage ships without passing the Quality Checklist at the end of this document.

---

## 1. MANDATORY DESIGN PRINCIPLES

### Non-Negotiable Rules

| # | Principle | Violation Consequence |
|---|-----------|----------------------|
| 1 | **Mobile-first, never desktop-only** | Instant rejection |
| 2 | **Dark mode as default for premium/SaaS** | Looks cheap without it |
| 3 | **Maximum 2 font families per page** | Typography chaos |
| 4 | **Every element must have a purpose** | No decorative orphans |
| 5 | **60fps animations or none at all** | Janky = amateur |
| 6 | **Contrast ratio ≥ 4.5:1 for body, ≥ 3:1 for large text** | Accessibility failure |
| 7 | **Load time < 3s on 4G** | User bounce |
| 8 | **No generic stock imagery** | Instant AI-generated vibe |
| 9 | **Consistent 8px spacing scale** | Visual rhythm destruction |
| 10 | **Hero section must communicate value in 3 seconds** | Failed conversion |
| 11 | **CTAs must be visually dominant** | Lost conversions |
| 12 | **No more than 3 primary actions per viewport** | Decision paralysis |
| 13 | **Scroll depth > 60% before footer** | Engagement failure |
| 14 | **Micro-interactions on every interactive element** | Feels dead |
| 15 | **Glassmorphism only with purpose, never as decoration** | 2020 called |

### The "Anti-AI-Generated" Rules

**What makes designs look AI-generated:**
- Generic gradient backgrounds (purple-to-blue default)
- Rounded corners on everything (border-radius: 9999px abuse)
- Centered text blocks wider than 65ch
- Stock photos with perfect smiles
- Generic icon sets (Phosphor overuse without curation)
- Excessive whitespace without content hierarchy
- Default Tailwind colors without customization
- Shadow abuse (box-shadow: 0 20px 25px -5px everywhere)
- No hover states on buttons
- Missing focus rings (accessibility violation)

**What makes designs look premium:**
- Custom color palettes with semantic meaning
- Asymmetric layouts with intentional tension
- Typography as the primary visual element
- Subtle animations that guide attention
- Photography with mood, not just information
- Consistent but unexpected spacing
- Details that reward exploration

---

## 2. TYPOGRAPHY HIERARCHY

### Font Pairings (Mandatory Selection)

| Tier | Primary | Secondary | Use Case |
|------|---------|-----------|----------|
| **Premium/SaaS** | Inter | Space Grotesk | Clean, technical, trustworthy |
| **Creative/Agency** | Clash Display | Satoshi | Bold, expressive, artistic |
| **Luxury** | Cormorant Garamond | Montserrat | Elegant, high-end, editorial |
| **Modern/Fintech** | Geist | Geist Mono | Ultra-modern, precise, data |
| **Editorial** | Editorial New | Söhne | Magazine-style, long-form |

### Type Scale (Desktop / Mobile)

```css
/* Root sizing */
:root {
  --text-xs: clamp(0.64rem, 0.05vw + 0.63rem, 0.68rem);    /* 10-11px */
  --text-sm: clamp(0.8rem, 0.17vw + 0.76rem, 0.94rem);     /* 13-15px */
  --text-base: clamp(1rem, 0.34vw + 0.91rem, 1.25rem);     /* 16-20px */
  --text-lg: clamp(1.25rem, 0.61vw + 1.1rem, 1.75rem);    /* 20-28px */
  --text-xl: clamp(1.56rem, 1vw + 1.31rem, 2.5rem);       /* 25-40px */
  --text-2xl: clamp(1.95rem, 1.56vw + 1.56rem, 3.5rem);   /* 31-56px */
  --text-3xl: clamp(2.44rem, 2.38vw + 1.85rem, 5rem);      /* 39-80px */
  --text-4xl: clamp(3.05rem, 3.54vw + 2.17rem, 7rem);      /* 49-112px */
  --text-5xl: clamp(3.81rem, 5.18vw + 2.52rem, 9.5rem);    /* 61-152px */
  --text-hero: clamp(4.77rem, 7.5vw + 2.9rem, 12rem);       /* 76-192px */
}

/* Line heights */
--leading-tight: 0.9;     /* Hero, display */
--leading-snug: 1.1;      /* H1, large headings */
--leading-normal: 1.3;    /* H2, H3 */
--leading-relaxed: 1.5;   /* Body text */
--leading-loose: 1.7;     /* Long-form reading */

/* Letter spacing */
--tracking-tight: -0.03em;   /* Hero, large headings */
--tracking-normal: -0.01em;    /* H1, H2 */
--tracking-wide: 0.01em;     /* Body */
--tracking-wider: 0.05em;    /* Labels, uppercase */
--tracking-widest: 0.1em;    /* Micro labels */
```

### Heading Rules

```css
/* Hero heading — maximum impact */
.hero-heading {
  font-size: var(--text-hero);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  font-weight: 700; /* or 800 for display fonts */
  text-wrap: balance;
  max-width: 15ch; /* Force line breaks for impact */
}

/* H1 — page titles */
.h1 {
  font-size: var(--text-4xl);
  line-height: var(--leading-snug);
  letter-spacing: var(--tracking-normal);
  font-weight: 600;
  text-wrap: balance;
  max-width: 25ch;
}

/* H2 — section headers */
.h2 {
  font-size: var(--text-3xl);
  line-height: var(--leading-normal);
  letter-spacing: var(--tracking-normal);
  font-weight: 600;
  text-wrap: balance;
  max-width: 35ch;
}

/* H3 — card/feature titles */
.h3 {
  font-size: var(--text-xl);
  line-height: var(--leading-normal);
  letter-spacing: var(--tracking-wide);
  font-weight: 500;
}

/* Body — primary reading */
.body {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  letter-spacing: var(--tracking-wide);
  font-weight: 400;
  max-width: 65ch; /* Optimal reading width */
  color: var(--text-secondary);
}

/* Caption — labels, metadata */
.caption {
  font-size: var(--text-xs);
  line-height: var(--leading-relaxed);
  letter-spacing: var(--tracking-widest);
  font-weight: 500;
  text-transform: uppercase;
  color: var(--text-tertiary);
}
```

### Typography Effects (Premium)

```css
/* Gradient text — use sparingly, only for hero accents */
.gradient-text {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Outline text — for dramatic contrast */
.outline-text {
  -webkit-text-stroke: 1px var(--text-primary);
  -webkit-text-fill-color: transparent;
}

/* Kinetic text — character-level animation ready */
.kinetic-text {
  font-variation-settings: 'wght' 100;
  transition: font-variation-settings 0.3s ease;
}
.kinetic-text:hover {
  font-variation-settings: 'wght' 900;
}
```

---

## 3. COLOR SYSTEM

### Primary Palettes

#### Palette A: Midnight Premium (SaaS/Fintech)
```css
:root {
  --bg-primary: #0a0a0f;        /* Deep void black */
  --bg-secondary: #12121a;      /* Elevated surface */
  --bg-tertiary: #1a1a25;       /* Card/component bg */
  --text-primary: #fafafa;      /* Pure white */
  --text-secondary: #a1a1aa;    /* Muted silver */
  --text-tertiary: #52525b;     /* Subtle */
  --accent-primary: #6366f1;    /* Indigo glow */
  --accent-secondary: #8b5cf6;  /* Violet shift */
  --accent-tertiary: #ec4899;   /* Pink highlight */
  --border-subtle: rgba(255,255,255,0.08);
  --border-strong: rgba(255,255,255,0.15);
}
```

#### Palette B: Warm Editorial (Agency/Creative)
```css
:root {
  --bg-primary: #faf9f6;        /* Warm white */
  --bg-secondary: #f5f0e8;      /* Cream */
  --bg-tertiary: #ede8e0;       /* Card bg */
  --text-primary: #1a1a1a;      /* Soft black */
  --text-secondary: #6b6b6b;    /* Warm gray */
  --text-tertiary: #a3a3a3;     /* Light gray */
  --accent-primary: #d97706;    /* Amber */
  --accent-secondary: #b45309;  /* Dark amber */
  --accent-tertiary: #f59e0b;   /* Light amber */
  --border-subtle: rgba(0,0,0,0.06);
  --border-strong: rgba(0,0,0,0.12);
}
```

#### Palette C: Cybernetic (Web3/Tech)
```css
:root {
  --bg-primary: #050505;        /* Absolute black */
  --bg-secondary: #0a0a0a;      /* Near black */
  --bg-tertiary: #111111;       /* Component bg */
  --text-primary: #00ff88;      /* Matrix green */
  --text-secondary: #00cc6a;    /* Muted green */
  --text-tertiary: #008844;     /* Dark green */
  --accent-primary: #00ff88;    /* Neon green */
  --accent-secondary: #00ccff;  /* Cyan */
  --accent-tertiary: #ff0066;   /* Hot pink */
  --border-subtle: rgba(0,255,136,0.1);
  --border-strong: rgba(0,255,136,0.3);
}
```

### Gradient Techniques

```css
/* Hero gradient — subtle depth */
.hero-gradient {
  background: radial-gradient(
    ellipse 80% 50% at 50% -20%,
    rgba(99, 102, 241, 0.3),
    transparent
  );
}

/* Mesh gradient — organic feel */
.mesh-gradient {
  background: 
    radial-gradient(at 40% 20%, hsla(250,100%,70%,0.3) 0px, transparent 50%),
    radial-gradient(at 80% 0%, hsla(280,100%,60%,0.2) 0px, transparent 50%),
    radial-gradient(at 0% 50%, hsla(340,100%,70%,0.2) 0px, transparent 50%),
    radial-gradient(at 80% 50%, hsla(220,100%,60%,0.2) 0px, transparent 50%),
    radial-gradient(at 0% 100%, hsla(280,100%,70%,0.3) 0px, transparent 50%);
}

/* Aurora gradient — animated background ready */
.aurora-gradient {
  background: linear-gradient(
    125deg,
    #667eea 0%,
    #764ba2 25%,
    #f093fb 50%,
    #f5576c 75%,
    #4facfe 100%
  );
  background-size: 400% 400%;
}
```

---

## 4. LAYOUT PATTERNS

### Grid System

```css
/* 12-column grid with fluid gutters */
.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: clamp(1rem, 2vw, 2rem);
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 clamp(1rem, 5vw, 4rem);
}

/* Common patterns */
.grid-hero { grid-template-columns: 1fr; }           /* Mobile */
@media (min-width: 768px) {
  .grid-hero { grid-template-columns: 1fr 1fr; }   /* Split */
}

.grid-cards { 
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr));
}

.grid-asymmetric {
  grid-template-columns: 2fr 1fr;
  gap: 4rem;
}
```

### Spacing Scale

```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.5rem;    /* 24px */
  --space-6: 2rem;      /* 32px */
  --space-8: 3rem;      /* 48px */
  --space-10: 4rem;     /* 64px */
  --space-12: 6rem;     /* 96px */
  --space-16: 8rem;     /* 128px */
  --space-20: 12rem;    /* 192px */
  --space-24: 16rem;    /* 256px */
}

/* Section spacing */
.section {
  padding: var(--space-16) 0;  /* 128px vertical */
}
.section-compact {
  padding: var(--space-10) 0;  /* 64px vertical */
}
.section-hero {
  padding: var(--space-24) 0 var(--space-16);  /* 256px top, 128px bottom */
  min-height: 100vh;
}
```

### Container Widths

```css
.container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 clamp(1rem, 5vw, 4rem);
}

.container-narrow {
  max-width: 900px;
}

.container-wide {
  max-width: 1600px;
}

.container-full {
  max-width: 100%;
  padding: 0;
}
```

### Responsive Breakpoints

```css
/* Mobile-first breakpoints */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

---

## 5. ANIMATION & INTERACTION

### Animation Philosophy

- **Purposeful:** Every animation guides attention or provides feedback
- **Performant:** Use `transform` and `opacity` only. Never animate `width`, `height`, `top`, `left`, `margin`, `padding`
- **Subtle:** Animations should be noticed but not distracting
- **Consistent:** Same easing curves throughout
- **Respectful:** Honor `prefers-reduced-motion`

### Easing Curves

```css
:root {
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
  --ease-in-out-cubic: cubic-bezier(0.65, 0, 0.35, 1);
  --ease-elastic: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-dramatic: cubic-bezier(0.87, 0, 0.13, 1);
}
```

### Entrance Animations

```css
/* Fade up — most common entrance */
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Fade in scale — for cards, images */
@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Slide in from side — for asymmetric layouts */
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(60px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Character stagger — for text reveals */
@keyframes charReveal {
  from {
    opacity: 0;
    transform: translateY(100%);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Apply with */
.animate-fade-up {
  animation: fadeUp 0.8s var(--ease-out-expo) forwards;
}
.animate-fade-up-delay-1 { animation-delay: 0.1s; }
.animate-fade-up-delay-2 { animation-delay: 0.2s; }
.animate-fade-up-delay-3 { animation-delay: 0.3s; }
```

### Scroll-Triggered Animations (GSAP)

```javascript
// GSAP ScrollTrigger pattern
// Install: gsap, @gsap/react

import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

// Fade up on scroll
const fadeUpElements = document.querySelectorAll('.gsap-fade-up');
fadeUpElements.forEach((el, i) => {
  gsap.from(el, {
    y: 50,
    opacity: 0,
    duration: 0.8,
    ease: 'power3.out',
    scrollTrigger: {
      trigger: el,
      start: 'top 85%',
      toggleActions: 'play none none none',
    },
  });
});

// Parallax effect
const parallaxElements = document.querySelectorAll('.gsap-parallax');
parallaxElements.forEach((el) => {
  gsap.to(el, {
    y: -100,
    ease: 'none',
    scrollTrigger: {
      trigger: el,
      start: 'top bottom',
      end: 'bottom top',
      scrub: true,
    },
  });
});

// Staggered card reveal
const cardGrid = document.querySelector('.card-grid');
gsap.from('.card-grid > *', {
  y: 60,
  opacity: 0,
  duration: 0.6,
  stagger: 0.1,
  ease: 'power3.out',
  scrollTrigger: {
    trigger: cardGrid,
    start: 'top 80%',
  },
});
```

### Hover States

```css
/* Button hover — lift and glow */
.btn-primary {
  transition: transform 0.3s var(--ease-out-expo),
              box-shadow 0.3s var(--ease-out-expo);
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px -10px var(--accent-primary);
}

/* Card hover — subtle lift with border glow */
.card {
  transition: transform 0.4s var(--ease-out-expo),
              border-color 0.4s var(--ease-out-expo);
}
.card:hover {
  transform: translateY(-4px);
  border-color: var(--accent-primary);
}

/* Link hover — underline animation */
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
  height: 1px;
  background: var(--accent-primary);
  transition: width 0.3s var(--ease-out-expo);
}
.link-animated:hover::after {
  width: 100%;
}

/* Image hover — zoom with overlay */
.image-hover {
  overflow: hidden;
}
.image-hover img {
  transition: transform 0.6s var(--ease-out-expo);
}
.image-hover:hover img {
  transform: scale(1.05);
}
```

### Micro-Interactions

```css
/* Focus ring — visible and beautiful */
:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}

/* Active state — press feedback */
.btn:active {
  transform: scale(0.98);
}

/* Loading state — shimmer */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.loading {
  background: linear-gradient(
    90deg,
    var(--bg-tertiary) 25%,
    var(--bg-secondary) 50%,
    var(--bg-tertiary) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

/* Toggle switch — smooth */
.toggle {
  transition: background-color 0.3s var(--ease-out-expo);
}
.toggle::after {
  transition: transform 0.3s var(--ease-elastic);
}
.toggle:checked::after {
  transform: translateX(20px);
}
```

---

## 6. COMPONENT PATTERNS

### Buttons

```css
/* Primary CTA — maximum visual weight */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-6);
  background: var(--accent-primary);
  color: white;
  font-weight: 600;
  font-size: var(--text-base);
  border-radius: 12px; /* Not 9999px — intentional */
  border: none;
  cursor: pointer;
  transition: all 0.3s var(--ease-out-expo);
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px -10px var(--accent-primary);
  filter: brightness(1.1);
}

/* Secondary — outlined */
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-6);
  background: transparent;
  color: var(--text-primary);
  font-weight: 600;
  font-size: var(--text-base);
  border-radius: 12px;
  border: 1px solid var(--border-strong);
  cursor: pointer;
  transition: all 0.3s var(--ease-out-expo);
}
.btn-secondary:hover {
  background: var(--bg-tertiary);
  border-color: var(--accent-primary);
}

/* Ghost — minimal */
.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: transparent;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: var(--text-sm);
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.3s var(--ease-out-expo);
}
.btn-ghost:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}
```

### Cards

```css
/* Standard card — elevated surface */
.card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: var(--space-6);
  transition: all 0.4s var(--ease-out-expo);
}
.card:hover {
  transform: translateY(-4px);
  border-color: var(--border-strong);
  box-shadow: 0 20px 40px -15px rgba(0,0,0,0.3);
}

/* Feature card — with icon accent */
.card-feature {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: var(--space-8);
  position: relative;
  overflow: hidden;
}
.card-feature::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  opacity: 0;
  transition: opacity 0.3s ease;
}
.card-feature:hover::before {
  opacity: 1;
}

/* Glass card — for hero overlays */
.card-glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: var(--space-8);
}
```

### Navigation

```css
/* Fixed nav — transparent to solid on scroll */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  padding: var(--space-4) 0;
  transition: all 0.4s var(--ease-out-expo);
}
.nav-scrolled {
  background: rgba(10, 10, 15, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-subtle);
}

/* Nav link — subtle underline */
.nav-link {
  position: relative;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: var(--text-sm);
  transition: color 0.3s ease;
}
.nav-link:hover {
  color: var(--text-primary);
}
.nav-link::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--accent-primary);
  transition: width 0.3s var(--ease-out-expo);
}
.nav-link:hover::after {
  width: 100%;
}
```

### Forms

```css
/* Input — minimal, focused */
.input {
  width: 100%;
  padding: var(--space-4) var(--space-5);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: var(--text-base);
  transition: all 0.3s var(--ease-out-expo);
}
.input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}
.input::placeholder {
  color: var(--text-tertiary);
}

/* Label — small, uppercase */
.label {
  display: block;
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}
```

---

## 7. VISUAL EFFECTS

### Glassmorphism (Use Sparingly)

```css
.glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
}

/* Dark variant */
.glass-dark {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.05);
}
```

### Shadows (Elevation System)

```css
:root {
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  --shadow-glow: 0 0 40px -10px var(--accent-primary);
}
```

### 3D Transforms

```css
/* Perspective container */
.perspective-container {
  perspective: 1000px;
}

/* 3D card tilt */
.card-3d {
  transform-style: preserve-3d;
  transition: transform 0.5s var(--ease-out-expo);
}
.card-3d:hover {
  transform: rotateY(5deg) rotateX(5deg) translateZ(20px);
}

/* Floating element */
.float-3d {
  transform: translateZ(50px);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}
```

### Noise & Texture

```css
/* Subtle noise overlay */
.noise-overlay::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%' height='100%' filter='url(%23noise)'/%3E%3C/svg%3E");
  opacity: 0.03;
  pointer-events: none;
}

/* Gradient mesh background */
.mesh-bg {
  background: 
    radial-gradient(at 40% 20%, hsla(250,100%,70%,0.15) 0px, transparent 50%),
    radial-gradient(at 80% 0%, hsla(280,100%,60%,0.1) 0px, transparent 50%),
    radial-gradient(at 0% 50%, hsla(340,100%,70%,0.1) 0px, transparent 50%);
}
```

---

## 8. CONTENT STRATEGY

### Hero Section Structure

```
[Navigation — fixed, minimal]
↓
[Hero — 100vh, asymmetric]
  - Left: Headline (max 15ch) + Subheadline (max 25ch) + CTA
  - Right: Visual (3D element, abstract shape, or product mockup)
  - Background: Gradient or subtle animation
↓
[Social Proof — logos, stats, testimonials]
  - "Trusted by X+ companies"
  - 3-5 client logos (grayscale, hover color)
↓
[Problem/Agitation — 2-3 sentences]
  - "Most solutions are X. We do Y."
↓
[Solution — feature grid]
  - 3-6 features, icon + title + description
↓
[How It Works — 3 steps]
  - Numbered, visual, minimal text
↓
[Social Proof — testimonial cards]
  - Photo, name, role, quote, rating
↓
[CTA Section — high contrast]
  - Headline + CTA button (same as hero)
↓
[FAQ — accordion]
  - 5-7 questions, concise answers
↓
[Footer — minimal]
  - Logo, links, social, copyright
```

### Conversion Optimization

1. **One primary CTA per section** — never compete
2. **CTA buttons must contrast** — highest saturation on page
3. **Use directional cues** — arrows, gaze direction in images
4. **Urgency without fake scarcity** — "Limited spots" only if true
5. **Risk reversal** — "Free trial", "No credit card", "Cancel anytime"
6. **Visual hierarchy** — Most important element = biggest + most contrast
7. **White space around CTAs** — Isolate for attention

### Content Density Rules

- **Hero:** 20% content, 80% whitespace/negative space
- **Feature sections:** 40% content, 60% whitespace
- **Testimonials:** 50% content, 50% whitespace
- **Footer:** 60% content, 40% whitespace

---

## 9. PERFORMANCE RULES

### Animation Performance

```css
/* GPU-accelerated properties only */
.animated {
  will-change: transform, opacity;
  transform: translateZ(0); /* Force GPU layer */
}

/* Remove will-change after animation */
.animated-done {
  will-change: auto;
}
```

### Loading Strategy

```html
<!-- Critical CSS inline -->
<style>
  /* Above-fold styles only */
</style>

<!-- Async load full stylesheet -->
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">

<!-- Lazy load images -->
<img src="hero.webp" alt="" loading="eager"> <!-- Above fold -->
<img src="feature.webp" alt="" loading="lazy"> <!-- Below fold -->

<!-- Preload critical fonts -->
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
```

### Performance Budget

| Metric | Target | Maximum |
|--------|--------|---------|
| First Contentful Paint | < 1.5s | 2.5s |
| Largest Contentful Paint | < 2.5s | 4.0s |
| Time to Interactive | < 3.5s | 7.5s |
| Cumulative Layout Shift | < 0.1 | 0.25 |
| Total Page Weight | < 1MB | 3MB |
| JavaScript Bundle | < 200KB | 500KB |

### Progressive Enhancement

```javascript
// Check for reduced motion preference
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (!prefersReducedMotion) {
  // Initialize animations
  initAnimations();
}

// Check for WebGL support before loading 3D
const supportsWebGL = !!document.createElement('canvas').getContext('webgl');

if (supportsWebGL) {
  loadThreeJS();
} else {
  // Fallback to CSS animation
  loadFallbackAnimation();
}
```

---

## 10. QUALITY CHECKLIST

### Before Shipping — Mandatory Verification

#### Visual Design
- [ ] Typography uses exactly 2 font families
- [ ] Type scale follows the clamp() system
- [ ] No text wider than 65ch (body) or 25ch (headings)
- [ ] Color contrast ≥ 4.5:1 for all body text
- [ ] Accent color used consistently (not randomly)
- [ ] No generic gradients (purple-to-blue default)
- [ ] Shadows follow elevation system (not arbitrary)
- [ ] Border radius is intentional (not 9999px everywhere)
- [ ] Glassmorphism has purpose (not decoration)
- [ ] Images have alt text and are optimized (WebP)

#### Layout
- [ ] Mobile-first responsive (test at 320px, 768px, 1440px)
- [ ] Grid system used consistently
- [ ] Spacing follows 8px scale
- [ ] Container max-width respected
- [ ] No horizontal scroll at any breakpoint
- [ ] Touch targets ≥ 44px on mobile

#### Animation
- [ ] Animations are 60fps (transform/opacity only)
- [ ] Reduced motion preference respected
- [ ] No animation on page load > 1s total
- [ ] Scroll animations use Intersection Observer or GSAP
- [ ] Hover states on ALL interactive elements
- [ ] Loading states for async actions
- [ ] No layout shift during animation

#### Interaction
- [ ] Focus rings visible and styled
- [ ] Tab navigation works logically
- [ ] Form validation with clear error messages
- [ ] Buttons have active/pressed states
- [ ] Links have hover/focus states
- [ ] No broken links or 404s

#### Performance
- [ ] Page weight < 1MB
- [ ] Images lazy-loaded below fold
- [ ] Fonts preloaded if critical
- [ ] No render-blocking resources
- [ ] Core Web Vitals passing

#### Content
- [ ] Hero communicates value in 3 seconds
- [ ] One clear CTA per section
- [ ] No placeholder text (lorem ipsum)
- [ ] No generic stock photos
- [ ] Testimonials have real names and photos
- [ ] FAQ answers are concise and helpful

#### Anti-Patterns Check
- [ ] No "Welcome to our website" text
- [ ] No "Click here" link text
- [ ] No centered text blocks > 65ch
- [ ] No more than 3 font sizes in a section
- [ ] No decorative elements without purpose
- [ ] No auto-playing audio/video
- [ ] No popups on load (exit intent only)

---

## APPENDIX A: Common Patterns

### Hero Patterns

```html
<!-- Split Hero -->
<section class="hero grid">
  <div class="hero-content">
    <span class="caption">New: AI-Powered</span>
    <h1 class="hero-heading">Build faster with intelligence</h1>
    <p class="body">The only platform that combines design, code, and AI in one seamless workflow.</p>
    <div class="hero-ctas">
      <button class="btn-primary">Start Free Trial</button>
      <button class="btn-secondary">Watch Demo</button>
    </div>
  </div>
  <div class="hero-visual">
    <!-- 3D element, abstract shape, or product mockup -->
  </div>
</section>

<!-- Centered Hero (for minimal brands) -->
<section class="hero hero-centered">
  <h1 class="hero-heading">Less is more</h1>
  <p class="body">We build websites that communicate without noise.</p>
  <button class="btn-primary">View Our Work</button>
</section>
```

### Feature Grid

```html
<section class="section">
  <div class="container">
    <h2 class="h2">Everything you need</h2>
    <div class="grid grid-cards">
      <div class="card-feature">
        <div class="feature-icon">⚡</div>
        <h3 class="h3">Lightning Fast</h3>
        <p class="body">Optimized for 60fps and sub-second load times.</p>
      </div>
      <!-- Repeat -->
    </div>
  </div>
</section>
```

### Testimonial Card

```html
<div class="card testimonial">
  <div class="testimonial-stars">★★★★★</div>
  <p class="testimonial-quote">"The best investment we've made for our online presence."</p>
  <div class="testimonial-author">
    <img src="avatar.webp" alt="" class="testimonial-avatar">
    <div>
      <p class="testimonial-name">Sarah Chen</p>
      <p class="testimonial-role">CEO, TechFlow</p>
    </div>
  </div>
</div>
```

---

## APPENDIX B: Tech Stack Recommendations

### Recommended Libraries

| Purpose | Library | Why |
|---------|---------|-----|
| Animation | GSAP + ScrollTrigger | Industry standard, performant |
| 3D | Three.js | WebGL, widely supported |
| Icons | Lucide | Clean, consistent, tree-shakeable |
| Fonts | Fontsource | Self-hosted, no Google Fonts dependency |
| CSS | Tailwind CSS | Utility-first, rapid development |
| Framework | Next.js | SSG, performance, SEO |

### CDN Links (for quick prototypes)

```html
<!-- GSAP -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>

<!-- Three.js -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<!-- Lucide Icons -->
<script src="https://unpkg.com/lucide@latest"></script>
```

---

## APPENDIX C: Quick Reference

### Spacing Quick Reference

| Token | Value | Use Case |
|-------|-------|----------|
| space-1 | 4px | Tight gaps, icon padding |
| space-2 | 8px | Inline elements, small gaps |
| space-4 | 16px | Component padding |
| space-6 | 24px | Card padding |
| space-8 | 32px | Section internal spacing |
| space-10 | 48px | Section padding |
| space-16 | 128px | Major section separation |

### Color Quick Reference

| Role | Light Mode | Dark Mode |
|------|-----------|-----------|
| Background | #fafafa | #0a0a0f |
| Surface | #ffffff | #12121a |
| Text Primary | #1a1a1a | #fafafa |
| Text Secondary | #6b6b6b | #a1a1aa |
| Border | rgba(0,0,0,0.08) | rgba(255,255,255,0.08) |

---

> **Remember:** This document is a living standard. Every webpage we produce must meet or exceed these specifications. When in doubt, reference the award-winning sites on MotionSites, Land-Book, and Awwwards for inspiration. Never ship mediocre work.

*Last updated: 2026-06-10*
