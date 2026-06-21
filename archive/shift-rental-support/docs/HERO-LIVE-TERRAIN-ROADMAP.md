# SHIFT Hero — “Live Terrain” roadmap

Track progress across sessions. Check `[ ]` → `[x]` as you complete items.  
**Spec reference:** original “SHIFT HERO VISUAL — LIVE TERRAIN” brief (procedural 2.5D command cartography).

**Primary files today**

| Area | Path |
|------|------|
| Landing markup + hero CSS | `public/index.html` |
| Canvas engine | `public/hero-terrain.js` |
| Operator / deploy | `README.md` |

**How to verify after each change**

- [ ] `node server.js` → `http://localhost:3000/` (not `file://`)
- [ ] Hard reload (cache bust on `hero-terrain.js` query string when you ship)
- [ ] Chrome DevTools → Performance (short recording, no jank spikes)
- [ ] **Reduce motion** on + off (macOS: Accessibility → Display)
- [ ] **Low battery** simulation if you use `getBattery` lite path
- [ ] **Mobile Safari** or iOS simulator (Canvas + DPR)

---

## Phase 0 — Baseline & definition of done

**Goal:** Lock what “highest caliber” means so work doesn’t churn.

- [x] **0.1** Canonical spec: original “LIVE TERRAIN” prompt + **this roadmap** are the working source of truth.
- [x] **0.2** **Acceptance criteria (v1):** (1) Full-bleed terrain under hero, copy readable. (2) Grid reads axonometric at glance. (3) Hub reads as instrument vs nodes. (4) ~60fps on target hardware + IO pause off-screen. (5) Bidirectional particle streams obvious. (6) Reduced motion = rich static frame. (7) Low-battery degrades safely. (8) No broken canvas composites; version `hero-terrain.js`. (9) WCAG AA pass on final stack. (10) Safari/Chrome/Firefox + iOS smoke.
- [x] **0.3** Capture **reference stills** — **`docs/assets/README.md`** defines naming (`hero-current.png`, `hero-target.png`); add PNGs when you snapshot (**manual** drop).
- [x] **0.4** **Layout decision:** **Hybrid** — full-bleed `#terrain` behind `#hero-section`; **45% / 55%** via copy + `.hero-visual--spacer`; hub at **~72.5% W** desktop, **50% / 42%** when stacked ≤1024px.

**Exit:** Signed-off target layout + perf floor (fps / device class).

---

## Phase 1 — Composition & layout (biggest spec gap)

**Goal:** Match “command view” integration with typography and vignette, not only the boxed visual.

- [x] **1.1** **DOM audit** — See HTML comment on `#hero-section`: backing → host → canvas/vignette/SVG → `.hero-matte` → `.hero-bg` → `.hero-copy` → spacer → tooltip.
- [x] **1.2** **Full-bleed** — `.hero-terrain-backing` + `pointer-events: none`; mouse on `#hero-section` → `hero-terrain.js`.
- [x] **1.3** **Hero-scale matte** — `.hero-matte` radial; canvas vignette uses **hub** (`hx`,`hy`).
- [x] **1.4** **`mix-blend-mode`** — `exclusion` on title + legibility `text-shadow`; `prefers-contrast: more` + **`forced-colors`** hardening. **Phase 9.2** tightens body/label copy contrast.
- [x] **1.5** **Glass polish** — Nav: top hairline + inset highlight + depth shadow; hero: instrument bezel (inset frame, cyan corner ticks), grain layer, vignette retune.
- [x] **1.6** **Ratio** — **45% / 55%** spacer preserved.

**Exit:** Screenshot matches “typography integrated with cartography,” not “card with wallpaper.”

---

## Phase 2 — Basemap & topology (axonometric + districts)

**Goal:** Readable **non-literal city grid** at 30° feel, spec densities.

- [x] **2.1** **Grid geometry** — Two families at **true 30°** run (`H * tan(30°)` per step), **120px** index spacing, **1px** stroke (`hero-terrain.js` `drawGrid`).
- [x] **2.2** **Grid breathing** — **4s** cycle; opacity **~0.038–0.070** (QW.1 OLED read).
- [x] **2.3** **Edge fade on grid** — `gridEdgeFade()` scales per-line alpha from **~0.12** at rim → **full** inward (`source-over` only).
- [x] **2.4** **District blocks** — **9** zones, convex **4–6** verts, fill **`rgba(255,159,10,0.033)`** (QW.2 bump), no stroke.
- [x] **2.5** **District parallax** — Translate **`parallaxDX * 0.09`** (~90% of vehicle’s `norm*18*0.12` vs `norm*22` pass — “slower layer”).
- [x] **2.6** **Scan pulse** — **8s** cycle; peak alpha **0.12** (was 0.1) for visibility on `#000`.

**Exit:** At a glance, reads “map substrate,” not “decorative lines.”

---

## Phase 3 — Fleet nodes (five entities, status, interaction)

**Goal:** Apple/Tesla-grade clarity per node + hover physics.

- [x] **3.1** **Node stack audit** — Outer halo / mid ring / core gradient per spec (`shadowBlur` tiers, white core **2px**, amber edge).
- [x] **3.2** **Status encoding** — **Active** (amber, 1.5s double pulse), **charging** (teal, breathe not double-pulse), **idle** (slate, **30%** opacity, slower drift).
- [x] **3.3** **Brownian + easing** — Bounded wander **~20px** from origin, **~0.05** smoothing factor (tune until “liquid,” not jittery).
- [x] **3.4** **Mouse repulsion** — **50px** influence, force ~**1/d** capped; no explosions near cursor.
- [x] **3.5** **Hover hit-test** — **30px** radius: scale **6 → 10px**, shadow **40 → 60**, tooltip **ID + yield** (copy from spec strings).
- [x] **3.6** **High contrast** — `prefers-contrast: more`: **2px white stroke** on nodes (canvas draw path).
- [x] **3.7** **Golden-angle placement** — Re-verify **φ spiral** positions feel balanced in **tall and wide** viewports.

**Exit:** Any node state readable in 2s without a legend.

---

## Phase 4 — Command core (dodecagon hub)

**Goal:** Precision instrument, not a generic glow orb.

- [x] **4.1** **Dodecagon accuracy** — **12** sides, **48px** outer diameter (**24px** radius), **2px** cyan stroke; vertices align with port dots.
- [x] **4.2** **Rotation** — **12s/rev** chosen; documented in `hero-terrain.js` (conflicts with 0.5 rpm in brief).
- [x] **4.3** **Inner core** — **24px** diameter fill, radial **white → cyan**, `shadowBlur ~30` cyan tint.
- [x] **4.4** **Heartbeat scale** — **3s** ease **1.0 → 1.05 → 1.0** (`hubHeartbeatScale`, cosine halves).
- [x] **4.5** **Port tracers** — **12** dots **2px**, **~2s** cadence, **micro-beads** on outward streak + tip spark.
- [x] **4.6** **Hub hover** — Near hub: **~4×** angular velocity vs idle (maps brief’s 0.5→2 rpm intent; base remains 12s/rev / 4.2).

**Exit:** Hub reads “engineered,” distinct from vehicle nodes.

---

## Phase 5 — Data tethers & particles (yield streams)

**Goal:** Bidirectional “traffic,” not a single gradient line.

- [x] **5.1** **Bezier quality** — Quadratic curves; ctrl **slow wave** via `elapsed` (multi-sine on mid-point Y).
- [x] **5.2** **Gradient stroke** — **Cyan at hub → amber at vehicle** on tether (1px); entrance **dash** tied to `T_TETHERS` / `tetherProgress`.
- [x] **5.3** **Particle count** — **~22** per path per direction (lite **~10**); **POOL 260** so all streams fill; battery/lite still cap.
- [x] **5.4** **Speed lanes** — **40–80 px/s** variance per lane for density realism.
- [x] **5.5** **Fade envelope** — **0→1** first **10%** of path, hold, **1→0** last **10%** (upstream/downstream math verified in `drawPathParticles`).
- [x] **5.6** **Path caching** — **Path2D** per tether rebuilt in `buildPaths` each frame (ctrl animates); `stroke(Path2D)` in `drawTethers`. Low path count; full static cache not possible without splitting curve.

**Exit:** Streams read as “two-way data” in motion.

---

## Phase 6 — Animation choreography

**Goal:** Entrance and ambient loops feel authored.

- [x] **6.1** **Entrance timeline** — `T_GRID`…`T_PARTICLES` match spec (0.2 / 0.8 / 1.2+150ms stagger / 1.6 / 2.0) + CSS **800ms** canvas fade.
- [x] **6.2** **Elastic hub** — Entrance uses sine-envelope overshoot **~1.11 → 1.0** over hub window.
- [x] **6.3** **Ambient drift** — **fbm**-steered velocity targets + small jitter; idle scaling preserved.
- [x] **6.4** **Hub vertical float** — **±3px**, **4s** sine (documented on `floatY` in `drawHub`).
- [x] **6.5** **Sync ripple** — **`SYNC_RIPPLE_INTERVAL_SEC` 6**, hub-distance sort, **`SYNC_RIPPLE_STAGGER_MS` 95**; stronger radius + outer blur while `ripple` decays.

**Exit:** Reload feels like an instrument boot sequence.

---

## Phase 7 — CSS / Houdini integration

**Goal:** Spec’d stack, not just “CSS variables from JS.”

- [x] **7.1** **`@property`** — `--shift-terrain-parallax`, **`--mouse-x`**, **`--mouse-y`** registered; browsers without `@property` ignore safely.
- [ ] **7.2** **Paint worklet (optional)** — If you want true Houdini: **grid or vignette** in a worklet; document **Chrome-only** vs fallback.
- [x] **7.3** **Parallax host** — **`PARALLAX_THROTTLE_MS` (100)** → ~**10 Hz** `setProperty` on **`#hero-terrain-host`**; **canvas** uses its own `transform` in CSS (documented in JS).

**Exit:** Reduced JS thrash; clearer separation paint vs layout.

---

## Phase 8 — Performance & battery (Apple-grade)

**Goal:** 60fps target where promised; graceful degradation.

- [x] **8.1** **DPR cap** — **max DPR 2** on init + resize (commented; iPad Pro stays 2× backing store).
- [x] **8.2** **RAF discipline** — **Single** `frame()` RAF chain; **IO always on** (pause off-screen); file-header note; one-shot sizing RAF only.
- [x] **8.3** **Particle pool** — **POOL** pre-alloc; hot path in-place only (Path2D tether rebuild is O(5) and documented).
- [x] **8.4** **Shadow blur cost** — **EWMA** frame ms → **`cheapShadows`** (trim hub/node blur, skip scan pulse) with hysteresis.
- [x] **8.5** **`getBattery` path** — **`particleCapScale` 0.5**, **`hubRotationPaused`** when low + !charging; **`.catch`** if API rejects (no prompt).
- [x] **8.6** **`prefers-reduced-motion`** — **Live `matchMedia` sync** + **change** handler: static **`frame()`** once, **no** reboot pulse when enabling; full loop when disabling.

**Exit:** Performance panel: stable frame time on target hardware list.

---

## Phase 9 — Accessibility & QA

**Goal:** Ship-grade, not demo-grade.

- [x] **9.1** **Keyboard** — **`#fleet-terrain-desc`** (visually hidden) + **`aria-describedby`** on **`#hero-section`** for fleet diagram semantics.
- [x] **9.2** **Contrast** — **`--hero-body-readable`**, stronger body shadows; **`prefers-contrast: more`** for label/body/trust; **`forced-colors: active`** resets title blend. **Manual OLED / APCA tooling** still recommended (`docs/HERO-VERIFY.md`).
- [x] **9.3** **Seizure / vestibular** — **Code comment** on node pulse (smooth ramps, localized glow; no full-canvas flash) — formal audit still manual.
- [ ] **9.4** **Cross-browser** — Safari, Firefox, Chrome (desktop + iOS).
- [x] **9.5** **Regression checklist** — **`docs/HERO-VERIFY.md`** (Phase 0 verify + hero-specific checks).

**Exit:** Sign-off from a short a11y pass.

---

## Phase 10 — Fallback & resilience

**Goal:** Zero-asset promise with real-world failure modes.

- [x] **10.1** **Canvas failure** — **`getContext` null** → show **`#terrain-fallback`**; **`try/catch`** around draw path → **`console.warn`** + fallback + hide canvas.
- [x] **10.2** **CSP** — Documented in **`README.md`** (inline `style` on landing, `script-src` for external `hero-terrain.js`, proxy configuration).
- [x] **10.3** **Caching** — **`README.md`** + existing **`?v=`** on script tag; bump on each terrain ship.

**Exit:** Degraded mode still on-brand.

---

## Phase 11 — Documentation & handoff

- [x] **11.1** Update **`README.md`** “Brand / landing” (hero) context with link to this roadmap (**screenshot** still **0.3** / optional moodboard).
- [x] **11.2** Add **`README.md`** subsection “Hero terrain” with perf knobs (constants table at top of `hero-terrain.js`).
- [ ] **11.3** Optional: **Loom** or GIF in `docs/` for motion review (no autoplay on landing).

---

## Suggested session order (dependency-aware)

1. **Phase 0** (definition)  
2. **Phase 1** (layout — unlocks blend + vignette spec)  
3. **Phase 2** + **Phase 4** (readability: ground + hub)  
4. **Phase 3** + **Phase 5** (entities + streams)  
5. **Phase 6** (polish pass)  
6. **Phase 8** (perf after visuals stable)  
7. **Phase 7** (Houdini optional / last)  
8. **Phase 9–11**

---

## Quick wins (if you need momentum before Phase 1)

- [x] **QW.1** Increase grid **base alpha** slightly + ensure **two line families** read on OLED.
- [x] **QW.2** Bump **district** fill to max **0.03–0.04** if still invisible.
- [x] **QW.3** Add **subtle noise** overlay (canvas or CSS) for “film grain” terminal feel.
- [x] **QW.4** Tune **glass-vignette-layer** gradient stops to match spec language (“70% center clear → edge dark”).

---

## Session log

| Date | Work |
|------|------|
| 2026-04-11 | **Phase 0** (0.1, 0.2, 0.4) + **Phase 1** (1.1–1.3, 1.6): full-bleed terrain, `.hero-matte`, hub anchor `0.725W` / mobile stack, pointer on `#hero-section`, `hero-terrain.js?v=20260411v3`. |
| 2026-04-11 | **Phase 2** complete: 30° axonometric grid + `gridEdgeFade`, breathing band, 9 districts @ 0.028, parallax `*0.09`, scan pulse α 0.12, `?v=20260411v4`. |
| 2026-04-11 | **Phase 1.4–1.5**, **QW.3–4**, **3.3**, **4.2**, **5.3**, **6.2**: nav/hero instrument glass, grain + vignette, node smoothing 0.05, elastic hub entrance, particle density + POOL 260, `?v=20260411v5`. |
| 2026-04-11 | **Phase 3** (complete), **4** (complete), **5.1–5.2**, **5.4–5.5**, **6.1**: node stack + status + repulsion 1/d, hub heartbeat 3s + port micro-beads, tether wave on `elapsed`, speeds 40–80, `?v=20260411v6`. |
| 2026-04-11 | **5.6**, **6.3–6.5**, **8.1**: Path2D tether strokes, fbm drift, sync ripple tuning + constants, DPR comment, `?v=20260411v7`. |
| 2026-04-11 | **7.1**, **7.3**, **8.2–8.6**, **9.1**, **9.3**, **10.1**, **11.1–11.2**, **QW.1–2**: `@property` mouse vars, EWMA cheap shadows, IO+RM live toggle, a11y fleet blurb, canvas try/catch fallback, README hero section, grid/district OLED bump, `?v=20260411v8`. |
| 2026-04-11 | **9.2**, **9.5**, **10.2–10.3**, **0.3** (naming doc): hero copy contrast tokens + HC modes, `docs/HERO-VERIFY.md`, README CSP/cache, `docs/assets/README.md`. |

---

*Last updated: 2026-04-11 — adjust dates/checkboxes as you ship.*
