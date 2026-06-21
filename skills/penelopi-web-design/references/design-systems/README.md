# Brand Design System Library

Curated DESIGN.md files extracted from real-world brand websites.

## Structure

```
design-systems/
├── ai-devtools/          # Developer platforms, SaaS, CLI tools
│   ├── vercel.md
│   ├── linear.md
│   ├── raycast.md
│   ├── supabase.md
│   ├── cursor.md
│   ├── warp.md
│   └── framer.md
├── fintech/              # Banking, payments, crypto
│   ├── stripe.md
│   ├── wise.md
│   ├── revolut.md
│   └── coinbase.md
├── consumer/             # Lifestyle, retail, media
│   ├── apple.md
│   ├── nike.md
│   ├── spotify.md
│   ├── airbnb.md
│   └── notion.md
├── automotive/           # Luxury, performance
│   ├── bmw.md
│   ├── ferrari.md
│   ├── lamborghini.md
│   └── tesla.md
└── retro/                # Nostalgia, vintage, Y2K
    ├── dell-1996.md
    └── nintendo-2001.md
```

## Usage

When a prompt mentions a brand, load the matching DESIGN.md and apply its tokens:

```
"Build a landing page like Stripe" → load fintech/stripe.md
"Make it look like Linear" → load ai-devtools/linear.md
"Retro 90s vibe" → load retro/dell-1996.md
```

## Format

Each file follows the Google Stitch DESIGN.md spec:
1. Visual Theme & Atmosphere
2. Color Palette & Roles
3. Typography Rules
4. Component Stylings
5. Layout Principles
6. Depth & Elevation
7. Do's and Don'ts
8. Responsive Behavior
9. Agent Prompt Guide
