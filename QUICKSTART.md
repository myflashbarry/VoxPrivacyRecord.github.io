# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:

```bash
# Check Python (need 3.8+)
python --version

# Check Node.js (need 18+)
node --version

# Check ffmpeg
ffmpeg -version
```

If anything is missing, install:
- **Python:** [python.org](https://python.org)
- **Node.js:** [nodejs.org](https://nodejs.org)
- **ffmpeg:** 
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: [ffmpeg.org/download.html](https://ffmpeg.org/download.html)

## Step 1: Start Backend (Terminal 1)

```bash
# Navigate to backend
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload

# Or use the convenience script:
# ./run.sh        # macOS/Linux
# run.bat         # Windows
```

✅ **Backend running at:** http://localhost:8000

Visit http://localhost:8000/docs to see API documentation.

## Step 2: Start Frontend (Terminal 2)

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Create .env file
cp .env.example .env

# (Optional) Edit .env if backend is not on localhost:8000

# Run development server
npm run dev
```

✅ **Frontend running at:** http://localhost:5173

## Step 3: Test the System

1. **Open browser** to http://localhost:5173

2. **Enter username** (anything, e.g., "testuser")

3. **Allow microphone** when prompted

4. **Read the displayed text** and record

5. **Submit** the recording

6. **Check** that next task loads automatically

7. **Verify files:**
   ```bash
   # In another terminal
   ls backend/recordings/
   # Should see .wav files
   
   sqlite3 backend/db.sqlite3 "SELECT * FROM recordings;"
   # Should see database entries
   ```

## Common Issues

### "Cannot connect to backend"
- Make sure backend is running (Terminal 1)
- Check http://localhost:8000 in browser
- Verify no errors in backend terminal

### "ffmpeg not found"
- Install ffmpeg (see Prerequisites)
- Restart backend after installing

### Microphone not working
- Grant browser permissions when asked
- Try Chrome or Firefox (best support)
- Check system microphone settings

## Next Steps

- **Add more users:** Just use different usernames
- **View progress:** Check http://localhost:8000/api/admin/user_stats
- **Export data:** Visit http://localhost:8000/api/admin/export_metadata
- **Deploy:** See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup

## Development Tips

### Backend

- **Auto-reload enabled:** Code changes restart server automatically
- **View logs:** Check terminal for request logs
- **API docs:** http://localhost:8000/docs (interactive Swagger UI)
- **Database:** Use SQLite browser or CLI to inspect `backend/db.sqlite3`

### Frontend

- **Hot reload:** Changes appear immediately in browser
- **Console:** Open browser DevTools (F12) for debugging
- **API calls:** Check Network tab to see API requests
- **Environment:** Edit `frontend/.env` to change API URL

## File Locations

```
backend/
├── recordings/        # Audio files (WAV format)
├── db.sqlite3         # SQLite database
└── *.py              # Python source code

frontend/
├── src/              # React source code
├── dist/             # Built files (after npm run build)
└── .env              # Configuration
```

## Data Structure

### JSONL Files (source/)
```json
{
  "entry_id": "B0000_I01_P000000",
  "secret_text": "Text to read...",
  "question_for_secret": "Question to ask..."
}
```

### Audio Filenames
```
user-alice__lang-zh__type-pair__role-secret__item-123__ts-20251115T101530.wav
```

### Database Schema
- **users:** username, created_at
- **recordings:** username, language, task_type, role, item_id, file_path, created_at

## Stopping the System

1. **Stop frontend:** Ctrl+C in Terminal 2
2. **Stop backend:** Ctrl+C in Terminal 1
3. **Deactivate venv:** Type `deactivate`

## Full Clean Restart

```bash
# Stop both servers (Ctrl+C)

# Clean backend
cd backend
rm -rf db.sqlite3 recordings/
# Restart backend

# Clean frontend cache
cd frontend
rm -rf node_modules/.vite
# Restart frontend
```

---

**Need help?** Check [README.md](README.md) or [DEPLOYMENT.md](DEPLOYMENT.md) for more details.

**Ready for production?** See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.

