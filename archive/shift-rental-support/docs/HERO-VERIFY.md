# Hero / landing — quick regression checklist

Run after meaningful changes to `public/index.html` or `public/hero-terrain.js`. (Phase **9.5** / roadmap Phase 0 verify block.)

## Environment

- [ ] `node server.js` → open **`http://localhost:3000/`** (not `file://`).
- [ ] Hard reload; confirm Network **`hero-terrain.js`** returns **200** and expected **`?v=`** query.

## Motion & performance

- [ ] **Reduce motion** (OS) on → static hero canvas, no animation churn.
- [ ] **Reduce motion** off → motion returns after reload or toggle (if supported).
- [ ] DevTools **Performance** short recording while moving pointer over hero — no sustained jank.
- [ ] Scroll hero mostly off-screen → CPU should drop (IntersectionObserver pauses RAF).

## Visual / contrast (Phase 9.2 spot-check)

- [ ] Headline + body readable on **OLED** / dark room (left column over terrain).
- [ ] **Increase contrast** (macOS / Windows) → title loses blend, body/label brighter.
- [ ] **Windows High Contrast** / `forced-colors` → title does not rely on `mix-blend-mode` alone.

## Cross-browser (Phase 9.4 — smoke)

- [ ] **Safari** (desktop): canvas, parallax, tooltip on nodes.
- [ ] **Chrome** or **Edge**: same.
- [ ] **Firefox**: same.
- [ ] **iOS Safari** (or simulator): layout stack ≤1024px, canvas not blank.

## A11y

- [ ] Screen reader: hero section exposes **`#fleet-terrain-desc`** via **`aria-describedby`**.

## Failure modes

- [ ] With devtools blocking **`hero-terrain.js`**, page should still render (degraded / fallback per implementation).
