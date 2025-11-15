# Project Structure

Complete directory tree and file descriptions for VoxPrivacyRecord.

## Directory Tree

```
VoxPrivacyRecord.github.io/
│
├── README.md                    # Main project documentation
├── QUICKSTART.md               # 5-minute quick start guide
├── DEPLOYMENT.md               # Production deployment guide
├── PROJECT_STRUCTURE.md        # This file
├── .gitignore                  # Git ignore rules
│
├── .github/
│   └── workflows/
│       └── deploy-frontend.yml # GitHub Actions for auto-deployment
│
├── source/                      # Source data files (JSONL)
│   ├── deepseek_secret_filter_results_filtered_zh.jsonl  # Chinese data (200 items)
│   └── deepseek_secret_filter_results_filtered_en.jsonl  # English data (200 items)
│
├── backend/                     # Python FastAPI backend
│   ├── main.py                 # FastAPI application & API endpoints
│   ├── config.py               # Configuration management
│   ├── database.py             # SQLAlchemy models & DB operations
│   ├── data_loader.py          # JSONL data loading
│   ├── task_manager.py         # Task assignment logic
│   ├── audio_utils.py          # Audio conversion (ffmpeg)
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment template
│   ├── run.sh                  # Startup script (macOS/Linux)
│   ├── run.bat                 # Startup script (Windows)
│   ├── BACKEND.md              # Backend documentation
│   ├── recordings/             # Audio files storage (created at runtime)
│   └── db.sqlite3              # SQLite database (created at runtime)
│
└── frontend/                    # React + TypeScript frontend
    ├── index.html              # HTML entry point
    ├── package.json            # NPM dependencies & scripts
    ├── vite.config.ts          # Vite build configuration
    ├── tsconfig.json           # TypeScript configuration
    ├── tsconfig.node.json      # TypeScript config for Vite
    ├── .env.example            # Environment template
    ├── .gitignore              # Frontend-specific ignores
    │
    └── src/                    # Source code
        ├── main.tsx            # React entry point
        ├── App.tsx             # Main app component
        ├── App.css             # Global styles
        ├── types.ts            # TypeScript type definitions
        ├── vite-env.d.ts       # Vite environment types
        │
        ├── components/         # React components
        │   ├── LoginScreen.tsx         # User login/identification
        │   ├── RecordingScreen.tsx     # Main recording interface
        │   ├── ProgressBar.tsx         # Progress tracking display
        │   └── RecordingControls.tsx   # Audio recording controls
        │
        └── services/           # API service layer
            └── api.ts          # Backend API communication
```

## File Descriptions

### Root Level

**README.md**
- Main project documentation
- Architecture overview
- Setup instructions
- API documentation
- Deployment overview

**QUICKSTART.md**
- 5-minute setup guide
- Prerequisites check
- Step-by-step startup
- Common issues & solutions

**DEPLOYMENT.md**
- Production deployment guide
- Backend deployment options (Render, Railway, own server)
- Frontend deployment to GitHub Pages
- Configuration for production
- Troubleshooting

**PROJECT_STRUCTURE.md**
- This file
- Complete directory tree
- File descriptions

**.gitignore**
- Ignore backend recordings and database
- Ignore node_modules and build outputs
- Ignore environment files

### Backend Files

**main.py** (280 lines)
- FastAPI application setup
- CORS middleware configuration
- API endpoint implementations:
  - `POST /api/login` - User login/creation
  - `GET /api/next_task` - Task assignment
  - `POST /api/upload_recording` - Audio upload
  - `GET /api/admin/export_metadata` - Data export
  - `GET /api/admin/user_stats` - User statistics
- Audio file handling
- Database session management

**config.py** (50 lines)
- Pydantic settings management
- Environment variable loading
- Default configuration values
- Path configuration for:
  - Database location
  - Recordings directory
  - Source JSONL files
  - CORS origins

**database.py** (130 lines)
- SQLAlchemy models:
  - `User` - User information
  - `Recording` - Recording metadata
- Database initialization
- Session management
- Progress calculation functions
- Helper queries

**data_loader.py** (70 lines)
- JSONL file loading
- Data caching in memory
- DataItem class for structured access
- Language-specific data retrieval

**task_manager.py** (150 lines)
- Task assignment algorithm
- Priority logic:
  1. Chinese pairs
  2. English pairs
  3. Chinese extra questions
  4. English extra questions
- Random sampling without replacement
- Pair completion tracking

**audio_utils.py** (80 lines)
- ffmpeg integration
- Audio format conversion (WebM → WAV)
- Filename generation with metadata encoding
- Error handling for conversion

**requirements.txt** (7 packages)
- fastapi - Web framework
- uvicorn - ASGI server
- python-multipart - File upload support
- sqlalchemy - ORM
- aiosqlite - Async SQLite
- pydantic - Data validation
- pydantic-settings - Settings management

**run.sh / run.bat**
- Convenience startup scripts
- Virtual environment activation
- Dependency checking
- ffmpeg verification
- Server startup

**BACKEND.md**
- Detailed backend documentation
- API endpoint specifications
- Database schema
- Audio processing details
- Configuration options
- Testing procedures
- Troubleshooting

### Frontend Files

**index.html** (15 lines)
- HTML entry point
- Root div mounting point
- Script module loading

**package.json**
- NPM dependencies:
  - react, react-dom
  - typescript
  - vite
  - axios
- Build scripts:
  - `dev` - Development server
  - `build` - Production build
  - `preview` - Preview build

**vite.config.ts**
- Vite build configuration
- React plugin
- Base path for GitHub Pages
- Server settings

**tsconfig.json**
- TypeScript compiler options
- Strict mode enabled
- ES2020 target
- React JSX

**src/main.tsx**
- React application bootstrap
- Root component mounting
- StrictMode wrapper

**src/App.tsx** (30 lines)
- Main application component
- Login state management
- Screen routing (Login vs Recording)
- User session handling

**src/App.css** (150 lines)
- Global styles
- Button styles with gradients
- Input field styles
- Error/success message styles
- Loading animations
- Responsive layout

**src/types.ts** (40 lines)
- TypeScript interfaces:
  - `Progress` - User progress tracking
  - `Task` - Recording task details
  - `LoginResponse` - API response
  - `NextTaskResponse` - API response
  - `UploadResponse` - API response
  - `RecordingState` - Recording UI state

**src/services/api.ts** (120 lines)
- Axios HTTP client setup
- API base URL configuration
- Error handling
- API functions:
  - `login()` - User login
  - `getNextTask()` - Fetch next task
  - `uploadRecording()` - Upload audio
  - `testConnection()` - Health check

**src/components/LoginScreen.tsx** (100 lines)
- Username input form
- Connection testing
- Error display
- Task overview information
- Submit handler

**src/components/RecordingScreen.tsx** (200 lines)
- Main recording interface
- Progress display integration
- Task display
- Recording controls integration
- Upload handling
- Completion state
- Error handling

**src/components/ProgressBar.tsx** (100 lines)
- Visual progress bars
- Four progress tracks:
  - Chinese pairs
  - English pairs
  - Chinese extra questions
  - English extra questions
- Total progress calculation
- Color-coded completion

**src/components/RecordingControls.tsx** (180 lines)
- MediaRecorder API integration
- Recording state management
- Audio capture from microphone
- Recording timer
- Playback preview
- Submit/discard actions
- Microphone permission handling
- Error handling

## Data Flow

### 1. User Login
```
User → LoginScreen → api.login() → POST /api/login → Database → Response
```

### 2. Task Assignment
```
User → RecordingScreen → api.getNextTask() → GET /api/next_task → TaskManager → DataLoader → Response
```

### 3. Recording & Upload
```
User → RecordingControls (MediaRecorder) → Blob → api.uploadRecording() → POST /api/upload_recording → ffmpeg conversion → File + Database → Response
```

### 4. Progress Update
```
Upload Success → Update Progress State → Fetch Next Task → Display New Task
```

## Key Design Decisions

### Backend

1. **SQLite for simplicity**
   - Easy setup, no separate database server
   - Suitable for research project scale
   - Can migrate to PostgreSQL if needed

2. **FastAPI for modern Python**
   - Automatic API documentation
   - Type hints and validation
   - Async support
   - Fast development

3. **ffmpeg for audio conversion**
   - Industry standard
   - Reliable and well-tested
   - Converts browser WebM to research-friendly WAV

4. **Structured filenames**
   - Encode metadata in filename
   - Easy file filtering and grouping
   - No need to query database for basic info

### Frontend

1. **React + TypeScript**
   - Type safety
   - Component reusability
   - Modern development experience

2. **Vite for build**
   - Fast development server
   - Quick builds
   - GitHub Pages compatible

3. **MediaRecorder API**
   - Native browser support
   - No external dependencies
   - Works on Chrome, Firefox, Edge

4. **No authentication**
   - Username-only identification
   - Suitable for trusted research participants
   - Can add JWT tokens if needed

## Runtime Generated Files

These files are created during operation:

```
backend/
├── db.sqlite3                          # SQLite database
├── recordings/                         # Audio storage
│   ├── user-alice__lang-zh__type-pair__role-secret__item-123__ts-*.wav
│   ├── user-alice__lang-zh__type-pair__role-question__item-123__ts-*.wav
│   └── ... (more recordings)
└── __pycache__/                        # Python bytecode

frontend/
├── dist/                               # Production build
│   ├── index.html
│   ├── assets/
│   │   ├── index-*.js
│   │   └── index-*.css
│   └── vite.svg
└── node_modules/                       # NPM packages
```

## Environment Files

### backend/.env
```env
API_CORS_ORIGINS=http://localhost:5173,https://yourusername.github.io
RECORDINGS_DIR=recordings
DB_PATH=db.sqlite3
```

### frontend/.env
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Port Usage

- **Backend:** 8000 (default, configurable)
- **Frontend:** 5173 (Vite default, configurable)

## Dependencies Summary

### Backend (Python)
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- python-multipart==0.0.6
- sqlalchemy==2.0.23
- aiosqlite==0.19.0
- pydantic==2.5.0
- pydantic-settings==2.1.0

### Frontend (Node.js)
- react@18.2.0
- react-dom@18.2.0
- axios@1.6.2
- typescript@5.2.2
- vite@5.0.8
- @vitejs/plugin-react@4.2.1

### External
- ffmpeg (system package)

## Extending the System

### Add New Language

1. Add JSONL file to `source/`
2. Update `config.py` with new path
3. Update `data_loader.py` to load new file
4. Update `task_manager.py` with new quotas
5. Update frontend types and UI

### Add Authentication

1. Install `python-jose` and `passlib`
2. Add User password field to database
3. Implement JWT token generation
4. Add authentication middleware
5. Update frontend to handle tokens

### Use Cloud Storage

1. Install `boto3` (for AWS S3)
2. Update `audio_utils.py` to upload to S3
3. Store S3 URL in database instead of local path
4. Update configuration with S3 credentials

### Add Progress Resume

Currently implemented! Users can:
- Close browser and return later
- System remembers progress
- Continues from last completed task

---

**This structure supports:**
- Easy local development
- Simple deployment
- Clear separation of concerns
- Maintainable codebase
- Research-friendly data organization

