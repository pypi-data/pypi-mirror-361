# Contributing to EasyTranscribe

Thank you for your interest in contributing to EasyTranscribe! This guide will help you get started with contributing to the project.

## Ways to Contribute

- 🐛 **Bug Reports** - Help us identify and fix issues
- 💡 **Feature Requests** - Suggest new features or improvements
- 📖 **Documentation** - Improve our documentation
- 🧪 **Testing** - Add tests or test the software
- 💻 **Code Contributions** - Submit bug fixes or new features

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/akhshyganesh/easytranscribe.git
cd easytranscribe

# Add the original repository as upstream
git remote add upstream https://github.com/akhshyganesh/easytranscribe.git
```

### 2. Set Up Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Branch

```bash
# Create a branch for your feature or fix
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

## Development Guidelines

### Code Style

We follow Python PEP 8 standards with some additional guidelines:

- **Line Length**: Maximum 88 characters (Black formatter default)
- **Imports**: Use absolute imports, group them logically
- **Docstrings**: Use Google-style docstrings for all public functions
- **Type Hints**: Add type hints for function parameters and return values

Example:

```python
def transcribe_audio_file(
    file_path: str,
    model_name: str = "base",
    verbose: bool = False
) -> str:
    """
    Transcribe an audio file to text using Whisper.

    Args:
        file_path: Path to the audio file to transcribe
        model_name: Whisper model to use for transcription
        verbose: Whether to show detailed processing information

    Returns:
        The transcribed text from the audio file

    Raises:
        FileNotFoundError: If the audio file doesn't exist
        ValueError: If the model name is invalid
    """
```

### Testing

#### Running Tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=easytranscribe

# Run specific test file
python -m pytest tests/test_speech_to_text.py

# Run tests with verbose output
python -m pytest -v
```

#### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names: `test_transcribe_audio_file_with_valid_input`
- Test both success and failure cases
- Use fixtures for common test data

Example test:

```python
import pytest
from easytranscribe import transcribe_audio_file

def test_transcribe_audio_file_with_nonexistent_file():
    """Test that transcribing a nonexistent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        transcribe_audio_file("nonexistent_file.wav")

def test_transcribe_audio_file_with_valid_file(sample_audio_file):
    """Test successful transcription of a valid audio file."""
    result = transcribe_audio_file(sample_audio_file)
    assert isinstance(result, str)
    assert len(result) > 0
```

### Documentation

#### Building Documentation

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material mkdocstrings[python]

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

#### Documentation Guidelines

- Use clear, concise language
- Include code examples for all features
- Add docstrings to all public functions and classes
- Update documentation when adding new features

## Submitting Changes

### 1. Commit Guidelines

Follow conventional commit format:

```bash
# Format: type(scope): description
git commit -m "feat(cli): add support for batch file processing"
git commit -m "fix(audio): resolve microphone permission issue on macOS"
git commit -m "docs(api): add examples for transcribe_audio_file"
```

**Commit Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `test`: Adding or modifying tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

### 2. Pull Request Process

1. **Update your branch** with the latest changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run the full test suite**:
   ```bash
   python -m pytest
   python -m pytest --cov=easytranscribe
   ```

3. **Run linting and formatting**:
   ```bash
   black easytranscribe tests
   flake8 easytranscribe tests
   mypy easytranscribe
   ```

4. **Create a pull request** with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Reference to any related issues
   - Screenshots/examples if applicable

### 3. Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested this change manually

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
```

## Code Review Process

1. **Automated Checks**: All PRs must pass automated tests and linting
2. **Peer Review**: At least one maintainer will review your code
3. **Feedback**: Address any feedback promptly and professionally
4. **Approval**: Once approved, a maintainer will merge your PR

## Development Setup for Different Areas

### Core Transcription Features

```bash
# Test audio functionality
python -c "from easytranscribe import capture_and_transcribe; print(capture_and_transcribe())"

# Test file processing
python -c "from easytranscribe import transcribe_audio_file; print(transcribe_audio_file('test.wav'))"
```

### CLI Development

```bash
# Test CLI commands
easytranscribe --help
easytranscribe live --model tiny
easytranscribe logs --stats
```

### Documentation Development

```bash
# Live reload documentation
mkdocs serve --dev-addr 127.0.0.1:8001

# Test documentation builds
mkdocs build --strict
```

## Release Process

For maintainers releasing new versions:

1. **Update Version**: Update version in `easytranscribe/_version.py`
2. **Update Changelog**: Add changes to `CHANGELOG.md`
3. **Create Release**: Use GitHub releases with proper tagging
4. **PyPI Upload**: Automated via GitHub Actions

## Community Guidelines

- **Be Respectful**: Treat all contributors with respect and kindness
- **Be Patient**: Remember that contributors have different experience levels
- **Be Helpful**: Provide constructive feedback and assistance
- **Stay On Topic**: Keep discussions relevant to the project

## Getting Help

- **Discord/Slack**: [Link to community chat if available]
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: [maintainer email] for sensitive issues

## Recognition

Contributors will be:
- Listed in the project's contributors section
- Mentioned in release notes for significant contributions
- Eligible for maintainer status based on consistent contributions

Thank you for contributing to EasyTranscribe! 🎤✨
