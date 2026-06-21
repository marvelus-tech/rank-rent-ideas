#!/usr/bin/env node
/**
 * TaskPilot shared library
 * Pure Node.js, no external deps.
 */

import fs from 'fs';
import path from 'path';
import https from 'https';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WORKSPACE = path.resolve(__dirname, '..');
const OBSIDIAN_TASKS = path.join(process.env.HOME || '/Users/oktos', 'Obsidian/Penelopi/Tasks');
const MASTER_FILE = path.join(OBSIDIAN_TASKS, 'TaskPilot-Master.md');
const DAILY_DIR = path.join(OBSIDIAN_TASKS, 'Daily');

const TELEGRAM_ENV = path.join(WORKSPACE, 'skills/brownstone-bleeding-edge/.env');
const DEFAULT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '';
const DEFAULT_CHAT = process.env.TELEGRAM_CHAT_ID || '47930691';

export function getLocalToday() {
  return new Date().toLocaleDateString('en-CA');
}

export function getLocalDateStr(d = new Date()) {
  return d.toLocaleDateString('en-CA');
}

export function loadTelegramCreds() {
  let token = process.env.TELEGRAM_BOT_TOKEN || DEFAULT_TOKEN;
  let chatId = process.env.TELEGRAM_CHAT_ID || DEFAULT_CHAT;
  try {
    if (fs.existsSync(TELEGRAM_ENV)) {
      const envContent = fs.readFileSync(TELEGRAM_ENV, 'utf8');
      const tokenMatch = envContent.match(/TELEGRAM_BOT_TOKEN=(.+)/);
      const chatMatch = envContent.match(/TELEGRAM_CHAT_ID=(.+)/);
      if (tokenMatch) token = tokenMatch[1].trim();
      if (chatMatch) chatId = chatMatch[1].trim();
    }
  } catch (e) {}
  return { token, chatId };
}

async function sendTelegramRequest(method, payloadObj) {
  const { token } = loadTelegramCreds();
  const url = `https://api.telegram.org/bot${token}/${method}`;
  const payload = JSON.stringify(payloadObj);

  return new Promise((resolve) => {
    const req = https.request(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.ok === true);
        } catch {
          resolve(false);
        }
      });
    });
    req.on('error', () => resolve(false));
    req.write(payload);
    req.end();
  });
}

export async function sendTelegram(text, chatIdOverride = null, disableNotification = false) {
  const { chatId } = loadTelegramCreds();
  const targetChat = chatIdOverride || chatId;
  return sendTelegramRequest('sendMessage', {
    chat_id: targetChat,
    text,
    parse_mode: 'MarkdownV2',
    disable_web_page_preview: true,
    disable_notification: !!disableNotification
  });
}

export async function sendTelegramWithButtons(text, buttons, chatIdOverride = null, disableNotification = false) {
  const { chatId } = loadTelegramCreds();
  const targetChat = chatIdOverride || chatId;

  const normalizeButton = (btn) => {
    if (!btn) return null;
    if (typeof btn === 'string') {
      const action = btn.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 48) || 'action';
      return { text: btn, callback_data: `taskpilot:${action}` };
    }
    if (typeof btn === 'object' && btn.text) {
      if (btn.callback_data || btn.url || btn.switch_inline_query || btn.switch_inline_query_current_chat) {
        return btn;
      }
      const action = String(btn.text).toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 48) || 'action';
      return { ...btn, callback_data: `taskpilot:${action}` };
    }
    return null;
  };

  const rows = Array.isArray(buttons?.[0]) ? buttons : [Array.isArray(buttons) ? buttons : [buttons]];
  const inline_keyboard = rows
    .map(row => (Array.isArray(row) ? row : [row]).map(normalizeButton).filter(Boolean))
    .filter(row => row.length > 0);

  return sendTelegramRequest('sendMessage', {
    chat_id: targetChat,
    text,
    parse_mode: 'MarkdownV2',
    disable_web_page_preview: true,
    disable_notification: !!disableNotification,
    reply_markup: { inline_keyboard }
  });
}

export async function editTelegramMessage(chatId, messageId, text) {
  const { token } = loadTelegramCreds();
  const url = `https://api.telegram.org/bot${token}/editMessageText`;
  const payload = JSON.stringify({
    chat_id: chatId,
    message_id: messageId,
    text: text,
    parse_mode: 'MarkdownV2',
    disable_web_page_preview: true
  });
  return new Promise((resolve) => {
    const req = https.request(url, { method: 'POST', headers: { 'Content-Type': 'application/json' } }, (res) => {
      let data = ''; res.on('data', c => data += c); res.on('end', () => resolve(true));
    });
    req.on('error', () => resolve(false));
    req.write(payload); req.end();
  });
}

export function ensureDirs() {
  fs.mkdirSync(OBSIDIAN_TASKS, { recursive: true });
  fs.mkdirSync(DAILY_DIR, { recursive: true });
}

export function readMaster() {
  ensureDirs();
  if (!fs.existsSync(MASTER_FILE)) {
    // recreate skeleton if missing
    const skeleton = `# TaskPilot Master Registry\n\n> ... \n\n## Active Tasks\n\n<!-- TASKS:BEGIN -->\n<!-- TASKS:END -->\n\n## Completed (last 30 days)\n\n<!-- DONE:BEGIN -->\n<!-- DONE:END -->\n`;
    fs.writeFileSync(MASTER_FILE, skeleton);
  }
  return fs.readFileSync(MASTER_FILE, 'utf8');
}

export function writeMaster(content) {
  fs.writeFileSync(MASTER_FILE, content, 'utf8');
}

export function parseTaskLine(line) {
  // - [ ] Task desc ⏰ 14:00 📅 2026-06-11 #must-do #work <!-- id:abc123 -->
  const match = line.match(/^\s*-\s*\[([ x])\]\s*(.+?)(?:\s+⏰\s*(\d{1,2}:\d{2}))?(?:\s+📅\s*(\d{4}-\d{2}-\d{2}))?\s*(#\S+(?:\s+#\S+)*)?\s*(?:<!--\s*id:([a-z0-9-]+)\s*(?:created:(\d+))?\s*-->)?\s*$/i);
  if (!match) return null;
  const [, checked, desc, time, date, tagsStr, id, created] = match;
  const tags = tagsStr ? tagsStr.trim().split(/\s+/).filter(t => t.startsWith('#')) : [];
  const priority = tags.find(t => ['#must-do', '#should-do', '#nice-to-have', '#overdue', '#done'].includes(t)) || '#nice-to-have';
  return {
    id: id || Date.now().toString(36),
    checked: checked === 'x',
    text: desc.trim(),
    time: time || null,
    date: date || null,
    tags,
    priority,
    raw: line.trim(),
    created: created ? parseInt(created) : Date.now()
  };
}

export function formatTaskLine(task) {
  const check = task.checked ? 'x' : ' ';
  let line = `- [${check}] ${task.text}`;
  if (task.time) line += ` ⏰ ${task.time}`;
  if (task.date) line += ` 📅 ${task.date}`;
  const otherTags = task.tags.filter(t => !['#must-do','#should-do','#nice-to-have','#overdue','#done'].includes(t));
  const prio = task.priority || '#nice-to-have';
  line += ` ${prio}`;
  if (otherTags.length) line += ` ${otherTags.join(' ')}`;
  if (task.id) line += ` <!-- id:${task.id} created:${task.created || Date.now()} -->`;
  return line;
}

export function getActiveTasks(content) {
  const begin = content.indexOf('<!-- TASKS:BEGIN -->');
  const end = content.indexOf('<!-- TASKS:END -->');
  if (begin === -1 || end === -1) return [];
  const section = content.substring(begin + '<!-- TASKS:BEGIN -->'.length, end);
  return section.split('\n')
    .map(l => l.trim())
    .filter(l => l.startsWith('- ['))
    .map(parseTaskLine)
    .filter(Boolean);
}

export function getDoneTasks(content) {
  const begin = content.indexOf('<!-- DONE:BEGIN -->');
  const end = content.indexOf('<!-- DONE:END -->');
  if (begin === -1 || end === -1) return [];
  const section = content.substring(begin + '<!-- DONE:BEGIN -->'.length, end);
  return section.split('\n')
    .map(l => l.trim())
    .filter(l => l.startsWith('- ['))
    .map(parseTaskLine)
    .filter(Boolean);
}

export function updateActiveTasks(content, tasks) {
  const beginMarker = '<!-- TASKS:BEGIN -->';
  const endMarker = '<!-- TASKS:END -->';
  const begin = content.indexOf(beginMarker);
  const end = content.indexOf(endMarker);
  if (begin === -1 || end === -1) {
    // fallback append
    return content + '\n\n<!-- TASKS:BEGIN -->\n' + tasks.map(formatTaskLine).join('\n') + '\n<!-- TASKS:END -->\n';
  }
  const before = content.substring(0, begin + beginMarker.length);
  const after = content.substring(end);
  const newSection = '\n' + tasks.map(formatTaskLine).join('\n') + '\n';
  return before + newSection + after;
}

export function addTaskToMaster(content, newTask) {
  const tasks = getActiveTasks(content);
  tasks.push(newTask);
  return updateActiveTasks(content, tasks);
}

export function markTaskDone(content, taskIdOrText) {
  let tasks = getActiveTasks(content);
  let done = getDoneTasks(content);
  const now = getLocalToday();
  let found = false;
  tasks = tasks.filter(t => {
    const match = (t.id === taskIdOrText) || t.text.toLowerCase().includes(taskIdOrText.toLowerCase());
    if (match) {
      t.checked = true;
      t.priority = '#done';
      t.tags = [...new Set([...t.tags.filter(tt => !tt.startsWith('#')), '#done'])];
      done.unshift({ ...t, date: now }); // move to done
      found = true;
      return false;
    }
    return true;
  });
  if (!found) return { content, found: false };
  let newContent = updateActiveTasks(content, tasks);
  // update done section
  const beginD = newContent.indexOf('<!-- DONE:BEGIN -->');
  const endD = newContent.indexOf('<!-- DONE:END -->');
  if (beginD !== -1 && endD !== -1) {
    const beforeD = newContent.substring(0, beginD + '<!-- DONE:BEGIN -->'.length);
    const afterD = newContent.substring(endD);
    const doneLines = done.slice(0, 50).map(formatTaskLine).join('\n'); // keep last 50
    newContent = beforeD + '\n' + doneLines + '\n' + afterD;
  }
  return { content: newContent, found: true };
}

// Simple natural language date/time parser
export function parseNaturalDateTime(input) {
  const now = new Date();
  let date = null;
  let time = null;
  let text = input.trim();

  // Extract time: support "at 2pm", "by 14:00", "2:30pm", "9am", "14:00"
  let timePhrase = null;
  let hh = null, mm = 0, ap = null;
  // 1. with prefix: at/by/around 2pm or 14:30
  let m = text.match(/\b(at|by|around)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b/i);
  if (m) {
    timePhrase = m[0];
    hh = parseInt(m[2], 10);
    mm = m[3] ? parseInt(m[3], 10) : 0;
    ap = m[4] ? m[4].toLowerCase() : null;
  } else {
    // 2. no prefix 2pm / 2:30pm
    m = text.match(/\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b/i);
    if (m) {
      timePhrase = m[0];
      hh = parseInt(m[1], 10);
      mm = m[2] ? parseInt(m[2], 10) : 0;
      ap = m[3] ? m[3].toLowerCase() : null;
    } else {
      // 3. 24h 14:00
      m = text.match(/\b(\d{1,2}):(\d{2})\b/);
      if (m) {
        timePhrase = m[0];
        hh = parseInt(m[1], 10);
        mm = parseInt(m[2], 10);
        ap = null;
      }
    }
  }
  if (hh !== null && timePhrase) {
    if (ap === 'pm' && hh < 12) hh += 12;
    if (ap === 'am' && hh === 12) hh = 0;
    time = `${hh.toString().padStart(2,'0')}:${mm.toString().padStart(2,'0')}`;
    text = text.replace(timePhrase, '').trim();
  }

  // Relative dates
  const lower = text.toLowerCase();
  let targetDate = new Date(now);

  if (/\btoday\b/.test(lower)) {
    date = getLocalDateStr(now);
    text = text.replace(/\btoday\b/i, '').trim();
  } else if (/\btomorrow\b/.test(lower)) {
    targetDate.setDate(targetDate.getDate() + 1);
    date = getLocalDateStr(targetDate);
    text = text.replace(/\btomorrow\b/i, '').trim();
  } else {
    const inHoursMins = lower.match(/in\s+(\d+)\s*(hours?|hrs?|minutes?|mins?)/i);
    if (inHoursMins) {
      const num = parseInt(inHoursMins[1], 10);
      const unit = inHoursMins[2] ? inHoursMins[2].toLowerCase() : 'hours';
      if (/min/.test(unit)) {
        targetDate.setMinutes(targetDate.getMinutes() + num);
      } else {
        targetDate.setHours(targetDate.getHours() + num);
      }
      date = getLocalDateStr(targetDate);
      if (!time) time = `${targetDate.getHours().toString().padStart(2,'0')}:${targetDate.getMinutes().toString().padStart(2,'0')}`;
      text = text.replace(/in\s+\d+\s*(hours?|hrs?|minutes?|mins?)/i, '').trim();
    } else if (/in\s+(\d+)\s*days?/i.test(lower)) {
      const d = parseInt(lower.match(/in\s+(\d+)\s*days?/i)[1], 10);
      targetDate.setDate(targetDate.getDate() + d);
      date = getLocalDateStr(targetDate);
      text = text.replace(/in\s+\d+\s*days?/i, '').trim();
    } else if (/(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i.test(lower)) {
      const dayMatch = lower.match(/(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i);
      const dayName = dayMatch[2].toLowerCase();
      const days = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday'];
      const targetDay = days.indexOf(dayName);
      let diff = (targetDay - now.getDay() + 7) % 7;
      if (diff === 0) diff = 7; // next week if today
      if (dayMatch[1]) diff += 7;
      targetDate.setDate(targetDate.getDate() + diff);
      date = getLocalDateStr(targetDate);
      text = text.replace(/(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i, '').trim();
    } else if (/(\d{4}-\d{2}-\d{2})/.test(text)) {
      const dMatch = text.match(/(\d{4}-\d{2}-\d{2})/);
      date = dMatch[1];
      text = text.replace(dMatch[0], '').trim();
    } else if (date === null) {
      // default to today if time mentioned, else no date
      if (time) {
        date = getLocalDateStr(now);
      }
    }
  }

  // Clean up text
  text = text.replace(/\s+/g, ' ').trim();

  // Remove leftover time prepositions and punctuation after date/time removal
  text = text.replace(/\b(at|by|around)\b/gi, '').replace(/\s*[:\-–]\s*$/g, '').trim();
  text = text.replace(/\s+/g, ' ').trim();

  // Strip priority words and tags from text (keep desc clean)
  text = text.replace(/\b(must[\s\-]?do|should[\s\-]?do|nice[\s\-]?to[\s\-]?have|urgent|critical|asap|deadline|very important|key task|priority task)\b/gi, '');
  text = text.replace(/\s+#(must-do|should-do|nice-to-have|overdue|done)\b/gi, '');
  text = text.replace(/(^|\s)#(?=\s|$)/g, ' ').replace(/#+$/g, '');
  text = text.replace(/\s+/g, ' ').trim();

  // Priority detection on ORIGINAL input
  let priority = '#nice-to-have';
  const inpLower = input.toLowerCase();
  if (/(must|critical|urgent|deadline|very important|asap|right now)/.test(inpLower)) {
    priority = '#must-do';
  } else if (/(should|important|priority|key)/.test(inpLower)) {
    priority = '#should-do';
  }

  return { text: text || 'Untitled task', date, time, priority };
}

export function generateDailySnapshot(dateStr = null) {
  const date = dateStr || getLocalToday();
  const master = readMaster();
  const active = getActiveTasks(master);
  const dueToday = active.filter(t => t.date === date || !t.date);
  const overdue = active.filter(t => t.date && t.date < date && !t.checked);

  let md = `# Daily Task Snapshot — ${date}\n\n`;
  md += `Generated: ${new Date().toLocaleString('en-AU')}\n\n`;
  
  md += `## MUST-DO Today\n`;
  const must = dueToday.filter(t => t.priority === '#must-do');
  if (must.length === 0) md += '_None_\n';
  must.forEach(t => md += `- [ ] ${t.text}${t.time ? ' ⏰ ' + t.time : ''} ${t.priority}\n`);

  md += `\n## Due Today / Active\n`;
  dueToday.filter(t => t.priority !== '#must-do').forEach(t => {
    md += `- [${t.checked ? 'x' : ' '}] ${t.text}${t.time ? ' ⏰ ' + t.time : ''} ${t.priority}\n`;
  });

  if (overdue.length) {
    md += `\n## Overdue\n`;
    overdue.forEach(t => md += `- [ ] ${t.text} 📅 ${t.date} ${t.priority} #overdue\n`);
  }

  md += `\n---\n[Full registry](TaskPilot-Master.md)\n`;
  return md;
}

export function saveDailySnapshot(dateStr = null) {
  const date = dateStr || getLocalToday();
  const content = generateDailySnapshot(date);
  const file = path.join(DAILY_DIR, `${date}.md`);
  fs.writeFileSync(file, content, 'utf8');
  return file;
}

export function escapeMdV2(str) {
  // Escape for Telegram MarkdownV2
  return str.replace(/([_*\[\]()~`>#+\-=|{}.!])/g, '\\$1');
}
