# Remotion Webapp Sizzle Template

A production-ready Remotion template for creating demo/sizzle videos of web applications. Features animated search fields, browser window mockups, typewriter effects, and professional scene transitions.

---

## 🚀 What's Included

### Components

| Component | Purpose | File |
|-----------|---------|------|
| **SearchField** | Animated search/address bar with typewriter effect | `components/SearchField.tsx` |
| **BrowserWindow** | Chrome/Safari-style browser frame | `components/BrowserWindow.tsx` |
| **WebAppScene** | Complete scene: search → app name → browser demo | `components/WebAppScene.tsx` |
| **SizzleTransition** | Professional scene transitions (fade, slide, wipe, flip, clock) | `components/SizzleTransition.tsx` |
| **Cursor** | Blinking cursor for typewriter | `components/Cursor.tsx` |

### Hooks

| Hook | Purpose | File |
|------|---------|------|
| **useTypewriter** | Reusable typewriter animation with start offset | `hooks/useTypewriter.ts` |

---

## 🎬 Scenes (What Gets Animated)

Each `WebAppScene` follows this timeline:

1. **0-2s** — Background fades in with brand color gradient
2. **0-4s** — Search field types out query (e.g., "AI voice agents for small business")
3. **2-3s** — App name + tagline reveal with scale animation
4. **3-5s** — Browser window slides up into view
5. **4-6s** — Simulated app content (nav, hero, CTAs, feature cards) fades in

---

## 🎨 Customization

### Change the showcased apps

Edit `Master.tsx`:

```tsx
<WebAppScene
  appName="Your App"
  appUrl="yourapp.com"
  searchQuery="what people search to find you"
  tagline="Your value proposition"
  color="#hexcolor"
  startFrame={0}
/>
```

### Change transition style

```tsx
// Options: "fade", "slide-left", "slide-right", "slide-up", "slide-down", "wipe", "flip", "clock"
<SizzleTransition transitionType="wipe" durationInFrames={30}>
  {scenes}
</SizzleTransition>
```

### Pre-built transition exports

```tsx
import { FadeTransition, SlideLeftTransition, WipeTransition } from "./components/SizzleTransition";

<FadeTransition sceneDuration={150}>
  <Scene1 />
  <Scene2 />
</FadeTransition>
```

---

## 📐 Composition Presets

| Preset | ID | Dimensions | Best For |
|--------|-----|-----------|----------|
| Horizontal | `WebAppShowcase` | 1920×1080 | YouTube, website hero, presentations |
| Vertical | `WebAppVertical` | 1080×1920 | TikTok, Reels, Shorts |
| Square | `WebAppSquare` | 1080×1080 | Instagram feed, Twitter |

---

## 🛠️ Setup

```bash
# 1. Create project
npx create-video@latest my-sizzle
cd my-sizzle

# 2. Install transitions package
npx remotion add @remotion/transitions

# 3. Install Tailwind
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 4. Copy template files
cp -r /Users/oktos/.openclaw/workspace/remotion-starter-template/src/* ./src/

# 5. Start dev server
npm run dev
```

### Tailwind Config

`tailwind.config.js`:
```js
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
};
```

---

## 🎯 Animation Patterns Used

| Pattern | Implementation | Use Case |
|---------|---------------|----------|
| **Typewriter** | `useTypewriter` hook | Search queries, commands |
| **Fade In** | `interpolate(frame, [start, end], [0, 1])` | Backgrounds, text reveals |
| **Scale Pop** | `interpolate(frame, [start, end], [0.9, 1])` | Element entrances |
| **Slide Up** | `interpolate(frame, [start, end], [100, 0])` + `translateY` | Browser window reveal |
| **Blink** | `frame % interval` + `interpolate` | Cursor, loading indicators |
| **3D Rotate** | `perspective` + `rotateX`/`rotateY` | Dramatic transitions |
| **Spring** | `springTiming({ config: { damping: 200 } })` | Scene transitions |

---

## 🎬 Rendering

```bash
# Preview
npm run dev

# Render MP4 (1920×1080)
npx remotion render src/index.ts WebAppShowcase out/sizzle.mp4

# Render vertical for social
npx remotion render src/index.ts WebAppVertical out/sizzle-vertical.mp4

# Render still frame
npx remotion still src/index.ts WebAppShowcase --frame=150 out/poster.png
```

---

## 💡 Pro Tips

1. **Search queries** — Use real search terms your customers would type. This makes the demo relatable.

2. **Brand colors** — Match `color` prop to your app's primary color for visual consistency.

3. **Scene count** — 3-5 scenes optimal for 30-60 second sizzle reels.

4. **Transition speed** — `durationInFrames: 20-30` (0.7-1s) feels premium. Faster = snappier, slower = cinematic.

5. **Typewriter speed** — `charsPerSecond: 20-30` for short queries, `15-20` for longer sentences.

6. **StartFrame offset** — Use `startFrame` in `WebAppScene` to stagger animations when not using `TransitionSeries`.

7. **Replace mock content** — The feature cards in `WebAppScene` are CSS shapes. Replace with real screenshots by importing images:
   ```tsx
   import { Img } from "remotion";
   <Img src={screenshotUrl} />
   ```

---

## 🔗 Resources

- [Remotion Transitions Docs](https://www.remotion.dev/docs/transitions)
- [Jonny Burger's Original Session](https://gist.github.com/JonnyBurger/5b801182176f1b76447901fbeb5a84ac)
- [Remotion Best Practices](https://github.com/remotion-dev/remotion)

---

*Template v2.0 — Webapp Sizzle Edition*
