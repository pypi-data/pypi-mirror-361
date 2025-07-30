import sys
import time
import whisper
import numpy as np
import sounddevice as sd

from typing import Optional
from easytranscribe.transcription_logger import log_transcription


def capture_and_transcribe(model_name: str = "turbo") -> str:
    """
    Captures audio from microphone and transcribes to text using Whisper.
    Waits for user to start speaking, then stops after 3 seconds of silence.
    """
    print("Speak into the microphone...")

    # Audio settings
    samplerate = 16000
    chunk_duration = 0.5  # seconds per chunk
    chunk_size = int(samplerate * chunk_duration)
    silence_threshold = 0.01  # Audio level threshold for silence detection
    silence_duration = 3.0  # seconds of silence before stopping
    min_recording_time = 2.0  # minimum recording time after speech starts

    print(f"Listening... (will stop after {silence_duration} seconds of silence)")

    # Recording state
    audio_data = []
    started_speaking = False
    recording_start_time: float | None = None
    last_speech_time: float | None = None

    try:
        with sd.InputStream(samplerate=samplerate, channels=1, dtype=np.float32):
            while True:
                # Record a chunk
                chunk = sd.rec(
                    chunk_size, samplerate=samplerate, channels=1, dtype=np.float32
                )
                sd.wait()  # Wait for recording to complete
                audio_data.append(chunk.flatten())

                # Calculate audio level
                audio_level = np.abs(chunk).mean()
                is_silent = audio_level < silence_threshold
                current_time = time.time()

                # Check if user started speaking
                if not started_speaking:
                    if not is_silent:
                        started_speaking = True
                        recording_start_time = current_time
                        last_speech_time = current_time
                        print("Started speaking... Recording now.")
                    continue

                # Update last speech time if not silent
                if not is_silent:
                    last_speech_time = current_time

                # Check minimum recording time
                if (
                    recording_start_time is not None
                    and isinstance(recording_start_time, float)
                    and current_time - recording_start_time < min_recording_time
                ):
                    continue

                if (
                    last_speech_time is not None
                    and isinstance(last_speech_time, float)
                    and (current_time - last_speech_time) >= silence_duration
                ):
                    silence_time = current_time - last_speech_time
                    print(
                        f"Detected {silence_time:.1f} seconds of silence. Stopping recording."
                    )
                    break

                # Debug output every few seconds
                if recording_start_time is not None:
                    recording_time = current_time - recording_start_time
                    if (
                        int(recording_time) % 3 == 0
                        and recording_time - int(recording_time) < chunk_duration
                    ):
                        silence_time = (
                            current_time - last_speech_time if last_speech_time else 0
                        )
                        print(
                            f"Recording... {recording_time:.1f}s (silence: {silence_time:.1f}s, level: {audio_level:.4f})"
                        )

    except KeyboardInterrupt:
        print("\nRecording interrupted by user.")

    if not audio_data:
        print("No audio recorded.")
        return ""

    # Calculate audio duration
    audio = np.concatenate(audio_data)
    audio_duration = len(audio) / samplerate
    print(f"Recording complete. Recorded {audio_duration:.1f} seconds of audio.")
    print("Transcribing...")

    # Transcribe with Whisper and measure processing time
    transcription_start_time = time.time()
    model = whisper.load_model(model_name)
    result = model.transcribe(audio, fp16=False)
    transcribed_text = result["text"].strip()
    processing_time = time.time() - transcription_start_time

    print("Transcribed text:", transcribed_text)

    # Log the transcription
    try:
        log_transcription(
            model_name=model_name,
            transcribed_text=transcribed_text,
            audio_duration=audio_duration,
            processing_time=processing_time,
        )
        print(
            f"Transcription logged successfully (Duration: {audio_duration:.1f}s, Processing: {processing_time:.1f}s)"
        )
    except Exception as e:
        print(f"Warning: Failed to log transcription: {e}")

    return transcribed_text

def transcribe_audio_file(filepath: str, model_name: str = "turbo") -> str:
    """
    Transcribes an audio file to text using Whisper.
    
    Args:
        filepath: Path to the audio file
        model_name: Whisper model to use for transcription
        
    Returns:
        Transcribed text from the audio file
        
    Raises:
        FileNotFoundError: If the audio file doesn't exist
        Exception: If transcription fails
    """
    import os
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Audio file not found: {filepath}")
    
    print(f"Transcribing file: {filepath}")
    transcription_start_time = time.time()
    
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(filepath, fp16=False)
        transcribed_text = result["text"].strip()
        processing_time = time.time() - transcription_start_time

        print("Transcribed text:", transcribed_text)

        # Log the transcription
        try:
            log_transcription(
                model_name=model_name,
                transcribed_text=transcribed_text,
                audio_duration=None,
                processing_time=processing_time,
                audio_file=filepath
            )
            print(
                f"Transcription logged successfully (File: {filepath}, Processing: {processing_time:.1f}s)"
            )
        except Exception as e:
            print(f"Warning: Failed to log transcription: {e}")

        return transcribed_text
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise
