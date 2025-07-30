import os
import time
from typing import Optional


def log_transcription(
    model_name: str,
    transcribed_text: str,
    audio_duration: Optional[float] = None,
    processing_time: Optional[float] = None,
    audio_file: Optional[str] = None,
) -> None:
    """
    Logs transcription details to a log file.

    Args:
        model_name: Name of the Whisper model used
        transcribed_text: The transcribed text
        audio_duration: Duration of audio in seconds (for live recording)
        processing_time: Time taken for processing in seconds
        audio_file: Path to audio file (for file transcription)
    """
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"transcription_{time.strftime('%Y-%m-%d')}.log")

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {model_name}\n")
            if audio_file:
                f.write(f"Audio File: {audio_file}\n")
            if audio_duration is not None:
                f.write(f"Audio Duration: {audio_duration:.1f}s\n")
            if processing_time is not None:
                f.write(f"Processing Time: {processing_time:.1f}s\n")
            f.write(f"Transcribed Text: {transcribed_text}\n")
            f.write("-" * 40 + "\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")
        raise
