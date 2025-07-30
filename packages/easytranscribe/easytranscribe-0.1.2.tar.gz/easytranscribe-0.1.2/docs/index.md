# EasyTranscribe

<div class="hero">
    <h1>🎤 Easy Speech-to-Text Transcription</h1>
    <p class="hero-description">
        Transform speech into text effortlessly with OpenAI's Whisper.
        Support for live microphone input and audio file processing.
    </p>
</div>

[![PyPI version](https://badge.fury.io/py/easytranscribe.svg)](https://badge.fury.io/py/easytranscribe)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **🎤 Live Microphone Transcription** - Real-time speech capture with automatic silence detection
- **📁 Audio File Processing** - Support for multiple audio formats (WAV, MP3, M4A, etc.)
- **📊 Automatic Logging** - Comprehensive logging with timestamps and performance metrics
- **🔧 Simple CLI Interface** - Easy-to-use command-line tools for quick transcription
- **🐍 Python API** - Clean, intuitive API for integration into your projects
- **📈 Log Analysis** - Built-in tools to view transcription history and statistics

## Quick Start

### Installation

```bash
pip install easytranscribe
```

### Live Transcription

Start transcribing from your microphone immediately:

```bash
easytranscribe live
```

### File Transcription

Transcribe an audio file:

```bash
easytranscribe file path/to/audio.wav
```

### Python API

```python
from easytranscribe import capture_and_transcribe, transcribe_audio_file

# Live microphone transcription
text = capture_and_transcribe()
print(f"You said: {text}")

# File transcription
text = transcribe_audio_file("audio.wav")
print(f"File content: {text}")
```

## Use Cases

- **Meeting Notes** - Automatically transcribe meetings and calls
- **Voice Memos** - Convert voice recordings to searchable text
- **Accessibility** - Provide text alternatives for audio content
- **Content Creation** - Transcribe interviews, podcasts, and videos
- **Development** - Add speech-to-text capabilities to your applications

## Why EasyTranscribe?

- **Zero Configuration** - Works out of the box with sensible defaults
- **High Accuracy** - Powered by OpenAI's state-of-the-art Whisper model
- **Multiple Models** - Choose from tiny to large models based on your needs
- **Cross-Platform** - Works on Windows, macOS, and Linux
- **Extensible** - Easy to integrate with other AI tools and workflows

## Getting Started

Ready to start transcribing? Check out our [Installation Guide](installation.md) and [Quick Start Tutorial](quickstart.md).

---

<style>
.hero {
    text-align: center;
    padding: 2rem 0;
    margin-bottom: 2rem;
}

.hero h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    background: linear-gradient(45deg, #2196F3, #1976D2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-description {
    font-size: 1.2rem;
    color: #666;
    max-width: 600px;
    margin: 0 auto 2rem;
    line-height: 1.6;
}
</style>
