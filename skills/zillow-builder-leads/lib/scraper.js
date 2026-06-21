const axios = require('axios');
const cheerio = require('cheerio');
require('dotenv').config();

const FIRECRAWL_API_KEY = process.env.FIRECRAWL_API_KEY;
const FIRECRAWL_BASE_URL = 'https://api.firecrawl.dev/v1';

/**
 * Scrape Zillow for builder leads
 * @param {string} city - City name
 * @param {string} state - State abbreviation
 * @param {number} days - Number of days back to search (default 365)
 * @param {boolean} enrich - Whether to enrich with contact info
 */
async function findBuilders(city, state, days = 365, enrich = false) {
  console.log(`🔍 Searching for builders in ${city}, ${state} (past ${days} days)...`);
  
  const builders = new Map();
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);
  
  // Step 1: Scrape Zillow sold listings
  const soldListings = await scrapeSoldListings(city, state, days);
  console.log(`📊 Found ${soldListings.length} sold listings`);
  
  // Step 2: Identify builders from listings
  for (const listing of soldListings) {
    const builderName = extractBuilderName(listing);
    if (builderName) {
      if (!builders.has(builderName)) {
        builders.set(builderName, {
          name: builderName,
          homesSold: 0,
          priceRange: { min: Infinity, max: 0 },
          cities: new Set(),
          listings: [],
          contact: {}
        });
      }
      
      const builder = builders.get(builderName);
      builder.homesSold++;
      builder.cities.add(listing.city || city);
      
      if (listing.price) {
        builder.priceRange.min = Math.min(builder.priceRange.min, listing.price);
        builder.priceRange.max = Math.max(builder.priceRange.max, listing.price);
      }
      
      builder.listings.push(listing);
    }
  }
  
  // Step 3: Enrich with contact info if requested
  if (enrich) {
    console.log('🔍 Enriching builder contact information...');
    for (const [name, builder] of builders) {
      builder.contact = await enrichBuilderContact(name, city, state);
    }
  }
  
  // Step 4: Format output
  const results = Array.from(builders.values()).map(b => ({
    name: b.name,
    homesSold: b.homesSold,
    priceRange: b.priceRange.min === Infinity ? 'Unknown' : `$${formatPrice(b.priceRange.min)} - $${formatPrice(b.priceRange.max)}`,
    cities: Array.from(b.cities),
    contact: b.contact,
    listings: b.listings.map(l => ({
      address: l.address,
      price: l.price ? `$${formatPrice(l.price)}` : 'Unknown',
      soldDate: l.soldDate,
      beds: l.beds,
      baths: l.baths,
      sqft: l.sqft,
      url: l.url
    }))
  }));
  
  // Sort by homes sold (descending)
  results.sort((a, b) => b.homesSold - a.homesSold);
  
  return {
    searchParams: { city, state, days, enrich },
    totalBuilders: results.length,
    totalHomes: soldListings.length,
    builders: results
  };
}

/**
 * Scrape Zillow sold listings using Firecrawl
 */
async function scrapeSoldListings(city, state, days) {
  const listings = [];
  
  // Try multiple Zillow URL patterns
  const urls = [
    `https://www.zillow.com/${city.toLowerCase().replace(/\s+/g, '-')}-${state.toLowerCase()}/sold/`,
    `https://www.zillow.com/homes/${city}_${state}_rb/`,
    `https://www.zillow.com/${city.toLowerCase().replace(/\s+/g, '-')}-${state.toLowerCase()}/`
  ];
  
  for (const url of urls) {
    try {
      console.log(`🌐 Scraping: ${url}`);
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
        const extracted = extractListingsFromContent(response.data.data, city, state);
        listings.push(...extracted);
        
        if (listings.length > 0) break; // Stop if we found listings
      }
    } catch (error) {
      console.error(`❌ Error scraping ${url}:`, error.message);
    }
  }
  
  return listings;
}

/**
 * Extract listings from scraped content
 */
function extractListingsFromContent(data, city, state) {
  const listings = [];
  const content = data.markdown || data.html || '';
  
  // Parse with cheerio if HTML available
  const $ = data.html ? cheerio.load(data.html) : null;
  
  if ($) {
    // Look for listing cards
    $('article[data-testid="property-card"], .list-card, .photo-cards_photo-card').each((i, el) => {
      const $el = $(el);
      
      const listing = {
        address: $el.find('[data-testid="property-card-address"], .list-card-address').text().trim(),
        price: parsePrice($el.find('[data-testid="property-card-price"], .list-card-price').text()),
        beds: parseNumber($el.find('[data-testid="property-card-beds"]').text()),
        baths: parseNumber($el.find('[data-testid="property-card-baths"]').text()),
        sqft: parseNumber($el.find('[data-testid="property-card-sqft"]').text()),
        city: city,
        state: state,
        soldDate: extractSoldDate($el.text()),
        url: $el.find('a').attr('href') || '',
        description: $el.text()
      };
      
      if (listing.address && listing.price) {
        listings.push(listing);
      }
    });
  }
  
  // Fallback: regex extraction from markdown
  if (listings.length === 0 && content) {
    const lines = content.split('\n');
    for (const line of lines) {
      // Look for patterns like "$500,000 · 3 bds · 2 ba · 1,500 sqft"
      const match = line.match(/\$([\d,]+)\s*·\s*(\d+)\s*bds?\s*·\s*(\d+)\s*ba\s*·\s*([\d,]+)\s*sqft/);
      if (match) {
        listings.push({
          address: line.split('·')[0].trim(),
          price: parseInt(match[1].replace(/,/g, '')),
          beds: parseInt(match[2]),
          baths: parseInt(match[3]),
          sqft: parseInt(match[4].replace(/,/g, '')),
          city: city,
          state: state,
          soldDate: extractSoldDate(line),
          description: line
        });
      }
    }
  }
  
  return listings;
}

/**
 * Extract builder name from listing
 */
function extractBuilderName(listing) {
  const text = (listing.description || '') + ' ' + (listing.address || '');
  
  // Common builder name patterns
  const builderPatterns = [
    /by\s+([A-Z][a-zA-Z\s]+(?:Homes|Builders|Construction|Development|Properties|Group|LLC|Inc\.?))/i,
    /([A-Z][a-zA-Z\s]+(?:Homes|Builders|Construction|Development|Properties|Group|LLC|Inc\.?))\s+community/i,
    /(?:Lennar|D\.?R\.?\s+Horton|Pulte|Taylor\s+Morrison|KB\s+Home|Meritage|Perry\s+Homes|David\s+Weekley|Highland|Wilshire|CalAtlantic|Beazer|Centex|Ryan|NVR|Rausch\s+Coleman|LGI|HistoryMaker|First\s+Texas|Bloomfield|CastleRock|Tri\s+Pointe|Woodside| Plantation|Grand\s+Homes|Shaddock|Britton|Jefferson|Drees|Coventry|K\s+Hovnanian|Mattamy|Ryan|M/I|Drees|Wilshire|Wade\s+Jurney|Adams|Ashton\s+Woods|Belmont|Brookfield|Chesmar|Dunhill|Empire|Gehan|HistoryMaker|Ivory|J\s+Patrick|K\s+B|Lennar|MainVue|Meritage|Newmark|Perry|Plantation|Pulte|Ryland|Shaddock|Taylor\s+Morrison|Trendmaker|Village|Westin|Wilshire|Woodside)/i
  ];
  
  for (const pattern of builderPatterns) {
    const match = text.match(pattern);
    if (match) {
      return match[1] || match[0];
    }
  }
  
  // Check if it's a known builder from community name
  if (listing.address) {
    const communityMatch = listing.address.match(/at\s+([A-Z][a-zA-Z\s]+)/);
    if (communityMatch) {
      return communityMatch[1].trim();
    }
  }
  
  return null;
}

/**
 * Enrich builder with contact information
 */
async function enrichBuilderContact(builderName, city, state) {
  const contact = {
    phone: null,
    website: null,
    email: null,
    address: null
  };
  
  // Try to find builder website
  const searchQueries = [
    `${builderName} ${city} ${state} builder contact`,
    `${builderName} official website`,
    `${builderName} phone number`
  ];
  
  for (const query of searchQueries) {
    try {
      // Use Firecrawl to search
      const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
      const response = await axios.post(`${FIRECRAWL_BASE_URL}/scrape`, {
        url: searchUrl,
        formats: ['markdown'],
        onlyMainContent: true
      }, {
        headers: {
          'Authorization': `Bearer ${FIRECRAWL_API_KEY}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data.success) {
        const content = response.data.data.markdown || '';
        
        // Extract phone
        const phoneMatch = content.match(/\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/);
        if (phoneMatch && !contact.phone) contact.phone = phoneMatch[0];
        
        // Extract website
        const websiteMatch = content.match(/https?:\/\/[^\s\"]+\.(com|net|org)/);
        if (websiteMatch && !contact.website) contact.website = websiteMatch[0];
        
        // Extract email
        const emailMatch = content.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
        if (emailMatch && !contact.email) contact.email = emailMatch[0];
      }
    } catch (error) {
      console.error(`❌ Error enriching ${builderName}:`, error.message);
    }
  }
  
  return contact;
}

// Helper functions
function parsePrice(text) {
  if (!text) return null;
  const match = text.replace(/[^\d]/g, '');
  return match ? parseInt(match) : null;
}

function parseNumber(text) {
  if (!text) return null;
  const match = text.match(/(\d+)/);
  return match ? parseInt(match[1]) : null;
}

function extractSoldDate(text) {
  if (!text) return null;
  const match = text.match(/(Sold|Closed)\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})/i);
  return match ? match[2] : null;
}

function formatPrice(price) {
  if (price >= 1000000) {
    return (price / 1000000).toFixed(1) + 'M';
  } else if (price >= 1000) {
    return (price / 1000).toFixed(0) + 'K';
  }
  return price.toString();
}

module.exports = {
  findBuilders,
  scrapeSoldListings,
  extractBuilderName,
  enrichBuilderContact
};
