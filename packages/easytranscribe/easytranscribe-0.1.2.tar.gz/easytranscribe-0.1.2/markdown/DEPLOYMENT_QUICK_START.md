# 🚀 EasyTranscribe Automated Deployment System

This repository now includes a complete automated deployment system that handles versioning, git operations, GitHub integration, and PyPI publishing.

## Quick Start

```bash
# Run interactive deployment
python deploy.py

# Or specify version bump directly
python deploy.py patch   # Bug fixes
python deploy.py minor   # New features  
python deploy.py major   # Breaking changes
```

## What Gets Automated

✅ **Version Management**
- Updates `_version.py`, `pyproject.toml`, and `setup.py`
- Follows semantic versioning (major.minor.patch)

✅ **Git Operations**
- Creates commit with version bump
- Creates git tag (e.g., `v1.2.3`)
- Creates new release branch
- Pushes to origin and upstream remotes
- Returns to develop branch automatically

✅ **GitHub Integration**
- Automatically creates Pull Request
- Uses GitHub CLI if available
- Includes detailed release notes

✅ **PyPI Publishing**
- Builds package with proper metadata
- Option to test on Test PyPI first
- Publishes to production PyPI

✅ **CI/CD Pipeline**
- GitHub Actions workflow included
- Tests on multiple Python versions
- Automatic publishing on tag push

## Files Added

- `deploy.py` - Main deployment script
- `requirements-dev.txt` - Development dependencies
- `.github/workflows/ci-cd.yml` - GitHub Actions workflow
- `DEPLOYMENT.md` - Detailed deployment guide

## Pre-requisites Setup

1. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Configure PyPI credentials** (create `~/.pypirc`):
   ```ini
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

3. **Install GitHub CLI** (optional, for auto PR creation):
   ```bash
   brew install gh        # macOS
   gh auth login
   ```

## Typical Workflow

1. **Develop and test your changes**
2. **Run deployment script:**
   ```bash
   python deploy.py minor  # for new features
   ```
3. **Review the auto-created Pull Request**
4. **Merge PR to main** - GitHub Actions will auto-publish to PyPI

## Safety Features

- ✅ Validates environment before starting
- ✅ Shows what will change before proceeding
- ✅ Asks for confirmation at each major step
- ✅ Can test on Test PyPI before production
- ✅ Creates separate branch for review
- ✅ Comprehensive error handling

## Example Output

```
🚀 Starting EasyTranscribe deployment process...
   Current version: 0.1.0

🔍 Validating environment...
   ✅ Environment validation passed!

📋 Version bump options:
   1. patch  - Bug fixes (0.1.0 -> 0.1.1)
   2. minor  - New features (0.1.0 -> 0.2.0)
   3. major  - Breaking changes (0.1.0 -> 1.0.0)

Select version bump type (patch/minor/major): minor

📈 Version will be bumped: 0.1.0 -> 0.2.0

Proceed with deployment to version 0.2.0? (y/N): y

📝 Updating version from 0.1.0 to 0.2.0
   ✅ Updated easytranscribe/_version.py
   ✅ Updated pyproject.toml

🏷️  Creating git commit and tag for version 0.2.0
🚀 Pushing to branch: release-0.2.0
📋 Creating GitHub Pull Request for release-0.2.0
   ✅ Pull Request created successfully!

🎯 Version 0.2.0 has been committed and pushed!
   Branch: release-0.2.0
   Tag: v0.2.0

Publish to PyPI now? (y/N): y
Publish to Test PyPI first? (recommended) (y/N): y

📦 Building package for PyPI
   ✅ Package built successfully!
🚀 Publishing to Test PyPI
   ✅ Successfully published to Test PyPI!

Test publication successful! Publish to production PyPI? (y/N): y
🚀 Publishing to PyPI
   ✅ Successfully published to PyPI!

🔄 Finalizing deployment...
   Current branch: release-0.2.0
📤 Pushing changes to upstream...
   ✅ Pushed release branch and tag to origin
🔄 Switching back to develop branch...
   ✅ Successfully returned to develop branch and updated

🎉 Deployment completed successfully!
   New version: 0.2.0
   Branch: release-0.2.0
   Tag: v0.2.0
   Returned to develop branch
```

See `DEPLOYMENT.md` for detailed documentation and troubleshooting.
