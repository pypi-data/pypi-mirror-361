#!/bin/bash
# Documentation build and deployment script

set -e

echo "🏗️  Building EasyTranscribe Documentation"

# Check if we're in the right directory
if [ ! -f "mkdocs.yml" ]; then
    echo "❌ Error: mkdocs.yml not found. Please run this script from the project root."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "docs-venv" ]; then
    echo "📦 Creating documentation virtual environment..."
    python -m venv docs-venv
fi

# Activate virtual environment
source docs-venv/bin/activate

# Install documentation dependencies
echo "📚 Installing documentation dependencies..."
pip install -r docs-requirements.txt

# Install the package in development mode for mkdocstrings
echo "🔧 Installing easytranscribe for documentation generation..."
pip install -e .

# Build documentation
echo "🏗️  Building documentation..."
mkdocs build

echo "✅ Documentation built successfully!"
echo "📁 Output directory: site/"
echo ""
echo "To serve locally: mkdocs serve"
echo "To deploy to GitHub Pages: mkdocs gh-deploy"

# Deactivate virtual environment
deactivate
