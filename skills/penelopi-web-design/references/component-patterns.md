# Component Patterns

## shadcn/ui Base Components

### Installation
```bash
npx shadcn@latest add button badge card accordion dialog navigation-menu tabs sheet separator avatar alert input select textarea checkbox radio-group switch
```

### Most Used for Landing Pages

| Component | Use Case | Pattern |
|-----------|----------|---------|
| `Button` | CTAs, actions | Size hierarchy: default → lg for hero |
| `Badge` | Labels, status | "New", "Beta", "Popular" |
| `Card` | Content containers | Feature cards, pricing tiers, testimonials |
| `Accordion` | FAQ sections | Single collapsible, clean styling |
| `Dialog` | Modals, video players | Max-w-4xl for video |
| `Sheet` | Mobile navigation | Side drawer, w-[280px] |
| `Tabs` | Feature showcases | Animated underline indicator |
| `Input` | Forms | Always with Label, never placeholder-as-label |
| `Select` | Dropdowns | Solid option backgrounds |

### Customizing Components

```tsx
// Extend variants in the component file
const buttonVariants = cva(
  "...",
  {
    variants: {
      variant: {
        default: "...",
        outline: "...",
        // Add custom
        gradient: "bg-gradient-to-r from-primary to-accent text-white hover:opacity-90",
        ghost: "hover:bg-accent/10 hover:text-accent",
      },
      size: {
        default: "h-10 px-4",
        sm: "h-9 px-3",
        lg: "h-12 px-8 text-base",
        icon: "h-10 w-10",
      },
    },
  }
)
```

## Hero Section Pattern

```tsx
function Hero() {
  return (
    <section className="relative overflow-hidden py-24 md:py-32">
      <div className="container grid lg:grid-cols-2 gap-12 items-center">
        {/* Text */}
        <div className="space-y-6">
          <Badge variant="secondary">Now in beta</Badge>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
            Your words,<br />supercharged
          </h1>
          <p className="text-lg text-muted-foreground max-w-xl">
            Write 10x faster with AI that learns your style. No more staring at blank pages.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Button size="lg">Start Free Trial</Button>
            <Button size="lg" variant="outline">Watch Demo</Button>
          </div>
          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <span>50K+ users</span>
            <span>4.9 rating</span>
          </div>
        </div>
        
        {/* Visual */}
        <div className="relative hidden lg:block">
          <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-accent/20 rounded-2xl blur-3xl" />
          <img src="/hero-visual.png" alt="Product demo" className="relative rounded-2xl shadow-2xl" />
        </div>
      </div>
    </section>
  )
}
```

## Feature Cards Pattern

```tsx
const features = [
  { icon: Zap, title: "Lightning Fast", description: "..." },
  { icon: Shield, title: "Secure", description: "..." },
  { icon: Globe, title: "Global", description: "..." },
]

function Features() {
  return (
    <section className="py-24">
      <div className="container">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Everything you need</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">...</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((f, i) => (
            <Card key={i} className="border-border/50 hover:border-primary/50 transition-all hover:-translate-y-1 hover:shadow-lg">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <f.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>{f.title}</CardTitle>
                <CardDescription>{f.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
```

## Pricing Table Pattern

```tsx
const plans = [
  { name: "Free", price: 0, features: ["..."], cta: "Get Started" },
  { name: "Pro", price: 19, features: ["..."], popular: true, cta: "Start Trial" },
  { name: "Team", price: 49, features: ["..."], cta: "Contact Sales" },
]

function Pricing() {
  return (
    <section className="py-24">
      <div className="container">
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map(plan => (
            <Card key={plan.name} className={cn(
              "relative",
              plan.popular && "border-primary shadow-lg scale-105"
            )}>
              {plan.popular && (
                <Badge className="absolute -top-3 left-1/2 -translate-x-1/2">
                  Most Popular
                </Badge>
              )}
              <CardHeader>
                <CardTitle>{plan.name}</CardTitle>
                <div className="text-4xl font-bold">
                  ${plan.price}
                  <span className="text-base font-normal text-muted-foreground">/mo</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {plan.features.map(f => (
                    <li key={f} className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {f}
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Button className="w-full" variant={plan.popular ? "default" : "outline"}>
                  {plan.cta}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
```

## FAQ Accordion Pattern

```tsx
const faqs = [
  { q: "How does it work?", a: "Our platform uses AI to..." },
  { q: "Is there a free trial?", a: "Yes, you get 14 days..." },
]

function FAQ() {
  return (
    <section className="py-24 max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
      <Accordion type="single" collapsible className="w-full">
        {faqs.map((faq, i) => (
          <AccordionItem key={i} value={`item-${i}`}>
            <AccordionTrigger>{faq.q}</AccordionTrigger>
            <AccordionContent>{faq.a}</AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  )
}
```

## Testimonial Cards Pattern

```tsx
const testimonials = [
  { quote: "...", author: "Sarah Chen", role: "Content Lead", company: "Stripe" },
]

function Testimonials() {
  return (
    <section className="py-24">
      <div className="container">
        <h2 className="text-3xl font-bold text-center mb-12">Loved by teams</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((t, i) => (
            <Card key={i} className="bg-muted/50">
              <CardContent className="pt-6">
                <Quote className="h-8 w-8 text-primary/20 mb-4" />
                <p className="text-lg mb-6">{t.quote}</p>
                <div className="flex items-center gap-3">
                  <Avatar>
                    <AvatarImage src={`/avatars/${t.author.toLowerCase()}.jpg`} />
                    <AvatarFallback>{t.author[0]}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium">{t.author}</p>
                    <p className="text-sm text-muted-foreground">{t.role}, {t.company}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
```

## Form Patterns

### Consistent Form Styling
```css
/* All form elements styled as a GROUP */
.input,
.select,
.textarea {
  border: 2px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px; /* Prevents iOS zoom */
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input:focus,
.select:focus,
.textarea:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-subtle);
  outline: none;
}
```

### Textarea Border Radius
Pill-shaped inputs look wrong on textareas:
```css
.input, .select { border-radius: 100px; }
.textarea { border-radius: 16px; } /* Softer, not pill */
```

### Dropdown Options
```css
.select {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;
}
/* Options need solid backgrounds — can't inherit backdrop-filter */
.select option {
  background: #1a1a2e;
  color: white;
}
```

### Form with Validation
```tsx
function ContactForm() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [touched, setTouched] = useState(false)

  const validate = () => {
    if (!email) return 'Email is required'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Enter a valid email'
    return ''
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setTouched(true)
    const err = validate()
    if (err) { setError(err); return }
    // Submit...
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="email">Email address</Label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={e => { setEmail(e.target.value); if (touched) setError(validate()) }}
          onBlur={() => { setTouched(true); setError(validate()) }}
          className={cn(error && touched && "border-destructive")}
        />
        {error && touched && (
          <p className="text-sm text-destructive mt-1">{error}</p>
        )}
      </div>
      <Button type="submit">Submit</Button>
    </form>
  )
}
```

## Loading States

### Skeleton Screens
```tsx
function SkeletonCard() {
  return (
    <div className="rounded-xl border p-6 space-y-4">
      <div className="flex items-center gap-4">
        <div className="h-12 w-12 rounded-full bg-muted animate-pulse" />
        <div className="space-y-2">
          <div className="h-4 w-24 rounded bg-muted animate-pulse" />
          <div className="h-3 w-16 rounded bg-muted animate-pulse" />
        </div>
      </div>
      <div className="space-y-2">
        <div className="h-3 w-full rounded bg-muted animate-pulse" />
        <div className="h-3 w-4/5 rounded bg-muted animate-pulse" />
      </div>
    </div>
  )
}
```

### Button Loading State
```tsx
<Button disabled={isLoading}>
  {isLoading ? (
    <>
      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      Processing...
    </>
  ) : (
    'Submit'
  )}
</Button>
```

## Error States

### Form Error
```tsx
<div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
  <div className="flex gap-3">
    <AlertCircle className="h-5 w-5 text-destructive shrink-0" />
    <div>
      <p className="font-medium text-destructive">Something went wrong</p>
      <p className="text-sm text-destructive/80">Please try again or contact support.</p>
    </div>
  </div>
</div>
```

### Empty State
```tsx
<div className="text-center py-16">
  <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
  <h3 className="text-lg font-medium mb-2">No results found</h3>
  <p className="text-muted-foreground mb-6">Try adjusting your search or filters.</p>
  <Button variant="outline">Clear Filters</Button>
</div>
```

## Anti-Patterns

- ❌ Placeholder text used as labels — always use `<Label>`
- ❌ Form elements styled individually — style as a group
- ❌ Missing error/loading/empty states — these are part of the design
- ❌ No focus styles on custom components — always visible focus
- ❌ Inconsistent spacing between similar components — use a scale
- ❌ Hardcoded colors in components — use CSS variables
