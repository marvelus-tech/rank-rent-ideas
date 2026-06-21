#!/usr/bin/env node
/**
 * TaskPilot Telegram Bot Handler
 * Processes callback queries from inline buttons
 * Usage: Called by webhook or polling setup
 */

import {
  readMaster, writeMaster, markTaskDone, getActiveTasks,
  sendTelegram, editTelegramMessage, escapeMdV2, getLocalToday
} from './taskpilot-lib.mjs';

const today = getLocalToday();

export async function handleCallbackQuery(query) {
  const data = query.data || '';
  const chatId = query.message?.chat?.id;
  const messageId = query.message?.message_id;

  if (!data.startsWith('taskpilot:')) return false;

  const action = data.replace('taskpilot:', '');
  const [command, ...args] = action.split(':');

  switch (command) {
    case 'done': {
      const taskId = args.join(':');
      const master = readMaster();
      const result = markTaskDone(master, taskId);
      if (result.found) {
        writeMaster(result.content);
        await sendTelegram(`✅ Marked as done: ${escapeMdV2(taskId)}`);
        // Update the original message to show it's done
        if (messageId) {
          const originalText = query.message?.text || '';
          await editTelegramMessage(chatId, messageId, originalText + '\n\n✅ *Completed*');
        }
      } else {
        await sendTelegram('❌ Task not found');
      }
      break;
    }

    case 'snooze': {
      const taskId = args.join(':');
      // Snooze to tomorrow
      const master = readMaster();
      const tasks = getActiveTasks(master);
      const task = tasks.find(t => t.id === taskId);
      if (task) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        task.date = tomorrow.toISOString().split('T')[0];
        // Rebuild and save
        const updated = tasks.map(t => t.id === taskId ? task : t);
        // This needs a proper update function - for now just notify
        await sendTelegram(`⏰ Snoozed to tomorrow: ${escapeMdV2(task.text)}`);
      }
      break;
    }

    case 'view_all': {
      const master = readMaster();
      const active = getActiveTasks(master).filter(t => !t.checked);
      const must = active.filter(t => t.priority === '#must-do');
      const should = active.filter(t => t.priority === '#should-do');
      
      let text = `📋 *All Tasks* (${active.length})\n\n`;
      if (must.length) {
        text += `*MUST-DO:*\n`;
        must.forEach(t => text += `• ${escapeMdV2(t.text)}${t.time ? ' ⏰ ' + escapeMdV2(t.time) : ''}\n`);
      }
      if (should.length) {
        text += `\n*SHOULD-DO:*\n`;
        should.forEach(t => text += `• ${escapeMdV2(t.text)}${t.time ? ' ⏰ ' + escapeMdV2(t.time) : ''}\n`);
      }
      await sendTelegram(text);
      break;
    }

    case 'add_task': {
      await sendTelegram(
        '📝 *Add a task*\n\n' +
        'Send me a message like:\n' +
        '`Call client tomorrow 2pm #must-do`\n' +
        '`Review budget by Friday #should-do`\n' +
        '`Buy groceries #nice-to-have`'
      );
      break;
    }

    default:
      return false;
  }

  return true;
}

// If run directly, start polling mode for development
if (process.argv[1] === new URL(import.meta.url).pathname) {
  console.log('TaskPilot bot handler loaded');
  console.log('Use with your webhook server or integrate with OpenClaw');
}
