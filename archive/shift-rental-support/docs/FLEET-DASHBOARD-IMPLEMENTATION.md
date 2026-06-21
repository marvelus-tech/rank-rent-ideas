# Fleet Owner — Unified Command Dashboard

**Implementation tracker** for the “single pane of glass” fleet operator experience.  
Check `[ ]` → `[x]` as you ship. Use **Session log** at the bottom after each work block so the next session knows where to resume.

**Source brief:** original “FLEET OWNER: Unified Command Dashboard” implementation prompt (telemetry, maintenance queue, distribution, real-time, a11y).

### Canonical source of truth (Phase 0.1)

| Artifact | Role |
|----------|------|
| **[`FLEET-DASHBOARD-IMPLEMENTATION.md`](./FLEET-DASHBOARD-IMPLEMENTATION.md)** (this file) | Phased delivery, checklists, verification, session handoff |
| **[`FLEET-DASHBOARD-BRIEF.md`](./FLEET-DASHBOARD-BRIEF.md)** | Product intent, layout, interfaces, stack direction |
| **Figma / wireframes** | Visual spec — [_not linked yet; add URL in brief when ready_] |

---

## Current state (snapshot)

| Item | Status |
|------|--------|
| Marketing shell | `public/index.html` |
| Auth stub flow | `public/sign-in.html` → `public/fleet-dashboard.html` |
| Dashboard UI | **Phase 1–3 Kanban** — `fleet-dashboard.html` + `data/fleet/vehicles.json` + `data/fleet/maintenance.json` |
| Backend for dashboard | **Not started** (prompt targets PostgreSQL + Redis + WebSocket) |

**Strategic fork:** **Path B active** — static HTML through Phase 1 (done) and Phase 2–4 UI until complexity warrants **React + TypeScript** (Vite app, see Architecture decisions below).

---

## Primary files (update as scaffold evolves)

| Area | Path (today) | Path (target) |
|------|----------------|---------------|
| Dashboard entry | `public/fleet-dashboard.html` | Later: Vite → `public/fleet/` or separate dev port |
| API / WebSocket | — | `server.js` extensions or separate service |
| Shared design tokens | inline in HTML | shared CSS variables / theme module |
| Product brief | — | [`docs/FLEET-DASHBOARD-BRIEF.md`](./FLEET-DASHBOARD-BRIEF.md) |
| Fleet fixtures | `public/data/fleet/vehicles.json` | vehicles / telemetry-shaped mocks |
| Maintenance fixtures | `public/data/fleet/maintenance.json` | Kanban columns + work orders |
| Distribution fixtures | `public/data/fleet/distribution.json` | channels, yield, auto-pricing, seeded calendar |

---

## How to verify after each change

- [x] `node server.js` → dashboard at `http://localhost:3000/fleet-dashboard.html` (or dev URL after React migration)
- [x] **Breakpoints:** 1440px, 1024px, and mobile (sidebar collapse behavior)
- [x] **Keyboard:** Tab order logical; no keyboard traps in modals/drag surfaces _(matrix: Tab cards / checkboxes in select mode, Enter → modal, Escape closes)_
- [ ] **Screen reader smoke:** vehicle status + revenue/maintenance copy exposed (see A11y phase)
- [ ] **Reduce motion:** animations respect `prefers-reduced-motion`
- [ ] **Color-blind:** status legible via **shape/icon**, not color alone

---

## Phase 0 — Spec lock & scaffolding

**Goal:** Same as hero roadmap — avoid churn; pick stack path and “definition of done” per slice.

- [x] **0.1** Confirm **single source of truth:** this doc + [`FLEET-DASHBOARD-BRIEF.md`](./FLEET-DASHBOARD-BRIEF.md); Figma/wireframes: _TBD — see brief_
- [ ] **0.2** **Acceptance criteria (v1 dashboard):** (1) 12-col bento grid responsive at 1440 / 1024. (2) Collapsible sidebar 256px ↔ 72px. (3) Top bar shows **live connection** state (amber syncing / cyan idle — can be stubbed until WebSocket exists). (4) At least **one** vehicle card per spec state (active, maintenance, idle, offline) with correct visual + a11y label. (5) Maintenance queue shows **three columns** with placeholder or real data. (6) Distribution row: channel toggles + yield slider + stub sync indicators. (7) Drag-and-drop **or** documented interim (keyboard-first scheduling) if DnD slips.
- [x] **0.3** **Repo layout decision:** where React+TS app lives; how it builds into `public/` or separate port
- [x] **0.4** **Mock vs live data:** e.g. JSON fixtures + MSW, or SQLite extension of existing `shift-rental.db` until Postgres

### Architecture decisions (0.3 / 0.4)

| Topic | Decision |
|-------|----------|
| **Now (Phase 1–4 UI)** | Single-file **`public/fleet-dashboard.html`** + vanilla JS — no bundler, fast to iterate. |
| **React + TS (later)** | Add **Vite** app under e.g. `fleet-dashboard/` or `client-fleet/`; output to `public/fleet/` **or** dev on `:5173` with API proxy to Express. Migrate when DnD, charts, and Query layers justify it. |
| **Mock data** | **`public/data/fleet/`** JSON fixtures (add when Phase 2 starts) **plus** optional Express routes reading **`shift-rental.db`** for vehicles/rentals. Postgres + Redis per spec when Phase 5–6 land. |

**Exit (Phase 0):** 0.3 + 0.4 locked above. **0.2** stays open until full v1 (matrix + maintenance + distribution + DnD/interim note).

---

## Phase 1 — Shell: layout, grid, sidebar, top bar

**Goal:** Industrial command-center frame (bento + collapse + real-time indicator slot).

### Layout & grid

- [x] **1.1** Full-width **dashboard shell** (no marketing chrome bleed-through)
- [x] **1.2** **12-column CSS Grid** main viewport with documented `grid-template-areas` or explicit spans
- [x] **1.3** Breakpoints: **1440px** and **1024px** (reflow rules written in doc or code comments)
- [x] **1.4** **Bento** regions reserved: hero matrix **8 cols**, maintenance **4 cols**, distribution **12 cols** (bottom)

### Sidebar

- [x] **1.5** Sidebar **256px** expanded, **72px** collapsed (icons only + tooltips)
- [x] **1.6** Persist collapse preference (`localStorage` or user prefs API later)
- [x] **1.7** Mobile: overlay drawer or bottom nav — **decide and document**

### Top bar

- [x] **1.8** **WebSocket / sync status** pill: **amber** when syncing, **cyan** when idle (stubbed OK with tooltip “Simulated”)
- [x] **1.9** Fleet/owner context label (placeholder until auth)

**Exit:** Empty grid regions render correctly at all breakpoints; sidebar collapse works.

---

## Phase 2 — A. Fleet Status Matrix (hero, 8 columns)

**Goal:** `VehicleCardGrid` — cards, states, hover overlay, bulk actions.

### Card grid

- [x] **2.1** Card footprint **280×160px** (fixed bento cell or responsive scale with max)
- [x] **2.2** **Active / yielding:** 4px **amber left border**; **live revenue** tick ($/sec animation; respect `prefers-reduced-motion`)
- [x] **2.3** **Maintenance:** **cyan top border**; wrench icon **pulse** (or static + SR text if reduced motion)
- [x] **2.4** **Idle / docked:** **grayscale ~60%**; **Deploy** ghost CTA
- [x] **2.5** **Offline:** **red** status dot + **last seen** timestamp
- [x] **2.6** **Color-blind:** distinct **shapes** per status (circle / square / triangle per spec) **in addition to** color — _idle uses **ring** (hollow circle) as fourth shape_

### Hover overlay

- [x] **2.7** **Fuel/battery** progress bar (amber fill)
- [x] **2.8** **Location:** mini-map thumbnail **80×80** (Mapbox static image or placeholder tile)
- [x] **2.9** **Active booking:** renter avatar + **time remaining**

### Bulk actions

- [x] **2.10** Checkbox **selection mode** (select all / clear)
- [x] **2.11** Actions: **Batch schedule maintenance** | **Dynamic price adjust** (wire to API or toast stub)

### Interaction & a11y

- [x] **2.12** **Tab** through cards; **Enter** opens detail modal (or side panel)
- [x] **2.13** SR string pattern: *“Vehicle {name}, status {state}, …”* including revenue where relevant

**Exit:** All four states visible in dev build; hover overlay works; keyboard path documented.

---

## Phase 3 — B. Maintenance Command Center (right, 4 columns)

**Goal:** `MaintenanceQueue` — Kanban, AI badges, DnD, vendor + cost copy.

### Kanban

- [x] **3.1** Columns: **Due Soon** | **In Progress** | **Completed**
- [x] **3.2** Column counts + empty states

### AI & data display

- [ ] **3.3** **Prediction badges** (amber chip), e.g. *“Predicted brake wear in 2 weeks”*
- [ ] **3.4** **Cost forecasting** block: projected cost **vs** revenue at risk if delayed

### Drag-and-drop & scheduling

- [ ] **3.5** **@dnd-kit/core** (or equivalent): drag vehicle/work order card to **calendar slot**
- [ ] **3.6** **Keyboard** alternative: move focus + explicit “schedule to date” without pointer-only flow

### Vendor integration

- [ ] **3.7** **Vendor API** abstraction (interface + mock); document “Uber for Mechanics” pattern as integration target, not blocker for UI

**Exit:** Three columns populated (mock OK); at least one drag operation works e2e in happy path.

---

## Phase 4 — C. Multi-channel distribution (bottom, 12 columns)

**Goal:** `DistributionMatrix` — channels, sync, yield engine, unified calendar.

### Channels

- [x] **4.1** Toggles: **SHIFT Native** (locked on) | **Turo** | **Getaround** | **Kayak**
- [x] **4.2** **Inventory sync** indicators: green parity / **red** price desync alert

### Yield engine

- [x] **4.3** Slider: **Aggressive (max revenue)** ↔ **Conservative (max utilization)**
- [x] **4.4** **Auto-pricing** toggle + **confidence** score (e.g. *“93% confidence…”*)

### Calendar

- [x] **4.5** **Cross-platform** availability view (which channel holds which booking window) — _seeded table view_
- [x] **4.6** Link calendar to real booking data or seeded fixtures — _`public/data/fleet/distribution.json`_

**Exit:** All controls render; optimistic UI on toggles (see Phase 6) optional but listed below.

---

## Phase 5 — Data model & persistence

**Goal:** Align implementation with Postgres + Redis as specified (can lag UI behind mocks).

### Redis (telemetry, TTL 5m)

- [ ] **5.1** Key pattern `vehicle:{id}:telemetry` with fields: `lat`, `lng`, `fuel_level`, `odometer`, `status`, `current_booking_id`, `revenue_today`
- [ ] **5.2** TTL **5 minutes**; refresh strategy documented

### PostgreSQL

- [ ] **5.3** `maintenance_events` table (fix enum typo: use `'corrective'` not `' corrective'`)
  - Suggested enums: `type`: `preventive` | `corrective` | `inspection`
  - `status`: `scheduled` | `in_progress` | `completed` | `cancelled`
- [ ] **5.4** Migrations folder + idempotent seed for dev

### SQLite bridge (optional short-term)

- [ ] **5.5** If staying on existing DB first: mapping doc from prompt’s SQL → current schema

**Exit:** Migrations run clean; dev seed loads N vehicles + maintenance rows.

---

## Phase 6 — API & real-time

**Goal:** REST + WebSocket contracts; optimistic UI.

### REST (examples from brief)

- [ ] **6.1** `POST /api/v1/fleet/maintenance/schedule` — bulk scheduling
- [ ] **6.2** `PUT /api/v1/fleet/distribution/channels` — channel configs
- [ ] **6.3** `GET /api/v1/fleet/yield/optimization` — AI pricing recommendations (stub OK)

### WebSocket

- [ ] **6.4** `GET /api/v1/fleet/telemetry/stream` — **Socket.io** or native WS (pick one; document)
- [ ] **6.5** Room: `fleet:{owner_id}`
- [ ] **6.6** Events: `vehicle.status_update`, `booking.completed`, `maintenance.alert`

### Client state

- [ ] **6.7** **Zustand** — UI selection, sidebar, local toggles
- [ ] **6.8** **TanStack Query** — server state, stale-while-revalidate
- [ ] **6.9** **Optimistic updates** on distribution toggles + rollback on error

**Exit:** At least one real event end-to-end (can be scripted emitter); rest stubbed with types.

---

## Phase 7 — Visual analytics & maps

- [ ] **7.1** Charts: **Tremor** or **Recharts** — dark mode, **amber/cyan** series
- [ ] **7.2** **Mapbox GL JS** — dark style; vehicle markers **pulsing amber** (respect reduced motion)
- [ ] **7.3** Map token handling (env, never commit secrets)

**Exit:** One chart + map integrated into dashboard (even if data is mock).

---

## Phase 8 — Accessibility & QA hardening

- [ ] **8.1** Audit: focus order, landmarks (`main`, `nav`, `aside`)
- [ ] **8.2** Live region for **connection status** changes
- [ ] **8.3** DnD: keyboard + SR instructions
- [ ] **8.4** Contrast check on amber/cyan on `#000` / `#141414` backgrounds (WCAG targets)

**Exit:** Short a11y checklist signed off for v1.

---

## Dependencies & risks (living list)

| Risk | Mitigation |
|------|------------|
| Mapbox / API costs | Static map thumbnails first; feature-flag GL |
| DnD + keyboard complexity | Phase 3.6 non-negotiable for v1 if DnD ships |
| Postgres vs current SQLite | Phase 5.5 bridge or parallel `docker-compose` for Postgres+Redis |
| WebSocket auth | Defer until real sign-in; use `owner_id` from session |

---

## Session log (append only)

_Template — copy a block per session._

```
### YYYY-MM-DD — Session title
- **Worked on:** (phases / IDs, e.g. 1.5–1.8)
- **Shipped:** (PR/commit/sha if any)
- **Blocked by:** 
- **Next session starts at:** (first unchecked item)
- **Notes:** 
```

---

### 2026-04-13 — Tracker created
- **Worked on:** Documentation only; `fleet-dashboard.html` remains skeleton.
- **Shipped:** `docs/FLEET-DASHBOARD-IMPLEMENTATION.md`
- **Blocked by:** None
- **Next session starts at:** Phase **0.2** (acceptance criteria) + **0.3** (React scaffold location)
- **Notes:** Prompt’s SQL had a typo in `' corrective'` — corrected to `'corrective'` in Phase 5.3.

### 2026-04-13 — Phase 0.1 canonical sources
- **Worked on:** **0.1** single source of truth
- **Shipped:** [`docs/FLEET-DASHBOARD-BRIEF.md`](./FLEET-DASHBOARD-BRIEF.md); tracker updated with **Canonical source of truth** table + Primary files row
- **Blocked by:** None
- **Next session starts at:** **0.2** (lock v1 acceptance criteria) or **0.3 + 0.4** then **Phase 1** shell in `fleet-dashboard.html`
- **Notes:** Figma explicitly deferred; add link in brief when a file exists.

### 2026-04-13 — Phase 3.1–3.2 maintenance Kanban
- **Worked on:** **3.1–3.2** — three columns, counts, empty state (Completed column)
- **Shipped:** `public/data/fleet/maintenance.json`; `maint-kanban` UI + `fetch` in `fleet-dashboard.html`
- **Next session starts at:** **3.3–3.4** (AI chips + cost vs revenue-at-risk) **or** **Phase 4** distribution row
- **Notes:** No DnD yet (**3.5**). Narrow rail: columns stack below **520px** width.

### 2026-04-13 — Phase 2 fleet matrix
- **Worked on:** **2.1–2.13** — `vehicles.json` + matrix UI in `fleet-dashboard.html`
- **Shipped:** Four states, hover overlay, `aria-label` copy, detail modal, select mode + batch stubs + `aria-live` toasts; revenue `requestAnimationFrame` (disabled when `prefers-reduced-motion`)
- **Blocked by:** None
- **Next session starts at:** **Phase 3** maintenance Kanban (3 columns) **or** **Phase 4** distribution row — recommend **3.1–3.2** next to fill right rail
- **Notes:** Load JSON via `fetch`; requires HTTP server. **0.2** still open (maintenance + distribution + DnD/interim).

### 2026-04-13 — Phase 0.3–0.4 + Phase 1 shell
- **Worked on:** **0.3**, **0.4** (architecture table); **1.1–1.9** (`public/fleet-dashboard.html`)
- **Shipped:** Collapsible sidebar `256px`↔`72px` + `localStorage`; 12-col bento (8 / 4 / 12); top bar fleet context + **sync pill** (simulated 7s idle/sync cycle, respects `prefers-reduced-motion`); **≤767px** drawer + backdrop + hamburger + Escape
- **Blocked by:** None
- **Next session starts at:** **Phase 2** (vehicle cards, four states) **or** **Phase 3** Kanban columns — recommend **2.x** first to fill matrix panel
- **Notes:** **0.2** remains unchecked until v1 feature checklist is met.
