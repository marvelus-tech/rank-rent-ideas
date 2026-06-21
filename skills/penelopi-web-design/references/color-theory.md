# Color Theory

## The 60-30-10 Rule

Every palette needs hierarchy. Equal distribution creates noise.

- **60% Dominant** — Background, large sections, main surfaces
- **30% Secondary** — Cards, sidebars, navigation, secondary surfaces
- **10% Accent** — CTAs, links, badges, highlights, the thing you want users to click

## Palette Generation Strategies

### 1. Monochromatic + Accent
One hue family + one contrasting accent.

```css
:root {
  --hue-primary: 220;  /* Blue family */
  --bg-primary: hsl(var(--hue-primary), 20%, 5%);
  --bg-secondary: hsl(var(--hue-primary), 20%, 12%);
  --text-primary: hsl(var(--hue-primary), 10%, 95%);
  --text-secondary: hsl(var(--hue-primary), 10%, 65%);
  --accent: hsl(25, 95%, 53%);  /* Warm orange — complementary */
  --accent-hover: hsl(25, 95%, 45%);
}
```

### 2. Analogous
Adjacent hues on the color wheel. Harmonious, natural.

```css
:root {
  --bg-primary: #0f172a;       /* Dark blue */
  --bg-secondary: #1e293b;      /* Slightly lighter blue */
  --accent: #06b6d4;            /* Cyan (adjacent to blue) */
  --accent-alt: #8b5cf6;        /* Violet (other side of blue) */
}
```

### 3. Complementary
Opposite hues on the wheel. High energy, tension.

```css
:root {
  --bg-primary: #0a0a0a;
  --text-primary: #fafafa;
  --accent: #22c55e;     /* Green */
  --accent-alt: #ef4444;  /* Red (complementary-ish in RGB) */
}
```

### 4. Split-Complementary
Base hue + two adjacent to its complement. Balanced but vibrant.

```css
:root {
  --bg-primary: #1a1a2e;
  --accent: #e94560;      /* Coral/pink */
  --accent-alt: #f4d03f;  /* Yellow-gold */
  --text: #eee;
}
```

### 5. IDE Theme Inspired
Dark backgrounds + syntax-highlighting inspired accents. Unique to developer tools.

```css
/* Tokyo Night inspired */
:root {
  --bg-primary: #1a1b26;
  --bg-secondary: #24283b;
  --text-primary: #a9b1d6;
  --text-secondary: #565f89;
  --accent: #7aa2f7;      /* Blue */
  --accent-alt: #bb9af7;  /* Purple */
  --accent-warm: #ff9e64; /* Orange */
  --accent-cool: #73daca; /* Teal */
}

/* Dracula inspired */
:root {
  --bg-primary: #282a36;
  --bg-secondary: #44475a;
  --text-primary: #f8f8f2;
  --text-secondary: #6272a4;
  --accent: #ff79c6;      /* Pink */
  --accent-alt: #bd93f9;  /* Purple */
  --accent-warm: #ffb86c; /* Orange */
  --accent-cool: #50fa7b; /* Green */
}
```

## Dark Mode Implementation

### Option 1: CSS Media Query (System Preference)
```css
:root {
  --bg-primary: #ffffff;
  --text-primary: #0a0a0a;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #0a0a0a;
    --text-primary: #fafafa;
  }
}
```

### Option 2: Class-Based Toggle
```css
:root {
  --bg-primary: #ffffff;
  --text-primary: #0a0a0a;
}

.dark {
  --bg-primary: #0a0a0a;
  --text-primary: #fafafa;
}
```
```typescript
// Toggle
const toggleDarkMode = () => {
  document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme', 
    document.documentElement.classList.contains('dark') ? 'dark' : 'light'
  );
};

// Initialize
const saved = localStorage.getItem('theme');
if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
  document.documentElement.classList.add('dark');
}
```

### Option 3: Tailwind CSS (Recommended)
```typescript
// tailwind.config.ts
export default {
  darkMode: 'class', // or 'media' for system preference
  // ...
}
```
```html
<!-- Light mode by default, .dark class toggles -->
<html class="dark">
  <body class="bg-white dark:bg-black text-black dark:text-white">
    <!-- Content -->
  </body>
</html>
```

## Contrast & Accessibility

### WCAG 2.1 AA Requirements
- **Normal text** (< 18px or < 14px bold): 4.5:1 contrast ratio minimum
- **Large text** (≥ 18px or ≥ 14px bold): 3:1 contrast ratio minimum
- **UI components**: 3:1 against adjacent colors

### Quick Contrast Check
```css
/* Bad — barely visible */
.text-muted { color: #888; } /* On white: ~3.5:1 — fails AA for small text */

/* Good — clearly readable */
.text-muted { color: #666; } /* On white: ~5.7:1 — passes AA */

/* Excellent — very readable */
.text-muted { color: #555; } /* On white: ~7.4:1 — passes AAA */
```

### Tools
- Use WebAIM Contrast Checker
- Use Stark plugin for Figma/Sketch
- Use APCA for next-gen perceptual contrast (more accurate than WCAG ratios)

## Color Function Trick

```css
/* Generate tints and shades from a base */
--accent: #ff6b35;
--accent-10: color-mix(in srgb, var(--accent) 10%, transparent);
--accent-20: color-mix(in srgb, var(--accent) 20%, transparent);
--accent-light: color-mix(in srgb, var(--accent) 80%, white);
--accent-dark: color-mix(in srgb, var(--accent) 80%, black);
```

## Gradients That Don't Suck

```css
/* Subtle, atmospheric gradient */
.atmospheric {
  background: linear-gradient(
    135deg,
    hsl(220, 30%, 8%) 0%,
    hsl(240, 30%, 12%) 50%,
    hsl(260, 30%, 10%) 100%
  );
}

/* Mesh gradient (CSS only) */
.mesh {
  background:
    radial-gradient(at 40% 20%, hsla(28, 100%, 74%, 0.15) 0px, transparent 50%),
    radial-gradient(at 80% 0%, hsla(189, 100%, 56%, 0.1) 0px, transparent 50%),
    radial-gradient(at 0% 50%, hsla(355, 100%, 93%, 0.15) 0px, transparent 50%),
    hsl(220, 20%, 8%);
}

/* Border gradient (for cards, buttons) */
.gradient-border {
  position: relative;
  background: var(--bg-secondary);
  border-radius: 12px;
}
.gradient-border::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(135deg, var(--accent), var(--accent-alt));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}
```

## Semantic Color Roles

```css
:root {
  /* Surfaces */
  --bg-primary: #0a0a0a;      /* Main background */
  --bg-secondary: #171717;     /* Cards, sections */
  --bg-tertiary: #262626;     /* Elevated elements */
  --bg-elevated: #333333;     /* Hover states, dropdowns */
  
  /* Text */
  --text-primary: #fafafa;    /* Headlines, important text */
  --text-secondary: #a3a3a3;  /* Body, descriptions */
  --text-muted: #737373;      /* Captions, metadata */
  --text-inverted: #0a0a0a;   /* Text on accent backgrounds */
  
  /* Accents */
  --accent: #22c55e;          /* Primary CTA, links */
  --accent-hover: #16a34a;    /* Hover state */
  --accent-subtle: rgba(34, 197, 94, 0.1); /* Subtle backgrounds */
  --accent-alt: #3b82f6;      /* Secondary accent, info */
  
  /* Status */
  --success: #22c55e;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #3b82f6;
  
  /* Borders */
  --border: #262626;
  --border-strong: #404040;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.3);
  --shadow-lg: 0 12px 40px rgba(0,0,0,0.4);
  --shadow-glow: 0 0 40px rgba(34, 197, 94, 0.15);
}
```

## Anti-Patterns

- ❌ Using default Tailwind colors without modification (`slate-50` through `slate-900`)
- ❌ #ffffff white and #000000 black (use off-white `#fafafa` and off-black `#0a0a0a`)
- ❌ Pure gray for text (`#808080`) — always tint toward your primary hue
- ❌ More than 3-4 hues in a palette
- ❌ Accent colors that don't contrast with their container
- ❌ No hover states defined for interactive colors
- ❌ Inaccessible color combinations (always check contrast)
