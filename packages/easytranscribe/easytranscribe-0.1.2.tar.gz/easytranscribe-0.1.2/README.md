# EasyTranscribe

A simple Python-based voice assistant that captures speech from your microphone or from recorded file, detects silence, and transcribes spoken words to text using OpenAI Whisper. Easily extensible for integration with LLMs like Ollama or Gemma.

## Features

- Real-time microphone audio capture
- Automatic silence detection and recording stop
- Speech-to-text transcription using Whisper
- Comprehensive transcription logging with detailed metrics
- Easy integration with other AI models

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/akhshyganesh/easytranscribe.git
   cd easytranscribe
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main script:
```bash
python main.py
```
Speak into your microphone. The assistant will automatically stop recording after a few seconds of silence and transcribe your speech.

# easytranscribe

[![PyPI version](https://badge.fury.io/py/easytranscribe.svg)](https://badge.fury.io/py/easytranscribe)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Easy speech-to-text transcription from audio files or live microphone input using OpenAI's Whisper.

## ✨ Features

- 🎤 **Live microphone transcription** with automatic silence detection
- 📁 **Audio file transcription** supporting multiple formats
- 📊 **Automatic logging** with timestamps and performance metrics
- 🔧 **Simple CLI interface** for quick usage
- 🐍 **Easy Python API** for integration into your projects
- 📈 **Log analysis tools** to view transcription history and statistics

## 🚀 Quick Start

### Installation

```bash
pip install easytranscribe
```

### Python API

**Live microphone transcription:**
```python
from easytranscribe import capture_and_transcribe

# Start live transcription (speaks and waits for silence)
text = capture_and_transcribe(model_name="base")
print(f"You said: {text}")
```

**Audio file transcription:**
```python
from easytranscribe import transcribe_audio_file

# Transcribe an audio file
text = transcribe_audio_file("path/to/audio.wav", model_name="base")
print(f"Transcription: {text}")
```

**View transcription logs:**
```python
from easytranscribe import view_logs

# View today's logs with statistics
logs = view_logs(date="today", stats=True)
print(f"Total entries: {logs['total_count']}")
```

### Command Line Interface

**Live transcription:**
```bash
easytranscribe live --model base
```

**File transcription:**
```bash
easytranscribe file path/to/audio.wav --model base
```

**View logs:**
```bash
# View today's logs
easytranscribe logs --date today --stats

# View last 10 entries
easytranscribe logs --tail 10

# List available log dates
easytranscribe logs --list-dates
```

## 📋 Available Whisper Models

| Model  | Size | Speed | Accuracy | Use Case |
|--------|------|-------|----------|----------|
| `tiny` | 39MB | Fastest | Good | Real-time, low resource |
| `base` | 74MB | Fast | Better | Balanced performance |
| `small` | 244MB | Medium | Good | Higher accuracy |
| `medium` | 769MB | Slow | Very Good | Professional use |
| `large` | 1550MB | Slowest | Best | Maximum accuracy |
| `turbo` | 809MB | Fast | Excellent | Best balance (default) |

## 🔧 Configuration

### Audio Settings (Live Recording)

The package automatically handles:
- ✅ Silence detection (3 seconds of silence stops recording)
- ✅ Minimum recording time (2 seconds)
- ✅ Audio level monitoring
- ✅ Automatic microphone input

### Logging

Transcriptions are automatically logged to `logs/transcription_YYYY-MM-DD.log` with:
- 📅 Timestamp
- 🤖 Model used
- ⏱️ Processing time
- 🎵 Audio duration (for live recording)
- 📝 Transcribed text

## 🛠️ Development

### Install from Source

```bash
git clone https://github.com/akhshyganesh/easytranscribe.git
cd easytranscribe
pip install -e .
```

### Run Tests

```bash
python test/test_integration.py
```

## 📄 Requirements

- Python 3.8+
- OpenAI Whisper
- sounddevice (for microphone input)
- numpy

## 📖 Documentation

For comprehensive documentation, examples, and API reference, visit:

**🌐 [EasyTranscribe Documentation](https://akhshyganesh.github.io/easytranscribe/)**

The documentation includes:
- 🚀 [Quick Start Guide](https://akhshyganesh.github.io/easytranscribe/quickstart/)
- 💻 [CLI Usage](https://akhshyganesh.github.io/easytranscribe/cli/)
- 🐍 [Python API](https://akhshyganesh.github.io/easytranscribe/api/)
- 📝 [Examples](https://akhshyganesh.github.io/easytranscribe/examples/)
- ⚙️ [Configuration](https://akhshyganesh.github.io/easytranscribe/configuration/)
- 🔧 [Advanced Usage](https://akhshyganesh.github.io/easytranscribe/advanced/)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the amazing speech recognition model
- [sounddevice](https://github.com/spatialaudio/python-sounddevice) for microphone input handling
