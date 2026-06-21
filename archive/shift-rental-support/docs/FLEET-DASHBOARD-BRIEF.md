# Fleet Owner — Unified Command Dashboard (product brief)

**Canonical with:** [`FLEET-DASHBOARD-IMPLEMENTATION.md`](./FLEET-DASHBOARD-IMPLEMENTATION.md) (phases, checklists, session log).  
**Design / UX:** Figma or wireframe link — add here when available: _(none yet)_.

---

## Objective

Build the **central nervous system** for fleet operators: one pane for real-time telemetry, predictive maintenance, and multi-channel distribution—replacing spreadsheet + inbox workflows with a command-center UX.

---

## Layout (bento)

| Zone | Span | Name |
|------|------|------|
| Main hero | 8 cols | Fleet Status Matrix (`VehicleCardGrid`) |
| Right rail | 4 cols | Maintenance Command Center (`MaintenanceQueue`) |
| Bottom | 12 cols | Multi-Channel Distribution (`DistributionMatrix`) |

- **Shell:** Full-width dashboard; sidebar **256px** ↔ **72px** collapsed.
- **Grid:** 12-column CSS Grid; breakpoints **1440px** and **1024px**.
- **Top bar:** Real-time layer indicator — **amber** syncing, **cyan** idle.

---

## Interfaces (summary)

### VehicleCardGrid

- Cards **280×160px**; states: **active/yielding**, **maintenance**, **idle/docked**, **offline**.
- Hover overlay: fuel/battery bar, **80×80** map thumb, booking (avatar + time left).
- Bulk: selection mode → batch maintenance / dynamic pricing.

### MaintenanceQueue

- Kanban: **Due Soon** | **In Progress** | **Completed**.
- AI prediction chips; drag to calendar; vendor integration pattern; cost vs revenue-at-risk.

### DistributionMatrix

- Channels: SHIFT (always on), Turo, Getaround, Kayak; sync parity indicators.
- Yield slider (aggressive ↔ conservative); auto-pricing + confidence; unified availability calendar.

---

## Implementation path (short term)

Static shell and next UI slices ship in **`public/fleet-dashboard.html`**; React/Vite is deferred until Kanban + DnD + data hooks need it. See **[`FLEET-DASHBOARD-IMPLEMENTATION.md`](./FLEET-DASHBOARD-IMPLEMENTATION.md)** → *Architecture decisions*.

## Technical direction (target stack)

- **Frontend:** React, TypeScript, Zustand, TanStack Query, Tremor or Recharts, Mapbox GL, `@dnd-kit/core`.
- **Data:** PostgreSQL (maintenance, etc.), Redis (telemetry TTL ~5m), WebSocket room `fleet:{owner_id}`.
- **Events:** `vehicle.status_update`, `booking.completed`, `maintenance.alert`.

---

## Accessibility (non-negotiable for v1)

Keyboard through cards; meaningful screen-reader labels; status encoded with **shape + color** (color-blind safe).
