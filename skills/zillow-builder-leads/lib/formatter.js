const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const fs = require('fs').promises;

/**
 * Format builder leads as JSON
 */
function formatAsJSON(data) {
  return JSON.stringify(data, null, 2);
}

/**
 * Format builder leads as CSV
 */
async function formatAsCSV(data, outputPath) {
  const csvWriter = createCsvWriter({
    path: outputPath,
    header: [
      { id: 'name', title: 'Builder Name' },
      { id: 'homesSold', title: 'Homes Sold' },
      { id: 'priceRange', title: 'Price Range' },
      { id: 'cities', title: 'Cities' },
      { id: 'phone', title: 'Phone' },
      { id: 'website', title: 'Website' },
      { id: 'email', title: 'Email' },
      { id: 'sampleAddress', title: 'Sample Address' },
      { id: 'samplePrice', title: 'Sample Price' }
    ]
  });

  const records = data.builders.map(b => ({
    name: b.name,
    homesSold: b.homesSold,
    priceRange: b.priceRange,
    cities: b.cities.join(', '),
    phone: b.contact?.phone || '',
    website: b.contact?.website || '',
    email: b.contact?.email || '',
    sampleAddress: b.listings[0]?.address || '',
    samplePrice: b.listings[0]?.price || ''
  }));

  await csvWriter.writeRecords(records);
  return outputPath;
}

/**
 * Format as markdown report
 */
function formatAsMarkdown(data) {
  let md = `# Builder Leads Report\n\n`;
  md += `**Search:** ${data.searchParams.city}, ${data.searchParams.state}\n`;
  md += `**Time Period:** Past ${data.searchParams.days} days\n`;
  md += `**Total Builders:** ${data.totalBuilders}\n`;
  md += `**Total Homes:** ${data.totalHomes}\n\n`;
  md += `---\n\n`;

  for (const builder of data.builders) {
    md += `## ${builder.name}\n\n`;
    md += `- **Homes Sold:** ${builder.homesSold}\n`;
    md += `- **Price Range:** ${builder.priceRange}\n`;
    md += `- **Cities:** ${builder.cities.join(', ')}\n`;
    
    if (builder.contact?.phone) {
      md += `- **Phone:** ${builder.contact.phone}\n`;
    }
    if (builder.contact?.website) {
      md += `- **Website:** ${builder.contact.website}\n`;
    }
    if (builder.contact?.email) {
      md += `- **Email:** ${builder.contact.email}\n`;
    }
    
    md += `\n### Recent Sales\n\n`;
    for (const listing of builder.listings.slice(0, 3)) {
      md += `- ${listing.address} — ${listing.price} (${listing.soldDate || 'Date unknown'})\n`;
    }
    
    md += `\n---\n\n`;
  }

  return md;
}

/**
 * Save output in multiple formats
 */
async function saveOutput(data, basePath) {
  const outputs = {};
  
  // JSON
  const jsonPath = `${basePath}.json`;
  await fs.writeFile(jsonPath, formatAsJSON(data));
  outputs.json = jsonPath;
  
  // CSV
  const csvPath = `${basePath}.csv`;
  await formatAsCSV(data, csvPath);
  outputs.csv = csvPath;
  
  // Markdown
  const mdPath = `${basePath}.md`;
  await fs.writeFile(mdPath, formatAsMarkdown(data));
  outputs.markdown = mdPath;
  
  return outputs;
}

module.exports = {
  formatAsJSON,
  formatAsCSV,
  formatAsMarkdown,
  saveOutput
};
