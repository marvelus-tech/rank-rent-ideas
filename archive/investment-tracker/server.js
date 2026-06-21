const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const marked = require('marked');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Data directory
const DATA_DIR = path.join(__dirname, 'data');
const OBSIDIAN_DIR = path.join(process.env.HOME, 'Obsidian', 'Penelopi', 'Investments');

// Ensure directories exist
async function ensureDirs() {
  await fs.mkdir(DATA_DIR, { recursive: true });
  await fs.mkdir(OBSIDIAN_DIR, { recursive: true });
}

// Read data file
async function readData(category) {
  const filePath = path.join(DATA_DIR, `${category}.json`);
  try {
    const data = await fs.readFile(filePath, 'utf8');
    return JSON.parse(data);
  } catch {
    return { items: [] };
  }
}

// Write data file
async function writeData(category, data) {
  const filePath = path.join(DATA_DIR, `${category}.json`);
  await fs.writeFile(filePath, JSON.stringify(data, null, 2));
}

// Read Obsidian note
async function readObsidianNote(notePath) {
  const fullPath = path.join(OBSIDIAN_DIR, notePath);
  try {
    const content = await fs.readFile(fullPath, 'utf8');
    return marked.parse(content);
  } catch {
    return '<p>Note not found. Create it in Obsidian.</p>';
  }
}

// API Routes

// Get all items for a category
app.get('/api/:category', async (req, res) => {
  try {
    const data = await readData(req.params.category);
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Add item to category
app.post('/api/:category', async (req, res) => {
  try {
    const data = await readData(req.params.category);
    const newItem = {
      id: `${req.params.category}-${Date.now()}`,
      ...req.body,
      added: new Date().toISOString().split('T')[0]
    };
    data.items.push(newItem);
    await writeData(req.params.category, data);
    res.json(newItem);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update item
app.put('/api/:category/:id', async (req, res) => {
  try {
    const data = await readData(req.params.category);
    const index = data.items.findIndex(item => item.id === req.params.id);
    if (index === -1) {
      return res.status(404).json({ error: 'Item not found' });
    }
    data.items[index] = { ...data.items[index], ...req.body };
    await writeData(req.params.category, data);
    res.json(data.items[index]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete item
app.delete('/api/:category/:id', async (req, res) => {
  try {
    const data = await readData(req.params.category);
    data.items = data.items.filter(item => item.id !== req.params.id);
    await writeData(req.params.category, data);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get Obsidian note
app.get('/api/note/:path(*)', async (req, res) => {
  try {
    const html = await readObsidianNote(req.params.path);
    res.json({ html });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Initialize and start
ensureDirs().then(() => {
  app.listen(PORT, () => {
    console.log(`Investment Tracker running on http://localhost:${PORT}`);
    console.log(`Data directory: ${DATA_DIR}`);
    console.log(`Obsidian directory: ${OBSIDIAN_DIR}`);
  });
});
