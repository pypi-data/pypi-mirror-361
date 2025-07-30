# Installation

## Requirements

EasyTranscribe requires Python 3.8 or higher and works on Windows, macOS, and Linux.

## Install from PyPI

The easiest way to install EasyTranscribe is from PyPI using pip:

```bash
pip install easytranscribe
```

## Install from Source

If you want the latest development version or want to contribute to the project:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/akhshyganesh/easytranscribe.git
   cd easytranscribe
   ```

2. **Install in development mode:**
   ```bash
   pip install -e .
   ```

   Or install with development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## System Dependencies

### macOS

On macOS, you may need to install PortAudio for audio capture:

```bash
brew install portaudio
```

### Linux (Ubuntu/Debian)

Install audio development libraries:

```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
```

### Linux (CentOS/RHEL/Fedora)

```bash
sudo yum install portaudio-devel
# or for newer versions:
sudo dnf install portaudio-devel
```

### Windows

On Windows, the audio dependencies are typically included with the pip installation. If you encounter issues, try:

```bash
pip install pipwin
pipwin install pyaudio
```

## Verification

Verify your installation by running:

```bash
easytranscribe --version
```

You should see output similar to:
```
easytranscribe 0.1.1
```

## Whisper Models

EasyTranscribe will automatically download Whisper models on first use. The available models are:

| Model  | Size | Speed | Accuracy |
|--------|------|-------|----------|
| tiny   | 39 MB | Fastest | Good |
| base   | 74 MB | Fast | Better |
| small  | 244 MB | Medium | Good |
| medium | 769 MB | Slow | Better |
| large  | 1550 MB | Slowest | Best |
| turbo  | 805 MB | Fast | Best |

The `base` model is used by default as it provides a good balance of speed and accuracy.

## Troubleshooting

### Permission Denied Error

If you get a permission denied error when trying to access the microphone:

- **macOS**: Grant microphone permissions to your terminal application in System Preferences > Security & Privacy > Privacy > Microphone
- **Linux**: Make sure your user is in the `audio` group: `sudo usermod -a -G audio $USER`
- **Windows**: Ensure microphone privacy settings allow desktop applications to access the microphone

### Audio Device Issues

If you encounter audio device errors, list available devices:

```python
import sounddevice as sd
print(sd.query_devices())
```

### Installation Issues

If you encounter issues during installation:

1. **Update pip**: `pip install --upgrade pip`
2. **Use virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install easytranscribe
   ```
3. **Check Python version**: `python --version` (must be 3.8+)

### Getting Help

If you're still having trouble:

- Check the [GitHub Issues](https://github.com/akhshyganesh/easytranscribe/issues) for known problems
- Create a new issue if your problem isn't already reported
- Include your operating system, Python version, and error messages
