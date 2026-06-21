#!/usr/bin/env node
/**
 * TaskPilot Reminder System
 * - Morning brief (08:00 silent-ish) with MUST-DO / SHOULD-DO / NICE-TO-HAVE sections
 * - Urgency: T-4h, T-1h, T-15m for MUST-DO
 * - Overdue alerts
 * Called by cron every 15min or specific times.
 * 
 * Usage: node taskpilot-reminders.mjs [morning|--morning-brief|check|--check-urgency|overdue]
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import {
  readMaster, getActiveTasks, saveDailySnapshot,
  sendTelegram, sendTelegramWithButtons, escapeMdV2, getLocalToday
} from './taskpilot-lib.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WORKSPACE = path.resolve(__dirname, '..');
const ALERTED_PATH = path.join(WORKSPACE, 'data', 'alerted-tasks.json');
const MORNING_BRIEF_SENT_PATH = path.join(WORKSPACE, 'data', 'morning-brief-sent.flag');

const rawArg = (process.argv[2] || '').toLowerCase();
const mode = rawArg === '--morning-brief' || rawArg === 'morning' || rawArg === '08:00' || rawArg === 'brief' ? 'morning' :
             rawArg === '--check-urgency' || rawArg === 'check' || rawArg === '15min' ? 'check' :
             rawArg === 'overdue' || rawArg === '--overdue' ? 'overdue' : (rawArg || 'check');
const now = new Date();
const today = getLocalToday();
const hhmm = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`;

const master = readMaster();
const active = getActiveTasks(master).filter(t => !t.checked);

function loadAlertedState() {
  try {
    if (!fs.existsSync(ALERTED_PATH)) return { day: today, sent: {}, overdueSweepDay: null };
    const parsed = JSON.parse(fs.readFileSync(ALERTED_PATH, 'utf8'));
    if (!parsed || typeof parsed !== 'object') return { day: today, sent: {}, overdueSweepDay: null };
    const overdueSweepDay = typeof parsed.overdueSweepDay === 'string' ? parsed.overdueSweepDay : null;
    if (parsed.day !== today) return { day: today, sent: {}, overdueSweepDay };
    return {
      day: today,
      sent: parsed.sent && typeof parsed.sent === 'object' ? parsed.sent : {},
      overdueSweepDay
    };
  } catch {
    return { day: today, sent: {}, overdueSweepDay: null };
  }
}

function saveAlertedState(state) {
  fs.mkdirSync(path.dirname(ALERTED_PATH), { recursive: true });
  fs.writeFileSync(ALERTED_PATH, JSON.stringify(state, null, 2));
}

function getDueToday(tasks) {
  return tasks.filter(t => !t.date || t.date === today);
}

function taskDedupeKey(task) {
  if (task?.id) return `id:${task.id}`;
  const raw = `${task?.text || ''}|${task?.date || ''}|${task?.time || ''}`
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ');
  return `fp:${raw}`;
}

function wasMorningBriefSentToday() {
  try {
    if (!fs.existsSync(MORNING_BRIEF_SENT_PATH)) return false;
    const flag = fs.readFileSync(MORNING_BRIEF_SENT_PATH, 'utf8').trim();
    return flag === today;
  } catch {
    return false;
  }
}

function markMorningBriefSent() {
  fs.mkdirSync(path.dirname(MORNING_BRIEF_SENT_PATH), { recursive: true });
  fs.writeFileSync(MORNING_BRIEF_SENT_PATH, today, 'utf8');
}

async function morningBrief() {
  if (wasMorningBriefSentToday()) {
    console.log('Morning brief already sent today — skipping duplicate');
    return;
  }
  const dueToday = getDueToday(active);
  const must = dueToday.filter(t => t.priority === '#must-do');
  const should = dueToday.filter(t => t.priority === '#should-do');
  const nice = dueToday.filter(t => t.priority === '#nice-to-have');

  const total = must.length + should.length + nice.length;
  if (total === 0) {
    console.log('Morning brief: 0 tasks today');
    return;
  }

  const todayStr = today;
  let brief = `☀️ *Morning Brief — ${escapeMdV2(todayStr)}*\n\n`;
  
  if (must.length > 0) {
    brief += `*🚨 MUST-DO (${must.length}):*\n`;
    must.forEach(t => {
      brief += `• ${escapeMdV2(t.text)}${t.time ? " ⏰ " + escapeMdV2(t.time) : ""}\n`;
    });
    brief += `\n`;
  }
  
  if (should.length > 0) {
    brief += `*📋 SHOULD-DO (${should.length}):*\n`;
    should.forEach(t => {
      brief += `• ${escapeMdV2(t.text)}${t.time ? " ⏰ " + escapeMdV2(t.time) : ""}\n`;
    });
    brief += `\n`;
  }
  
  if (nice.length > 0) {
    brief += `*✨ NICE-TO-HAVE (${nice.length}):*\n`;
    nice.forEach(t => {
      brief += `• ${escapeMdV2(t.text)}${t.time ? " ⏰ " + escapeMdV2(t.time) : ""}\n`;
    });
    brief += `\n`;
  }
  
  brief += `Total: ${total} tasks due today`;

  // Build inline keyboard buttons for each MUST-DO task
  const taskButtons = must.slice(0, 5).map(t => ([
    { text: `✅ ${t.text.slice(0, 20)}${t.text.length > 20 ? '...' : ''}`, callback_data: `taskpilot:done:${t.id}` }
  ]));

  const controlButtons = [
    [
      { text: '📋 View All', callback_data: 'taskpilot:view_all' },
      { text: '➕ Add Task', callback_data: 'taskpilot:add_task' }
    ]
  ];

  const allButtons = [...taskButtons, ...controlButtons];

  const ok = await sendTelegramWithButtons(brief, allButtons, null, true);
  if (ok) {
    markMorningBriefSent();
    console.log('Morning brief sent with buttons');
  } else {
    // Fallback to plain text if buttons fail
    const ok2 = await sendTelegram(brief, null, true);
    if (ok2) {
      markMorningBriefSent();
      console.log('Morning brief sent (plain text fallback)');
    } else {
      console.log('Morning brief send FAILED');
    }
  }
}

async function urgencyCheck() {
  // Find MUST-DO with time today, compute delta
  const musts = active.filter(t => t.priority === '#must-do' && t.date === today && t.time);
  let alerted = 0;
  const state = loadAlertedState();

  for (const t of musts) {
    if (!t.time) continue;
    const [h,m] = t.time.split(':').map(Number);
    const due = new Date(now);
    due.setHours(h, m, 0, 0);
    const msLeft = due - now;
    const minsLeft = Math.round(msLeft / 60000);

    let bucket = null;
    let alert = null;
    if (minsLeft > 0 && minsLeft <= 15) {
      bucket = 't15';
      alert = `⏰ T-15min: *${escapeMdV2(t.text)}* ⏰${escapeMdV2(t.time)}`;
    } else if (minsLeft > 0 && minsLeft <= 60) {
      bucket = 't1h';
      alert = `⏰ T-1h: *${escapeMdV2(t.text)}* ⏰${escapeMdV2(t.time)}`;
    } else if (minsLeft > 0 && minsLeft <= 240) {
      bucket = 't4h';
      alert = `⏰ T-4h: *${escapeMdV2(t.text)}* ⏰${escapeMdV2(t.time)}`;
    } else if (minsLeft < 0 && minsLeft > -60) {
      bucket = 'overdue';
      alert = `⚠️ OVERDUE: *${escapeMdV2(t.text)}* (was ⏰${escapeMdV2(t.time)})`;
    }

    if (!alert || !bucket) continue;

    const dedupeKey = `${today}:${taskDedupeKey(t)}:${bucket}`;
    if (state.sent[dedupeKey]) continue;

    // Add action buttons for urgency alerts
    const buttons = [[
      { text: '✅ Done', callback_data: `taskpilot:done:${t.id}` },
      { text: '⏰ Snooze', callback_data: `taskpilot:snooze:${t.id}` }
    ]];

    const ok = await sendTelegramWithButtons(alert, buttons);
    if (ok) {
      state.sent[dedupeKey] = Date.now();
      alerted++;
    }

    // small delay
    await new Promise(r => setTimeout(r, 300));
  }

  saveAlertedState(state);

  if (alerted === 0) {
    console.log('No urgency alerts');
  } else {
    console.log(`${alerted} urgency alerts sent`);
  }
}

async function overdueSweep() {
  const todayStr = today;
  const ov = active.filter(t => t.date && t.date < todayStr);
  if (ov.length === 0) {
    console.log('Overdue: 0 tasks');
    return;
  }
  let text = `⚠️ ${ov.length} overdue: ${ov.slice(0,3).map(t => escapeMdV2(t.text)).join(', ')}`;
  if (ov.length > 3) text += ` +${ov.length-3} more`;
  await sendTelegram(text);
  console.log('Overdue sweep sent');
}

async function main() {
  if (mode === 'morning' || mode === '08:00' || mode === 'brief') {
    await morningBrief();
  } else if (mode === 'check' || mode === '15min') {
    await urgencyCheck();

    // deterministic overdue reminder: once daily at/after 18:05
    const state = loadAlertedState();
    if (hhmm >= '18:05' && state.overdueSweepDay !== today) {
      await overdueSweep();
      state.overdueSweepDay = today;
      saveAlertedState(state);
    }
  } else if (mode === 'overdue') {
    await overdueSweep();
  } else {
    console.log('Modes: morning | check | overdue');
  }
  // Always keep snapshot fresh on reminder runs
  saveDailySnapshot();
}

main().catch(e => { console.error(e); process.exit(1); });
