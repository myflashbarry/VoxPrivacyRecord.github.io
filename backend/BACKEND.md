# Backend Documentation

Detailed documentation for the VoxPrivacyRecord backend API server.

## Architecture

### Technology Stack
- **Framework:** FastAPI (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **Audio Processing:** ffmpeg
- **CORS:** Enabled for cross-origin requests

### Components

1. **main.py** - FastAPI application and API endpoints
2. **database.py** - SQLAlchemy models and database operations
3. **data_loader.py** - JSONL data file loading and caching
4. **task_manager.py** - Task assignment logic
5. **audio_utils.py** - Audio conversion utilities
6. **config.py** - Configuration management

## API Endpoints

### Health Check

**GET /**

Check if the API is running.

**Response:**
```json
{
  "status": "ok",
  "message": "VoxPrivacyRecord API is running",
  "ffmpeg_available": true
}
```

### User Login

**POST /api/login**

Create or retrieve a user.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `username` (string)

**Response:**
```json
{
  "username": "alice",
  "progress": {
    "zh_pairs_done": 5,
    "en_pairs_done": 3,
    "zh_extra_questions_done": 2,
    "en_extra_questions_done": 1
  }
}
```

### Get Next Task

**GET /api/next_task**

Get the next recording task for a user.

**Query Parameters:**
- `username` (required): The username

**Response:**
```json
{
  "username": "alice",
  "task": {
    "language": "zh",
    "task_type": "pair",
    "role": "secret",
    "item_id": "B0000_I01_P000000",
    "text": "我在工作中假装自己是无神论者，但每晚睡前都会祈祷。"
  },
  "progress": {
    "zh_pairs_done": 5,
    "en_pairs_done": 3,
    "zh_extra_questions_done": 2,
    "en_extra_questions_done": 1
  }
}
```

When all tasks complete:
```json
{
  "username": "alice",
  "task": null,
  "progress": { ... },
  "message": "All tasks completed! Thank you for your participation."
}
```

### Upload Recording

**POST /api/upload_recording**

Upload an audio recording.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `username` (string)
  - `language` (string): "zh" or "en"
  - `task_type` (string): "pair" or "extra_question"
  - `role` (string): "secret" or "question"
  - `item_id` (string)
  - `audio` (file): Audio file (typically WebM from browser)

**Response:**
```json
{
  "status": "ok",
  "file_path": "recordings/user-alice__lang-zh__type-pair__role-secret__item-123__ts-20251115T101530.wav",
  "filename": "user-alice__lang-zh__type-pair__role-secret__item-123__ts-20251115T101530.wav",
  "progress": {
    "zh_pairs_done": 6,
    "en_pairs_done": 3,
    "zh_extra_questions_done": 2,
    "en_extra_questions_done": 1
  },
  "message": "Recording uploaded successfully"
}
```

### Export Metadata (Admin)

**GET /api/admin/export_metadata**

Export all recording metadata as JSON.

**Response:**
```json
{
  "total_recordings": 150,
  "recordings": [
    {
      "id": 1,
      "username": "alice",
      "language": "zh",
      "task_type": "pair",
      "role": "secret",
      "item_id": "B0000_I01_P000000",
      "file_path": "recordings/user-alice__...",
      "created_at": "2025-11-15T10:15:30"
    },
    ...
  ]
}
```

### User Statistics (Admin)

**GET /api/admin/user_stats**

Get progress statistics for all users.

**Response:**
```json
{
  "total_users": 10,
  "users": [
    {
      "username": "alice",
      "created_at": "2025-11-15T09:00:00",
      "progress": {
        "zh_pairs_done": 20,
        "en_pairs_done": 20,
        "zh_extra_questions_done": 10,
        "en_extra_questions_done": 10
      }
    },
    ...
  ]
}
```

## Task Assignment Logic

### Priority Order

1. **Chinese pairs** (until 20 completed)
2. **English pairs** (until 20 completed)
3. **Chinese extra questions** (until 10 completed)
4. **English extra questions** (until 10 completed)

### Pair Logic

A "pair" consists of:
1. Recording of `secret_text`
2. Recording of `question_for_secret` for the **same item**

The system:
- Assigns `secret_text` first for a new item
- Remembers which item is incomplete
- Assigns `question_for_secret` for the same item next
- Only counts as complete when both are done

### Sampling Strategy

- Items are randomly selected from available pool
- Items already used by the user are avoided when possible
- If all items exhausted, items are reused
- Different users can record the same items (this is expected)

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Recordings Table

```sql
CREATE TABLE recordings (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    language TEXT NOT NULL,
    task_type TEXT NOT NULL,
    role TEXT NOT NULL,
    item_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username)
);
```

## Audio Processing

### Input Format
- Typically WebM with Opus codec (from browser MediaRecorder)
- Other formats supported by ffmpeg also work

### Output Format
- **Codec:** PCM 16-bit little-endian
- **Sample Rate:** 16 kHz
- **Channels:** Mono (1 channel)
- **Container:** WAV
- **Extension:** `.wav`

### Conversion Command
```bash
ffmpeg -i input.webm -acodec pcm_s16le -ar 16000 -ac 1 output.wav
```

### Filename Convention
```
user-{username}__lang-{zh|en}__type-{pair|extraQ}__role-{secret|question}__item-{item_id}__ts-{timestamp}.wav
```

Examples:
- `user-alice__lang-zh__type-pair__role-secret__item-B0000_I01_P000000__ts-20251115T101530.wav`
- `user-bob__lang-en__type-extraQ__role-question__item-B0000_I02_P000001__ts-20251115T143022.wav`

## Configuration

### Environment Variables

**API_CORS_ORIGINS**
- Comma-separated list of allowed origins
- Default: `*` (allow all)
- Production: Set to your frontend URL(s)

**RECORDINGS_DIR**
- Directory for audio files
- Default: `recordings/` (relative to backend/)

**DB_PATH**
- SQLite database file path
- Default: `db.sqlite3` (relative to backend/)

**ZH_JSONL_PATH**
- Path to Chinese data file
- Default: `../source/deepseek_secret_filter_results_filtered_zh.jsonl`

**EN_JSONL_PATH**
- Path to English data file
- Default: `../source/deepseek_secret_filter_results_filtered_en.jsonl`

### Example .env
```env
API_CORS_ORIGINS=https://yourusername.github.io,http://localhost:5173
RECORDINGS_DIR=recordings
DB_PATH=db.sqlite3
ZH_JSONL_PATH=../source/deepseek_secret_filter_results_filtered_zh.jsonl
EN_JSONL_PATH=../source/deepseek_secret_filter_results_filtered_en.jsonl
```

## Running the Backend

### Development Mode
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using the Script
```bash
cd backend
./run.sh          # macOS/Linux
# OR
run.bat           # Windows
```

## Testing

### Manual Testing

```bash
# Health check
curl http://localhost:8000/

# Login
curl -X POST http://localhost:8000/api/login -F "username=testuser"

# Get next task
curl "http://localhost:8000/api/next_task?username=testuser"

# Upload recording (with actual file)
curl -X POST http://localhost:8000/api/upload_recording \
  -F "username=testuser" \
  -F "language=zh" \
  -F "task_type=pair" \
  -F "role=secret" \
  -F "item_id=B0000_I01_P000000" \
  -F "audio=@test.webm"
```

### Database Queries

```bash
# Open database
sqlite3 backend/db.sqlite3

# List all users
SELECT * FROM users;

# Count recordings per user
SELECT username, COUNT(*) as count 
FROM recordings 
GROUP BY username;

# View recent recordings
SELECT * FROM recordings 
ORDER BY created_at DESC 
LIMIT 10;

# Exit
.quit
```

## Troubleshooting

### "ffmpeg not found"
- Install ffmpeg
- Verify: `ffmpeg -version`
- Restart backend

### "CORS error"
- Check `API_CORS_ORIGINS` in .env
- Include exact frontend URL
- Restart backend after changes

### "Database locked"
- Close any SQLite browser/editor
- Only one process should write at a time
- For production, consider PostgreSQL

### Recordings not saving
- Check disk space: `df -h`
- Verify directory exists and is writable
- Check backend logs for errors

### Large file uploads failing
- Default FastAPI limit: 2GB
- Network timeout: Increase if needed
- Consider chunked uploads for very large files

## Performance Optimization

### For More Users

1. **Use multiple workers:**
   ```bash
   uvicorn main:app --workers 4
   ```

2. **Use production ASGI server:**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Database optimization:**
   - Add indexes if many users
   - Consider PostgreSQL for >1000 users

4. **Storage optimization:**
   - Use cloud storage (S3, R2, etc.)
   - Stream uploads directly

### Monitoring

- Check logs: `uvicorn` outputs to stdout
- Monitor disk usage: `du -sh recordings/`
- Watch database size: `ls -lh db.sqlite3`

## Security Considerations

1. **No authentication** - Username only
   - Fine for research with trusted participants
   - Add JWT tokens for public deployment

2. **File upload validation:**
   - Currently accepts any audio file
   - Add size limits if needed
   - Validate audio format if needed

3. **Rate limiting:**
   - Not implemented
   - Add for public deployments

4. **CORS:**
   - Set specific origins in production
   - Avoid `*` in production

## Data Export

### Export recordings metadata
```bash
curl http://localhost:8000/api/admin/export_metadata > metadata.json
```

### Backup database
```bash
cp db.sqlite3 backups/db-$(date +%Y%m%d).sqlite3
```

### Backup recordings
```bash
tar -czf backups/recordings-$(date +%Y%m%d).tar.gz recordings/
```

### CSV Export
```python
import sqlite3
import csv

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute('SELECT * FROM recordings')

with open('recordings.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(cursor.fetchall())
```

---

For frontend documentation, see [frontend/README.md](../frontend/README.md).
For deployment instructions, see [DEPLOYMENT.md](../DEPLOYMENT.md).

