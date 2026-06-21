# Layout & Spatial Composition Patterns

## Core Principle

Layout is about creating visual tension and hierarchy. Predictable layouts are forgettable layouts.

## Grid Systems

### CSS Grid for 2D Layouts
```css
/* Hero with asymmetric grid */
.hero-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 64px;
  align-items: center;
  min-height: 80vh;
}

@media (max-width: 768px) {
  .hero-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}

/* Bento grid */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 200px;
  gap: 16px;
}
.bento-item-large {
  grid-column: span 2;
  grid-row: span 2;
}
.bento-item-wide {
  grid-column: span 2;
}

/* Asymmetric feature grid */
.features-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 24px;
}
.features-grid .feature-main {
  grid-row: span 2;
}
```

### Flexbox for 1D Layouts
```css
/* Horizontal scroll (mobile only) */
.card-scroll {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none; /* Firefox */
}
.card-scroll::-webkit-scrollbar { display: none; }
.card-scroll > * {
  flex-shrink: 0;
  scroll-snap-align: start;
}
```

## Asymmetric Compositions

### Overlapping Elements
```css
.section-overlap {
  position: relative;
}
.section-overlap .image {
  position: absolute;
  right: -5%;
  top: -10%;
  width: 45%;
  z-index: 1;
}
.section-overlap .content {
  position: relative;
  z-index: 2;
  width: 60%;
}
```

### Diagonal Flow
```css
.diagonal-section {
  position: relative;
  clip-path: polygon(0 0, 100% 5%, 100% 100%, 0 95%);
  padding: 120px 0;
}
```

### Off-Center Hero
```css
.hero-off-center {
  display: grid;
  grid-template-columns: 1fr 1fr;
}
.hero-off-center .text {
  padding-right: 80px;
  align-self: center;
}
.hero-off-center .visual {
  position: relative;
  right: -10vw; /* Bleeds off-screen */
  width: 55vw;
}
```

## Section Patterns

### Split Section (Alternating)
```css
.split-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
  padding: 120px 0;
}
.split-section:nth-child(even) {
  direction: rtl; /* Flips order */
}
.split-section:nth-child(even) > * {
  direction: ltr; /* Content stays LTR */
}
```

### Full-Bleed Hero
```css
.hero-full-bleed {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.hero-full-bleed::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url('/hero-bg.jpg') center/cover;
  filter: brightness(0.4);
}
.hero-full-bleed .content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 800px;
}
```

### Sticky Sidebar
```css
.sticky-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 64px;
}
.sticky-layout .sidebar {
  position: sticky;
  top: 24px;
  align-self: start;
  height: fit-content;
}
```

## Spacing Scale

Use a consistent spacing scale. Never use arbitrary values.

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;
  --space-9: 96px;
  --space-10: 128px;
  --space-11: 192px;
}
```

**Tailwind equivalent:** 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48 (in rem: 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 12)

## Container Patterns

```css
/* Max-width container with padding */
.container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
}
@media (max-width: 768px) {
  .container { padding: 0 16px; }
}

/* Full-width sections with contained content */
.section-full {
  width: 100%;
}
.section-full .section-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 96px 24px;
}
```

## Z-Index Hierarchy

```css
:root {
  --z-base: 0;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-drawer: 300;
  --z-modal: 400;
  --z-popover: 500;
  --z-toast: 600;
  --z-tooltip: 700;
}
```

## Negative Space

Generous negative space signals confidence. Crowded layouts signal anxiety.

```css
/* Section spacing */
.section {
  padding: 96px 0; /* Desktop */
}
@media (max-width: 768px) {
  .section {
    padding: 48px 0; /* Mobile */
  }
}

/* Between major elements */
.hero-title { margin-bottom: 24px; }
.hero-subtitle { margin-bottom: 32px; }
.hero-cta { margin-bottom: 64px; }
```

## Common Layout Anti-Patterns

- ❌ Everything centered — creates static, boring composition
- ❌ Equal column widths everywhere — no hierarchy
- ❌ No whitespace between sections — feels cramped
- ❌ Content touching viewport edges — always use padding
- ❌ Inconsistent vertical rhythm — stick to a scale
- ❌ Fixed widths on mobile — always fluid below 768px
- ❌ Horizontal scroll on mobile — unacceptable
