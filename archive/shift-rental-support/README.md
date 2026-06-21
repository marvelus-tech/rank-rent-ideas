# SHIFT Rental Support

Workspace app: fleet support chat + marketing landing under **`~/.openclaw/workspace/shift-rental-support`**. Default HTTP port **3000** (`PORT` env overrides).

```bash
cd ~/.openclaw/workspace/shift-rental-support
npm install && node server.js
# Landing http://localhost:3000/  ·  Chat http://localhost:3000/support
```

Public demo helpers: **`DEMO-ACCESS.md`** (`./start-with-cloudflare.sh` / `./start-with-ngrok.sh` — both assume port **3000**).

## Data & API

- **SQLite** — `shift-rental.db` (seed via `npm run seed` / `seed-database.js`). Swap data by editing the seed file or replacing `db.query` usage in `server.js` for a real database.
- **Chatbot lookups** — booking id (`RNT-…`), email, phone, partial name + vehicle; extension/billing requests log to `support.log`.

## Hero terrain (`public/hero-terrain.js`)

Canvas-driven hero on the landing page. Tune behavior via constants in the script (see top comment block), including:

- **Entrance** — `T_GRID`, `T_HUB`, `T_NODES`, `T_TETHERS`, `T_PARTICLES`
- **Particles** — `POOL`, per-stream counts in `assignParticles`, `particleCapScale` when battery-saver path runs
- **Motion** — `hubOmega`, `SYNC_RIPPLE_INTERVAL_SEC`, `SYNC_RIPPLE_STAGGER_MS`
- **CSS bridge** — `PARALLAX_THROTTLE_MS` (~10 Hz) driving `--mouse-x` / `--mouse-y` on `#hero-terrain-host`

Full checklist: `docs/HERO-LIVE-TERRAIN-ROADMAP.md`. Regression smoke: `docs/HERO-VERIFY.md`.

## Production (Phase 10.2–10.3)

**Caching** — Bump the query string on the script tag in `public/index.html` when you ship `hero-terrain.js` changes (e.g. `hero-terrain.js?v=…`) so CDN and browsers fetch the new file.

**CSP** — `index.html` uses a large **inline** `<style>` block. If you add `Content-Security-Policy`:

- Either allow **`style-src 'unsafe-inline'`** (simplest for this landing), or move CSS to external files and allow those origins.
- Keep **`script-src`** compatible with **`public/hero-terrain.js`** (same origin or explicit host); avoid relying on inline script for the terrain if you tighten CSP.
- `connect-src` only if the page calls APIs you control.

Default `node server.js` does **not** set CSP; configure at your reverse proxy (nginx, Cloudflare, etc.).

## Copy to another machine

```bash
cp -r ~/.openclaw/workspace/shift-rental-support ~/shift-rental-backup
# on target: place under that host's ~/.openclaw/workspace/shift-rental-support (or any path), then:
cd ~/shift-rental-backup   # or the new path
npm install
```
