# Python API

The EasyTranscribe Python API provides a clean, intuitive interface for integrating speech-to-text functionality into your applications.

## Core Functions

### `capture_and_transcribe()`

Capture audio from microphone and transcribe to text using Whisper.

```python
def capture_and_transcribe(
    model_name: str = "turbo",
    verbose: bool = False
) -> str
```

#### Parameters

- **`model_name`** (`str`, optional): Whisper model to use. Default: `"turbo"`
  - Options: `"tiny"`, `"base"`, `"small"`, `"medium"`, `"large"`, `"turbo"`
- **`verbose`** (`bool`, optional): Show detailed recording information. Default: `False`

#### Returns

- **`str`**: The transcribed text from the audio

#### Example

```python
from easytranscribe import capture_and_transcribe

# Basic usage
text = capture_and_transcribe()
print(f"You said: {text}")

# With custom model and verbose output
text = capture_and_transcribe(
    model_name="medium",
    verbose=True
)
print(f"Transcribed: {text}")
```

#### Behavior

- Waits for user to start speaking
- Automatically stops after 3 seconds of silence
- Minimum recording duration of 2 seconds after speech detection
- Returns empty string if no speech is detected

### `transcribe_audio_file()`

Transcribe an audio file to text using Whisper.

```python
def transcribe_audio_file(
    file_path: str,
    model_name: str = "base",
    verbose: bool = False
) -> str
```

#### Parameters

- **`file_path`** (`str`): Path to the audio file
- **`model_name`** (`str`, optional): Whisper model to use. Default: `"base"`
- **`verbose`** (`bool`, optional): Show processing information. Default: `False`

#### Returns

- **`str`**: The transcribed text from the audio file

#### Raises

- **`FileNotFoundError`**: If the audio file doesn't exist
- **`Exception`**: If the file format is unsupported or corrupted

#### Example

```python
from easytranscribe import transcribe_audio_file

# Basic file transcription
text = transcribe_audio_file("meeting.wav")
print(f"Meeting transcript: {text}")

# With high-accuracy model
text = transcribe_audio_file(
    "interview.mp3",
    model_name="large",
    verbose=True
)
```

## Logging Functions

### `view_logs()`

View transcription logs with filtering options.

```python
def view_logs(
    date: Optional[str] = None,
    tail: Optional[int] = None,
    show_stats: bool = False
) -> None
```

#### Parameters

- **`date`** (`str`, optional): Date filter (YYYY-MM-DD format or "today")
- **`tail`** (`int`, optional): Show last N entries
- **`show_stats`** (`bool`, optional): Display statistics summary

#### Example

```python
from easytranscribe import view_logs

# Show all logs
view_logs()

# Show today's logs
view_logs(date="today")

# Show last 10 entries
view_logs(tail=10)

# Show statistics
view_logs(show_stats=True)
```

### `get_available_log_dates()`

Get a list of dates that have transcription logs.

```python
def get_available_log_dates() -> List[str]
```

#### Returns

- **`List[str]`**: List of date strings in YYYY-MM-DD format

#### Example

```python
from easytranscribe import get_available_log_dates

dates = get_available_log_dates()
print(f"Logs available for: {', '.join(dates)}")
```

## Advanced Usage Examples

### Voice-Activated Note Taking

```python
import datetime
from pathlib import Path
from easytranscribe import capture_and_transcribe

class VoiceNoteTaker:
    def __init__(self, notes_dir="voice_notes"):
        self.notes_dir = Path(notes_dir)
        self.notes_dir.mkdir(exist_ok=True)

    def take_note(self, model="base"):
        """Take a single voice note."""
        print("🎤 Speak your note...")
        text = capture_and_transcribe(model_name=model, verbose=True)

        if text.strip():
            timestamp = datetime.datetime.now()
            filename = f"note_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = self.notes_dir / filename

            with open(filepath, 'w') as f:
                f.write(f"Voice Note - {timestamp}\n")
                f.write("=" * 40 + "\n\n")
                f.write(text)

            print(f"📝 Note saved: {filepath}")
            return filepath
        else:
            print("❌ No speech detected")
            return None

    def take_multiple_notes(self, count=5):
        """Take multiple voice notes in sequence."""
        notes = []
        for i in range(count):
            print(f"\n--- Note {i+1}/{count} ---")
            note_file = self.take_note()
            if note_file:
                notes.append(note_file)

            if i < count - 1:
                input("Press Enter for next note...")

        return notes

# Usage
note_taker = VoiceNoteTaker()
note_taker.take_note()
```

### Meeting Transcription System

```python
import json
from datetime import datetime
from pathlib import Path
from easytranscribe import transcribe_audio_file

class MeetingTranscriber:
    def __init__(self, output_dir="transcripts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def transcribe_meeting(self, audio_file, meeting_title=None, attendees=None):
        """Transcribe a meeting recording with metadata."""
        print(f"🎧 Transcribing: {audio_file}")

        # Transcribe with high accuracy
        transcript = transcribe_audio_file(
            audio_file,
            model_name="medium",
            verbose=True
        )

        # Create meeting metadata
        meeting_data = {
            "title": meeting_title or f"Meeting {datetime.now().date()}",
            "date": datetime.now().isoformat(),
            "audio_file": str(audio_file),
            "attendees": attendees or [],
            "transcript": transcript,
            "word_count": len(transcript.split()),
            "duration_estimate": f"{len(transcript.split()) / 150:.1f} minutes"
        }

        # Save transcript
        output_file = self.output_dir / f"meeting_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(output_file, 'w') as f:
            json.dump(meeting_data, f, indent=2)

        print(f"📄 Transcript saved: {output_file}")
        return meeting_data

    def batch_transcribe(self, audio_files):
        """Transcribe multiple meeting recordings."""
        results = []
        for audio_file in audio_files:
            try:
                result = self.transcribe_meeting(audio_file)
                results.append(result)
            except Exception as e:
                print(f"❌ Error transcribing {audio_file}: {e}")

        return results

# Usage
transcriber = MeetingTranscriber()
meeting = transcriber.transcribe_meeting(
    "team_meeting.wav",
    meeting_title="Weekly Team Standup",
    attendees=["Alice", "Bob", "Charlie"]
)
```

### Real-time Voice Assistant Integration

```python
import threading
import queue
from easytranscribe import capture_and_transcribe

class VoiceAssistant:
    def __init__(self):
        self.listening = False
        self.response_queue = queue.Queue()

    def listen_continuously(self):
        """Listen for voice commands continuously."""
        print("🎤 Voice assistant started. Say 'stop listening' to exit.")

        while self.listening:
            try:
                # Capture voice input
                text = capture_and_transcribe(model_name="base")

                if text:
                    print(f"Heard: {text}")

                    # Check for stop command
                    if "stop listening" in text.lower():
                        self.listening = False
                        print("👋 Voice assistant stopped.")
                        break

                    # Process command
                    response = self.process_command(text)
                    if response:
                        print(f"Response: {response}")

            except KeyboardInterrupt:
                self.listening = False
                break

    def process_command(self, text):
        """Process voice commands."""
        text_lower = text.lower()

        if "what time" in text_lower:
            return f"Current time is {datetime.now().strftime('%H:%M')}"
        elif "take note" in text_lower:
            print("📝 Ready for your note...")
            note = capture_and_transcribe(model_name="base")
            if note:
                with open("quick_notes.txt", "a") as f:
                    f.write(f"{datetime.now()}: {note}\n")
                return "Note saved!"
        elif "read notes" in text_lower:
            try:
                with open("quick_notes.txt", "r") as f:
                    notes = f.read().strip()
                return f"Recent notes: {notes[-200:]}" if notes else "No notes found"
            except FileNotFoundError:
                return "No notes file found"
        else:
            return "Command not recognized"

    def start(self):
        """Start the voice assistant."""
        self.listening = True
        listen_thread = threading.Thread(target=self.listen_continuously)
        listen_thread.daemon = True
        listen_thread.start()
        return listen_thread

# Usage
assistant = VoiceAssistant()
thread = assistant.start()
thread.join()  # Wait for assistant to stop
```

### Audio File Batch Processor

```python
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from easytranscribe import transcribe_audio_file

class BatchTranscriber:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers

    def transcribe_file(self, file_path, output_dir):
        """Transcribe a single file."""
        try:
            print(f"Processing: {file_path.name}")
            text = transcribe_audio_file(str(file_path), model_name="base")

            # Save transcript
            output_file = output_dir / f"{file_path.stem}_transcript.txt"
            with open(output_file, 'w') as f:
                f.write(f"Transcript of: {file_path.name}\n")
                f.write("=" * 50 + "\n\n")
                f.write(text)

            return {"file": str(file_path), "success": True, "output": str(output_file)}

        except Exception as e:
            return {"file": str(file_path), "success": False, "error": str(e)}

    def process_directory(self, input_dir, output_dir=None, file_patterns=None):
        """Process all audio files in a directory."""
        input_path = Path(input_dir)
        output_path = Path(output_dir or input_path / "transcripts")
        output_path.mkdir(exist_ok=True)

        # Default audio file patterns
        if file_patterns is None:
            file_patterns = ["*.wav", "*.mp3", "*.m4a", "*.flac"]

        # Find all audio files
        audio_files = []
        for pattern in file_patterns:
            audio_files.extend(input_path.glob(pattern))

        print(f"Found {len(audio_files)} audio files")

        # Process files in parallel
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.transcribe_file, file_path, output_path)
                for file_path in audio_files
            ]

            for future in futures:
                result = future.result()
                results.append(result)

                if result["success"]:
                    print(f"✅ {Path(result['file']).name}")
                else:
                    print(f"❌ {Path(result['file']).name}: {result['error']}")

        # Summary
        successful = sum(1 for r in results if r["success"])
        print(f"\nProcessing complete: {successful}/{len(results)} files successful")

        return results

# Usage
processor = BatchTranscriber(max_workers=2)
results = processor.process_directory("audio_files/", "transcripts/")
```

## Error Handling

### Common Exceptions

```python
from easytranscribe import transcribe_audio_file, capture_and_transcribe

try:
    # File transcription
    text = transcribe_audio_file("nonexistent.wav")
except FileNotFoundError:
    print("Audio file not found")
except Exception as e:
    print(f"Transcription error: {e}")

try:
    # Live transcription
    text = capture_and_transcribe()
except PermissionError:
    print("Microphone access denied")
except Exception as e:
    print(f"Recording error: {e}")
```

### Best Practices

1. **Always handle exceptions** when processing user-provided files
2. **Use appropriate models** for your use case (speed vs accuracy)
3. **Enable verbose mode** during development for debugging
4. **Validate audio files** before processing
5. **Consider timeout handling** for live transcription in automated systems

The EasyTranscribe Python API is designed to be simple yet powerful, making it easy to add speech-to-text capabilities to any Python application.
