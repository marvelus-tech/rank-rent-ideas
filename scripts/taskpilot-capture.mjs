#!/usr/bin/env node
/**
 * TaskPilot Capture Engine
 * Usage: node taskpilot-capture.mjs "task description tomorrow 2pm #must-do"
 * Or from agent: parses natural language, adds to master, optionally sends confirmation.
 */

import { readMaster, addTaskToMaster, writeMaster, parseNaturalDateTime, formatTaskLine, sendTelegram, escapeMdV2, saveDailySnapshot } from './taskpilot-lib.mjs';

const input = process.argv.slice(2).join(' ').trim();

if (!input) {
  console.error('Usage: node taskpilot-capture.mjs "<natural language task>"');
  process.exit(1);
}

async function main() {
  const masterContent = readMaster();
  const parsed = parseNaturalDateTime(input);
  const cleanText = (parsed.text || '')
    .replace(/(^|\s)#(must-do|should-do|nice-to-have)\b/gi, ' ')
    .replace(/(^|\s)#(?=\s|$|[^\w])/g, ' ')
    .replace(/#+$/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  const newTask = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2,6),
    checked: false,
    text: cleanText || 'Untitled task',
    time: parsed.time,
    date: parsed.date,
    tags: [],
    priority: parsed.priority,
    created: Date.now()
  };

  const updated = addTaskToMaster(masterContent, newTask);
  writeMaster(updated);

  // Also update today's daily snapshot
  const snapFile = saveDailySnapshot();

  const timeStr = parsed.time ? `⏰ ${escapeMdV2(parsed.time)}` : '';
  const dateStr = parsed.date ? `📅 ${escapeMdV2(parsed.date)}` : '';
  const prio = escapeMdV2(parsed.priority);
  const msg = `✅ Captured: *${escapeMdV2(cleanText || 'Untitled task')}* ${timeStr} ${dateStr} ${prio}`;

  console.log(msg);
  console.log(`Saved to: ${snapFile}`);

  // Send to Telegram (dense, scannable)
  const ok = await sendTelegram(msg);
  if (ok) console.log('Sent to Telegram');
  else console.log('TG send failed (likely MDV2 escape issue or rate)');
  process.exit(0);
}

main().catch(e => { console.error(e); process.exit(1); });
