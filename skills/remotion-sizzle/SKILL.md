---
name: remotion-sizzle
emoji: 🎬
description: One-command setup for Remotion webapp sizzle videos with animated search fields, browser mockups, typewriter effects, and professional transitions.
---

# remotion-sizzle

Create polished demo/sizzle videos for web applications in minutes. Animated search fields that type out queries, browser window mockups, and cinematic scene transitions — all in one command.

## What You Get

| Feature | Description |
|---------|-------------|
| 🔍 Animated Search Field | Types out search queries with blinking cursor |
| 🌐 Browser Window | Chrome/Safari-style frame with traffic lights + URL bar |
| ✍️ Typewriter Effect | Progressive text reveal with customizable speed |
| 🎬 5 Transitions | Fade, slide, wipe, flip, clock — all with spring physics |
| 📐 3 Presets | Horizontal (YouTube), vertical (TikTok/Reels), square (Instagram) |
| 🎨 Brand Colors | Match your app's primary color per scene |
| ⚛️ React + Tailwind | Full component architecture, easy to customize |

## Prerequisites

- Node.js 18+ (`node --version`)
- npm or yarn

## Usage

### One-Command Setup (Recommended)

```bash
# From the template directory
bash /Users/oktos/.openclaw/workspace/remotion-starter-template/setup-remotion-sizzle.sh my-video

cd my-video
npm run dev
```

The script handles everything:
1. ✅ Creates Remotion project
2. ✅ Installs `@remotion/transitions`, `tailwindcss`, `postcss`, `autoprefixer`
3. ✅ Copies all template components, hooks, and scenes
4. ✅ Creates `tailwind.config.js` and `postcss.config.js`
5. ✅ Sets up `package.json` scripts
6. ✅ Ready to run `npm run dev`

### Manual Setup (If Script Fails)

```bash
npx create-video@latest my-video
cd my-video
npx remotion add @remotion/transitions
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Copy template files
cp -r /Users/oktos/.openclaw/workspace/remotion-starter-template/src/* ./src/
```

### Render Video

```bash
# Preview in browser
npm run dev

# Build 1920×1080 (YouTube/presentations)
npm run build

# Build 1080×1920 (TikTok/Reels/Shorts)
npm run buildVertical

# Export poster frame
npm run still
```

## Customization

### Change Showcased Apps

Edit `src/Master.tsx`:

```tsx
<WebAppScene
  appName="YourProduct"
  appUrl="yourproduct.com"
  searchQuery="what customers type in Google"
  tagline="Your value proposition"
  color="#your-brand-color"
  startFrame={0}
/>
```

### Change Transition Style

```tsx
// Options: fade, slide-left, slide-right, slide-up, slide-down, wipe, flip, clock
<SizzleTransition transitionType="wipe" durationInFrames={30}>
  <Scene1 />
  <Scene2 />
</SizzleTransition>
```

### Add a Scene

Create a new file in `src/components/MyScene.tsx`, then import and add to `Master.tsx`:

```tsx
import { MyScene } from "./components/MyScene";

// In Master.tsx:
<SizzleTransition transitionType="slide-left">
  <WebAppScene ... />
  <MyScene />  {/* your new scene */}
</SizzleTransition>
```

## Components

| Component | Props | Purpose |
|-----------|-------|---------|
| `SearchField` | `query`, `startFrame`, `charsPerSecond`, `isAddressBar` | Animated search/URL input |
| `BrowserWindow` | `children`, `url`, `title` | Chrome-style browser frame |
| `WebAppScene` | `appName`, `appUrl`, `searchQuery`, `tagline`, `color` | Complete showcase scene |
| `SizzleTransition` | `transitionType`, `durationInFrames`, `sceneDurationInFrames` | Scene transitions wrapper |
| `Cursor` | `blinking`, `color` | Blinking text cursor |

## Hooks

| Hook | Returns | Purpose |
|------|---------|---------|
| `useTypewriter` | `{ displayedText, isTyping, isComplete, visibleChars }` | Reusable typewriter animation |

## Composition Presets

| Preset | ID | Resolution | Use Case |
|--------|-----|-----------|----------|
| Horizontal | `WebAppShowcase` | 1920×1080 | YouTube, pitch decks, website hero |
| Vertical | `WebAppVertical` | 1080×1920 | TikTok, Instagram Reels, YouTube Shorts |
| Square | `WebAppSquare` | 1080×1080 | Instagram feed, Twitter/X |

## Scene Timeline (Per Scene)

| Time | Action |
|------|--------|
| 0.0s | Background fades in (brand gradient) |
| 0.0s | Search field types query |
| 2.0s | App name + tagline scale into view |
| 3.0s | Browser window slides up |
| 4.0s | Mock app content (nav, hero, CTAs) fades in |
| 6.0s | Scene complete, transition begins |

## Architecture

```
src/
├── Root.tsx              # Entry point — registers compositions
├── Master.tsx            # Master composition — scenes + transitions
├── index.ts              # Remotion bundle entry
├── index.css             # Tailwind directives
├── components/
│   ├── SearchField.tsx   # Animated search bar
│   ├── BrowserWindow.tsx # Browser chrome frame
│   ├── WebAppScene.tsx   # Complete scene assembly
│   ├── SizzleTransition.tsx # Transition wrapper + presets
│   └── Cursor.tsx        # Blinking cursor
└── hooks/
    └── useTypewriter.ts  # Typewriter animation hook
```

## Pro Tips

1. **Search queries** — Use real terms your customers would type. Makes demo relatable.
2. **Brand colors** — Match `color` prop to app primary color for consistency.
3. **Scene count** — 3-5 scenes optimal for 30-60 second sizzle reels.
4. **Transition speed** — `durationInFrames: 20-30` (0.7-1s) feels premium.
5. **Typewriter speed** — `charsPerSecond: 25` for short queries, `15-20` for longer.
6. **Replace mock content** — Feature cards in `WebAppScene` are CSS shapes. Import real screenshots with `Img` from Remotion.

## Resources

- [Remotion Docs](https://www.remotion.dev/docs)
- [Remotion Transitions](https://www.remotion.dev/docs/transitions)
- [Jonny Burger's Original Session](https://gist.github.com/JonnyBurger/5b801182176f1b76447901fbeb5a84ac)
- Template source: `~/.openclaw/workspace/remotion-starter-template/`

## License

MIT — based on Remotion and Jonny Burger's open-source work.
