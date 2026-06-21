# Deploy to GitHub Pages

## Step-by-Step Instructions

### 1. Create a GitHub Repository

Go to https://github.com/new and create a new repository:
- **Name:** `consultation-recorder` (or anything you want)
- **Visibility:** Public (required for free GitHub Pages)
- **Initialize with README:** Yes (optional)

### 2. Upload the Files

**Option A: Web Upload (Easiest)**
1. Go to your new repo on GitHub
2. Click "Add file" → "Upload files"
3. Drag `index.html` into the upload area
4. Click "Commit changes"

**Option B: Command Line**
```bash
# Create a folder for the project
mkdir ~/consultation-recorder
cd ~/consultation-recorder

# Copy the HTML file
cp /Users/oktos/.openclaw/workspace/consultation-recorder/index.html .

# Initialize git repo
git init
git add index.html
git commit -m "Initial commit"

# Connect to GitHub (replace with your username)
git remote add origin https://github.com/YOUR_USERNAME/consultation-recorder.git
git branch -M main
git push -u origin main
```

### 3. Enable GitHub Pages

1. Go to your repo on GitHub
2. Click **Settings** (tab at top)
3. Scroll down to **Pages** section (left sidebar)
4. Under "Source", select **Deploy from a branch**
5. Select **main** branch
6. Click **Save**

### 4. Wait for Deployment

- GitHub will build your site (takes 1-2 minutes)
- Refresh the Pages section
- You'll see: **Your site is live at `https://yourusername.github.io/consultation-recorder`**

### 5. Update the Webhook URL (Important!)

Your HTML already has the ngrok URL. GitHub Pages is HTTPS, so you need:

**Option A: Use a CORS proxy** (Quick workaround)
The webhook runs on HTTP (localhost/ngrok), but GitHub Pages is HTTPS.Browsers block mixed content.

Add this to your HTML before the closing `</body>`:
```javascript
// For GitHub Pages + ngrok backend
// You'll need to handle CORS or use a service like webhook.site temporarily
```

**Option B: Deploy backend too** (Better long-term)
Deploy the Flask server to a free service like:
- **Render.com** (free tier)
- **Railway.app** (free tier)  
- **Heroku** (free tier with credit card)

Then update the WEBHOOK_URL to your deployed backend.

### 6. Share With Clients

Once deployed, your URL will be:
```
https://YOUR_USERNAME.github.io/consultation-recorder
```

**Example:** `https://okeito.github.io/consultation-recorder`

---

## Quick Test Setup (Without Backend Deploy)

If you want to test GitHub Pages NOW without deploying the backend:

1. **Upload just the HTML** to GitHub Pages
2. **Open it locally** for actual recordings (file:// works fine)
3. **Show clients the design** via GitHub Pages URL
4. **Demo functionality** via screen share with local version

---

## Full Production Setup

For a complete client-ready solution:

1. **Frontend:** GitHub Pages (free, permanent)
2. **Backend:** Deploy Flask to Render/Railway (free tier)
3. **Domain:** Use custom domain (optional, ~$10/year)

**Backend deployment to Render:**
```bash
# 1. Create render.yaml in your backend folder
cat > /Users/oktos/.openclaw/workspace/consultation-webhook/render.yaml << 'EOF'
services:
  - type: web
    name: consultation-webhook
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn server:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
EOF

# 2. Push to GitHub
# 3. Connect Render to your GitHub repo
# 4. Render gives you: https://consultation-webhook.onrender.com
```

---

## Summary

| Component | Current | Production |
|-----------|---------|------------|
| Frontend | Local file | GitHub Pages (free) |
| Backend | ngrok (temporary) | Render/Railway (free tier) |
| URL | Changes daily | Permanent custom domain |

**Want me to help with any of these steps?**
- Set up the GitHub repo?
- Deploy to Render?
- Configure custom domain?