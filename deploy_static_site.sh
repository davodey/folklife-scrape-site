#!/bin/bash

echo "🚀 Deploying Multi-Site Static Site..."

# Generate static site
echo "📁 Generating static site..."
python generate_static_site_multi.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Static site generated successfully!"
    echo ""
    echo "📁 Files generated in docs/ directory:"
echo "  - index.html (Folklife main page)"
echo "  - index_festival.html (Festival main page)"
    echo "  - layout_folklife_*.html (81 folklife cluster pages)"
    echo "  - layout_festival_*.html (291 festival cluster pages)"
    echo ""
    echo "🌐 Test locally:"
    echo "  cd docs && python -m http.server 8000"
    echo "  Open http://localhost:8000"
    echo ""
    echo "🚀 Deploy to GitHub Pages:"
    echo "  git add docs/"
    echo "  git commit -m 'Update static site'"
    echo "  git push"
    echo ""
    echo "🎯 Deploy to DigitalOcean Spaces:"
    echo "  s3cmd sync docs/ s3://your-space-name/ --acl-public --delete-removed"
    echo ""
    echo "💡 The static site includes:"
    echo "  - Multi-site navigation (Folklife ↔ Festival)"
    echo "  - CDN image serving from DigitalOcean Spaces"
    echo "  - Distance-sorted cluster views"
    echo "  - Responsive design with outline buttons"
    echo "  - Modal image viewer"
else
    echo "❌ Error generating static site"
    exit 1
fi
