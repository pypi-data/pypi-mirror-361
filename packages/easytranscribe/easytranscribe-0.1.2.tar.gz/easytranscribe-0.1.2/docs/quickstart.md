# Quick Start

This guide will get you up and running with EasyTranscribe in just a few minutes.

## 1. Basic Live Transcription

The simplest way to start is with live microphone transcription:

```bash
easytranscribe live
```

1. Run the command
2. Speak into your microphone
3. The tool will automatically detect when you stop speaking
4. Your transcribed text will be displayed

!!! tip "Pro Tip"
    The tool waits for 3 seconds of silence before stopping the recording. This gives you time to pause naturally while speaking.

## 2. Transcribe an Audio File

To transcribe an existing audio file:

```bash
easytranscribe file /path/to/your/audio.wav
```

Supported formats include: WAV, MP3, M4A, FLAC, and more.

## 3. Using Different Models

EasyTranscribe supports multiple Whisper models. Use a faster model for quick transcription:

```bash
# Fastest (less accurate)
easytranscribe live --model tiny

# Balanced (default)
easytranscribe live --model base

# Most accurate (slower)
easytranscribe live --model large
```

## 4. Verbose Output

Get detailed information about the transcription process:

```bash
easytranscribe live --verbose
```

This shows:
- Recording status
- Model loading progress
- Processing time
- Audio duration

## 5. Python API Basics

### Live Transcription

```python
from easytranscribe import capture_and_transcribe

# Basic usage
text = capture_and_transcribe()
print(f"You said: {text}")

# With options
text = capture_and_transcribe(
    model_name="base",
    verbose=True
)
```

### File Transcription

```python
from easytranscribe import transcribe_audio_file

# Transcribe a file
text = transcribe_audio_file("meeting_recording.wav")
print(f"Meeting transcript: {text}")

# With custom model
text = transcribe_audio_file(
    "interview.mp3",
    model_name="medium"
)
```

## 6. Viewing Logs

EasyTranscribe automatically logs all transcriptions. View your recent activity:

```bash
# Show today's transcriptions
easytranscribe logs

# Show specific date
easytranscribe logs --date 2025-07-13

# Show statistics
easytranscribe logs --stats

# List available log dates
easytranscribe logs --list-dates
```

## 7. Complete Example Workflow

Here's a typical workflow using EasyTranscribe:

```bash
# 1. Start with a quick transcription
easytranscribe live --model tiny --verbose

# 2. For important content, use a better model
easytranscribe live --model medium

# 3. Process some audio files
easytranscribe file recording1.wav
easytranscribe file recording2.mp3

# 4. Review your transcription history
easytranscribe logs --stats
easytranscribe logs --tail 10
```

## 8. Integration Example

Here's how to integrate EasyTranscribe into a simple note-taking script:

```python
#!/usr/bin/env python3
"""Simple voice note taker using EasyTranscribe."""

import datetime
from pathlib import Path
from easytranscribe import capture_and_transcribe

def take_voice_note():
    """Capture a voice note and save it to a file."""
    print("🎤 Ready to take a voice note. Start speaking...")

    # Capture and transcribe
    text = capture_and_transcribe(model_name="base", verbose=True)

    if text.strip():
        # Save to file with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_note_{timestamp}.txt"

        Path(filename).write_text(f"Voice Note - {datetime.datetime.now()}\n\n{text}\n")
        print(f"📝 Voice note saved to: {filename}")
    else:
        print("❌ No speech detected")

if __name__ == "__main__":
    take_voice_note()
```

## Next Steps

Now that you're familiar with the basics:

- Learn about [CLI Usage](cli.md) for advanced command-line options
- Explore the [Python API](api.md) for programmatic usage
- Check out [Examples](examples.md) for more use cases
- Read about [Configuration](configuration.md) options

## Common First-Time Issues

### Microphone Not Working
- Check your system's microphone permissions
- Try `easytranscribe live --verbose` to see detailed error messages

### Poor Transcription Quality
- Try a larger model: `--model medium` or `--model large`
- Ensure you're in a quiet environment
- Speak clearly and at a moderate pace

### Slow Performance
- Use a smaller model: `--model tiny` or `--model base`
- Close other resource-intensive applications
- Consider using a GPU if available (automatically detected)
