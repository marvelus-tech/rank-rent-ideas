# Accessibility Checklist (WCAG 2.1 AA)

## Semantic HTML

### Required Elements
```html
<!-- Page structure -->
<body>
  <a href="#main" class="skip-link">Skip to content</a>
  
  <header>
    <nav aria-label="Main navigation">
      <!-- Navigation -->
    </nav>
  </header>
  
  <main id="main">
    <section aria-labelledby="features-heading">
      <h2 id="features-heading">Features</h2>
      <!-- Content -->
    </section>
  </main>
  
  <footer>
    <!-- Footer content -->
  </footer>
</body>
```

### Heading Hierarchy
- ONE `<h1>` per page
- Logical progression: `<h1>` → `<h2>` → `<h3>` → `<h4>`
- Never skip levels (don't go `<h2>` → `<h4>`)
- Headings should describe the section that follows

### Landmarks
```html
<header>      <!-- banner -->
<nav>         <!-- navigation -->
<main>        <!-- main -->
<aside>       <!-- complementary -->
<section>     <!-- region (with aria-label or aria-labelledby) -->
<article>     <!-- article -->
<footer>      <!-- contentinfo -->
```

## Color Contrast

### WCAG AA Requirements
| Element | Ratio | Example |
|---------|-------|---------|
| Normal text (< 18px) | 4.5:1 | `#555` on `#fff` = 7.4:1 ✓ |
| Large text (≥ 18px or ≥ 14px bold) | 3:1 | `#888` on `#fff` = 3.5:1 ✗ |
| UI components (buttons, form fields) | 3:1 | Border, focus indicators |
| Graphical objects | 3:1 | Icons, charts |

### Testing
```bash
# Chrome DevTools → Elements → Accessibility → Contrast ratio
# Or use online tools:
# - WebAIM Contrast Checker
# - Stark plugin (Figma/Sketch)
# - axe DevTools extension
```

## Focus Management

### Visible Focus States
```css
/* NEVER do this */
:focus { outline: none; } /* ❌ Removes focus indicator */

/* DO this instead */
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

/* Or custom focus ring */
.interactive:focus-visible {
  box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px var(--accent);
}
```

### Focus Trap in Modals
```tsx
function Modal({ isOpen, onClose, children }) {
  const modalRef = useRef(null)
  
  useEffect(() => {
    if (!isOpen) return
    
    const modal = modalRef.current
    const focusable = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    
    first?.focus()
    
    const handleKeyDown = (e) => {
      if (e.key !== 'Tab') return
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }
    
    modal.addEventListener('keydown', handleKeyDown)
    return () => modal.removeEventListener('keydown', handleKeyDown)
  }, [isOpen])
  
  return (
    <div ref={modalRef} role="dialog" aria-modal="true">
      {children}
    </div>
  )
}
```

## Screen Reader Support

### Alt Text
```html
<!-- Descriptive for informative images -->
<img src="dashboard.png" alt="Dashboard showing analytics with 50% growth in users" />

<!-- Empty for decorative images -->
<img src="decorative-wave.svg" alt="" />

<!-- Descriptive for functional images -->
<button>
  <img src="search.svg" alt="Search products" />
</button>
```

### ARIA Labels
```tsx
<!-- Icon-only buttons MUST have aria-label -->
<Button size="icon" aria-label="Close dialog">
  <X className="h-4 w-4" />
</Button>

<!-- Complex UI elements -->
<nav aria-label="Breadcrumb">
  <ol>...</ol>
</nav>

<!-- Live regions for dynamic content -->
<div aria-live="polite" aria-atomic="true">
  {notification}
</div>
```

### Form Labels
```tsx
<!-- Always associated -->
<Label htmlFor="email">Email address</Label>
<Input id="email" type="email" />

<!-- Or aria-labelledby -->
<Input aria-labelledby="email-label" />
<span id="email-label">Email address</span>

<!-- Or aria-label (fallback only) -->
<Input aria-label="Email address" />
```

## Keyboard Navigation

### Interactive Elements
All of these MUST be keyboard accessible:
- Buttons (`<button>` or `role="button"` + tabindex)
- Links (`<a href="...">`)
- Form controls (`<input>`, `<select>`, `<textarea>`)
- Custom components (need tabindex, key handlers)

### Custom Components
```tsx
function CustomButton({ onClick, children }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onClick()
    }
  }
  
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      className="..."
    >
      {children}
    </div>
  )
}
```

### Tab Order
- Natural DOM order is usually correct
- `tabindex="0"` for custom interactive elements
- `tabindex="-1"` for programmatic focus (not in tab order)
- NEVER use positive tabindex values (creates confusion)

## Motion & Animation

### Reduced Motion
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
const prefersReducedMotion = 
  typeof window !== 'undefined' && 
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Framer Motion
<motion.div
  initial={prefersReducedMotion ? false : { opacity: 0 }}
  animate={{ opacity: 1 }}
/>
```

## ARIA Patterns

### Accordion
```html
<div class="accordion">
  <h3>
    <button 
      aria-expanded="false" 
      aria-controls="section1"
      id="accordion1"
    >
      Section 1
    </button>
  </h3>
  <div 
    id="section1" 
    role="region" 
    aria-labelledby="accordion1"
    hidden
  >
    Content...
  </div>
</div>
```

### Tabs
```html
<div class="tabs">
  <div role="tablist" aria-label="Feature categories">
    <button role="tab" aria-selected="true" aria-controls="panel1" id="tab1">Tab 1</button>
    <button role="tab" aria-selected="false" aria-controls="panel2" id="tab2">Tab 2</button>
  </div>
  <div role="tabpanel" id="panel1" aria-labelledby="tab1">...</div>
  <div role="tabpanel" id="panel2" aria-labelledby="tab2" hidden>...</div>
</div>
```

## Skip Links
```html
<a href="#main" class="skip-link">
  Skip to main content
</a>

<style>
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--bg-primary);
  color: var(--text-primary);
  padding: 8px 16px;
  z-index: 100;
  transition: top 0.2s;
}
.skip-link:focus {
  top: 0;
}
</style>
```

## Accessibility Pre-Ship Checklist

- [ ] Color contrast meets WCAG AA (4.5:1 text, 3:1 UI)
- [ ] Focus states visible on ALL interactive elements
- [ ] Semantic HTML: nav, main, section, article, footer, header
- [ ] One `<h1>` per page, logical heading hierarchy
- [ ] Alt text on all images (decorative: `alt=""`)
- [ ] Form labels associated with inputs
- [ ] Icon-only buttons have `aria-label`
- [ ] Keyboard navigation works for all interactives
- [ ] Skip-to-content link present
- [ ] `prefers-reduced-motion` respected
- [ ] ARIA used correctly (not overused)
- [ ] Tested with screen reader (NVDA, VoiceOver, JAWS)
- [ ] Tested with keyboard only (Tab, Enter, Space, Arrow keys)
