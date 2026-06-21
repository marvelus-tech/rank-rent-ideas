const express = require('express');
const { findBuilders } = require('./lib/scraper');
const { formatAsJSON, formatAsCSV, formatAsMarkdown } = require('./lib/formatter');

const app = express();
app.use(express.json());

/**
 * API: Search for builders
 * GET /api/builders?city=Austin&state=TX&days=365&enrich=true
 */
app.get('/api/builders', async (req, res) => {
  try {
    const { city = 'Austin', state = 'TX', days = '365', enrich = 'false' } = req.query;
    
    const results = await findBuilders(
      city,
      state,
      parseInt(days),
      enrich === 'true'
    );
    
    res.json({
      success: true,
      data: results
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * API: Health check
 */
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

/**
 * API: Get builder by name
 */
app.get('/api/builders/:name', async (req, res) => {
  try {
    const { city = 'Austin', state = 'TX' } = req.query;
    const results = await findBuilders(city, state, 365, true);
    
    const builder = results.builders.find(b => 
      b.name.toLowerCase().includes(req.params.name.toLowerCase())
    );
    
    if (!builder) {
      return res.status(404).json({ success: false, error: 'Builder not found' });
    }
    
    res.json({ success: true, data: builder });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Zillow Builder Leads API running on port ${PORT}`);
  console.log(`📖 API Documentation:`);
  console.log(`   GET /api/health           - Health check`);
  console.log(`   GET /api/builders         - Search builders (query: city, state, days, enrich)`);
  console.log(`   GET /api/builders/:name   - Get specific builder`);
});

module.exports = app;
