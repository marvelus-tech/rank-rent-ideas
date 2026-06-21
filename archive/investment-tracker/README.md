# Investment Tracker

Track your investment ideas, business opportunities, and strategic insights — all synced with Obsidian.

## Features

- **5 Categories**: Stocks, Crypto, Business Niches, Business Models, Insights
- **Obsidian Integration**: Each item links to an Obsidian note for detailed analysis
- **Presentation Mode**: Clean, full-screen view for showcasing to friends
- **Status Tracking**: Researching → Tracking → Invested → Exited
- **Tag System**: Organize by themes (solana, ai, rank-and-rent, etc.)

## Quick Start

```bash
cd ~/.openclaw/workspace/investment-tracker
npm install
npm start
```

Open http://localhost:3001

## Usage

### Adding Items
1. Click "+ Add Item"
2. Fill in details (name, ticker, status, tags, notes)
3. Link to an Obsidian note (e.g., `Investments/Stocks/TSLA.md`)
4. Save

### Obsidian Integration
- Click any item to see details
- Obsidian notes render as markdown in the sidebar
- Click "Open in Obsidian" to edit the note

### Presentation Mode
- Click "Present" button in header
- Hides chrome, shows items in clean grid
- Perfect for showcasing to friends

### Keyboard Shortcuts
- `Esc` — Close modal
- `Ctrl+P` — Toggle presentation mode

## Data Structure

Items are stored in `data/` as JSON:
- `stocks.json` — Stock ideas
- `crypto.json` — Crypto investments
- `niches.json` — Business niches
- `models.json` — Business models
- `insights.json` — Strategic insights

## Obsidian Vault

Create notes in `~/Obsidian/Penelopi/Investments/`:
```
Investments/
├── Stocks/
│   └── TSLA.md
├── Crypto/
│   └── SOL.md
├── Niches/
│   └── Plumbing-San-Antonio.md
├── Models/
│   └── AI-Agency.md
└── Insights/
    └── Wyoming-LLC.md
```

## API Endpoints

- `GET /api/:category` — List items
- `POST /api/:category` — Add item
- `PUT /api/:category/:id` — Update item
- `DELETE /api/:category/:id` — Delete item
- `GET /api/note/:path` — Get Obsidian note as HTML

## Tech Stack

- **Backend**: Node.js + Express
- **Frontend**: Vanilla JS + CSS Grid
- **Markdown**: marked.js
- **Styling**: Custom CSS with CSS variables

## License

MIT
