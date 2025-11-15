# VoxPrivacyRecord - Speech Data Collection System

A complete web-based system for collecting human speech recordings for privacy research in Speech Language Models (SLMs). Built for ICLR 2026 paper on interactional privacy.

## 📋 Overview

This system allows multiple participants to:
- Record speech samples via a web interface (GitHub Pages)
- Submit audio recordings to a backend server
- Track progress across multiple recording tasks

### Recording Requirements per User

Each participant needs to record:
- **20 Chinese pairs** (secret text + question) = 40 recordings
- **20 English pairs** (secret text + question) = 40 recordings  
- **10 extra Chinese questions** = 10 recordings
- **10 extra English questions** = 10 recordings

**Total: 100 recordings per participant**

## 🏗️ Architecture

### Frontend (`frontend/`)
- **Tech Stack**: React + TypeScript + Vite
- **Deployment**: Static site on GitHub Pages
- **Features**: 
  - User login/identification
  - Browser-based audio recording (MediaRecorder API)
  - Progress tracking
  - Real-time task assignment

### Backend (`backend/`)
- **Tech Stack**: Python + FastAPI
- **Storage**: 
  - Audio files: WAV format (converted from WebM)
  - Metadata: SQLite database
- **Features**:
  - REST API for task management
  - Audio format conversion (WebM → WAV via ffmpeg)
  - Progress tracking per user
  - Intelligent task assignment

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** (for backend)
2. **Node.js 18+** and npm (for frontend)
3. **ffmpeg** (for audio conversion)

#### Install ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment (optional):**
```bash
cp .env.example .env
# Edit .env if needed
```

5. **Run the backend server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**API Documentation:** Visit `http://localhost:8000/docs` for interactive API docs.

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure API URL:**
```bash
cp .env.example .env
```

Edit `.env` and set the backend URL:
```env
VITE_API_BASE_URL=http://localhost:8000
```

4. **Run development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

5. **Build for production:**
```bash
npm run build
```

The production build will be in `frontend/dist/`

## 📁 File Naming Convention

Audio files are saved with structured filenames for easy organization:

```
user-{username}__lang-{zh|en}__type-{pair|extraQ}__role-{secret|question}__item-{item_id}__ts-{timestamp}.wav
```

### Examples:
- `user-Alice__lang-zh__type-pair__role-secret__item-37__ts-20251115T101530.wav`
- `user-Bob__lang-en__type-extraQ__role-question__item-89__ts-20251115T102030.wav`

This naming scheme allows you to easily:
- Filter by user
- Group by item_id (for A/B testing)
- Separate secret vs question recordings
- Identify pair vs extra-question recordings

## 🌐 Deployment

### Deploy Backend

The backend needs to be deployed on a server with Python and ffmpeg support. Options:

#### Option 1: Render.com (Recommended)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render dashboard
6. Deploy!

**Note:** Add build pack for ffmpeg on Render (see [Render docs](https://render.com/docs/native-runtimes))

#### Option 2: Railway.app

1. Create new project from GitHub repo
2. Configure root directory to `backend/`
3. Railway will auto-detect Python and install dependencies
4. Add ffmpeg buildpack
5. Deploy!

#### Option 3: Your Own Server

1. Clone repository to server
2. Install Python, ffmpeg, and dependencies
3. Use systemd or supervisor to run as a service
4. Set up nginx as reverse proxy
5. Configure SSL certificate (Let's Encrypt)

### Deploy Frontend (GitHub Pages)

1. **Build the frontend:**
```bash
cd frontend
npm run build
```

2. **Update `vite.config.ts` base path** (if needed):
```typescript
export default defineConfig({
  base: '/VoxPrivacyRecord.github.io/', // Your repo name
  // ...
})
```

3. **Deploy options:**

**Option A: Manual deployment**
```bash
# Copy dist/ contents to a gh-pages branch
git subtree push --prefix frontend/dist origin gh-pages
```

**Option B: Using gh-pages package**
```bash
npm install -g gh-pages
gh-pages -d frontend/dist
```

**Option C: GitHub Actions (automated)**

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install and Build
        run: |
          cd frontend
          npm install
          npm run build
      
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./frontend/dist
```

4. **Configure GitHub Pages:**
- Go to repository Settings → Pages
- Source: Deploy from branch
- Branch: `gh-pages` / root
- Save

5. **Update frontend .env for production:**
```env
VITE_API_BASE_URL=https://your-backend-url.com
```

Rebuild and redeploy after changing the API URL.

## 🔧 Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# CORS Configuration (required for GitHub Pages)
API_CORS_ORIGINS=https://yourusername.github.io

# Storage paths (optional, defaults work fine)
# RECORDINGS_DIR=recordings
# DB_PATH=db.sqlite3

# Data files (optional if using default locations)
# ZH_JSONL_PATH=../source/deepseek_secret_filter_results_filtered_zh.jsonl
# EN_JSONL_PATH=../source/deepseek_secret_filter_results_filtered_en.jsonl
```

### Frontend Configuration

Edit `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000  # Local dev
# VITE_API_BASE_URL=https://your-backend.onrender.com  # Production
```

## 📊 Data Management

### Export Metadata

Get all recording metadata as JSON:

```bash
curl http://localhost:8000/api/admin/export_metadata
```

Or visit in browser: `http://localhost:8000/api/admin/export_metadata`

### View User Statistics

```bash
curl http://localhost:8000/api/admin/user_stats
```

### Database Location

SQLite database: `backend/db.sqlite3`

You can query it directly:
```bash
sqlite3 backend/db.sqlite3
```

### Audio Files Location

All recordings: `backend/recordings/`

## 🎯 Usage Flow

1. **Participant opens the web page**
2. **Enters their username** (no password required)
3. **System assigns first task** based on quotas:
   - Priority: Chinese pairs → English pairs → Chinese extra → English extra
4. **Participant reads text and records**
5. **Reviews recording** (optional playback)
6. **Submits recording** → uploads to backend
7. **Backend converts audio** (WebM → WAV) and stores
8. **System assigns next task** automatically
9. **Repeat until all 100 recordings complete**
10. **Completion message** displayed

## 🔍 API Endpoints

### `POST /api/login`
Login or create user
- **Body:** `username` (form data)
- **Response:** User info + progress

### `GET /api/next_task?username={username}`
Get next recording task
- **Response:** Task details + progress

### `POST /api/upload_recording`
Upload audio recording
- **Body:** Multipart form with username, language, task_type, role, item_id, audio file
- **Response:** Success status + updated progress

### `GET /api/admin/export_metadata`
Export all recording metadata (JSON)

### `GET /api/admin/user_stats`
Get statistics for all users

## 📝 Research Use

After collecting recordings, you can:

1. **Construct A-B scenarios:**
   - User A speaks secret + question
   - User B speaks same question (from extra recordings)
   - Test if SLM leaks secret from A to B

2. **Analyze by item_id:**
   - Group all recordings of same item
   - Compare different speakers
   - Test privacy leakage patterns

3. **Filter recordings:**
```bash
# All recordings for a user
ls backend/recordings/user-Alice__*

# All recordings for a specific item
ls backend/recordings/*__item-37__*

# All secret recordings
ls backend/recordings/*__role-secret__*
```

## 🛠️ Troubleshooting

### "ffmpeg not found" error
- Install ffmpeg (see Prerequisites)
- Verify: `ffmpeg -version`

### "Cannot connect to backend"
- Check backend is running: `curl http://localhost:8000/`
- Check CORS settings in `backend/.env`
- Check firewall/network settings

### Microphone not working
- Grant browser microphone permissions
- Try different browser (Chrome/Firefox recommended)
- Check system microphone settings

### Audio conversion fails
- Ensure ffmpeg is installed and in PATH
- Check disk space
- Check backend logs for errors

## 📄 Project Structure

```
VoxPrivacyRecord.github.io/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── database.py             # Database models
│   ├── data_loader.py          # JSONL loading
│   ├── task_manager.py         # Task assignment logic
│   ├── audio_utils.py          # Audio conversion
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment template
│   ├── recordings/             # Audio files (created)
│   └── db.sqlite3              # Database (created)
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API services
│   │   ├── types.ts            # TypeScript types
│   │   ├── App.tsx             # Main app
│   │   └── main.tsx            # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── .env.example
├── source/
│   ├── deepseek_secret_filter_results_filtered_zh.jsonl
│   └── deepseek_secret_filter_results_filtered_en.jsonl
├── README.md
└── .gitignore
```

## 📜 License

This project is for research purposes. Please cite appropriately if used in publications.

## 🙋 Support

For issues or questions:
1. Check this README
2. Review API docs at `/docs`
3. Check backend logs
4. Open GitHub issue

## ✅ Checklist for Deployment

- [ ] Install ffmpeg on backend server
- [ ] Set up backend with correct CORS origins
- [ ] Test backend API endpoints
- [ ] Build frontend with production API URL
- [ ] Deploy frontend to GitHub Pages
- [ ] Test end-to-end recording flow
- [ ] Verify audio files are being saved as .wav
- [ ] Check database is recording metadata
- [ ] Test with multiple users
- [ ] Monitor disk space for recordings

---

**Built with ❤️ for Speech Language Model Privacy Research - ICLR 2026**
