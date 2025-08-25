#!/bin/bash

# Deploy to Cloudflare Pages
# Usage: ./deploy-to-cloudflare.sh [domain]

set -e

DOMAIN=${1:-"your-domain.com"}

echo "🚀 Deploying to Cloudflare for domain: $DOMAIN"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required files exist
if [ ! -f "generate_static_site_optimized.py" ]; then
    echo "❌ generate_static_site_optimized.py not found"
    echo "   Please run this script from the project root directory"
    exit 1
fi

if [ ! -f "layout_clusters_final.csv" ]; then
    echo "❌ layout_clusters_final.csv not found"
    echo "   Please run the deduplication script first"
    exit 1
fi

# Update the CDN configuration for Cloudflare
echo "🔧 Updating CDN configuration for Cloudflare..."
sed -i.bak "s|SELECTED_CDN = \"digitalocean\"|SELECTED_CDN = \"cloudflare\"|" generate_static_site_optimized.py
sed -i.bak "s|https://your-domain.com|https://$DOMAIN|" generate_static_site_optimized.py

# Generate optimized static site
echo "📝 Generating optimized static site..."
python3 generate_static_site_optimized.py

if [ ! -d "static_site_optimized" ]; then
    echo "❌ Static site generation failed"
    exit 1
fi

# Restore original configuration
echo "🔄 Restoring original configuration..."
mv generate_static_site_optimized.py.bak generate_static_site_optimized.py

echo ""
echo "✅ Optimized static site generated successfully!"
echo ""
echo "🌐 Next steps to deploy to Cloudflare:"
echo ""
echo "1. Go to [cloudflare.com](https://cloudflare.com) and sign up"
echo "2. Add your domain: $DOMAIN"
echo "3. Update nameservers to Cloudflare's nameservers"
echo "4. Go to Pages → Create a project"
echo "5. Connect your GitHub repository or upload the static_site_optimized/ folder"
echo "6. Set build settings:"
echo "   - Build command: (leave empty for static site)"
echo "   - Build output directory: /"
echo "   - Root directory: (leave empty)"
echo "7. Deploy!"
echo ""
echo "📁 Your optimized site is in: static_site_optimized/"
echo "⚡ Features enabled:"
echo "   - Lazy loading images"
echo "   - Cache headers"
echo "   - Performance optimizations"
echo "   - Cloudflare CDN ready"
echo ""
echo "🔧 To test locally:"
echo "   cd static_site_optimized"
echo "   python3 -m http.server 8000"
echo "   Open http://localhost:8000"
echo ""
echo "📊 Performance improvements expected:"
echo "   - 3-5x faster loading"
echo "   - Better Core Web Vitals"
echo "   - Global CDN distribution"
echo "   - Automatic image optimization"
