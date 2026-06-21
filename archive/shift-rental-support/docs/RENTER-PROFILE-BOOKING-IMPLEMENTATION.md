# Renter — Profile & Booking Management

**Implementation tracker** for the renter “command center”: identity hub, active trip hero, history stream, and contextual support.  
Check `[ ]` → `[x]` as you ship. Append the **Session log** after each work block so the next session can resume without re-reading the whole prompt.

**Source:** “RENTER: Profile & Booking Management” implementation prompt (objective, components, data model, APIs, flows, security).

---

## Canonical artifacts

| Artifact | Role |
|----------|------|
| **[`RENTER-PROFILE-BOOKING-IMPLEMENTATION.md`](./RENTER-PROFILE-BOOKING-IMPLEMENTATION.md)** (this file) | Phased delivery, checklists, schema/API mapping, verification, session handoff |
| **Product spec (verbatim detail)** | Embedded in sections A–D below + **Target interfaces** |
| **Existing chat support** | `public/support.html` + `server.js` support/chat paths — integration point for contextual wrapper |

---

## Current state (snapshot) — update when things change

| Item | Status |
|------|--------|
| Renter entry | `public/renter-login.html` → `public/renter.html` (stub auth, demo `sessionStorage`) |
| UI depth | **Placeholder tiles only** — no profile hero, no active trip, no history list |
| Backend | **SQLite** `vehicles`, `rentals`, `support_logs` — **no** `users`, `bookings`, `reviews`, renter auth |
| Framework | **Static HTML** demo; prompt targets **React web + React Native** — see **Stack fork** |

### Stack fork (decide in Phase 0)

| Path | When to choose |
|------|----------------|
| **A — Incremental HTML/CSS/JS** | Fastest demo continuity; reuse SHIFT tokens from `index.html` / `renter.html` |
| **B — React (web) + shared types** | When component count and state justify it; can live under e.g. `apps/renter-web/` and build to `public/renter/` |
| **C — React Native** | Out of this repo until a mobile app repo exists; track as **phase “Mobile parity”** |

**This doc tracks features regardless of path**; implementation tasks note **HTML** vs **React** where it matters.

---

## Schema mapping (prompt → repo reality)

The prompt assumes `users`, `bookings`, `reviews`, lat/lng, vehicle photos. **Today’s seed schema** (`seed-database.js`):

| Prompt concept | Current SQLite | Gap / migration notes |
|----------------|----------------|------------------------|
| `users` / `renter_id` | *None* | Add `renters` or `users` + `renter_id` on `rentals`, or demo with **single renter** keyed by `email` until auth exists |
| `bookings` | `rentals` | Treat `rentals` as bookings; map statuses: `Confirmed`/`Active`/`Completed`/`Cancelled` |
| `start_time` / `end_time` | `pickup_date`, `dropoff_date` (TEXT) | Parse as ISO or normalized DATETIME for countdowns |
| `vehicle.photos[0]` | No `photo_url` on `vehicles` | Add column or use placeholder + lazy-load URL later |
| `pickup_lat` / `pickup_lng` | *None* | Add columns or separate `locations` table for maps + geofence |
| `rating_given` / reviews | *None* | Add `reviews` table or defer to Phase N |
| Tier / miles / avatar | *None* | `renter_profile` table or JSON column; or **mock** in API until modeled |

**Suggested v1 view (conceptual)** — adapt table/column names when you add `renters`:

```sql
-- Target shape after minimal migration (not runnable until renter_id exists)
CREATE VIEW IF NOT EXISTS renter_dashboard AS
SELECT
  r.email AS renter_key,
  COUNT(rt.id) AS total_trips,
  (
    SELECT json_object(
      'booking_id', a.booking_id,
      'vehicle_make', v.make,
      'vehicle_model', v.model,
      'pickup_date', a.pickup_date,
      'dropoff_date', a.dropoff_date,
      'status', a.status,
      'pickup_location', a.pickup_location
    )
    FROM rentals a
    JOIN vehicles v ON v.vehicle_id = a.vehicle_id
    WHERE a.email = r.email
      AND a.status IN ('Confirmed', 'Active')
    ORDER BY a.pickup_date ASC
    LIMIT 1
  ) AS active_booking_json
FROM (SELECT DISTINCT email FROM rentals) r
LEFT JOIN rentals rt ON rt.email = r.email
GROUP BY r.email;
```

Paginated history (prompt-style), adapted:

```sql
SELECT r.booking_id, r.pickup_date, r.dropoff_date, r.total_cost, r.status,
       v.make, v.model, v.vehicle_id,
       r.pickup_location, r.dropoff_location
FROM rentals r
JOIN vehicles v ON v.vehicle_id = r.vehicle_id
WHERE r.email = ?
ORDER BY r.pickup_date DESC
LIMIT ? OFFSET ?;
```

---

## Target TypeScript interfaces (shared spec)

Use these in a future `packages/renter-types` or inline in React; for HTML demo, treat as **JSON contract** for API responses.

### A — `RenterIdentity`

```ts
interface RenterIdentity {
  id: string;
  name: string;
  avatarUrl: string | null;
  initials: string;
  memberSince: string; // ISO date
  tier: {
    label: 'Silver Driver' | 'Gold Member' | string;
    nextTierLabel: string | null;
    progress: number; // 0..1 toward next tier
  };
  stats: {
    tripsCompleted: number;
    totalMiles: number;
    ratingGivenAvg: number | null;
    ratingReceivedAvg: number | null;
  };
  verification: {
    email: boolean;
    phone: boolean;
    driversLicense: boolean;
    insuranceOnFile: boolean;
  };
  coverGradientSeed: string; // hash for deterministic CSS gradient
}
```

### B — `ActiveTripCard`

```ts
interface ActiveTripCard {
  bookingId: string;
  status: 'Confirmed' | 'Active' | string;
  phase: 'confirmed' | 'pre_trip_inspection' | 'active' | 'post_trip_inspection' | 'completed';
  vehicle: {
    make: string;
    model: string;
    year?: number;
    photoUrl: string | null;
    category?: string;
  };
  pickup: { label: string; lat: number | null; lng: number | null; at: string };
  dropoff: { label: string; at: string };
  countdown: {
    target: string; // ISO
    label: 'pickup' | 'return';
  };
  actions: {
    unlockAvailable: boolean;
    mapsUrl: string | null;
    contactOwnerChatContext: BookingContext | null;
  };
  documents: Array<{ id: string; label: string; type: 'contract' | 'insurance' | 'inspection' }>;
}

interface BookingContext {
  id: string;
  vehicleModel: string;
  pickupAt: string;
  status: string;
}
```

### C — `TripHistory`

```ts
type HistoryFilter = 'all' | 'completed' | 'cancelled' | 'disputed';

interface TripHistoryItem {
  bookingId: string;
  startTime: string;
  endTime: string;
  totalCost: number;
  status: string;
  vehicleThumbUrl: string | null;
  make: string;
  model: string;
  pickupLocation: string;
  receiptUrl?: string; // PDF endpoint
  rebookQuery?: { category?: string; location?: string };
}

interface TripHistoryPage {
  items: TripHistoryItem[];
  page: number;
  total: number;
  filter: HistoryFilter;
}
```

### D — `EmbeddedSupport`

```ts
type IssueCategory = 'pre_trip' | 'active_trip' | 'post_trip' | 'general';

interface SupportChatInit {
  bookingId?: string;
  vehicleModel?: string;
  urgency?: 'low' | 'medium' | 'high';
  issueCategory?: IssueCategory;
  prefilledMessage?: string;
}

declare function openSupportChat(context?: SupportChatInit): void;
```

---

## API contract (Express) — align with `server.js`

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/renter/profile` | Aggregated dashboard: identity + stats + active booking summary |
| `GET` | `/api/v1/renter/bookings?status=&page=&limit=` | Paginated history + filters |
| `POST` | `/api/v1/bookings/:id/extend` | Extension request + pricing (stub OK) |
| `GET` | `/api/v1/bookings/:id/receipt.pdf` | PDF receipt (stub: HTML or static PDF first) |
| `PUT` | `/api/v1/renter/profile` | Avatar URL, preferences (stub OK) |

**Demo auth (until real JWT/session):** e.g. `?email=` query or header `X-Demo-Renter-Email` — **document chosen approach in Session log** and replace later.

---

## UX flows (acceptance anchors)

### Flow A — Pre-trip (~24h before)

- [ ] Surface countdown + “View check-in instructions” (modal; owner notes — map from `rentals.notes` or new column)
- [ ] “I’m here” → stub SMS/owner ping or server log + optimistic UI
- [ ] Push: deferred until OneSignal/Firebase (track under **Mobile / notifications**)

### Flow B — Active trip

- [ ] Persistent “trip active” indicator + time remaining (from `dropoff_date`)
- [ ] Vehicle controls (horn/lights/lock): **spec only** unless integration exists — mark as mock
- [ ] Extend: sheet/modal with prorated quote + confirm (wire to `POST .../extend` when ready)

### Flow C — Post-trip return

- [ ] Guided photo upload (4 angles) — camera API + storage TBD
- [ ] Fuel/charge confirmation slider
- [ ] Receipt: immediate download + “email copy” (stub)
- [ ] Review: stars + tags → needs `reviews` table or local-only demo

---

## Security & privacy (backlog checklist)

- [ ] **Retention:** policy text + future job to anonymize >3y
- [ ] **Location:** reveal precise coords only inside policy window (needs lat/lng + server rule)
- [ ] **GDPR export:** `GET /api/v1/renter/export` → ZIP (trips, chats, receipts) — late phase
- [ ] **PII minimization** on history cards (mask phone/email in list views)

---

## Phase 0 — Spec lock & data model v1

**Goal:** Runnable slices without blocking on React Native.

- [ ] **0.1** Confirm stack path (HTML vs React web) and update **Primary files** table below
- [ ] **0.2** **Renter identity key for demo:** e.g. logged-in email from stub login → pass to API (may require extending `renter-login.html` / `sessionStorage`)
- [ ] **0.3** **Schema decision:** minimal columns on `rentals` + optional `renter_profiles` **or** mock profile JSON from server until DB ready
- [ ] **0.4** **Status model** for trip progress bar: map `rentals.status` + synthetic phases vs new `trip_phase` column
- [ ] **0.5** Document **geofence / unlock** as stubbed boolean from server until real GPS

**Exit:** Session log entry + first `GET /api/v1/renter/profile` returning **mock or real** JSON consumed by `renter.html`.

---

## Phase 1 — Layout shell (mobile-first, desktop 3-column)

**Goal:** Structure matches prompt before deep data.

- [ ] **1.1** **Mobile:** single column, card stack; bottom sheet component pattern for actions (CSS + minimal JS)
- [ ] **1.2** **Desktop (≥1024px):** 3 columns — **Profile sidebar | Active trip hero | History stream**
- [ ] **1.3** Breakpoints documented: 360, 768, 1024, 1280
- [ ] **1.4** Sticky behavior: identity header or trip hero **or** documented alternative
- [ ] **1.5** `prefers-reduced-motion` respected for countdown tick animations

**Exit:** Responsive shell with placeholder content in each region.

---

## Phase 2 — A. Identity header (`RenterIdentity`)

- [ ] **2.1** Cover: deterministic **amber/cyan** gradient from `coverGradientSeed` (hash of renter id/email)
- [ ] **2.2** Avatar: default **initials** in amber circle; upload → `PUT profile` + storage **or** deferred with file input stub
- [ ] **2.3** Tier badge + **progress** to next tier (mock data OK)
- [ ] **2.4** Stats row: trips | miles | ratings (from API or placeholders)
- [ ] **2.5** Verification row: 4 green checks — wire to real flags when columns exist

**Exit:** `GET /api/v1/renter/profile` drives header with **no** hardcoded name when possible.

---

## Phase 3 — B. Active booking hero (`ActiveTripCard`)

- [ ] **3.1** Large vehicle visual: image + gradient overlay; **blurhash/lazy** when using real URLs
- [ ] **3.2** **Countdown** to pickup or return (large type; **amber** if &lt;1h to pickup)
- [ ] **3.3** **Quick actions:** Primary “Unlock” (disabled + tooltip until geofence+window); Secondary maps deep link (Google/Apple) from `pickup_location` string or lat/lng
- [ ] **3.4** **Contact / support:** opens existing support surface with `booking_id` + vehicle in context (`openSupportChat` behavior)
- [ ] **3.5** **Trip progress bar:** 5 states; current = amber, future = dim
- [ ] **3.6** **Documents row:** Contract / Insurance / Inspection — links stubbed or static assets until generation exists

**Exit:** One real `Active` or `Confirmed` rental from DB renders end-to-end on hero.

---

## Phase 4 — C. Booking history stream (`TripHistory`)

- [ ] **4.1** Horizontal card: **80px thumb** | details | receipt action
- [ ] **4.2** Tabs: All | Completed | Cancelled | Disputed (disputed may be empty until modeled)
- [ ] **4.3** Search/filter: date range, model, location (client-side first OK)
- [ ] **4.4** Receipt: `GET .../receipt.pdf` or interim **print-friendly HTML**
- [ ] **4.5** **Book again** CTA: pre-fill query params to a future booking flow (or placeholder URL)
- [ ] **4.6** **Empty state:** illustration + CTA to fleet/marketing browse

**Exit:** `GET /api/v1/renter/bookings` populates list with pagination.

---

## Phase 5 — D. Support integration (`EmbeddedSupport`)

- [ ] **5.1** Floating **amber** bubble, bottom-right, 40px inset (match SHIFT tokens)
- [ ] **5.2** Open support UI with **metadata**: `booking_id`, vehicle, urgency heuristic from `pickup_date`
- [ ] **5.3** Optional **auto message** to agent channel (or visible pre-fill in composer only — product choice)
- [ ] **5.4** Header quick actions: **Emergency** (tel: link), **Report damage** (stub workflow), **Extend** (opens extend sheet)
- [ ] **5.5** Chat history persistence + search: **phase later** if current chat is session-only

**Exit:** From active trip, one tap opens support with **booking context** visible to the user.

---

## Phase 6 — Polish & cross-cutting

- [ ] **6.1** React Query + optimistic updates (only if on React) — e.g. favorite trip
- [ ] **6.2** Static map thumbnails for history (Mapbox Static or placeholder)
- [ ] **6.3** Interactive map on active trip (Mapbox/MapKit JS — key management)
- [ ] **6.4** A11y: landmarks, live region for countdown, focus trap in sheets
- [ ] **6.5** i18n hooks (if product requires)

---

## Phase 7 — Mobile app parity (deferred)

- [ ] React Native shell + shared types with web
- [ ] Push notifications (OneSignal/Firebase)
- [ ] Face ID / biometric confirm for extend payment

---

## Primary files (maintain as repo evolves)

| Area | Current | Target (example) |
|------|---------|------------------|
| Renter hub | `public/renter.html` | Same file OR `public/renter/index.html` SPA |
| Login stub | `public/renter-login.html` | Real auth callback |
| API | `server.js` | Modular `routes/renter.js` |
| Types | — | `src/types/renter.ts` or shared package |

---

## Verification checklist (run after each meaningful change)

- [ ] `node server.js` — renter pages load (`/renter.html`, `/renter-login.html`)
- [ ] Mobile width **360px**: single column, no horizontal scroll
- [ ] Desktop **1280px**: 3-column layout per spec
- [ ] Active trip: countdown uses correct timezone handling (document assumption: **local** vs **UTC**)
- [ ] Support bubble does not obscure primary CTAs (safe-area / `padding-bottom` on main)
- [ ] Keyboard: focus order profile → hero → history → FAB
- [ ] `prefers-reduced-motion`: no flashing countdown animations

---

## Session log

_Add a new block per work session (newest on top)._

### Template

```
#### YYYY-MM-DD — <short title>
- **Stack path:** HTML | React | other
- **Phase / tasks:** e.g. 2.1–2.3
- **Done:** …
- **Next:** …
- **Blockers:** …
- **How to verify:** …
```

#### 2026-04-13 — Fix: API must not return HTML (JSON parse error)

- **Stack path:** HTML + Express
- **Root cause:** `express.static` ran **before** `/api/v1/*` handlers. Unmatched paths hit `app.get('*')` → `index.html` → `response.json()` threw `Unexpected token '<'`. Same symptom if an **old** `node server.js` is still bound to the port (no renter routes yet).
- **Done:** Register **all API routes before** `express.static`; unknown `GET /api/...` → **404 JSON** (never SPA HTML). `renter.html` uses `fetchJson()` and detects HTML bodies with a clear error string.
- **Verify:** Restart server after pull; `curl -s http://localhost:3000/api/v1/renter/profile | head -c1` should be `{` not `<`.

#### 2026-04-13 — Renter APIs + dashboard shell (Phase 0 exit + Phase 1)

- **Stack path:** HTML + Express + SQLite (incremental)
- **Phase / tasks:** Phase 0 (profile + bookings API), Phase 1 (mobile stack + desktop 3-col), partial Phase 3/4/5 UI stubs
- **Done:**
  - `GET /api/v1/renter/profile` — identity, tier mock, stats from `rentals` by `email`; `active_booking` with trip progress steps
  - `GET /api/v1/renter/bookings` — paginated + filters `all|completed|cancelled|disputed`
  - Stubs: `POST .../extend`, `GET .../receipt.pdf`, `PUT .../renter/profile` → 501 JSON
  - `renter-login.html` stores `shift_renter_email` (defaults seed email if field empty)
  - `renter.html` — identity card (gradient cover), active trip hero (countdown, maps, disabled unlock, progress bar, doc placeholders), history stream (tabs + search), FAB → `support.html?booking=`
  - `support.html` — `?booking=RNT-XXXX` pre-sends lookup message after load
- **Next:** Real vehicle images / photo_url column; receipt PDF; geofence unlock; bottom sheets; wire verification flags in UI; React migration decision (Phase 0.3)
- **Blockers:** None
- **How to verify:** `node server.js` → `renter-login.html` → Continue → hub loads; try email `m.thompson@melbournelaw.com.au`; narrow & wide viewport; FAB opens support with booking context

#### 2026-04-13 — Receipts v1 (print-friendly HTML)

- **Stack path:** Express + HTML (no PDF yet)
- **Phase / tasks:** Phase 4.4 (Receipt download) — implemented as HTML-first
- **Done:**
  - `GET /api/v1/bookings/:id/receipt` returns a **print-ready receipt** (charges breakdown + trip + payment status)
  - `GET /api/v1/bookings/:id/receipt.pdf` now **302 redirects** to `/receipt` (until real PDF exists)
  - History “Receipt” button now opens receipt in a new tab (no alert)
- **Next:** Real PDF generation + email copy; add receipt link into Active Trip documents row
- **How to verify:** Open renter hub → History → click **Receipt**; or visit `/api/v1/bookings/RNT-1005/receipt`

---

## Progress summary (optional quick %)

| Phase | Weight (suggested) | Status |
|-------|------------------|--------|
| 0 Spec + data | 15% | In progress (APIs + email key live) |
| 1 Layout shell | 15% | In progress (3-col + stack done) |
| 2 Identity | 15% | In progress (header live; avatar upload later) |
| 3 Active trip | 20% | In progress (hero + countdown; unlock/PDF stub) |
| 4 History | 15% | In progress (list + tabs + search; PDF stub) |
| 5 Support | 10% | In progress (FAB + booking query param) |
| 6 Polish | 10% | Not started |

_Update the **Status** column as you go (e.g. Not started / In progress / Done)._
