"""Audio conversion utilities using ffmpeg."""
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple


def check_ffmpeg_installed() -> bool:
    """Check if ffmpeg is installed and accessible."""
    return shutil.which("ffmpeg") is not None


def generate_filename(username: str, language: str, task_type: str, role: str, item_id: str) -> str:
    """
    Generate a standardized filename for audio recordings.
    
    Format: user-{username}__lang-{zh|en}__type-{pair|extraQ}__role-{secret|question}__item-{item_id}__ts-{timestamp}.wav
    """
    # Sanitize username (remove special characters)
    safe_username = "".join(c if c.isalnum() or c in "-_" else "_" for c in username)
    
    # Generate timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    
    # Map task_type to short form
    type_short = "pair" if task_type == "pair" else "extraQ"
    
    filename = f"user-{safe_username}__lang-{language}__type-{type_short}__role-{role}__item-{item_id}__ts-{timestamp}.wav"
    
    return filename


def convert_to_wav(input_path: Path, output_path: Path) -> Tuple[bool, str]:
    """
    Convert audio file to WAV format using ffmpeg.
    
    Args:
        input_path: Path to input audio file (e.g., webm, ogg)
        output_path: Path where WAV file should be saved
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not check_ffmpeg_installed():
        return False, "ffmpeg is not installed. Please install ffmpeg to convert audio files."
    
    try:
        # ffmpeg command to convert to WAV
        # -i: input file
        # -acodec pcm_s16le: 16-bit PCM audio codec
        # -ar 16000: sample rate 16kHz (common for speech)
        # -ac 1: mono audio
        # -y: overwrite output file if exists
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            str(output_path)
        ]
        
        # Run ffmpeg
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode == 0:
            return True, "Conversion successful"
        else:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            return False, f"ffmpeg error: {error_msg[:200]}"
    
    except subprocess.TimeoutExpired:
        return False, "Conversion timed out (file too large or slow system)"
    except Exception as e:
        return False, f"Conversion error: {str(e)}"

