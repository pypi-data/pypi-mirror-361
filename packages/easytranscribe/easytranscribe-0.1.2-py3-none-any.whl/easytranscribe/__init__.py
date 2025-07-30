"""
easytranscribe: Simple speech-to-text from audio files or live microphone input.

This package provides easy-to-use functions for speech-to-text transcription using OpenAI's Whisper model.
Supports both live microphone recording and audio file transcription with automatic logging.
"""

from ._version import __version__

__author__ = "akhshyganesh"

from .speech_to_text import capture_and_transcribe, transcribe_audio_file
from .view_logs import view_logs, get_available_log_dates

__all__ = [
    "__version__",
    "capture_and_transcribe",
    "transcribe_audio_file",
    "view_logs",
    "get_available_log_dates",
]
