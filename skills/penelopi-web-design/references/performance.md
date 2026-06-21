# Performance Engineering

## Core Web Vitals Targets

| Metric | Target | Good | Needs Improvement | Poor |
|--------|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | < 2.5s | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| **INP** (Interaction to Next Paint) | < 200ms | ≤ 200ms | ≤ 500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | < 0.1 | ≤ 0.1 | ≤ 0.25 | > 0.25 |
| **TTFB** (Time to First Byte) | < 800ms | ≤ 800ms | ≤ 1.8s | > 1.8s |
| **FCP** (First Contentful Paint) | < 1.8s | ≤ 1.8s | ≤ 3.0s | > 3.0s |

## Images

### Optimization Checklist
- [ ] Use WebP or AVIF format (with JPEG/PNG fallback)
- [ ] Lazy load images below the fold (`loading="lazy"`)
- [ ] Preload hero/LCP image (`rel="preload" as="image"`)
- [ ] Use `srcset` for responsive images
- [ ] Always specify `width` and `height` to prevent CLS
- [ ] Use `fetchpriority="high"` for LCP image

### Responsive Images
```html
<img
  src="/image-800.jpg"
  srcset="/image-400.jpg 400w, /image-800.jpg 800w, /image-1200.jpg 1200w"
  sizes="(max-width: 768px) 100vw, 50vw"
  width="800"
  height="600"
  alt="Description"
  loading="lazy"
/>
```

### Next.js Image (Optimized)
```tsx
import Image from "next/image"

<Image
  src="/hero.png"
  alt="Product demo"
  width={800}
  height={600}
  priority={true} /* For LCP image */
  quality={85}
/>
```

## Fonts

### Loading Strategy
```html
<!-- Preconnect to font provider -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Preload critical fonts -->
<link rel="preload" 
  href="/fonts/ClashDisplay-Variable.woff2" 
  as="font" 
  type="font/woff2" 
  crossorigin
/>

<!-- Load with display=swap -->
<link href="https://fonts.googleapis.com/css2?family=...&display=swap" rel="stylesheet">
```

### CSS
```css
@font-face {
  font-family: 'Satoshi';
  src: url('/fonts/Satoshi-Variable.woff2') format('woff2');
  font-weight: 300 900;
  font-display: swap; /* Prevents invisible text */
  font-style: normal;
}
```

### Font Subsetting
Only load the character ranges you need:
```css
unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
```

## JavaScript

### Code Splitting
```tsx
// Next.js — automatic route splitting
// Vite — dynamic imports
const HeavyComponent = lazy(() => import('./HeavyComponent'))

function App() {
  return (
    <Suspense fallback={<Skeleton />}>
      <HeavyComponent />
    </Suspense>
  )
}
```

### Script Loading
```html
<!-- Critical — load immediately -->
<script src="critical.js"></script>

<!-- Deferred — execute after HTML parse -->
<script src="analytics.js" defer></script>

<!-- Async — execute when ready (non-blocking) -->
<script src="widget.js" async></script>

<!-- Third-party — use Partytown for non-essential -->
<script type="text/partytown" src="google-analytics.js"></script>
```

### Bundle Analysis
```bash
# Analyze bundle size
npx vite-bundle-visualizer
# or
npx @next/bundle-analyzer
```

## CSS

### Critical CSS
Inline above-the-fold CSS in `<head>`:
```html
<head>
  <style>
    /* Critical styles only */
    body { margin: 0; font-family: ... }
    .hero { ... }
  </style>
  <link rel="preload" href="/styles.css" as="style" onload="this.rel='stylesheet'">
</head>
```

### Tailwind Optimization
```js
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './public/index.html',
  ],
  // Purges unused styles automatically in production
}
```

### Unused CSS Removal
```bash
# PurgeCSS for non-Tailwind projects
npx purgecss --css styles.css --content index.html src/**/*.js --output dist/
```

## Caching

### Static Assets
```nginx
# nginx.conf
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

### HTML (with revalidation)
```nginx
location / {
  expires 1h;
  add_header Cache-Control "public, must-revalidate";
}
```

## Server-Side Rendering (SSR)

### When to Use
- Content-heavy sites (blogs, documentation)
- SEO-critical pages
- First load performance is paramount

### Next.js SSG
```tsx
// Static generation at build time
export async function getStaticProps() {
  const data = await fetchData()
  return { props: { data } }
}
```

### Next.js SSR
```tsx
// Server-side rendering per request
export async function getServerSideProps() {
  const data = await fetchData()
  return { props: { data } }
}
```

## Common Performance Anti-Patterns

- ❌ Loading all JavaScript upfront — code-split routes
- ❌ Unoptimized images — use WebP/AVIF, lazy load
- ❌ Loading all font weights — only load needed weights
- ❌ Missing width/height on images — causes CLS
- ❌ Synchronous third-party scripts — defer/async them
- ❌ Large CSS bundles — purge unused styles
- ❌ No compression — enable gzip/brotli
- ❌ No caching headers — set appropriate cache policies
- ❌ Client-side data fetching for initial render — use SSR/SSG
- ❌ Memory leaks in React — clean up useEffect subscriptions

## Performance Testing Tools

| Tool | Purpose |
|------|---------|
| Lighthouse | Comprehensive audit |
| PageSpeed Insights | Real-world performance |
| WebPageTest | Detailed waterfall analysis |
| GTmetrix | Performance monitoring |
| Chrome DevTools → Performance | Flame charts, bottlenecks |
| Chrome DevTools → Network | Request analysis |
| `vite-bundle-visualizer` | Bundle size analysis |

## Performance Pre-Ship Checklist

- [ ] Images optimized (WebP/AVIF, lazy loaded, sized)
- [ ] Fonts use `font-display: swap`
- [ ] No layout shift (images have width/height)
- [ ] JS bundle reasonably sized (code-split if > 200KB)
- [ ] CSS purged/bundled efficiently
- [ ] Compression enabled (gzip/brotli)
- [ ] Caching headers set appropriately
- [ ] Third-party scripts loaded async/defer
- [ ] LCP image preloaded with `fetchpriority="high"`
- [ ] Lighthouse score ≥ 90 on mobile
- [ ] PageSpeed Insights passes Core Web Vitals
