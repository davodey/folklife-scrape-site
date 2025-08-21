#!/bin/bash

# Deploy to DigitalOcean Spaces
# Usage: ./deploy-to-spaces.sh [space-name]

set -e

SPACE_NAME=${1:-"folklife-layouts"}

echo "🚀 Deploying to DigitalOcean Spaces: $SPACE_NAME"

# Check if s3cmd is installed
if ! command -v s3cmd &> /dev/null; then
    echo "❌ s3cmd is not installed. Please install it first:"
    echo "   brew install s3cmd"
    echo "   s3cmd --configure"
    exit 1
fi

# Check if s3cmd is configured
if [ ! -f ~/.s3cfg ]; then
    echo "❌ s3cmd is not configured. Please run:"
    echo "   s3cmd --configure"
    exit 1
fi

# Generate static site
echo "📝 Generating static site..."
python generate_static_site.py

if [ ! -d "static_site" ]; then
    echo "❌ Static site generation failed"
    exit 1
fi

# Upload to Spaces
echo "☁️  Uploading to DigitalOcean Spaces..."
s3cmd sync static_site/ s3://$SPACE_NAME/ --acl-public --delete-removed

echo ""
echo "✅ Deployed successfully!"
echo "🌐 Your site: https://$SPACE_NAME.nyc3.cdn.digitaloceanspaces.com"
echo ""
echo "📊 To monitor usage:"
echo "   - Go to DigitalOcean Spaces dashboard"
echo "   - Check transfer and storage usage"
echo ""
echo "🔧 To update:"
echo "   ./deploy-to-spaces.sh $SPACE_NAME"
