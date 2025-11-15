@echo off
REM Simple script to run the backend server on Windows

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if ffmpeg is installed
where ffmpeg >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: ffmpeg is not installed!
    echo Audio conversion will fail. Please install ffmpeg from https://ffmpeg.org/download.html
    echo.
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import fastapi" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the server
echo Starting backend server...
echo API will be available at http://localhost:8000
echo API docs at http://localhost:8000/docs
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000

