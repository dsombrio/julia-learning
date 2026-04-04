# Deploying TradBot CRM

## Part 1: Backend on Render.com

### 1. Create Render Account
- Go to **render.com**
- Sign up with GitHub (easiest)

### 2. Create PostgreSQL Database
- Click **"New +"** → **"PostgreSQL"**
- Name: `tradbot-crm-db`
- Region: Oregon (free)
- Click **Create Database**
- Wait 30 seconds, then copy the **Connection String** (starts with `postgres://...`)

### 3. Deploy Backend via GitHub

**Create GitHub Repo:**
1. Go to **github.com**
2. Click **"+"** → **"New repository"**
3. Name it `tradbot-crm-backend`
4. Keep it public (free)
5. Click **Create repository**

**Push code to GitHub (on your Mac):**
```bash
cd ~/.openclaw/workspace/crm-backend
git init
git add .
git commit -m "TradBot CRM Backend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tradbot-crm-backend.git
git push -u origin main
```

**Deploy on Render:**
1. Go to **render.com**
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub
4. Select `tradbot-crm-backend` repo
5. Settings:
   - Name: `tradbot-crm`
   - Region: Oregon
   - Branch: main
   - Root Directory: (leave empty)
   - Runtime: Node
   - Build Command: `npm install`
   - Start Command: `npm start`
6. Add Environment Variable:
   - Key: `DATABASE_URL`
   - Value: (paste the PostgreSQL connection string from step 2)
7. Click **Create Web Service**
8. Wait 2-3 minutes for deployment
9. Copy the URL (e.g., `https://tradbot-crm.onrender.com`)

## Part 2: Frontend on Netlify

### Update API URL
Before deploying, update the API URL in `config.js`:
```javascript
const API_CONFIG = {
  apiUrl: 'https://YOUR-RENDER-URL.onrender.com/api'
};
```

### Deploy
1. Go to **app.netlify.com/drop**
2. Drag the `crm-frontend` folder
3. Done! You'll get a URL like `stalwart-lily-9d8f42.netlify.app`

## Part 3: Custom Domain (Optional)

After deployment, you can add a custom domain in Netlify settings.

---

## Cost: $0/month

- Render free tier: 750 hours/month (enough for personal use)
- PostgreSQL free tier: 1 database
- Netlify free tier: unlimited sites
