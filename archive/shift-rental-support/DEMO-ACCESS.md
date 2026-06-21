# Quick Start - SHIFT Rental Support Demo

## For Your Colleague (The Easy Way)

### Option 1: Cloudflare Tunnel (Recommended - No signup needed)

1. **Install Cloudflare Tunnel** (one-time):
   ```bash
   brew install cloudflare/cloudflare/cloudflared
   ```

2. **Start the demo**:
   ```bash
   cd ~/.openclaw/workspace/shift-rental-support
   ./start-with-cloudflare.sh
   ```

3. **Share the public URL** that appears (looks like `https://abc123.trycloudflare.com`)

### Option 2: ngrok (If you have an account)

1. **Install ngrok** (one-time):
   ```bash
   brew install ngrok
   ngrok config add-authtoken YOUR_TOKEN  # Get token from ngrok.com
   ```

2. **Start the demo**:
   ```bash
   cd ~/.openclaw/workspace/shift-rental-support
   ./start-with-ngrok.sh
   ```

3. **Share the public URL** that appears (looks like `https://abc123.ngrok.io`)

---

## What They'll See

- **Landing page**: https://your-url.trycloudflare.com/
- **Support chat**: https://your-url.trycloudflare.com/support

The chatbot has knowledge of a 40-vehicle rental fleet and can answer questions about:
- Available vehicles (SUVs, vans, utes, trucks)
- Pricing and quotes
- Rental policies
- Vehicle specifications

---

## To Stop

Press **Ctrl+C** — this stops both the server and the tunnel.

---

## Troubleshooting

**Port 3000 in use?**
```bash
kill $(lsof -nP -t -iTCP:3000 -sTCP:LISTEN)
```

**Dependencies missing?**
```bash
cd ~/.openclaw/workspace/shift-rental-support
npm install
```
