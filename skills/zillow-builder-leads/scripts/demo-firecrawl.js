const axios = require('axios');
require('dotenv').config();

const FIRECRAWL_API_KEY = process.env.FIRECRAWL_API_KEY;
const FIRECRAWL_BASE_URL = 'https://api.firecrawl.dev/v1';

/**
 * Demo script to test Firecrawl Zillow scraping
 */
async function demo() {
  console.log('🔥 Firecrawl Zillow Demo\n');
  
  if (!FIRECRAWL_API_KEY) {
    console.error('❌ FIRECRAWL_API_KEY not set in .env');
    process.exit(1);
  }
  
  const city = 'Austin';
  const state = 'TX';
  const url = `https://www.zillow.com/${city.toLowerCase()}-${state.toLowerCase()}/`;
  
  console.log(`🌐 Scraping: ${url}\n`);
  
  try {
    const response = await axios.post(`${FIRECRAWL_BASE_URL}/scrape`, {
      url: url,
      formats: ['markdown', 'html'],
      onlyMainContent: true
    }, {
      headers: {
        'Authorization': `Bearer ${FIRECRAWL_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.data.success) {
      const data = response.data.data;
      
      console.log('✅ Success!\n');
      console.log('📄 Title:', data.metadata?.title || 'N/A');
      console.log('🔗 URL:', data.metadata?.sourceURL || 'N/A');
      
      // Extract listing count
      const content = data.markdown || '';
      const listingMatches = content.match(/\$[\d,]+/g);
      console.log(`💰 Price mentions found: ${listingMatches ? listingMatches.length : 0}`);
      
      // Show sample content
      console.log('\n📝 Sample content (first 1000 chars):');
      console.log(content.substring(0, 1000));
      
      // Save to file
      const fs = require('fs').promises;
      const timestamp = Date.now();
      await fs.writeFile(`demo-${timestamp}.json`, JSON.stringify(data, null, 2));
      console.log(`\n💾 Saved to: demo-${timestamp}.json`);
      
    } else {
      console.error('❌ Scraping failed:', response.data.error);
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.response) {
      console.error('Response:', error.response.data);
    }
  }
}

demo();
