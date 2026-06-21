# Signup Agent

Automated business directory signup with NAP (Name, Address, Phone) upload and CAPTCHA notifications.

## Features

- **Automated Signups**: Fills forms for business directories automatically
- **NAP Consistency**: Uses your business profile for consistent information across all directories
- **CAPTCHA Detection**: Pauses execution and notifies you when CAPTCHA is detected
- **Credential Generation**: Creates random usernames and strong passwords
- **Secure Storage**: Saves all credentials to a local JSON file
- **Success Tracking**: Logs results for each directory signup attempt
- **Anti-Detection**: Uses Brave Browser with stealth settings

## Supported Directories

- Yelp
- Angi (Angie's List)
- HomeAdvisor
- Thumbtack
- BBB
- Hotfrog
- Nextdoor
- Apple Maps
- Bing Places

## Installation

```bash
cd signup-agent
npm install
```

## Configuration

### 1. NAP Profile

Edit `config/nap-profile.json` with your business information:

```json
{
  "name": "Your Business Name",
  "category": "Your Category",
  "description": "Your description",
  "website": "https://yoursite.com",
  "email": "you@yoursite.com",
  "phone": "+1-555-555-5555",
  "address": {
    "street": "123 Main St",
    "city": "San Antonio",
    "state": "TX",
    "postcode": "78205",
    "country": "USA"
  }
}
```

### 2. Telegram Notifications (Optional)

Set environment variables for Telegram notifications:

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
```

## Usage

### List available directories
```bash
node cli.js --list
```

### Sign up to a specific directory
```bash
node cli.js --directory "Yelp"
```

### Sign up to all directories
```bash
node cli.js --all
```

## How It Works

1. **Browser Launch**: Opens Brave Browser with anti-detection settings
2. **Form Detection**: Navigates to the signup page and detects form fields
3. **CAPTCHA Check**: If CAPTCHA is detected, sends notification and pauses
4. **Form Filling**: Fills in business information from your NAP profile
5. **Submission**: Submits the form and checks for success
6. **Credential Save**: Saves generated credentials to `storage/credentials.json`

## CAPTCHA Flow

When a CAPTCHA is detected:
1. Agent sends desktop notification + Telegram message
2. Browser window stays open with CAPTCHA visible
3. Agent pauses and waits for you to solve it
4. After solving, agent automatically detects the CAPTCHA is gone
5. Agent continues with the signup process

## Output Files

- `storage/credentials.json` - All generated usernames and passwords
- `logs/signup-results.json` - Success/failure tracking
- `logs/combined.log` - Detailed execution logs

## Security Notes

- Credentials are stored in plain JSON (not encrypted). Keep this file secure.
- The agent runs in non-headless mode so you can see and interact with the browser.
- No external CAPTCHA solving services are used - you solve them manually.

## Troubleshooting

### Browser not launching
- Ensure Brave Browser is installed at `/Applications/Brave Browser.app`
- Or update the path in `signup-agent.js`

### Form fields not found
- Directory sites change their selectors frequently
- Update `config/directories.json` with the correct CSS selectors
- Use browser DevTools to inspect the form fields

### CAPTCHA not detected
- Some CAPTCHAs load dynamically after page load
- The agent checks at multiple points but may miss some
- Manual intervention is always possible

## License

MIT
