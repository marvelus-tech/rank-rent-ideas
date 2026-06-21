require('dotenv').config();
const path = require('path');
const fs = require('fs');
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { seedDatabase } = require('./seed-database');

const app = express();
const PORT = process.env.PORT || 3000;
const publicDir = path.join(__dirname, 'public');
const DB_PATH = path.join(__dirname, 'shift-rental.db');
const SUPPORT_LOG_PATH = path.join(__dirname, 'support.log');

const db = new sqlite3.Database(DB_PATH);

const query = (sql, params = []) =>
  new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
  });

const run = (sql, params = []) =>
  new Promise((resolve, reject) => {
    db.run(sql, params, function onRun(err) {
      if (err) reject(err);
      else resolve(this);
    });
  });

function appendSupportLog(entry) {
  const line = `[${new Date().toISOString()}] ${entry}\n`;
  fs.appendFileSync(SUPPORT_LOG_PATH, line);
}

function normalizePhone(input) {
  return (input || '').replace(/\D/g, '').slice(-10);
}

function detectIntent(message) {
  const text = message.toLowerCase();
  if (/extend|extension|add day|more day|longer/.test(text)) return 'extension';
  if (/bill|charge|invoice|payment|refund|receipt|cost/.test(text)) return 'billing';
  if (/fleet|vehicle|car options|available cars|categories/.test(text)) return 'fleet';
  if (/location|pickup|dropoff|branch|office|where/.test(text)) return 'locations';
  if (/help|assist|support|what can you do/.test(text)) return 'help';
  if (/booking|reservation|rnt-|@|\(\d{3}\)|\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|my\s+(car|rental)/.test(text)) return 'booking_lookup';
  return 'help';
}

function extractLookupTerms(message) {
  const bookingId = message.match(/RNT-\d{4}/i)?.[0]?.toUpperCase();
  const email = message.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i)?.[0]?.toLowerCase();
  const phoneRaw = message.match(/(?:\+1\s?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}/)?.[0];
  const phone = phoneRaw ? normalizePhone(phoneRaw) : null;

  let name = null;
  const cleaned = message
    .replace(/RNT-\d{4}/gi, '')
    .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, '')
    .replace(/(?:\+1\s?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}/g, '')
    .replace(/\b(booking|reservation|my|for|active|rental|rentals|what's|whats|lookup|please)\b/gi, '')
    .trim();

  if (cleaned.length >= 3) name = cleaned;

  return { bookingId, email, phone, name };
}

const RENTAL_SELECT = `SELECT r.*, v.make, v.model, v.category, v.year, v.vin, v.license_plate, v.daily_rate
       FROM rentals r
       JOIN vehicles v ON v.vehicle_id = r.vehicle_id`;

async function lookupRentals(message) {
  const { bookingId, email, phone, name } = extractLookupTerms(message);

  if (bookingId) {
    return query(`${RENTAL_SELECT} WHERE r.booking_id = ? LIMIT 1`, [bookingId]);
  }

  if (email) {
    return query(
      `${RENTAL_SELECT} WHERE lower(r.email) = ? ORDER BY r.created_at DESC LIMIT 3`,
      [email]
    );
  }

  if (phone) {
    return query(
      `${RENTAL_SELECT}
       WHERE REPLACE(REPLACE(REPLACE(REPLACE(r.phone, '(', ''), ')', ''), '-', ''), ' ', '') LIKE ?
       ORDER BY r.created_at DESC
       LIMIT 3`,
      [`%${phone}`]
    );
  }

  if (name) {
    return query(
      `${RENTAL_SELECT}
       WHERE lower(r.customer_name) LIKE lower(?) OR lower(v.make || ' ' || v.model) LIKE lower(?)
       ORDER BY CASE r.status WHEN 'Active' THEN 1 WHEN 'Confirmed' THEN 2 ELSE 3 END, r.created_at DESC
       LIMIT 5`,
      [`%${name}%`, `%${name}%`]
    );
  }

  return [];
}

const STATUS_EMOJI = {
  Active: '🟢',
  Confirmed: '🟡',
  Completed: '✅',
  Cancelled: '❌'
};

function rentalTotalDays(startDate, endDate) {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
  return Number.isFinite(days) && days > 0 ? days : 1;
}

function rowToRental(row) {
  return {
    booking_id: row.booking_id,
    customer_name: row.customer_name,
    email: row.email,
    car_year: row.year,
    car_make: row.make,
    car_model: row.model,
    category: row.category,
    license_plate: row.license_plate,
    vin: row.vin,
    start_date: row.pickup_date,
    end_date: row.dropoff_date,
    total_days: rentalTotalDays(row.pickup_date, row.dropoff_date),
    pickup_location: row.pickup_location,
    dropoff_location: row.dropoff_location,
    total_cost: Number(row.total_cost || 0).toFixed(2),
    daily_rate: Number(row.daily_rate || 0).toFixed(0),
    insurance_type: row.insurance_type || 'Not specified',
    payment_status: row.payment_status,
    notes: row.notes,
    status: row.status
  };
}

function formatRentalCard(rental) {
  const emoji = STATUS_EMOJI[rental.status] || '⚪';
  const isActive = rental.status === 'Active';
  const daysRemaining = isActive
    ? Math.ceil((new Date(rental.end_date) - new Date()) / (1000 * 60 * 60 * 24))
    : null;

  return `
**${emoji} Booking ${rental.booking_id}**
**${rental.customer_name}** • ${rental.email}

🚗 **${rental.car_year} ${rental.car_make} ${rental.car_model}** (${rental.category})
   Plate: \`${rental.license_plate}\` • VIN: ${rental.vin}

📅 **Rental Period:** ${rental.start_date} → ${rental.end_date} (${rental.total_days} days)
   ${isActive ? `⏰ **${daysRemaining} days remaining**` : `Status: ${rental.status}`}

📍 **Pickup:** ${rental.pickup_location}
📍 **Return:** ${rental.dropoff_location}

💰 **Total Cost:** $${rental.total_cost} AUD ($${rental.daily_rate}/day)
🛡️ **Cover:** ${rental.insurance_type} • ${rental.payment_status}
${rental.notes ? `\n📝 *${rental.notes}*` : ''}
  `.trim();
}

function sidebarBookingsFromRows(rows) {
  return rows.map((r) => ({
    booking_id: r.booking_id,
    customer_name: r.customer_name,
    email: r.email,
    status: r.status,
    make: r.make,
    model: r.model,
    category: r.category,
    pickup_date: r.pickup_date,
    dropoff_date: r.dropoff_date
  }));
}

function formatRentalResponse(rows) {
  if (!rows.length) {
    return {
      message:
        'I couldn\'t find a matching rental. Try one of these:\n- Booking ID (`RNT-1023`)\n- Email (`name@email.com`)\n- Phone (`0412 345 678`)\n- Name (`Michael`)',
      intent: 'booking_lookup',
      bookings: [],
      action: null
    };
  }

  const cards = rows.map((r) => formatRentalCard(rowToRental(r)));
  return {
    message: cards.join('\n\n---\n\n'),
    intent: 'booking_lookup',
    bookings: sidebarBookingsFromRows(rows),
    action: null
  };
}

function jsonReply(payload) {
  const { message, ...rest } = payload;
  return { ...rest, message, reply: message };
}

app.use(express.json());

// Before static + catch-all so /support always hits chat (avoids SPA fallback sending landing).
app.get(['/support', '/support/'], (req, res) => {
  res.sendFile(path.join(publicDir, 'support.html'));
});

app.get('/landing.html', (req, res) => {
  res.redirect(301, '/');
});

// API routes MUST be registered before express.static so /api/* is never mistaken for a static
// file and never falls through to the SPA catch-all (which would return HTML and break fetch().json()).

app.get('/api/health', async (req, res) => {
  try {
    const [vehicleCount] = await query('SELECT COUNT(*) AS count FROM vehicles');
    const [rentalCount] = await query('SELECT COUNT(*) AS count FROM rentals');
    res.json({
      ok: true,
      service: 'shift-rental-support',
      vehicles: vehicleCount.count,
      rentals: rentalCount.count,
      time: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message });
  }
});

app.get('/api/v1/fleet/vehicles', async (req, res) => {
  try {
    const rows = await query(
      `SELECT vehicle_id, make, model, year, category, daily_rate, mileage, fuel_type, color, status,
              vin, license_plate
       FROM vehicles
       ORDER BY status ASC, category ASC, make ASC, model ASC, year DESC`
    );

    const stateFromStatus = (status) => {
      if (status === 'Rented') return 'active';
      if (status === 'Maintenance') return 'maintenance';
      if (status === 'Available') return 'idle';
      return 'offline';
    };

    res.json({
      vehicles: rows.map((v) => ({
        id: v.vehicle_id,
        name: `${v.make} ${v.model} ${v.year}`,
        state: stateFromStatus(v.status),
        status: v.status,
        category: v.category,
        daily_rate: v.daily_rate,
        mileage: v.mileage,
        fuel_type: v.fuel_type,
        color: v.color,
        vin: v.vin,
        license_plate: v.license_plate
      }))
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

app.post('/api/chat', async (req, res) => {
  const message = (req.body?.message || '').trim();
  if (!message) return res.status(400).json({ error: 'message is required' });

  try {
    const intent = detectIntent(message);
    let payload;

    if (intent === 'booking_lookup') {
      const rows = await lookupRentals(message);
      payload = formatRentalResponse(rows);
      await run(
        'INSERT INTO support_logs (action_type, query_text, booking_id, metadata) VALUES (?, ?, ?, ?)',
        ['booking_lookup', message, rows[0]?.booking_id || null, JSON.stringify({ resultCount: rows.length })]
      );
    } else if (intent === 'extension') {
      payload = {
        intent,
        action: 'extension_requested',
        message:
          '🛠️ **Extension Request Received**\nPlease share your booking ID (`RNT-XXXX`) and desired new return date. I\'ll log this for a support specialist to confirm availability and pricing.'
      };
      await run(
        'INSERT INTO support_logs (action_type, query_text, metadata) VALUES (?, ?, ?)',
        ['extension_request', message, JSON.stringify({ priority: 'normal' })]
      );
    } else if (intent === 'billing') {
      payload = {
        intent,
        message:
          '💳 **Billing Support**\nI can help with charges, invoices, and refunds. Please provide your booking ID plus the billing concern. Example: `RNT-1023 charged twice`.'
      };
    } else if (intent === 'fleet') {
      const rows = await query(
        `SELECT category, COUNT(*) AS total,
                SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS available
         FROM vehicles
         GROUP BY category
         ORDER BY category`
      );
      payload = {
        intent,
        message:
          '🚗 **Current Fleet Snapshot**\n' +
          rows.map((r) => `- ${r.category}: ${r.available}/${r.total} available`).join('\n')
      };
    } else if (intent === 'locations') {
      payload = {
        intent,
        message:
          '📍 **SHIFT Melbourne Locations**\n- Melbourne Airport - Tullamarine\n- Melbourne CBD - Collins St\n- Melbourne CBD - Bourke St\n- South Yarra - Chapel St\n- St Kilda - Acland St\n- Richmond - Bridge Rd\n- Fitzroy - Brunswick St\n- Brunswick - Sydney Rd\n- Preston - High St\n- Box Hill - Station St\n- Chadstone - Dandenong Rd\n- Hawthorn - Glenferrie Rd\n- Geelong - Malop St\n- Frankston - Nepean Hwy\n- Essendon - Napier St\n- Docklands - Bourke St'
      };
    } else {
      payload = {
        intent: 'help',
        message:
          '🙌 **How I can help**\n- Lookup booking details\n- Request rental extension\n- Billing and payment support\n- Fleet availability by category\n- Pickup/dropoff locations\n\nTry: `What\'s my booking RNT-1023?`'
      };
    }

    appendSupportLog(`${intent.toUpperCase()} | ${message}`);
    res.json(jsonReply(payload));
  } catch (error) {
    appendSupportLog(`ERROR | ${message} | ${error.message}`);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

function renterEmailFromRequest(req) {
  const q = String(req.query.email || '')
    .trim()
    .toLowerCase();
  if (q) return q;
  const h = String(req.headers['x-demo-renter-email'] || '')
    .trim()
    .toLowerCase();
  return h || null;
}

/**
 * Demo-friendly resolution: never 404 just because the typed email has no rows.
 * If the request email is missing or unknown, use the latest rental row's email.
 * Production would return 404 or auth error instead of cross-user fallback.
 */
async function resolveRenterEmailContext(req) {
  const requested = renterEmailFromRequest(req);
  const [pick] = await query(
    `SELECT lower(trim(email)) AS e FROM rentals ORDER BY pickup_date DESC LIMIT 1`
  );
  const fallbackEmail = pick?.e ? String(pick.e).toLowerCase() : null;

  if (!fallbackEmail) {
    return {
      email: null,
      requested_email: requested || null,
      demo_fallback: false,
      empty_db: true
    };
  }

  if (!requested) {
    return {
      email: fallbackEmail,
      requested_email: null,
      demo_fallback: false,
      empty_db: false
    };
  }

  const [hit] = await query(
    `SELECT 1 AS ok FROM rentals WHERE lower(trim(email)) = ? LIMIT 1`,
    [requested]
  );

  if (hit) {
    return {
      email: requested,
      requested_email: requested,
      demo_fallback: false,
      empty_db: false
    };
  }

  return {
    email: fallbackEmail,
    requested_email: requested,
    demo_fallback: true,
    empty_db: false
  };
}

function bookingsStatusClause(statusFilter) {
  const f = String(statusFilter || 'all').toLowerCase();
  if (f === 'completed') return "AND r.status = 'Completed'";
  if (f === 'cancelled') return "AND r.status = 'Cancelled'";
  if (f === 'disputed') return 'AND 1 = 0';
  return '';
}

function tripProgressFromStatus(status) {
  const steps = [
    { id: 'confirmed', label: 'Confirmed' },
    { id: 'pre_trip', label: 'Pre-trip' },
    { id: 'active', label: 'Active' },
    { id: 'post_trip', label: 'Return' },
    { id: 'completed', label: 'Done' }
  ];
  let currentIndex = 0;
  if (status === 'Confirmed') currentIndex = 1;
  else if (status === 'Active') currentIndex = 2;
  else if (status === 'Completed') currentIndex = 4;
  else if (status === 'Cancelled') currentIndex = 0;
  return { steps, current_index: currentIndex };
}

app.get('/api/v1/renter/profile', async (req, res) => {
  try {
    const ctx = await resolveRenterEmailContext(req);
    if (!ctx.email) {
      return res.status(404).json({
        error: 'no_rentals',
        message: 'No rentals in the database yet. Run the app once to seed, or add rentals.'
      });
    }

    const rows = await query(
      `${RENTAL_SELECT} WHERE lower(r.email) = ? ORDER BY r.pickup_date DESC`,
      [ctx.email]
    );

    const customerName = rows[0].customer_name;
    const initials = customerName
      .split(/\s+/)
      .map((p) => p[0])
      .join('')
      .slice(0, 2)
      .toUpperCase();
    const totalTrips = rows.length;
    const completed = rows.filter((r) => r.status === 'Completed').length;

    const activeCandidates = rows
      .filter((r) => r.status === 'Confirmed' || r.status === 'Active')
      .sort((a, b) => String(a.pickup_date).localeCompare(String(b.pickup_date)));
    const active = activeCandidates[0] || null;

    let active_booking = null;
    if (active) {
      const progress = tripProgressFromStatus(active.status);
      active_booking = {
        booking_id: active.booking_id,
        status: active.status,
        progress,
        vehicle: {
          make: active.make,
          model: active.model,
          year: active.year,
          category: active.category,
          photo_url: null
        },
        pickup_date: active.pickup_date,
        dropoff_date: active.dropoff_date,
        pickup_location: active.pickup_location,
        dropoff_location: active.dropoff_location,
        total_cost: Number(active.total_cost || 0),
        payment_status: active.payment_status,
        actions: {
          unlock_available: false,
          maps_query: active.pickup_location
        }
      };
    }

    res.json({
      meta: {
        requested_email: ctx.requested_email,
        resolved_email: ctx.email,
        demo_fallback: ctx.demo_fallback
      },
      identity: {
        email: ctx.email,
        name: customerName,
        initials,
        cover_gradient_seed: ctx.email,
        tier: {
          label: 'Silver Driver',
          next_tier_label: 'Gold Member',
          progress: Math.min(0.95, 0.15 + completed * 0.12)
        },
        stats: {
          trips_completed: completed,
          total_trips: totalTrips,
          total_miles: null,
          rating_given_avg: null,
          rating_received_avg: null
        },
        verification: {
          email: true,
          phone: true,
          drivers_license: Boolean(active ? active.driver_license : rows[0].driver_license),
          insurance_on_file: Boolean((active || rows[0]).insurance_type)
        }
      },
      active_booking
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

app.get('/api/v1/renter/bookings', async (req, res) => {
  try {
    const ctx = await resolveRenterEmailContext(req);
    if (!ctx.email) {
      return res.status(404).json({
        error: 'no_rentals',
        message: 'No rentals in the database yet.'
      });
    }
    const { email } = ctx;
    const page = Math.max(1, parseInt(String(req.query.page || '1'), 10) || 1);
    const limit = Math.min(50, Math.max(1, parseInt(String(req.query.limit || '20'), 10) || 20));
    const offset = (page - 1) * limit;
    const statusFilter = String(req.query.status || 'all').toLowerCase();
    const extra = bookingsStatusClause(statusFilter);

    const [countRow] = await query(
      `SELECT COUNT(*) AS c FROM rentals r WHERE lower(r.email) = ? ${extra}`,
      [email]
    );
    const total = countRow ? Number(countRow.c) : 0;

    const itemRows = await query(
      `${RENTAL_SELECT} WHERE lower(r.email) = ? ${extra} ORDER BY r.pickup_date DESC LIMIT ? OFFSET ?`,
      [email, limit, offset]
    );

    const items = itemRows.map((r) => ({
      booking_id: r.booking_id,
      pickup_date: r.pickup_date,
      dropoff_date: r.dropoff_date,
      total_cost: Number(r.total_cost || 0),
      status: r.status,
      pickup_location: r.pickup_location,
      dropoff_location: r.dropoff_location,
      make: r.make,
      model: r.model,
      vehicle_id: r.vehicle_id,
      receipt_url: `/api/v1/bookings/${encodeURIComponent(r.booking_id)}/receipt.pdf`
    }));

    res.json({
      meta: {
        requested_email: ctx.requested_email,
        resolved_email: ctx.email,
        demo_fallback: ctx.demo_fallback
      },
      items,
      page,
      limit,
      total,
      filter: statusFilter
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

app.post('/api/v1/bookings/:id/extend', (req, res) => {
  res.status(501).json({ error: 'not_implemented', message: 'Trip extension API coming soon.' });
});

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function money(value) {
  const n = Number(value || 0);
  return `$${n.toFixed(2)}`;
}

app.get('/api/v1/bookings/:id/receipt', async (req, res) => {
  try {
    const bookingId = String(req.params.id || '').trim().toUpperCase();
    if (!bookingId) return res.status(400).send('Missing booking id');

    const rows = await query(`${RENTAL_SELECT} WHERE r.booking_id = ? LIMIT 1`, [bookingId]);
    if (!rows.length) return res.status(404).send('Receipt not found for that booking id.');

    const r = rows[0];
    const days = rentalTotalDays(r.pickup_date, r.dropoff_date);
    const daily = Number(r.daily_rate || 0);
    const base = daily * days;
    const total = Number(r.total_cost || base || 0);
    const taxesAndFees = Math.max(0, total - base);

    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.send(`<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SHIFT — Receipt ${escapeHtml(bookingId)}</title>
  <style>
    :root {
      --bg: #000;
      --card: #0d0d0d;
      --border: rgba(255,255,255,0.08);
      --text: rgba(255,255,255,0.92);
      --muted: rgba(255,255,255,0.55);
      --muted2: rgba(255,255,255,0.35);
      --amber: #ff9f0a;
      --cyan: #64d2ff;
      --font: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", system-ui, sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: var(--font);
      background: var(--bg);
      color: var(--text);
      -webkit-font-smoothing: antialiased;
    }
    .wrap { max-width: 920px; margin: 0 auto; padding: 28px 22px 56px; }
    .top {
      display: flex; align-items: baseline; justify-content: space-between; gap: 16px;
      margin-bottom: 18px;
    }
    .brand { font-weight: 700; letter-spacing: -0.02em; }
    .meta { color: var(--muted); font-size: 13px; }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 18px;
      overflow: hidden;
    }
    .card-head {
      padding: 18px 20px;
      display: flex; align-items: center; justify-content: space-between; gap: 16px;
      border-bottom: 1px solid var(--border);
      background:
        radial-gradient(ellipse 70% 120% at 0% 0%, rgba(255,159,10,0.14), transparent 55%),
        radial-gradient(ellipse 70% 120% at 100% 0%, rgba(100,210,255,0.10), transparent 55%);
    }
    h1 { margin: 0; font-size: 18px; letter-spacing: -0.02em; }
    .pill {
      font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
      padding: 8px 10px; border-radius: 999px;
      border: 1px solid rgba(255,159,10,0.35);
      background: rgba(255,159,10,0.08);
      color: var(--text);
      white-space: nowrap;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 16px;
      padding: 18px 20px 20px;
    }
    .box {
      grid-column: span 12;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px 14px;
      background: rgba(255,255,255,0.02);
    }
    @media (min-width: 900px) {
      .box--customer { grid-column: span 5; }
      .box--trip { grid-column: span 7; }
      .box--charges { grid-column: span 7; }
      .box--status { grid-column: span 5; }
    }
    .label { font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted2); margin-bottom: 10px; }
    .kv { display: grid; grid-template-columns: 140px 1fr; gap: 8px 12px; font-size: 13px; color: var(--muted); }
    .kv b { color: var(--text); font-weight: 600; }
    .table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .table tr + tr td { border-top: 1px solid var(--border); }
    .table td { padding: 10px 0; color: var(--muted); }
    .table td:last-child { text-align: right; color: var(--text); font-weight: 600; }
    .total { font-size: 16px; }
    .actions {
      display: flex; flex-wrap: wrap; gap: 10px;
      padding: 0 20px 18px;
      align-items: center;
    }
    a.btn {
      display: inline-flex; align-items: center; justify-content: center;
      height: 44px; padding: 0 18px;
      border-radius: 22px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.04);
      color: var(--text);
      text-decoration: none;
      font-weight: 600; font-size: 14px;
    }
    a.btn:hover { border-color: rgba(255,255,255,0.16); background: rgba(255,255,255,0.07); }
    .note { color: var(--muted2); font-size: 12px; padding: 0 20px 22px; line-height: 1.4; }
    @media print {
      body { background: #fff; color: #000; }
      .wrap { max-width: none; padding: 0; }
      .card, .box { border-color: #ddd; background: #fff; }
      .pill, .actions, .note { display: none !important; }
      .meta, .label, .kv, .table td { color: #333 !important; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="brand">SHIFT</div>
      <div class="meta">Receipt • ${escapeHtml(new Date().toISOString().slice(0, 10))}</div>
    </div>

    <div class="card">
      <div class="card-head">
        <h1>Receipt ${escapeHtml(bookingId)}</h1>
        <div class="pill">Print-ready</div>
      </div>

      <div class="grid">
        <div class="box box--customer">
          <div class="label">Customer</div>
          <div class="kv">
            <div>Name</div><b>${escapeHtml(r.customer_name)}</b>
            <div>Email</div><b>${escapeHtml(r.email)}</b>
            <div>Phone</div><b>${escapeHtml(r.phone)}</b>
          </div>
        </div>

        <div class="box box--trip">
          <div class="label">Trip</div>
          <div class="kv">
            <div>Vehicle</div><b>${escapeHtml(`${r.year} ${r.make} ${r.model}`)}</b>
            <div>Pickup</div><b>${escapeHtml(r.pickup_location)} • ${escapeHtml(r.pickup_date)}</b>
            <div>Return</div><b>${escapeHtml(r.dropoff_location)} • ${escapeHtml(r.dropoff_date)}</b>
            <div>Days</div><b>${escapeHtml(days)}</b>
          </div>
        </div>

        <div class="box box--charges">
          <div class="label">Charges</div>
          <table class="table" aria-label="Charges breakdown">
            <tr><td>Daily rate</td><td>${money(daily)} / day</td></tr>
            <tr><td>Base (${escapeHtml(days)} days)</td><td>${money(base)}</td></tr>
            <tr><td>Taxes & fees</td><td>${money(taxesAndFees)}</td></tr>
            <tr><td class="total">Total</td><td class="total">${money(total)}</td></tr>
          </table>
        </div>

        <div class="box box--status">
          <div class="label">Status</div>
          <div class="kv">
            <div>Rental</div><b>${escapeHtml(r.status)}</b>
            <div>Payment</div><b>${escapeHtml(r.payment_status)}</b>
            <div>Coverage</div><b>${escapeHtml(r.insurance_type || '—')}</b>
            <div>Plate</div><b>${escapeHtml(r.license_plate)}</b>
          </div>
        </div>
      </div>

      <div class="actions">
        <a class="btn" href="/renter.html">Back to hub</a>
        <a class="btn" href="/support.html?booking=${encodeURIComponent(bookingId)}">Open support</a>
        <a class="btn" href="#" onclick="window.print();return false;">Print</a>
      </div>
      <div class="note">PDF export is next. For now this receipt is print-friendly and can be saved as PDF from the browser print dialog.</div>
    </div>
  </div>
</body>
</html>`);
  } catch (error) {
    res.status(500).send('Receipt generation failed.');
  }
});

app.get('/api/v1/bookings/:id/receipt.pdf', (req, res) => {
  res.redirect(302, `/api/v1/bookings/${encodeURIComponent(req.params.id)}/receipt`);
});

app.put('/api/v1/renter/profile', (req, res) => {
  res.status(501).json({ error: 'not_implemented', message: 'Profile update API coming soon.' });
});

// ===== ROAST API =====
const roastPatterns = [
  {
    pattern: /\b(10x|10x your|10x my|10x our)\b/gi,
    roast: "'10x your revenue' — Every spammer says this. It's the 'Nigerian prince' of B2B.",
    fix: "Be specific about one metric you actually improve. 'Reduce no-shows by 30%' beats '10x everything' every time."
  },
  {
    pattern: /\b(guarantee|guaranteed|100%|money back|risk free)\b/gi,
    roast: "Guarantees scream desperation. Real businesses don't guarantee outcomes they don't control.",
    fix: "Replace with social proof: 'We've helped 3 Melbourne fleets increase utilization by 22%.'"
  },
  {
    pattern: /\b(quick call|15 minutes|15 min|brief call|quick chat)\b/gi,
    roast: "'Quick call' is a trap word. Everyone knows it's never quick.",
    fix: "Ask a question instead: 'What's your biggest pain point with fleet utilization right now?'"
  },
  {
    pattern: /\b(amazing|incredible|revolutionary|game.??changing|cutting.edge)\b/gi,
    roast: "Hype words trigger spam filters AND eye rolls. Two birds, one stone.",
    fix: "Use plain language. 'AI that predicts maintenance issues before they happen' > 'revolutionary AI solution'"
  },
  {
    pattern: /\b(transform|transform your|transform my|transform our)\b/gi,
    roast: "'Transform your business' — Have you met a business owner who wants to be 'transformed' by a stranger?",
    fix: "Start with their world, not yours. 'Noticed your fleet grew from 12 to 30 vehicles — how are you handling scheduling?'"
  },
  {
    pattern: /\b(I'm reaching out|I wanted to reach out|I am reaching out)\b/gi,
    roast: "'I'm reaching out' = 'I'm about to pitch you something.' They know. You know. We all know.",
    fix: "Lead with relevance: 'Saw your expansion to Geelong — congrats. How's the new location performing?'"
  },
  {
    pattern: /\b(let's|let us|we should|we can)\b/gi,
    roast: "'Let's jump on a call' assumes they want to talk to you. They don't. Yet.",
    fix: "Earn the conversation first. Share something valuable, then ask if they want to discuss."
  },
  {
    pattern: /\b(solution|platform|tool|software|product|service)\b/gi,
    roast: "Nobody wakes up wanting 'solutions.' They want problems solved.",
    fix: "Name the problem: 'Fleet sitting idle 40% of the time' > 'AI fleet management solution'"
  },
  {
    pattern: /\b(this week|tomorrow|ASAP|soon|urgent)\b/gi,
    roast: "Urgency from a stranger = pressure. Pressure = delete.",
    fix: "Remove all time pressure. Let them respond on their timeline."
  },
  {
    pattern: /\b(free|no cost|complimentary|at no charge)\b/gi,
    roast: "'Free' attracts freebie hunters, not buyers. And spam filters love flagging it.",
    fix: "If it's genuinely free, say 'pilot program' or 'beta access.' Otherwise, don't mention price."
  }
];

const spamWords = [
  'guarantee', 'guaranteed', '100%', 'money back', 'risk free',
  'free', 'no cost', 'complimentary', 'act now', 'limited time',
  'urgent', 'hurry', 'asap', 'don\'t miss', 'exclusive offer',
  'click here', 'buy now', 'order now', 'call now', 'act immediately',
  'congratulations', 'winner', 'selected', 'you won', 'prize',
  'earn extra cash', 'make money', 'work from home', 'income',
  'credit card', 'no credit check', 'loan', 'debt', 'mortgage',
  'viagra', 'weight loss', 'diet', 'pills', 'supplement'
];

function analyzeDM(text) {
  const issues = [];
  const fixes = [];
  let spamScore = 0;

  roastPatterns.forEach(({ pattern, roast, fix }) => {
    if (pattern.test(text)) {
      issues.push(roast);
      fixes.push(fix);
      spamScore += 15;
    }
  });

  const lowerText = text.toLowerCase();
  spamWords.forEach(word => {
    if (lowerText.includes(word.toLowerCase())) {
      spamScore += 10;
    }
  });

  const capsRatio = (text.match(/[A-Z]/g) || []).length / text.length;
  if (capsRatio > 0.3) {
    issues.push("SHOUTING WITH CAPS doesn't convey excitement. It conveys spam.");
    fixes.push("Use sentence case. Save emphasis for the one thing that actually matters.");
    spamScore += 20;
  }

  if (text.match(/!{2,}/)) {
    issues.push("Multiple exclamation marks!!! Look like spam!!!");
    fixes.push("One period. One exclamation mark max. Let the words do the work.");
    spamScore += 15;
  }

  if (text.length > 500) {
    issues.push("This DM is a novel. Nobody reads novels from strangers.");
    fixes.push("Cut to 2-3 sentences. 50-100 words max. Brevity is trust.");
    spamScore += 10;
  }

  if (text.match(/https?:\/\/|www\./)) {
    issues.push("Links in first DM = instant spam folder. Platforms flag this aggressively.");
    fixes.push("Remove the link. Get a reply first. Then share resources.");
    spamScore += 25;
  }

  const emojiCount = (text.match(/[\u{1F300}-\u{1F9FF}]/gu) || []).length;
  if (emojiCount > 3) {
    issues.push("Emoji overload looks like a marketing blast, not a personal message.");
    fixes.push("Max 1-2 emojis. Or zero. Professional > playful for first contact.");
    spamScore += 10;
  }

  if (issues.length === 0) {
    issues.push("This DM is... actually not terrible. But it's probably still too generic.");
    fixes.push("Add one specific detail about THEM. Their recent post, expansion, or fleet size. Show you did homework.");
    spamScore = Math.max(spamScore, 20);
  }

  return {
    issues: [...new Set(issues)],
    fixes: [...new Set(fixes)],
    spamScore: Math.min(spamScore, 100)
  };
}

function generateFix(text, analysis) {
  const businessMatch = text.match(/(car rental|fleet|rental|dealership|auto|automotive)/i);
  const business = businessMatch ? businessMatch[1] : 'business';
  const locationMatch = text.match(/(Melbourne|Sydney|Brisbane|Perth|Adelaide|Geelong|Gold Coast)/i);
  const location = locationMatch ? locationMatch[1] : '';

  const templates = [
    `Hey [Name], saw ${location ? location + ' ' : ''}${business} is expanding — congrats. Quick question: what's the biggest bottleneck with fleet scheduling right now?`,
    `Hi [Name], noticed ${location ? location + ' ' : ''}${business} grew fast. Curious — how are you handling maintenance prediction with that scale?`,
    `Hey [Name], saw your fleet update. Question: are you using any AI for utilization tracking, or still manual?`,
    `Hi [Name], ${location ? location + ' ' : ''}${business} looks busy. What's your current no-show rate like — and is it a pain point?`
  ];

  return templates[Math.floor(Math.random() * templates.length)];
}

app.post('/api/roast', (req, res) => {
  const text = (req.body?.dm || '').trim();
  if (!text) return res.status(400).json({ error: 'dm is required' });

  const analysis = analyzeDM(text);
  const fixedDM = generateFix(text, analysis);

  appendSupportLog(`ROAST | ${text.slice(0, 100)}...`);

  res.json({
    original: text,
    roast: analysis.issues,
    fix: analysis.fixes,
    fixedDM,
    spamScore: analysis.spamScore,
    risk: analysis.spamScore >= 70 ? 'high' : analysis.spamScore >= 40 ? 'medium' : 'low'
  });
});


app.use(express.static(publicDir));

app.get('*', (req, res) => {
  if (req.path.startsWith('/api')) {
    return res.status(404).json({
      error: 'not_found',
      path: req.path,
      hint: 'No handler for this API path. Use node server.js (shift-rental-support), not a static file server.'
    });
  }
  res.sendFile(path.join(publicDir, 'index.html'));
});

(async () => {
  try {
    await seedDatabase(db);
    app.listen(PORT, () => {
      console.log(`SHIFT Rental Support running on http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error('Failed to initialize database:', error);
    process.exit(1);
  }
})();
