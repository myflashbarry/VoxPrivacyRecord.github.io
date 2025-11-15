"""Main FastAPI application."""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import tempfile
from pathlib import Path

from config import settings
from database import init_db, get_db, User, Recording, get_user_progress
from data_loader import data_loader
from instruction_loader import instruction_loader
from task_manager import task_manager
from audio_utils import generate_filename, convert_to_wav, check_ffmpeg_installed


# Initialize FastAPI app
app = FastAPI(
    title="VoxPrivacyRecord API",
    description="Backend API for speech data collection system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and check dependencies on startup."""
    print("Initializing database...")
    init_db()
    print("Database initialized")
    
    print(f"Loaded {len(data_loader.zh_items)} Chinese items")
    print(f"Loaded {len(data_loader.en_items)} English items")
    
    print(f"Loaded {len(instruction_loader.instructions.get('zh_nobody', []))} zh_nobody instructions")
    print(f"Loaded {len(instruction_loader.instructions.get('zh_onlyme', []))} zh_onlyme instructions")
    print(f"Loaded {len(instruction_loader.instructions.get('en_nobody', []))} en_nobody instructions")
    print(f"Loaded {len(instruction_loader.instructions.get('en_onlyme', []))} en_onlyme instructions")
    
    if not check_ffmpeg_installed():
        print("WARNING: ffmpeg is not installed! Audio conversion will fail.")
        print("Please install ffmpeg: https://ffmpeg.org/download.html")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "VoxPrivacyRecord API is running",
        "ffmpeg_available": check_ffmpeg_installed()
    }


@app.post("/api/login")
async def login(
    username: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Login or create a new user.
    Returns the user's current progress.
    """
    if not username or len(username.strip()) == 0:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    
    username = username.strip()
    
    # Check if user exists
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        # Create new user
        user = User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created new user: {username}")
    
    # Get progress
    progress = get_user_progress(db, username)
    
    # Remove internal fields (starting with _)
    clean_progress = {k: v for k, v in progress.items() if not k.startswith("_")}
    
    return {
        "username": username,
        "progress": clean_progress
    }


@app.get("/api/next_task")
async def get_next_task(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Get the next recording task for a user.
    Returns task details and current progress.
    """
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    
    # Check if user exists
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please login first.")
    
    # Get progress
    progress = get_user_progress(db, username)
    clean_progress = {k: v for k, v in progress.items() if not k.startswith("_")}
    
    # Get next task
    task = task_manager.get_next_task(db, username)
    
    if task is None:
        # All tasks complete
        return {
            "username": username,
            "task": None,
            "progress": clean_progress,
            "message": "All tasks completed! Thank you for your participation."
        }
    
    return {
        "username": username,
        "task": task,
        "progress": clean_progress
    }


@app.post("/api/upload_recording")
async def upload_recording(
    username: str = Form(...),
    language: str = Form(...),
    task_type: str = Form(...),
    role: str = Form(...),
    item_id: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process an audio recording.
    Converts audio to WAV format and stores metadata.
    """
    # Validate user exists
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate parameters
    if language not in ["zh", "en"]:
        raise HTTPException(status_code=400, detail="Language must be 'zh' or 'en'")
    if task_type not in ["pair", "extra_question"]:
        raise HTTPException(status_code=400, detail="Task type must be 'pair' or 'extra_question'")
    if role not in ["secret", "question"]:
        raise HTTPException(status_code=400, detail="Role must be 'secret' or 'question'")
    
    # Verify item exists in data
    try:
        data_loader.get_item_by_id(language, item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Item {item_id} not found in {language} data")
    
    # Generate filename
    filename = generate_filename(username, language, task_type, role, item_id)
    output_path = settings.recordings_dir / filename
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_path = Path(temp_file.name)
            content = await audio.read()
            temp_file.write(content)
        
        # Convert to WAV
        success, message = convert_to_wav(temp_path, output_path)
        
        # Clean up temp file
        temp_path.unlink()
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Audio conversion failed: {message}")
        
        # Save metadata to database
        recording = Recording(
            username=username,
            language=language,
            task_type=task_type,
            role=role,
            item_id=item_id,
            file_path=str(output_path)
        )
        db.add(recording)
        db.commit()
        
        print(f"Saved recording: {filename}")
        
        # Get updated progress
        progress = get_user_progress(db, username)
        clean_progress = {k: v for k, v in progress.items() if not k.startswith("_")}
        
        return {
            "status": "ok",
            "file_path": str(output_path),
            "filename": filename,
            "progress": clean_progress,
            "message": "Recording uploaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up files on error
        if output_path.exists():
            output_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")


@app.get("/api/admin/export_metadata")
async def export_metadata(db: Session = Depends(get_db)):
    """
    Export all recording metadata as JSON.
    Useful for analysis and data management.
    """
    recordings = db.query(Recording).all()
    
    data = []
    for rec in recordings:
        data.append({
            "id": rec.id,
            "username": rec.username,
            "language": rec.language,
            "task_type": rec.task_type,
            "role": rec.role,
            "item_id": rec.item_id,
            "file_path": rec.file_path,
            "created_at": rec.created_at.isoformat()
        })
    
    return {
        "total_recordings": len(data),
        "recordings": data
    }


@app.get("/api/admin/user_stats")
async def get_user_stats(db: Session = Depends(get_db)):
    """Get statistics for all users."""
    users = db.query(User).all()
    
    stats = []
    for user in users:
        progress = get_user_progress(db, user.username)
        clean_progress = {k: v for k, v in progress.items() if not k.startswith("_")}
        stats.append({
            "username": user.username,
            "created_at": user.created_at.isoformat(),
            "progress": clean_progress
        })
    
    return {
        "total_users": len(stats),
        "users": stats
    }


@app.get("/api/admin/download_recordings")
async def download_all_recordings():
    """
    Download all recordings as a zip file.
    """
    import zipfile
    import tempfile
    from fastapi.responses import FileResponse
    import os
    from datetime import datetime
    
    recordings_path = settings.recordings_dir
    
    # Check if directory exists and has files
    if not recordings_path.exists():
        raise HTTPException(status_code=404, detail="Recordings directory not found")
    
    wav_files = list(recordings_path.glob('*.wav'))
    if not wav_files:
        raise HTTPException(status_code=404, detail="No recordings found")
    
    # Create zip file in data directory (persistent)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    zip_filename = f'recordings_{timestamp}.zip'
    zip_path = settings.data_dir / zip_filename
    
    # Create the zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for audio_file in wav_files:
            # Add file to zip with just the filename (not full path)
            zipf.write(audio_file, audio_file.name)
    
    # Return the zip file
    return FileResponse(
        path=str(zip_path),
        media_type='application/zip',
        filename=f'voxprivacy_recordings_{len(wav_files)}_files.zip'
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

