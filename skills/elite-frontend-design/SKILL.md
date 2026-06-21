# Elite Frontend Design

> **Version:** 1.0.0  
> **Purpose:** Mandatory design standards for all web design tasks  
> **Standard:** Award-winning caliber (Awwwards, Land-Book, MotionSites tier)

## Overview

This skill ensures every webpage produced by our team meets or exceeds the design quality of award-winning websites. It provides a comprehensive design system with specific CSS values, code patterns, and quality checks.

## Quick Start

When spawning a Codex sub-agent for any web design task, you MUST attach the Design Bible as context. This ensures every webpage — even minor ones — meets premium standards.

## Usage

### Method 1: Direct Attachment (Recommended)

When spawning a sub-agent for web design, always include the Design Bible path:

```
Read and follow the Design Bible at:
~/.openclaw/workspace/skills/elite-frontend-design/design-bible.md

This is MANDATORY for all web design tasks. No exceptions.
```

### Method 2: Skill Reference

Reference this skill in your task description:

```
Use the elite-frontend-design skill standards. 
Read the design-bible.md for complete specifications.
```

## Core Files

| File | Purpose |
|------|---------|
| `design-bible.md` | Complete design system with CSS values, patterns, and quality checklist |
| `SKILL.md` | This file — usage instructions and integration guide |

## Key Principles (Summary)

1. **Mobile-first, never desktop-only**
2. **Dark mode as default for premium/SaaS**
3. **Maximum 2 font families per page**
4. **Every element must have a purpose**
5. **60fps animations or none at all**
6. **Hero communicates value in 3 seconds**
7. **No generic stock imagery**
8. **Consistent 8px spacing scale**
9. **Micro-interactions on every interactive element**
10. **Quality checklist before shipping**

## Integration with Codex

### For Every Web Design Task

When you spawn a Codex sub-agent, your task message MUST include:

```markdown
## Design Standards (MANDATORY)

Before writing any code, read:
~/.openclaw/workspace/skills/elite-frontend-design/design-bible.md

You MUST follow all specifications in the Design Bible, including:
- Typography hierarchy with clamp() values
- Color system (use one of the provided palettes)
- Layout patterns (grid system, spacing scale)
- Animation rules (GSAP for scroll, CSS for hover)
- Component patterns (buttons, cards, navigation)
- Quality checklist (verify ALL items before completion)

### Anti-Patterns to AVOID:
- Generic gradient backgrounds (purple-to-blue default)
- Rounded corners on everything (border-radius: 9999px abuse)
- Centered text blocks wider than 65ch
- Stock photos with perfect smiles
- Default Tailwind colors without customization
- Shadow abuse (arbitrary box-shadow values)
- No hover states on buttons
- Missing focus rings

### Your deliverable MUST include:
1. Complete HTML/CSS/JS implementation
2. All animations implemented (not just described)
3. Responsive design (tested at 320px, 768px, 1440px)
4. Quality checklist verification (all items checked)
5. Screenshots or preview of the final result
```

## Design Bible Contents

The Design Bible (`design-bible.md`) contains:

1. **Mandatory Design Principles** — Non-negotiable rules
2. **Typography Hierarchy** — Font pairings, sizes, weights, line-heights
3. **Color System** — Palettes, gradients, dark mode
4. **Layout Patterns** — Grid systems, spacing, breakpoints
5. **Animation & Interaction** — Scroll triggers, hover states, micro-interactions
6. **Component Patterns** — Buttons, cards, navigation, forms, CTAs
7. **Visual Effects** — Glassmorphism, shadows, 3D transforms
8. **Content Strategy** — Structure for maximum conversion
9. **Performance Rules** — Animation performance, loading states
10. **Quality Checklist** — 20+ items to verify before shipping

## Quality Checklist Summary

Before any webpage is considered complete, verify:

- [ ] Typography uses exactly 2 font families
- [ ] Type scale follows clamp() system
- [ ] Color contrast ≥ 4.5:1 for body text
- [ ] Mobile-first responsive (320px, 768px, 1440px)
- [ ] Animations are 60fps (transform/opacity only)
- [ ] Hover states on ALL interactive elements
- [ ] Focus rings visible and styled
- [ ] Page weight < 1MB
- [ ] Hero communicates value in 3 seconds
- [ ] One clear CTA per section
- [ ] No placeholder text or generic stock photos
- [ ] No "Click here" or "Welcome to our website" text
- [ ] No centered text blocks wider than 65ch
- [ ] No more than 3 font sizes per section
- [ ] No decorative elements without purpose
- [ ] No auto-playing audio/video
- [ ] No popups on page load
- [ ] All images have alt text and are optimized (WebP)
- [ ] Tab navigation works logically
- [ ] Form validation with clear error messages
- [ ] No broken links or 404s

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-10 | Initial release based on MotionSites, Land-Book, Awwwards research |

---

*Remember: Every webpage is a reflection of our standards. Never ship mediocre work.*
