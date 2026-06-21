#!/usr/bin/env node
/**
 * TaskPilot EOD Audit (18:00 daily)
 * - Summarize completed today
 * - List remaining MUST-DO / due
 * - Generate tomorrow's daily snapshot
 * - Suggest carry-over
 * - Send dense report to TG
 */

import {
  readMaster, getActiveTasks, getDoneTasks, saveDailySnapshot,
  sendTelegram, escapeMdV2, writeMaster, formatTaskLine, getLocalToday
} from './taskpilot-lib.mjs';

const today = getLocalToday();
const master = readMaster();
const active = getActiveTasks(master).filter(t => !t.checked);
const doneAll = getDoneTasks(master);

const doneToday = doneAll.filter(t => t.date === today || (t.raw && t.raw.includes(today))); // rough

async function main() {
  const mustActive = active.filter(t => t.priority === '#must-do');
  const dueToday = active.filter(t => t.date === today || !t.date);
  const should = active.filter(t => t.priority === '#should-do');

  const overdueCount = active.filter(t => t.date && t.date < today).length;
  const report = `📋 EOD: ${doneToday.length}✅ ${dueToday.length}⏳ ${overdueCount}🔴`;

  // Refresh snapshot for tomorrow preview (silent side effect, no multiline report)
  const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];
  saveDailySnapshot(tomorrow);

  await sendTelegram(report);
  console.log('EOD audit sent');

  // Also ensure master has no stale #overdue
  let changed = false;
  const updatedActive = active.map(t => {
    if (t.date && t.date < today && t.priority !== '#overdue' && t.priority !== '#done') {
      t.priority = '#overdue';
      t.tags = [...new Set(t.tags.filter(tt => !['#must-do','#should-do','#nice-to-have'].includes(tt))), '#overdue'];
      changed = true;
      return t;
    }
    return t;
  });
  if (changed) {
    // rebuild content
    // simple: re-read and update section (but since we have list, use update fn? for now re-generate section)
    let content = readMaster();
    const begin = content.indexOf('<!-- TASKS:BEGIN -->');
    const end = content.indexOf('<!-- TASKS:END -->');
    if (begin !== -1 && end !== -1) {
      const before = content.substring(0, begin + '<!-- TASKS:BEGIN -->'.length);
      const after = content.substring(end);
      const lines = updatedActive.map(formatTaskLine).join('\n');
      content = before + '\n' + lines + '\n' + after;
      writeMaster(content);
    }
  }
}

main().catch(console.error);
