#!/usr/bin/env node
/**
 * TaskPilot Webhook Server
 * Receives Telegram callback queries and processes them
 * 
 * Usage:
 *   node taskpilot-webhook.mjs              # Start server
 *   node taskpilot-webhook.mjs --setup     # Show webhook setup instructions
 * 
 * Environment:
 *   TELEGRAM_BOT_TOKEN - Your bot token
 *   WEBHOOK_PORT       - Port to listen on (default: 3456)
 *   WEBHOOK_SECRET     - Secret path segment for security
 */

import http from 'http';
import https from 'https';
import { handleCallbackQuery } from './taskpilot-bot.mjs';
import { loadTelegramCreds } from './taskpilot-lib.mjs';

const PORT = process.env.WEBHOOK_PORT || 3456;
const SECRET = process.env.WEBHOOK_SECRET || 'taskpilot';

async function handleRequest(req, res) {
  // Only accept POST to /webhook/SECRET
  if (req.method !== 'POST' || !req.url.startsWith(`/webhook/${SECRET}`)) {
    res.writeHead(404);
    res.end('Not found');
    return;
  }

  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', async () => {
    try {
      const update = JSON.parse(body);
      
      // Handle callback queries (inline button presses)
      if (update.callback_query) {
        const handled = await handleCallbackQuery(update.callback_query);
        
        // Answer the callback query to remove loading state
        if (handled) {
          await answerCallbackQuery(update.callback_query.id);
        }
      }
      
      res.writeHead(200);
      res.end('OK');
    } catch (e) {
      console.error('Webhook error:', e);
      res.writeHead(500);
      res.end('Error');
    }
  });
}

async function answerCallbackQuery(callbackQueryId) {
  const { token } = loadTelegramCreds();
  const url = `https://api.telegram.org/bot${token}/answerCallbackQuery`;
  const payload = JSON.stringify({
    callback_query_id: callbackQueryId,
    text: 'Processing...'
  });
  
  return new Promise((resolve) => {
    const req = https.request(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(true));
    });
    req.on('error', () => resolve(false));
    req.write(payload);
    req.end();
  });
}

function showSetup() {
  const { token } = loadTelegramCreds();
  const webhookUrl = `https://YOUR_DOMAIN/webhook/${SECRET}`;
  
  console.log(`
🚀 TaskPilot Webhook Setup
==========================

1. Set your webhook URL with Telegram:
   curl -X POST "https://api.telegram.org/bot${token}/setWebhook" \\
     -H "Content-Type: application/json" \\
     -d '{"url": "${webhookUrl}"}'

2. Start this server:
   node taskpilot-webhook.mjs

3. Or use with a tunnel (ngrok/cloudflared):
   ngrok http ${PORT}
   # Then use the https URL + /webhook/${SECRET}

4. Test with:
   curl -X POST http://localhost:${PORT}/webhook/${SECRET} \\
     -H "Content-Type: application/json" \\
     -d '{"callback_query": {"id": "test", "data": "taskpilot:view_all", "message": {"chat": {"id": 47930691}, "message_id": 1}}}'
`);
}

// Main
if (process.argv.includes('--setup')) {
  showSetup();
} else {
  const server = http.createServer(handleRequest);
  server.listen(PORT, () => {
    console.log(`🎯 TaskPilot webhook listening on port ${PORT}`);
    console.log(`Webhook URL: /webhook/${SECRET}`);
    console.log('Run with --setup for configuration help');
  });
}
