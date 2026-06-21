const express = require('express');
const { exec } = require('child_process');
const path = require('path');

const app = express();
const PORT = 8765;
const SCAN_SCRIPT = path.join(__dirname, 'scan-ideas.js');
const NODE_PATH = '/usr/local/Cellar/node@22/22.22.1_3/bin/node';

// Serve static files
app.use(express.static(__dirname));

// Refresh endpoint - runs the scan script
app.get('/refresh', (req, res) => {
  console.log('🔄 Manual refresh triggered...');
  
  exec(`${NODE_PATH} ${SCAN_SCRIPT}`, (error, stdout, stderr) => {
    if (error) {
      console.error('Refresh failed:', error);
      return res.status(500).json({ 
        success: false, 
        error: 'Scan failed',
        details: stderr 
      });
    }
    
    console.log(stdout);
    res.json({ 
      success: true, 
      message: 'Projects refreshed',
      timestamp: new Date().toISOString()
    });
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`🚀 Mission Control Server running on http://localhost:${PORT}`);
  console.log(`📊 Dashboard: http://localhost:${PORT}`);
  console.log(`🔄 Refresh endpoint: http://localhost:${PORT}/refresh`);
});
