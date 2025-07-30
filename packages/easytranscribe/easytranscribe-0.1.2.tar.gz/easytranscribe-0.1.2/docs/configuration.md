# Configuration

EasyTranscribe works out of the box with sensible defaults, but offers several configuration options to customize its behavior for your specific needs.

## Environment Variables

### Model Configuration

**`EASYTRANSCRIBE_MODEL`**
: Default Whisper model to use when none is specified
: Default: `"base"`
: Options: `tiny`, `base`, `small`, `medium`, `large`, `turbo`

```bash
export EASYTRANSCRIBE_MODEL=medium
easytranscribe live  # Will use medium model
```

**`WHISPER_CACHE_DIR`**
: Directory where Whisper models are cached
: Default: `~/.cache/whisper` (Linux/macOS) or `%USERPROFILE%\.cache\whisper` (Windows)

```bash
export WHISPER_CACHE_DIR=/custom/model/cache
```

### Audio Configuration

**`EASYTRANSCRIBE_SAMPLE_RATE`**
: Audio sample rate for recording
: Default: `16000` (16 kHz)
: Note: Whisper works best with 16 kHz audio

```bash
export EASYTRANSCRIBE_SAMPLE_RATE=22050
```

**`EASYTRANSCRIBE_SILENCE_THRESHOLD`**
: Silence detection threshold (0.0 to 1.0)
: Default: `0.01`
: Lower values = more sensitive to silence

```bash
export EASYTRANSCRIBE_SILENCE_THRESHOLD=0.005
```

**`EASYTRANSCRIBE_SILENCE_DURATION`**
: Seconds of silence before stopping recording
: Default: `3.0`

```bash
export EASYTRANSCRIBE_SILENCE_DURATION=2.5
```

### Logging Configuration

**`EASYTRANSCRIBE_LOG_DIR`**
: Directory for transcription logs
: Default: `./logs` (current directory)

```bash
export EASYTRANSCRIBE_LOG_DIR=/var/log/easytranscribe
```

**`EASYTRANSCRIBE_LOG_LEVEL`**
: Logging verbosity level
: Default: `INFO`
: Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`

```bash
export EASYTRANSCRIBE_LOG_LEVEL=DEBUG
```

## Configuration File

Create a configuration file at `~/.config/easytranscribe/config.ini` (Linux/macOS) or `%APPDATA%\easytranscribe\config.ini` (Windows):

```ini
[model]
default = base
cache_dir = ~/.cache/whisper

[audio]
sample_rate = 16000
silence_threshold = 0.01
silence_duration = 3.0
min_recording_time = 2.0

[logging]
directory = ./logs
level = INFO
max_log_files = 30

[performance]
use_gpu = auto
num_threads = auto
```

### Configuration File Sections

#### `[model]` Section

**`default`**
: Default model name
: Options: `tiny`, `base`, `small`, `medium`, `large`, `turbo`

**`cache_dir`**
: Model cache directory path

#### `[audio]` Section

**`sample_rate`**
: Audio sample rate in Hz

**`silence_threshold`**
: Audio level threshold for silence detection (0.0 - 1.0)

**`silence_duration`**
: Seconds of silence before stopping

**`min_recording_time`**
: Minimum recording duration after speech starts

#### `[logging]` Section

**`directory`**
: Log file directory

**`level`**
: Log level (DEBUG, INFO, WARNING, ERROR)

**`max_log_files`**
: Maximum number of daily log files to keep

#### `[performance]` Section

**`use_gpu`**
: GPU usage preference
: Options: `auto`, `true`, `false`

**`num_threads`**
: Number of CPU threads to use
: Options: `auto`, or specific number

## Python Configuration

### Runtime Configuration

```python
import os
from easytranscribe import capture_and_transcribe

# Set environment variables at runtime
os.environ['EASYTRANSCRIBE_MODEL'] = 'medium'
os.environ['EASYTRANSCRIBE_SILENCE_DURATION'] = '2.0'

# Use configured settings
text = capture_and_transcribe()
```

### Configuration Class

For advanced users, create a custom configuration:

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TranscriptionConfig:
    model_name: str = "base"
    sample_rate: int = 16000
    silence_threshold: float = 0.01
    silence_duration: float = 3.0
    min_recording_time: float = 2.0
    log_dir: Path = Path("./logs")
    verbose: bool = False

def custom_transcribe(config: TranscriptionConfig):
    """Transcribe with custom configuration."""
    # Set up environment
    os.environ['EASYTRANSCRIBE_LOG_DIR'] = str(config.log_dir)

    # Use configuration
    from easytranscribe import capture_and_transcribe
    return capture_and_transcribe(
        model_name=config.model_name,
        verbose=config.verbose
    )

# Usage
config = TranscriptionConfig(
    model_name="medium",
    silence_duration=2.5,
    verbose=True
)
text = custom_transcribe(config)
```

## Device Configuration

### Audio Device Selection

List available audio devices:

```python
import sounddevice as sd
print(sd.query_devices())
```

Set default input device:

```python
import sounddevice as sd

# Set by device ID
sd.default.device[0] = 1  # Input device ID

# Set by device name
devices = sd.query_devices()
for i, device in enumerate(devices):
    if "USB Microphone" in device['name']:
        sd.default.device[0] = i
        break
```

### GPU Configuration

EasyTranscribe automatically detects and uses GPU when available. To force CPU usage:

```bash
export CUDA_VISIBLE_DEVICES=""
```

To specify GPU device:

```bash
export CUDA_VISIBLE_DEVICES=0  # Use first GPU
```

## Performance Tuning

### Model Selection by Use Case

```python
# Configuration for different scenarios
CONFIGS = {
    "quick_notes": {
        "model": "tiny",
        "silence_duration": 2.0,
    },
    "meetings": {
        "model": "medium",
        "silence_duration": 4.0,
    },
    "interviews": {
        "model": "large",
        "silence_duration": 5.0,
    },
    "real_time": {
        "model": "turbo",
        "silence_duration": 1.5,
    }
}

def get_config(use_case):
    return CONFIGS.get(use_case, CONFIGS["quick_notes"])
```

### Memory Optimization

For systems with limited memory:

```ini
[model]
default = tiny

[performance]
use_gpu = false
num_threads = 2
```

### Batch Processing Optimization

For processing many files:

```ini
[model]
default = base  # Good balance of speed/accuracy

[performance]
use_gpu = auto
num_threads = auto
```

## Security Configuration

### Log File Permissions

Set restrictive permissions on log files:

```bash
# Linux/macOS
chmod 600 ~/.config/easytranscribe/config.ini
chmod -R 700 /path/to/logs/

# Ensure log directory is secure
mkdir -p ~/.local/share/easytranscribe/logs
chmod 700 ~/.local/share/easytranscribe/logs
```

### Disable Logging

For privacy-sensitive applications:

```python
import os
os.environ['EASYTRANSCRIBE_LOG_LEVEL'] = 'ERROR'  # Minimal logging
```

Or create a privacy mode configuration:

```ini
[logging]
level = ERROR
directory = /tmp  # Temporary storage
max_log_files = 1
```

## Troubleshooting Configuration

### Check Current Configuration

```python
import os

def show_config():
    """Display current configuration."""
    config_vars = [
        'EASYTRANSCRIBE_MODEL',
        'EASYTRANSCRIBE_SAMPLE_RATE',
        'EASYTRANSCRIBE_SILENCE_THRESHOLD',
        'EASYTRANSCRIBE_SILENCE_DURATION',
        'EASYTRANSCRIBE_LOG_DIR',
        'EASYTRANSCRIBE_LOG_LEVEL'
    ]

    print("Current Configuration:")
    print("=" * 30)
    for var in config_vars:
        value = os.environ.get(var, "Not set")
        print(f"{var}: {value}")

show_config()
```

### Reset to Defaults

```bash
# Clear all EasyTranscribe environment variables
unset EASYTRANSCRIBE_MODEL
unset EASYTRANSCRIBE_SAMPLE_RATE
unset EASYTRANSCRIBE_SILENCE_THRESHOLD
unset EASYTRANSCRIBE_SILENCE_DURATION
unset EASYTRANSCRIBE_LOG_DIR
unset EASYTRANSCRIBE_LOG_LEVEL
```

### Configuration Validation

```python
def validate_config():
    """Validate configuration settings."""
    import os

    # Check model
    model = os.environ.get('EASYTRANSCRIBE_MODEL', 'base')
    valid_models = ['tiny', 'base', 'small', 'medium', 'large', 'turbo']
    if model not in valid_models:
        print(f"⚠️  Invalid model: {model}")

    # Check thresholds
    threshold = float(os.environ.get('EASYTRANSCRIBE_SILENCE_THRESHOLD', 0.01))
    if not 0.0 <= threshold <= 1.0:
        print(f"⚠️  Invalid silence threshold: {threshold}")

    # Check duration
    duration = float(os.environ.get('EASYTRANSCRIBE_SILENCE_DURATION', 3.0))
    if duration < 0.5:
        print(f"⚠️  Very short silence duration: {duration}")

    print("✅ Configuration validation complete")

validate_config()
```

This configuration system provides flexibility while maintaining ease of use for both simple and advanced use cases.
