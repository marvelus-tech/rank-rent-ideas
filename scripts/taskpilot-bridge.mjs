#!/usr/bin/env node
/**
 * TaskPilot OpenClaw Bridge
 * 
 * This script is called by OpenClaw when a button callback is detected.
 * Usage: node taskpilot-bridge.mjs <callback_data> <chat_id> [message_id]
 * 
 * Example:
 *   node taskpilot-bridge.mjs "taskpilot:done:abc123" 47930691 2785
 */

import { handleCallbackQuery } from './taskpilot-bot.mjs';

const callbackData = process.argv[2];
const chatId = process.argv[3];
const messageId = process.argv[4];

if (!callbackData || !chatId) {
  console.error('Usage: node taskpilot-bridge.mjs <callback_data> <chat_id> [message_id]');
  process.exit(1);
}

if (!callbackData.startsWith('taskpilot:')) {
  console.log('Not a TaskPilot callback, ignoring');
  process.exit(0);
}

const mockQuery = {
  id: `bridge-${Date.now()}`,
  data: callbackData,
  message: {
    chat: { id: parseInt(chatId, 10) },
    message_id: messageId ? parseInt(messageId, 10) : undefined
  }
};

handleCallbackQuery(mockQuery)
  .then(handled => {
    if (handled) {
      console.log('✅ TaskPilot action processed:', callbackData);
      process.exit(0);
    } else {
      console.log('❌ Unknown TaskPilot action:', callbackData);
      process.exit(1);
    }
  })
  .catch(e => {
    console.error('Error:', e);
    process.exit(1);
  });
