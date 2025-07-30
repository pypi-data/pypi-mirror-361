# CLI Usage

The EasyTranscribe command-line interface provides powerful tools for speech-to-text transcription. This guide covers all available commands and options.

## Command Structure

```bash
easytranscribe <command> [options]
```

## Global Options

### Version Information
```bash
easytranscribe --version
```
Shows the installed version of EasyTranscribe.

### Help
```bash
easytranscribe --help
easytranscribe <command> --help
```
Display help information for the main command or specific subcommands.

## Commands

### `live` - Live Microphone Transcription

Capture and transcribe speech from your microphone in real-time.

```bash
easytranscribe live [options]
```

#### Options

**`--model`** (default: `base`)
: Choose the Whisper model for transcription
: Choices: `tiny`, `base`, `small`, `medium`, `large`, `turbo`

**`--verbose`**
: Enable detailed output showing recording status and processing information

#### Examples

```bash
# Basic live transcription
easytranscribe live

# Use the fastest model
easytranscribe live --model tiny

# Use the most accurate model with verbose output
easytranscribe live --model large --verbose

# Quick transcription for notes
easytranscribe live --model base --verbose
```

#### Behavior

- **Automatic Start**: Recording begins when you start speaking
- **Silence Detection**: Stops after 3 seconds of silence
- **Minimum Duration**: Records for at least 2 seconds after speech starts
- **Real-time Feedback**: Shows recording status when `--verbose` is used

### `file` - Audio File Transcription

Transcribe speech from audio files supporting multiple formats.

```bash
easytranscribe file <filepath> [options]
```

#### Arguments

**`filepath`** (required)
: Path to the audio file to transcribe

#### Options

**`--model`** (default: `base`)
: Choose the Whisper model for transcription

**`--verbose`**
: Show processing information and timing

#### Supported Formats

- **WAV** - Uncompressed audio
- **MP3** - MPEG audio
- **M4A** - Apple audio format
- **FLAC** - Free lossless audio codec
- **OGG** - Ogg Vorbis
- **WMA** - Windows Media Audio
- And many more supported by FFmpeg

#### Examples

```bash
# Transcribe a WAV file
easytranscribe file recording.wav

# Transcribe with high accuracy
easytranscribe file interview.mp3 --model large

# Transcribe with verbose output
easytranscribe file meeting.m4a --model medium --verbose

# Process multiple files with a script
for file in *.wav; do
    easytranscribe file "$file" --model base
done
```

### `logs` - View Transcription History

Access and analyze your transcription history with comprehensive logging tools.

```bash
easytranscribe logs [options]
```

#### Options

**`--date`**
: Show logs for a specific date (format: YYYY-MM-DD) or use 'today'

**`--tail`**
: Show the last N log entries

**`--stats`**
: Display transcription statistics and summaries

**`--list-dates`**
: List all available log dates

#### Examples

```bash
# Show today's transcriptions
easytranscribe logs
easytranscribe logs --date today

# Show logs for a specific date
easytranscribe logs --date 2025-07-13

# Show last 10 transcriptions
easytranscribe logs --tail 10

# Show transcription statistics
easytranscribe logs --stats

# List all available log dates
easytranscribe logs --list-dates
```

#### Log Information

Each log entry includes:
- **Timestamp** - When the transcription occurred
- **Source Type** - Live microphone or file
- **Model Used** - Which Whisper model was used
- **Duration** - Length of audio processed
- **Processing Time** - How long transcription took
- **Text Content** - The transcribed text
- **File Path** - For file transcriptions

## Model Selection Guide

Choose the right model based on your needs:

| Model | Size | Speed | Use Case |
|-------|------|-------|----------|
| `tiny` | 39 MB | ⚡⚡⚡ | Quick notes, testing |
| `base` | 74 MB | ⚡⚡ | General use (default) |
| `small` | 244 MB | ⚡ | Better accuracy needed |
| `medium` | 769 MB | 🐌 | High accuracy important |
| `large` | 1550 MB | 🐌🐌 | Maximum accuracy |
| `turbo` | 805 MB | ⚡ | Best accuracy + speed balance |

!!! tip "Model Recommendation"
    - **For quick notes**: Use `tiny` or `base`
    - **For important content**: Use `medium` or `large`
    - **For real-time applications**: Use `turbo` or `base`
    - **For batch processing**: Use `large` for best results

## Advanced Usage Patterns

### Batch Processing
```bash
# Process all audio files in a directory
for file in audio_files/*.{wav,mp3,m4a}; do
    if [ -f "$file" ]; then
        echo "Processing: $file"
        easytranscribe file "$file" --model base --verbose
    fi
done
```

### Monitoring Logs
```bash
# Check for new transcriptions periodically
watch -n 30 'easytranscribe logs --tail 5'
```

### Creating Transcription Reports
```bash
# Generate a daily report
easytranscribe logs --date today --stats > daily_report.txt
```

### Scripted Voice Notes
```bash
#!/bin/bash
# voice_note.sh - Quick voice note script

echo "🎤 Recording voice note..."
TEXT=$(easytranscribe live --model base)

if [ -n "$TEXT" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    echo "Voice Note - $(date)" > "note_$TIMESTAMP.txt"
    echo "$TEXT" >> "note_$TIMESTAMP.txt"
    echo "📝 Saved to: note_$TIMESTAMP.txt"
else
    echo "❌ No speech detected"
fi
```

## Error Handling

### Common Exit Codes
- **0** - Success
- **1** - General error (file not found, invalid arguments, etc.)
- **2** - Audio device error
- **3** - Model loading error

### Troubleshooting Commands

Check your audio setup:
```bash
# Test microphone with verbose output
easytranscribe live --model tiny --verbose
```

Verify file accessibility:
```bash
# Check if file exists and is readable
ls -la your_audio_file.wav
file your_audio_file.wav
```

Test different models:
```bash
# Try the smallest model first
easytranscribe file test.wav --model tiny
```

## Integration with Other Tools

### Pipe to Text Processing
```bash
# Transcribe and count words
easytranscribe live | wc -w

# Transcribe and save to file
easytranscribe live > transcript.txt

# Transcribe and search for keywords
easytranscribe file audio.wav | grep -i "important"
```

### JSON Output (for scripting)
```bash
# Process logs programmatically
easytranscribe logs --date today | python parse_logs.py
```

This CLI interface makes EasyTranscribe powerful for both interactive use and automation scripts.
