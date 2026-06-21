# Typography System

## Core Principle

Typography is 80% of design. Get it right, and everything else follows.

## Banned Fonts (Never Use)

These are the #1 signal of AI-generated, uninspired design:

- Inter
- Roboto
- Arial
- Helvetica
- Open Sans
- Segoe UI
- system-ui (as primary)
- sans-serif (as sole font-family)

## Recommended Font Library

### Display / Headline Fonts

| Font | Character | Best For |
|------|-----------|----------|
| **Clash Display** | Geometric, bold, modern | Tech, SaaS, modern brands |
| **Cabinet Grotesk** | Warm geometric, friendly | Consumer apps, creative tools |
| **Satoshi** | Clean geometric, versatile | General purpose, clean aesthetics |
| **Playfair Display** | High-contrast serif | Editorial, luxury, fashion, publishing |
| **Cormorant Garamond** | Elegant serif, dramatic | Luxury, art, high-end services |
| **Space Grotesk** | Quirky geometric | Creative agencies, portfolios (use sparingly) |
| **Outfit** | Rounded geometric | Friendly, approachable, consumer |
| **Bebas Neue** | Condensed, impactful | Statements, headlines, posters |

### Body / Text Fonts

| Font | Character | Best For |
|------|-----------|----------|
| **Plus Jakarta Sans** | Friendly, modern, readable | General purpose, warm |
| **General Sans** | Neutral geometric, clean | Professional, corporate |
| **Instrument Sans** | Refined, slightly technical | Product, developer tools |
| **Source Sans 3** | Highly readable, neutral | Long-form content, documentation |
| **Literata** | Book-ish serif, comfortable | Editorial, publishing, blogs |
| **Manrope** | Geometric, slightly wide | Modern, friendly, headlines + body |

### Monospace / Code Fonts

| Font | Character | Best For |
|------|-----------|----------|
| **JetBrains Mono** | Clear, distinctive | Developer tools, code blocks |
| **DM Mono** | Warm, slightly wide | Technical but approachable |
| **IBM Plex Mono** | Neutral, highly legible | Documentation, data-heavy UIs |
| **Geist Mono** | Modern, sharp | Next.js/Vercel ecosystem |

## Pairing Strategies

### Strategy 1: Contrast (Editorial)
- **Display**: Playfair Display (serif)
- **Body**: Plus Jakarta Sans (sans)
- **Effect**: Classic-meets-modern, magazine quality

### Strategy 2: Harmony (Modern)
- **Display**: Satoshi (geometric)
- **Body**: General Sans (geometric)
- **Effect**: Ultra-clean, consistent, Swiss-inspired

### Strategy 3: Tension (Edgy)
- **Display**: Clash Display (bold geometric)
- **Body**: Source Sans 3 (humanist)
- **Effect**: Bold but readable, confident

### Strategy 4: Luxury (Premium)
- **Display**: Cormorant Garamond (elegant serif)
- **Body**: Instrument Sans (refined sans)
- **Effect**: High-end, refined, sophisticated

### Strategy 5: Technical (Developer)
- **Display**: JetBrains Mono (monospace)
- **Body**: IBM Plex Sans (neutral sans)
- **Effect**: Terminal aesthetic, developer-focused

## Type Scale

Use a modular scale. Minimum 3x jump between levels.

```css
/* Base scale (1rem = 16px) */
.display  { font-size: clamp(3rem, 8vw, 6rem);    line-height: 1;    letter-spacing: -0.02em; }
.h1       { font-size: clamp(2.5rem, 5vw, 4rem);   line-height: 1.1;  letter-spacing: -0.01em; }
.h2       { font-size: clamp(1.5rem, 3vw, 2.5rem); line-height: 1.2;  letter-spacing: -0.01em; }
.h3       { font-size: clamp(1.25rem, 2vw, 1.5rem);line-height: 1.3;  letter-spacing: 0; }
.body-lg  { font-size: 1.125rem;                     line-height: 1.6; }
.body     { font-size: 1rem;                         line-height: 1.6; }
.small    { font-size: 0.875rem;                     line-height: 1.5; }
.caption  { font-size: 0.75rem;                      line-height: 1.5; letter-spacing: 0.02em; }
```

## Weight Contrast

Don't be timid. Use weight to create drama.

```css
/* Strong contrast */
.hero-title   { font-weight: 700; }  /* Bold */
.hero-subtitle{ font-weight: 300; }  /* Light */

/* Or */
.display      { font-weight: 900; }  /* Black */
.body         { font-weight: 400; }  /* Regular */
```

## Loading Fonts

### Google Fonts (Simple)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Clash+Display:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Self-Hosted (Performance)
```css
@font-face {
  font-family: 'Satoshi';
  src: url('/fonts/Satoshi-Variable.woff2') format('woff2');
  font-weight: 300 900;
  font-display: swap;
  font-style: normal;
}
```

**Always use `font-display: swap`** to prevent invisible text during load.

**Preload critical fonts:**
```html
<link rel="preload" href="/fonts/ClashDisplay-Variable.woff2" as="font" type="font/woff2" crossorigin>
```

## CSS Font Variables

```css
:root {
  --font-display: 'Clash Display', 'Arial Black', sans-serif;
  --font-body: 'Plus Jakarta Sans', 'Helvetica Neue', sans-serif;
  --font-mono: 'JetBrains Mono', 'Courier New', monospace;
}
```

## Responsive Typography

```css
/* Desktop */
.hero-title { font-size: 64px; }
.section-title { font-size: 40px; }

/* Tablet */
@media (max-width: 1024px) {
  .hero-title { font-size: 48px; }
  .section-title { font-size: 32px; }
}

/* Mobile */
@media (max-width: 768px) {
  .hero-title { font-size: 36px; }
  .section-title { font-size: 24px; }
  body { font-size: 16px; } /* Never below 16px for readability */
}
```

## Tailwind Config

```typescript
// tailwind.config.ts
fontFamily: {
  display: ['var(--font-display)', 'Arial Black', 'sans-serif'],
  body: ['var(--font-body)', 'Helvetica Neue', 'sans-serif'],
  mono: ['var(--font-mono)', 'Courier New', 'monospace'],
}
```

## Anti-Patterns

- ❌ Using one font for everything
- ❌ Body font below 16px on mobile
- ❌ Line-height below 1.4 for body text
- ❌ Letter-spacing negative on body text
- ❌ Font weights 400-500 only (no contrast)
- ❌ Loading ALL weights of a font (load only what you use: 300, 400, 600, 700)
- ❌ Using `@import` for Google Fonts (blocks rendering — use `<link>` instead)
