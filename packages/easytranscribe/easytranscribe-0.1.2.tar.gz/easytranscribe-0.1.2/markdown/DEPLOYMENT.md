# Deployment Guide

This guide explains how to use the automated deployment script for EasyTranscribe.

## Quick Start

```bash
# Make the script executable
chmod +x deploy.py

# Run with interactive prompts
python deploy.py

# Or specify version bump type directly
python deploy.py patch   # 0.1.0 -> 0.1.1
python deploy.py minor   # 0.1.0 -> 0.2.0  
python deploy.py major   # 0.1.0 -> 1.0.0
```

## What the Script Does

The deployment script automates the entire release process:

1. **Version Bumping**: Updates version in all relevant files
2. **Git Operations**: Creates commit, tag, and pushes to new branch
3. **GitHub Integration**: Creates a Pull Request automatically
4. **PyPI Publishing**: Builds and publishes package to PyPI

## Prerequisites

### Required Tools

- **Python 3.8+** with pip
- **Git** (configured with your credentials)
- **GitHub CLI** (optional, for automatic PR creation)
  ```bash
  # Install GitHub CLI
  brew install gh        # macOS
  # or
  apt install gh         # Ubuntu
  # or
  winget install GitHub.cli  # Windows
  
  # Authenticate
  gh auth login
  ```

### PyPI Configuration

For automatic PyPI publishing, set up your credentials:

#### Option 1: API Tokens (Recommended)
```bash
# Create ~/.pypirc
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi] 
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_API_TOKEN_HERE
```

#### Option 2: Environment Variables
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_API_TOKEN_HERE
```

### Development Dependencies

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

## Deployment Workflow

### 1. Prepare for Release

Ensure your code is ready:
```bash
# Run tests
pytest __test__/

# Check code quality
black easytranscribe/
flake8 easytranscribe/

# Ensure working directory is clean
git status
```

### 2. Run Deployment Script

```bash
python deploy.py
```

The script will:
- Show current version
- Prompt for version bump type
- Display the new version for confirmation
- Check git status
- Update version files
- Create git commit and tag
- Create new release branch
- Create GitHub Pull Request
- Optionally publish to PyPI
- Push changes to upstream remotes
- Return to develop branch automatically

### 3. Review and Merge

1. Review the created Pull Request on GitHub
2. Merge the PR to main branch
3. The GitHub Actions workflow will automatically publish to PyPI

## Script Options

### Version Bump Types

- **patch**: Bug fixes and small updates (0.1.0 → 0.1.1)
- **minor**: New features, backward compatible (0.1.0 → 0.2.0)
- **major**: Breaking changes (0.1.0 → 1.0.0)

### Interactive vs Command Line

```bash
# Interactive mode (prompts for all options)
python deploy.py

# Direct mode (specify bump type)
python deploy.py patch

# Skip PyPI publication
python deploy.py minor  # Answer 'n' when prompted for PyPI
```

## Files Updated by Script

The script automatically updates:
- `easytranscribe/_version.py`
- `pyproject.toml`
- `setup.py` (if version is hardcoded)

## GitHub Actions Integration

The project includes a CI/CD pipeline (`.github/workflows/ci-cd.yml`) that:
- Runs tests on multiple Python versions
- Performs code quality checks
- Automatically publishes tagged releases to PyPI

## Troubleshooting

### Common Issues

**Git Authentication**:
```bash
# Configure git if needed
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**PyPI Authentication**:
```bash
# Test your PyPI credentials
twine check dist/*
```

**GitHub CLI Not Available**:
- The script will skip PR creation
- Manually create PR from the release branch

**Permission Errors**:
```bash
# Make script executable
chmod +x deploy.py
```

### Recovery from Failed Deployment

If deployment fails partway through:

1. **Revert version changes**:
   ```bash
   git checkout HEAD~1 -- easytranscribe/_version.py pyproject.toml
   ```

2. **Delete tag if created**:
   ```bash
   git tag -d v1.2.3
   git push origin :refs/tags/v1.2.3
   ```

3. **Delete branch if created**:
   ```bash
   git branch -D release-1.2.3
   git push origin --delete release-1.2.3
   ```

## Manual Publication

If you need to publish manually:

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Upload to production PyPI
twine upload dist/*
```

## Security Notes

- Never commit PyPI tokens to git
- Use API tokens instead of passwords
- Consider using GitHub's trusted publishing for PyPI
- Regularly rotate your API tokens
