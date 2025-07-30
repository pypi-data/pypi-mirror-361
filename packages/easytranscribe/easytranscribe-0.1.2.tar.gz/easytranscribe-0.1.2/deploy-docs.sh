#!/bin/bash
# Deploy documentation to GitHub Pages

set -e

echo "🚀 Deploying EasyTranscribe Documentation to GitHub Pages"

# Check if we're in the right directory
if [ ! -f "mkdocs.yml" ]; then
    echo "❌ Error: mkdocs.yml not found. Please run this script from the project root."
    exit 1
fi

# Check if we're on the right branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "⚠️  Warning: You're not on main/master branch (current: $CURRENT_BRANCH)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled. Please commit your changes first."
        exit 1
    fi
fi

# Install documentation dependencies if needed
if ! command -v mkdocs &> /dev/null; then
    echo "📦 Installing documentation dependencies..."
    pip install -r docs-requirements.txt
fi

# Install package for documentation generation
echo "🔧 Installing easytranscribe for documentation generation..."
pip install -e .

# Deploy to GitHub Pages
echo "🌐 Deploying to GitHub Pages..."
mkdocs gh-deploy --force

echo "✅ Documentation deployed successfully!"
echo "🌐 Visit: https://akhshyganesh.github.io/easytranscribe/"
echo ""
echo "Note: It may take a few minutes for changes to appear on GitHub Pages."
