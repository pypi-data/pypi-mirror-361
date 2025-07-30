# EasyTranscribe Documentation

This directory contains the source files for the EasyTranscribe documentation website.

## Quick Start

### Local Development

1. **Install documentation dependencies:**
   ```bash
   pip install -r docs-requirements.txt
   ```

2. **Install EasyTranscribe in development mode:**
   ```bash
   pip install -e .
   ```

3. **Serve documentation locally:**
   ```bash
   mkdocs serve
   ```

4. **Open in browser:**
   Navigate to `http://127.0.0.1:8000`

### Using the Build Script

Alternatively, use the provided build script:

```bash
./build-docs.sh
```

This script will:
- Create a virtual environment for documentation
- Install all dependencies
- Build the documentation
- Provide instructions for local serving and deployment

## Building Documentation

### Local Build
```bash
mkdocs build
```

### Deploy to GitHub Pages
```bash
mkdocs gh-deploy
```

## Documentation Structure

```
docs/
├── index.md              # Homepage
├── installation.md       # Installation guide
├── quickstart.md         # Quick start tutorial
├── cli.md               # CLI usage guide
├── api.md               # Python API documentation
├── configuration.md     # Configuration options
├── examples.md          # Basic examples
├── advanced.md          # Advanced usage patterns
├── reference.md         # API reference
├── contributing.md      # Contributing guidelines
└── changelog.md         # Project changelog
```

## Features

- **Material Design** - Modern, responsive theme
- **Code Highlighting** - Syntax highlighting for Python and shell
- **API Documentation** - Auto-generated from docstrings
- **Search** - Full-text search functionality
- **Dark/Light Mode** - Theme toggle
- **Mobile Friendly** - Responsive design

## Contributing to Documentation

1. **Edit markdown files** in the `docs/` directory
2. **Test changes locally** with `mkdocs serve`
3. **Submit pull request** with your improvements

### Writing Guidelines

- Use clear, concise language
- Include code examples for all features
- Add screenshots where helpful
- Keep navigation structure logical
- Test all code examples

### Code Examples

When adding code examples:

```python
# Always include imports
from easytranscribe import capture_and_transcribe

# Add comments explaining the code
text = capture_and_transcribe(model_name="base")  # Use base model
print(f"Transcribed: {text}")
```

## Dependencies

- **MkDocs** - Static site generator
- **Material Theme** - Modern theme for MkDocs
- **MkDocstrings** - API documentation from docstrings
- **PyMdown Extensions** - Enhanced markdown features

## Deployment

The documentation is automatically deployed to GitHub Pages when changes are pushed to the main branch.

Manual deployment:
```bash
mkdocs gh-deploy --force
```

## Troubleshooting

### Common Issues

1. **Import errors when building:**
   - Ensure EasyTranscribe is installed: `pip install -e .`

2. **Missing dependencies:**
   - Install docs requirements: `pip install -r docs-requirements.txt`

3. **Build failures:**
   - Check mkdocs.yml syntax
   - Ensure all referenced files exist

### Getting Help

- Check the [MkDocs documentation](https://www.mkdocs.org/)
- Review [Material theme docs](https://squidfunk.github.io/mkdocs-material/)
- Open an issue if you find documentation bugs
