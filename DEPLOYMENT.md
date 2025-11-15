# Deployment Guide

This guide provides step-by-step instructions for deploying the VoxPrivacyRecord system to production.

## Prerequisites

- GitHub account with Pages enabled
- Backend hosting service account (Render, Railway, or your own server)
- Domain name (optional)

## Part 1: Deploy Backend

### Option A: Deploy to Render.com (Recommended)

1. **Create account** at [render.com](https://render.com)

2. **Create new Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

3. **Configure the service:**
   - **Name:** `voxprivacyrecord-api` (or your choice)
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables:**
   - Click "Environment" tab
   - Add:
     ```
     API_CORS_ORIGINS=https://yourusername.github.io
     ```

5. **Add ffmpeg buildpack:**
   - In the "Environment" tab, add a build command:
     ```
     apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt
     ```
   - Or use Render's native environment selector and choose one with ffmpeg

6. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment (first deploy takes ~5 minutes)
   - Note your API URL: `https://voxprivacyrecord-api.onrender.com`

7. **Verify deployment:**
   - Visit `https://your-api.onrender.com/`
   - Should see: `{"status": "ok", "message": "VoxPrivacyRecord API is running"}`
   - Check `/docs` for API documentation

### Option B: Deploy to Railway.app

1. **Create account** at [railway.app](https://railway.app)

2. **Create new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your repository

3. **Configure:**
   - Railway will auto-detect Python
   - Click on the service → Settings
   - Set **Root Directory:** `backend`
   - Add environment variables in the Variables tab

4. **Add ffmpeg:**
   - Create `backend/nixpacks.toml`:
     ```toml
     [phases.setup]
     aptPkgs = ["ffmpeg"]
     ```

5. **Deploy:**
   - Railway deploys automatically
   - Get your URL from the "Deployments" tab

### Option C: Your Own Server

1. **SSH to your server**

2. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv ffmpeg nginx certbot
   ```

3. **Clone repository:**
   ```bash
   cd /opt
   sudo git clone https://github.com/yourusername/VoxPrivacyRecord.github.io.git
   cd VoxPrivacyRecord.github.io/backend
   ```

4. **Set up Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/voxprivacy.service
   ```
   
   Content:
   ```ini
   [Unit]
   Description=VoxPrivacyRecord API
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/opt/VoxPrivacyRecord.github.io/backend
   Environment="PATH=/opt/VoxPrivacyRecord.github.io/backend/venv/bin"
   ExecStart=/opt/VoxPrivacyRecord.github.io/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000

   [Install]
   WantedBy=multi-user.target
   ```

6. **Start service:**
   ```bash
   sudo systemctl enable voxprivacy
   sudo systemctl start voxprivacy
   sudo systemctl status voxprivacy
   ```

7. **Configure Nginx:**
   ```bash
   sudo nano /etc/nginx/sites-available/voxprivacy
   ```
   
   Content:
   ```nginx
   server {
       listen 80;
       server_name api.yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

8. **Enable site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/voxprivacy /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

9. **Set up SSL:**
   ```bash
   sudo certbot --nginx -d api.yourdomain.com
   ```

## Part 2: Deploy Frontend

### Step 1: Update Frontend Configuration

1. **Edit `frontend/.env` for production:**
   ```env
   VITE_API_BASE_URL=https://your-backend-url.onrender.com
   ```

2. **If using custom domain, update `vite.config.ts`:**
   ```typescript
   export default defineConfig({
     base: '/', // For custom domain
     // OR
     base: '/VoxPrivacyRecord.github.io/', // For GitHub Pages
   })
   ```

### Step 2: Manual Deployment

1. **Build the frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Deploy to GitHub Pages:**
   ```bash
   # Install gh-pages package
   npm install -g gh-pages

   # Deploy
   gh-pages -d dist
   ```

3. **Configure GitHub Pages:**
   - Go to your repository on GitHub
   - Settings → Pages
   - Source: Deploy from branch
   - Branch: `gh-pages` → `/` (root)
   - Save

4. **Wait 1-2 minutes** and visit:
   `https://yourusername.github.io/VoxPrivacyRecord.github.io/`

### Step 3: Automated Deployment (GitHub Actions)

1. **Add GitHub Secret:**
   - Go to repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `VITE_API_BASE_URL`
   - Value: `https://your-backend-url.onrender.com`
   - Save

2. **The workflow is already in place** at `.github/workflows/deploy-frontend.yml`

3. **Trigger deployment:**
   - Push to `main` branch
   - Or manually: Actions → "Deploy Frontend to GitHub Pages" → "Run workflow"

4. **Monitor deployment:**
   - Go to Actions tab
   - Watch the deployment progress
   - Should complete in 2-3 minutes

## Part 3: Verification

### Test Backend

```bash
# Health check
curl https://your-backend-url.com/

# Should return:
# {"status": "ok", "message": "VoxPrivacyRecord API is running", "ffmpeg_available": true}

# Test login
curl -X POST https://your-backend-url.com/api/login \
  -F "username=testuser"

# Should return user and progress data
```

### Test Frontend

1. **Visit your GitHub Pages URL**
2. **Enter a test username**
3. **Try recording a sample**
4. **Check backend logs** for upload confirmation

### Test End-to-End

1. Open frontend in browser
2. Login with username
3. Record and submit audio
4. Check backend recordings folder:
   ```bash
   ls backend/recordings/
   ```
5. Verify WAV file exists
6. Check database:
   ```bash
   sqlite3 backend/db.sqlite3 "SELECT * FROM recordings;"
   ```

## Part 4: Monitor and Maintain

### Backend Monitoring

**Render:**
- Check Logs tab for errors
- Monitor "Metrics" for usage
- Free tier sleeps after inactivity (30 min warm-up)

**Own Server:**
- Check logs: `sudo journalctl -u voxprivacy -f`
- Monitor disk space: `df -h`
- Check recordings folder size: `du -sh backend/recordings/`

### Frontend Monitoring

- **GitHub Pages status:** Repository → Environments → github-pages
- **Custom domain DNS:** Check your domain registrar

### Backup Data

Regular backups of:
1. **Database:**
   ```bash
   cp backend/db.sqlite3 backups/db-$(date +%Y%m%d).sqlite3
   ```

2. **Recordings:**
   ```bash
   tar -czf backups/recordings-$(date +%Y%m%d).tar.gz backend/recordings/
   ```

## Troubleshooting

### "CORS error" in browser console
- Update backend `API_CORS_ORIGINS` environment variable
- Must include your GitHub Pages URL exactly
- Restart backend after changing

### "Cannot connect to backend"
- Check backend is running and accessible
- Test with curl
- Check firewall rules
- Verify HTTPS (not HTTP) if using SSL

### "ffmpeg not found" in backend logs
- Render: Update build command to install ffmpeg
- Railway: Add nixpacks.toml
- Own server: `sudo apt install ffmpeg`

### Recordings not saving
- Check disk space on backend server
- Verify recordings directory is writable
- Check backend logs for errors

### GitHub Actions failing
- Check Actions tab for error messages
- Verify `VITE_API_BASE_URL` secret is set
- Ensure `gh-pages` branch can be created

## Scaling Considerations

### For More Users

1. **Upgrade backend plan:**
   - Render: Switch to paid plan for better performance
   - Railway: Increase resource limits

2. **Use CDN for frontend:**
   - Cloudflare Pages (instead of GitHub Pages)
   - Better global performance

3. **Optimize storage:**
   - Use cloud storage (S3, R2, etc.) instead of local disk
   - Stream uploads directly to cloud

### For Large Files

1. **Increase upload limits** in FastAPI
2. **Add progress bars** for uploads
3. **Implement chunked uploads**

## Security Recommendations

1. **Add authentication** if needed (JWT tokens)
2. **Rate limit** the API endpoints
3. **Validate file sizes** and formats
4. **Regular backups** of database and recordings
5. **Monitor for abuse** (unusually large files, spam)

## Cost Estimation

### Free Tier (Adequate for Research)
- **Render Free:** Backend hosting (sleeps after inactivity)
- **GitHub Pages:** Frontend hosting (unlimited static sites)
- **Total:** $0/month

### Paid (Better Performance)
- **Render Starter:** $7/month (always-on, better CPU)
- **Railway Hobby:** $5/month (better limits)
- **GitHub Pages:** Free
- **Total:** $5-7/month

### Storage Costs
- 100 recordings/user × 100 KB/recording = ~10 MB/user
- 100 users = ~1 GB total
- Included in free tiers

---

**You're all set! 🚀 Happy data collecting!**

For issues, check the main README or open a GitHub issue.

