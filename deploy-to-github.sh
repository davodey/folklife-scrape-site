#!/bin/bash

# Deploy to GitHub Pages
# Usage: ./deploy-to-github.sh [repo-name]

set -e

REPO_NAME=${1:-"folklife-layouts-viewer"}

echo "🚀 Deploying to GitHub Pages: $REPO_NAME"

# Check if git is configured
if ! git config --get user.name &> /dev/null; then
    echo "❌ Git is not configured. Please set your name and email:"
    echo "   git config --global user.name 'Your Name'"
    echo "   git config --global user.email 'your.email@example.com'"
    exit 1
fi

# Generate static site
echo "📝 Generating static site..."
python generate_static_site.py

if [ ! -d "static_site" ]; then
    echo "❌ Static site generation failed"
    exit 1
fi

# Navigate to static site directory
cd static_site

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial static site"
fi

# Check if remote exists
if ! git remote get-url origin &> /dev/null; then
    echo "🔗 Adding remote origin..."
    git remote add origin https://github.com/$(git config --get user.name)/$REPO_NAME.git
fi

# Add and commit changes
echo "💾 Committing changes..."
git add .
git commit -m "Update static site $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub
echo "☁️  Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Deployed successfully!"
echo "🌐 Your site: https://$(git config --get user.name).github.io/$REPO_NAME"
echo ""
echo "📊 To enable GitHub Pages:"
echo "   1. Go to your repo on GitHub"
echo "   2. Settings → Pages"
echo "   3. Source: 'Deploy from a branch'"
echo "   4. Branch: 'main' → '/' (root)"
echo ""
echo "🔧 To update:"
echo "   ./deploy-to-github.sh $REPO_NAME"
