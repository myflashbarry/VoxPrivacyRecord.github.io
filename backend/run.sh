#!/bin/bash
# Simple script to run the backend server

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "WARNING: ffmpeg is not installed!"
    echo "Audio conversion will fail. Please install ffmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu: sudo apt install ffmpeg"
    echo ""
fi

# Check if requirements are installed
echo "Checking dependencies..."
python -c "import fastapi" 2>/dev/null || {
    echo "Installing dependencies..."
    pip install -r requirements.txt
}

# Run the server
echo "Starting backend server..."
echo "API will be available at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
echo ""
uvicorn main:app --reload --host 0.0.0.0 --port 8000

