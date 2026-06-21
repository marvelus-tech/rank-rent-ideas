#!/usr/bin/env node
/**
 * TaskPilot Master Registry Manager
 * Commands:
 *   list [all|active|today]
 *   done <id|text>
 *   add "raw"
 *   snapshot [date]
 *   overdue
 */

import {
  readMaster, getActiveTasks, getDoneTasks, writeMaster, markTaskDone,
  parseNaturalDateTime, addTaskToMaster, saveDailySnapshot, formatTaskLine,
  sendTelegram, escapeMdV2, getLocalToday
} from './taskpilot-lib.mjs';

const cmd = (process.argv[2] || 'list').toLowerCase();
const arg = process.argv.slice(3).join(' ');

const master = readMaster();
let active = getActiveTasks(master);
const done = getDoneTasks(master);

function printTasks(tasks, title) {
  console.log(`\n${title} (${tasks.length})`);
  tasks.forEach(t => {
    const line = formatTaskLine(t);
    console.log(line);
  });
}

async function main() {
  if (cmd === 'list' || cmd === 'active') {
    printTasks(active.filter(t => !t.checked), 'ACTIVE TASKS');
    console.log(`\nUse: node taskpilot-master.mjs done "partial text or id"`);
  } else if (cmd === 'today') {
    const today = getLocalToday();
    const todays = active.filter(t => !t.checked && (!t.date || t.date === today));
    printTasks(todays, `TODAY (${today})`);
  } else if (cmd === 'done') {
    if (!arg) { console.error('Need task id or text snippet'); process.exit(1); }
    const res = markTaskDone(master, arg);
    if (res.found) {
      writeMaster(res.content);
      saveDailySnapshot();
      const msg = `✅ Completed: ${escapeMdV2(arg)}`;
      console.log(msg);
      await sendTelegram(msg);
    } else {
      console.log('No matching task found.');
    }
  } else if (cmd === 'add') {
    if (!arg) { console.error('Need task text'); process.exit(1); }
    const parsed = parseNaturalDateTime(arg);
    const nt = { id: Date.now().toString(36), checked:false, text:parsed.text, time:parsed.time, date:parsed.date, tags:[], priority:parsed.priority, created:Date.now() };
    const up = addTaskToMaster(master, nt);
    writeMaster(up);
    saveDailySnapshot();
    console.log('Added:', formatTaskLine(nt));
  } else if (cmd === 'snapshot') {
    const f = saveDailySnapshot(arg || undefined);
    console.log('Snapshot saved:', f);
  } else if (cmd === 'overdue') {
    const today = getLocalToday();
    const ov = active.filter(t => t.date && t.date < today && !t.checked);
    printTasks(ov, 'OVERDUE');
    if (ov.length) await sendTelegram(`⚠️ ${ov.length} overdue tasks. Run master list overdue.`);
  } else if (cmd === 'all') {
    printTasks(active, 'ALL ACTIVE (incl done in list)');
    printTasks(done.slice(0,10), 'RECENT DONE');
  } else {
    console.log('Commands: list | active | today | done <match> | add "text" | snapshot | overdue | all');
  }
}

main().catch(console.error);
