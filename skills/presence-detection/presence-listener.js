#!/usr/bin/env node
/**
 * Presence Detection Listener
 * Receives webhook calls from iPhone and forwards to OpenClaw
 * 
 * Usage: node presence-listener.js
 * Port: 8123 (configurable below)
 */

const http = require('http');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PRESENCE_PORT || 8123;
const OPENCLAW_API = 'http://127.0.0.1:18789';
const MEMORY_FILE = path.join(process.env.HOME, 'Obsidian/Penelopi/Daily', `${new Date().toISOString().split('T')[0]}.md`);

// Simple logging
function log(level, message) {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] [${level.toUpperCase()}] ${message}`);
}

// Append to memory file
function recordEvent(data) {
  const timestamp = new Date().toISOString();
  const entry = `
## Presence Event - ${timestamp}
- User: ${data.user}
- Status: ${data.status}
- Source: ${data.source}
- Confidence: ${data.confidence}
`;
  
  // Ensure directory exists
  const dir = path.dirname(MEMORY_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  fs.appendFileSync(MEMORY_FILE, entry);
  log('info', `Recorded event to ${MEMORY_FILE}`);
}

// Handle presence logic
function handlePresence(params) {
  const { user, status, source, confidence } = params;
  
  log('info', `Presence update: ${user} is ${status} (source: ${source}, confidence: ${confidence})`);
  
  // Record to memory file
  recordEvent(params);
  
  if (status === 'home') {
    // Trigger home mode
    log('info', 'Triggering home_mode');
    
    // If geofence triggered, also preheat
    if (source === 'geofence') {
      log('info', 'Geofence entry detected - triggering preheat_home');
      // Future: trigger preheat_home skill
    }
    
    // Future: trigger home_mode skill
    // exec('openclaw skills run home_mode');
    
  } else if (status === 'away') {
    // Set pending away (don't trigger immediately)
    log('info', 'Setting pending_away - will confirm after 10 minutes');
    
    // Schedule confirmation
    setTimeout(() => {
      log('info', 'Away mode confirmed after probation period');
      // Future: trigger away_mode skill
      // exec('openclaw skills run away_mode');
    }, 10 * 60 * 1000); // 10 minutes
  }
}

// Create HTTP server
const server = http.createServer((req, res) => {
  // Enable CORS for iPhone requests
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  // Parse URL
  const url = new URL(req.url, `http://${req.headers.host}`);
  
  // Health check endpoint
  if (url.pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }));
    return;
  }
  
  // Presence endpoint
  if (url.pathname === '/presence') {
    const params = {
      user: url.searchParams.get('user') || 'unknown',
      status: url.searchParams.get('status') || 'unknown',
      source: url.searchParams.get('source') || 'unknown',
      confidence: parseFloat(url.searchParams.get('confidence') || '0.5')
    };
    
    // Validate
    if (!['home', 'away'].includes(params.status)) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid status. Use home or away' }));
      return;
    }
    
    // Process presence update
    handlePresence(params);
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      success: true, 
      message: `Presence updated: ${params.user} is ${params.status}`,
      timestamp: new Date().toISOString()
    }));
    return;
  }
  
  // Default 404
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, '0.0.0.0', () => {
  log('info', `Presence listener running on http://0.0.0.0:${PORT}`);
  log('info', `Endpoints:`);
  log('info', `  - GET http://YOUR_IP:${PORT}/presence?user=okeito&status=home&source=wifi&confidence=1.0`);
  log('info', `  - GET http://YOUR_IP:${PORT}/health`);
  log('info', '');
  log('info', 'iPhone Shortcuts should use:');
  log('info', `  http://192.168.1.16:${PORT}/presence?user=okeito&status=home&source=wifi&confidence=1.0`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  log('info', 'Shutting down...');
  server.close(() => {
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  log('info', 'Shutting down...');
  server.close(() => {
    process.exit(0);
  });
});
