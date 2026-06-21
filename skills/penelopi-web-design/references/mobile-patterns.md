# Mobile-First Patterns

## Core Principle

Design for the thumb first. Desktop is an enhancement, not the baseline.

## Breakpoints

```css
/* Small Mobile */
@media (max-width: 480px) { }

/* Mobile */
@media (max-width: 768px) { }

/* Tablet */
@media (max-width: 1024px) { }

/* Desktop */
@media (max-width: 1280px) { }

/* Large Desktop */
@media (min-width: 1440px) { }
```

**Approach:** Mobile-first CSS — base styles for mobile, use `min-width` media queries to enhance for larger screens.

## Hero Section (Mobile)

```css
/* Base (mobile) */
.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 40px 16px;
  gap: 24px;
}
.hero-title { font-size: 32px; }
.hero-subtitle { font-size: 16px; }
.hero-cta { 
  flex-direction: column; 
  width: 100%; 
  gap: 12px;
}
.hero-cta .btn { width: 100%; max-width: 280px; }
.hero-visual { display: none; } /* Hide complex visuals on mobile */

/* Desktop enhancement */
@media (min-width: 769px) {
  .hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 64px;
    padding: 80px 0;
    text-align: left;
    align-items: center;
  }
  .hero-title { font-size: 64px; }
  .hero-visual { display: block; }
  .hero-cta { flex-direction: row; }
  .hero-cta .btn { width: auto; }
}
```

**Key Rule:** Grid reserves space for hidden columns. Flex doesn't. Switch from `grid` to `flex` on mobile when hiding one column.

## Navigation (Mobile)

```tsx
// Sheet/Drawer pattern
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Menu, X } from "lucide-react"

function MobileNav() {
  const [open, setOpen] = useState(false)

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-6 w-6" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-[280px]">
        <nav className="flex flex-col gap-6 mt-8">
          {links.map(link => (
            <a 
              key={link.href} 
              href={link.href}
              onClick={() => setOpen(false)}
              className="text-lg font-medium"
            >
              {link.label}
            </a>
          ))}
          <Button className="mt-4">Get Started</Button>
        </nav>
      </SheetContent>
    </Sheet>
  )
}
```

**Key Rule:** Navigation must become a sheet/drawer on mobile. Never horizontal scroll.

## Large Lists (Mobile)

```tsx
// Accordion with category headers (not horizontal scroll)
function MobileSelector({ categories }) {
  const [expanded, setExpanded] = useState(null)

  return (
    <div className="selector">
      {categories.map(cat => (
        <div key={cat.name} className="category">
          <button
            className="category-header"
            onClick={() => setExpanded(expanded === cat.name ? null : cat.name)}
          >
            <span>{cat.name}</span>
            <ChevronDown className={cn(
              "transition-transform",
              expanded === cat.name && "rotate-180"
            )} />
          </button>
          <div className={cn(
            "category-items overflow-hidden transition-all",
            expanded === cat.name ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
          )}>
            {cat.items.map(item => (
              <button key={item.id} className="item">{item.name}</button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
```

## Forms (Mobile)

```css
/* Stack vertically, full width */
.form-row {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-group {
  width: 100%;
}

/* Desktop: side by side */
@media (min-width: 769px) {
  .form-row {
    flex-direction: row;
  }
  .form-group {
    flex: 1;
  }
}
```

**Key Rule:** Even "half-width" fields go full-width on mobile. Never side-by-side on mobile.

## Cards & Grids (Mobile)

```css
/* Base: single column */
.card-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

/* Tablet: 2 columns */
@media (min-width: 769px) {
  .card-grid { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop: 3 columns */
@media (min-width: 1025px) {
  .card-grid { grid-template-columns: repeat(3, 1fr); }
}
```

## Touch Targets

Minimum 44x44px (Apple HIG) / 48x48px (Material Design):

```css
.btn,
.nav-link,
.icon-btn,
.checkbox,
.radio {
  min-height: 44px;
  min-width: 44px;
}

@media (max-width: 768px) {
  .btn {
    padding: 14px 24px; /* Larger touch area */
  }
}
```

## iOS Zoom Prevention

Font size below 16px on inputs triggers iOS zoom on focus:

```css
input, select, textarea {
  font-size: 16px; /* Minimum to prevent zoom */
}
```

## Status/Alert Cards (Mobile)

```css
.alert {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
}

@media (max-width: 768px) {
  .alert {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .alert-content {
    text-align: center;
  }
  .alert strong {
    display: block;
    text-align: center;
  }
}
```

**Key Rule:** Stacked flex items need BOTH `align-items: center` AND `text-align: center`.

## Font Scaling (Mobile)

```css
/* Desktop base */
.display { font-size: 64px; }
.h1 { font-size: 48px; }
.h2 { font-size: 36px; }
.h3 { font-size: 24px; }
.body { font-size: 16px; }
.small { font-size: 14px; }

/* Mobile */
@media (max-width: 768px) {
  .display { font-size: 40px; }
  .h1 { font-size: 32px; }
  .h2 { font-size: 24px; }
  .h3 { font-size: 20px; }
  .body { font-size: 16px; } /* Keep readable */
  .small { font-size: 13px; }
}
```

## Container Padding (Mobile)

```css
.container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px; /* Mobile: tighter */
}

@media (min-width: 769px) {
  .container { padding: 0 24px; }
}

@media (min-width: 1281px) {
  .container { padding: 0 32px; }
}
```

## Mobile Pre-Implementation Checklist

- [ ] Hero centers on mobile (not left-aligned with empty grid space)
- [ ] All grids collapse to single column below 768px
- [ ] Forms stack vertically (never side-by-side)
- [ ] Touch targets are 44px minimum
- [ ] Font sizes on inputs are 16px+ (prevent iOS zoom)
- [ ] Navigation uses sheet/drawer (not horizontal scroll)
- [ ] Large lists use accordion (not horizontal scroll)
- [ ] Status cards center properly (flex + text-align)
- [ ] Visual elements hidden or simplified on mobile
- [ ] Container padding appropriate for screen size
- [ ] Tested on actual device or responsive mode
- [ ] No horizontal scroll anywhere
