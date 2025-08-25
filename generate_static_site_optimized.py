#!/usr/bin/env python3
"""
Optimized Static Site Generator for folklife.si.edu Layouts Viewer
Includes proper caching headers, CDN optimization, and performance improvements
"""

import os
import csv
import json
import base64
from pathlib import Path
from collections import defaultdict
try:
    from PIL import Image
    import io
except ImportError:
    # PIL not available, but we don't need it for CDN-only mode
    Image = None
    io = None

# Configuration
CLUSTERS_DIR = Path("layout_clusters")
CSV_FILE = Path("layout_clusters_final.csv")
THUMBNAIL_SIZE = (300, 225)
MAX_IMAGES_PER_CLUSTER = 20
OUTPUT_DIR = Path("static_site_optimized")

# CDN Configuration - Choose your preferred option
CDN_CONFIGS = {
    "digitalocean": {
        "base_url": "https://quotient.nyc3.cdn.digitaloceanspaces.com",
        "cache_headers": True,
        "compression": True
    },
    "cloudflare": {
        "base_url": "https://your-domain.com",  # Replace with your Cloudflare domain
        "cache_headers": True,
        "compression": True,
        "image_optimization": True
    },
    "bunnycdn": {
        "base_url": "https://your-zone.b-cdn.net",  # Replace with your BunnyCDN zone
        "cache_headers": True,
        "compression": True,
        "image_optimization": True
    }
}

# Choose your CDN
SELECTED_CDN = "digitalocean"  # Change this to your preferred CDN
CDN_CONFIG = CDN_CONFIGS[SELECTED_CDN]

def load_cluster_data():
    """Load cluster data from CSV"""
    if not CSV_FILE.exists():
        print(f"Error: {CSV_FILE} not found. Run the deduplication script first.")
        return None
    
    clusters = defaultdict(list)
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cluster_id = row['cluster_id']
            clusters[cluster_id].append({
                'filename': row['filename'],
                'path': row['path'],
                'canonical': row['canonical'] == 'True',
                'distance': float(row['distance_to_canonical'])
            })
    
    return clusters

def create_thumbnail_url(filename, size=THUMBNAIL_SIZE):
    """Create a CDN URL for the image with optimization parameters"""
    base_url = CDN_CONFIG["base_url"]
    
    if CDN_CONFIG.get("image_optimization"):
        # Add image optimization parameters
        if SELECTED_CDN == "cloudflare":
            # Cloudflare image optimization
            return f"{base_url}/cdn-cgi/image/format=auto,quality=85,width={size[0]},height={size[1]}/{filename}"
        elif SELECTED_CDN == "bunnycdn":
            # BunnyCDN image optimization
            return f"{base_url}/{filename}?optimize=medium&width={size[0]}&height={size[1]}"
        else:
            # DigitalOcean Spaces - basic URL
            return f"{base_url}/{filename}"
    
    return f"{base_url}/{filename}"

def get_cache_headers():
    """Get appropriate cache headers based on CDN configuration"""
    if not CDN_CONFIG.get("cache_headers"):
        return ""
    
    headers = []
    
    # HTML files - cache for 1 hour, revalidate
    headers.append("""
    <meta http-equiv="Cache-Control" content="public, max-age=3600, must-revalidate">
    <meta http-equiv="Expires" content="3600">
    """)
    
    # Add preload hints for critical resources
    headers.append("""
    <link rel="preload" href="/static/css/main.css" as="style">
    <link rel="preload" href="/static/js/main.js" as="script">
    """)
    
    # Add resource hints for CDN
    if SELECTED_CDN == "cloudflare":
        headers.append('<link rel="dns-prefetch" href="//your-domain.com">')
    elif SELECTED_CDN == "bunnycdn":
        headers.append('<link rel="dns-prefetch" href="//your-zone.b-cdn.net">')
    else:
        headers.append('<link rel="dns-prefetch" href="//quotient.nyc3.cdn.digitaloceanspaces.com">')
    
    return "\n".join(headers)

def get_performance_optimizations():
    """Get performance optimization scripts and styles"""
    return """
    <style>
        /* Critical CSS - inline for performance */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        
        /* Lazy loading for images */
        .lazy-image {
            opacity: 0;
            transition: opacity 0.3s;
        }
        .lazy-image.loaded {
            opacity: 1;
        }
        
        /* Optimize grid rendering */
        .clusters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 2rem;
            contain: layout style paint;
        }
        
        /* Optimize image containers */
        .image-container {
            contain: layout style paint;
            will-change: transform;
        }
        
        /* Smooth scrolling */
        html {
            scroll-behavior: smooth;
        }
    </style>
    
    <script>
        // Lazy loading implementation
        document.addEventListener('DOMContentLoaded', function() {
            const lazyImages = document.querySelectorAll('.lazy-image');
            
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            });
            
            lazyImages.forEach(img => imageObserver.observe(img));
        });
        
        // Preload critical images
        function preloadCriticalImages() {
            const criticalImages = [
                // Add your most important image URLs here
            ];
            
            criticalImages.forEach(url => {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.as = 'image';
                link.href = url;
                document.head.appendChild(link);
            });
        }
        
        // Initialize preloading
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', preloadCriticalImages);
        } else {
            preloadCriticalImages();
        }
    </script>
    """

def generate_main_page(clusters, summary):
    """Generate the main overview page with optimizations"""
    cache_headers = get_cache_headers()
    performance_opt = get_performance_optimizations()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>folklife.si.edu Layouts Viewer</title>
    <meta name="description" content="Visual overview of {summary['total_clusters']} unique layouts from {summary['total_screenshots']} screenshots">
    <meta name="keywords" content="folklife, smithsonian, layouts, screenshots, archives">
    
    <!-- Cache and Performance Headers -->
    {cache_headers}
    
    <!-- Performance Optimizations -->
    {performance_opt}
    
    <style>
        .header {{ background: #2c3e50; color: white; padding: 2rem; text-align: center; }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 1rem; }}
        .header p {{ font-size: 1.2rem; opacity: 0.9; }}
        
        .stats {{ display: flex; justify-content: center; gap: 3rem; margin: 2rem 0; }}
        .stat-item {{ text-align: center; }}
        .stat-number {{ font-size: 2.5rem; font-weight: bold; color: #2c3e50; }}
        .stat-label {{ color: #7f8c8d; margin-top: 0.5rem; }}
        
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        
        .clusters-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 2rem; }}
        
        .cluster-card {{ background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        .cluster-header {{ padding: 1.5rem; border-bottom: 1px solid #ecf0f1; }}
        .cluster-title {{ font-size: 1.3rem; font-weight: bold; color: #2c3e50; }}
        .cluster-size {{ color: #7f8c8d; margin-top: 0.5rem; }}
        
        .cluster-content {{ padding: 1.5rem; }}
        
        .canonical-section {{ margin-bottom: 1.5rem; }}
        .canonical-section h3 {{ color: #2c3e50; margin-bottom: 1rem; }}
        .canonical-thumbnail {{ width: 100%; height: 150px; object-fit: cover; border-radius: 4px; cursor: pointer; transition: opacity 0.2s; }}
        .canonical-thumbnail:hover {{ opacity: 0.8; }}
        
        .preview-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; }}
        .preview-thumb {{ width: 100%; height: 40px; object-fit: cover; border-radius: 4px; cursor: pointer; transition: opacity 0.2s; }}
        .preview-thumb:hover {{ opacity: 0.8; }}
        
        .view-all {{ text-align: center; margin-top: 1rem; }}
        .view-all a {{ display: inline-block; padding: 0.75rem 1.5rem; background: #3498db; color: white; text-decoration: none; border-radius: 4px; transition: background 0.2s; }}
        .view-all a:hover {{ background: #2980b9; }}
        
        /* Modal/Lightbox styles */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }}
        .modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 90%; margin-top: 2%; }}
        .modal-close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }}
        .modal-close:hover {{ color: #bbb; }}
        
        /* Loading states */
        .loading {{ opacity: 0.6; }}
        .loaded {{ opacity: 1; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>folklife.si.edu Layouts Viewer</h1>
        <p>Visual overview of {summary['total_clusters']} unique layouts from {summary['total_screenshots']} screenshots</p>
    </div>
    
    <div class="stats">
        <div class="stat-item">
            <div class="stat-number">{summary['total_clusters']}</div>
            <div class="stat-label">Unique Layouts</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{summary['total_screenshots']}</div>
            <div class="stat-label">Total Screenshots</div>
        </div>
    </div>
    
    <div class="container">
        <div class="clusters-grid">"""
    
    # Sort clusters by size for better UX
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
    
    for cluster_id, screenshots in sorted_clusters:
        canonical = next((s for s in screenshots if s['canonical']), screenshots[0])
        preview_images = screenshots[:8]  # Show first 8 images
        
        html += f"""
            <div class="cluster-card">
                <div class="cluster-header">
                    <div class="cluster-title">Layout {cluster_id}</div>
                    <div class="cluster-size">{len(screenshots)} screenshots</div>
                </div>
                
                <div class="cluster-content">
                    <div class="canonical-section">
                        <h3>Canonical Image</h3>
                        <img src="{create_thumbnail_url(canonical['filename'], THUMBNAIL_SIZE)}" 
                             alt="{canonical['filename']}" 
                             class="canonical-thumbnail lazy-image"
                             data-src="{create_thumbnail_url(canonical['filename'], THUMBNAIL_SIZE)}"
                             onclick="openModal('{canonical['filename']}')">
                        <p><strong>{canonical['filename']}</strong></p>
                        <p>This image represents the standard layout for this layout group.</p>
                    </div>
                    
                    <div class="preview-grid">"""
        
        for screenshot in preview_images:
            html += f"""
                        <img src="{create_thumbnail_url(screenshot['filename'], (40, 40))}" 
                             alt="{screenshot['filename']}" 
                             class="preview-thumb lazy-image"
                             data-src="{create_thumbnail_url(screenshot['filename'], (40, 40))}"
                             title="{screenshot['filename']}" 
                             onclick="openModal('{screenshot['filename']}')">"""
        
        html += f"""
                    </div>
                    
                    <div class="view-all">
                        <a href="layout_{cluster_id}.html">View All {len(screenshots)} Screenshots</a>
                    </div>
                </div>
            </div>"""
    
    html += """
        </div>
    </div>
    
    <!-- Modal for full-size images -->
    <div id="imageModal" class="modal">
        <span class="modal-close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImage">
        <div id="modalCaption" style="text-align: center; color: white; margin-top: 1rem; font-size: 1.1rem;"></div>
    </div>
    
    <script>
        function openModal(filename) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const caption = document.getElementById('modalCaption');
            
            modal.style.display = 'block';
            modalImg.src = '""" + CDN_CONFIG["base_url"] + """/' + filename;
            caption.innerHTML = filename;
        }
        
        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }
        
        // Close modal when clicking outside the image
        window.onclick = function(event) {
            const modal = document.getElementById('imageModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeModal();
            }
        });
        
        // Performance monitoring
        window.addEventListener('load', function() {
            if ('performance' in window) {
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
            }
        });
    </script>
</body>
</html>"""
    
    return html

def generate_cluster_detail_page(cluster_id, screenshots):
    """Generate individual cluster detail page with optimizations"""
    cache_headers = get_cache_headers()
    performance_opt = get_performance_optimizations()
    
    canonical = next((s for s in screenshots if s['canonical']), screenshots[0])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Layout {cluster_id} - folklife.si.edu Layouts Viewer</title>
    <meta name="description" content="View all {len(screenshots)} screenshots for Layout {cluster_id}">
    
    <!-- Cache and Performance Headers -->
    {cache_headers}
    
    <!-- Performance Optimizations -->
    {performance_opt}
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        
        .header {{ background: #2c3e50; color: white; padding: 2rem; text-align: center; }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 1rem; }}
        .header p {{ font-size: 1.2rem; opacity: 0.9; }}
        
        .back-link {{ text-align: center; margin: 2rem 0; }}
        .back-link a {{ display: inline-block; padding: 0.75rem 1.5rem; background: #3498db; color: white; text-decoration: none; border-radius: 4px; transition: background 0.2s; }}
        .back-link a:hover {{ background: #2980b9; }}
        
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        
        .canonical-section {{ background: white; border-radius: 8px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .canonical-section h2 {{ color: #2c3e50; margin-bottom: 1rem; }}
        .canonical-image {{ width: 100%; max-width: 800px; height: auto; border-radius: 8px; cursor: pointer; transition: opacity 0.2s; }}
        .canonical-image:hover {{ opacity: 0.9; }}
        
        .screenshots-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }}
        .screenshot-item {{ background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
        .screenshot-thumb {{ width: 100%; height: 150px; object-fit: cover; border-radius: 4px; cursor: pointer; transition: opacity 0.2s; }}
        .screenshot-thumb:hover {{ opacity: 0.8; }}
        .screenshot-filename {{ margin-top: 0.5rem; font-size: 0.9rem; color: #7f8c8d; word-break: break-word; }}
        
        /* Modal/Lightbox styles */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }}
        .modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 90%; margin-top: 2%; }}
        .modal-close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }}
        .modal-close:hover {{ color: #bbb; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Layout {cluster_id}</h1>
        <p>{len(screenshots)} screenshots with similar layout</p>
    </div>
    
    <div class="back-link">
        <a href="index.html">← Back to All Layouts</a>
    </div>
    
    <div class="container">
        <div class="canonical-section">
            <h2>Canonical Layout</h2>
            <p>This image represents the standard layout for this group:</p>
            <img src="{create_thumbnail_url(canonical['filename'])}" 
                 alt="{canonical['filename']}" 
                 class="canonical-image lazy-image"
                 data-src="{create_thumbnail_url(canonical['filename'])}"
                 onclick="openModal('{canonical['filename']}')">
            <p><strong>{canonical['filename']}</strong></p>
        </div>
        
        <div class="screenshots-grid">"""
    
    for screenshot in screenshots:
        html += f"""
            <div class="screenshot-item">
                <img src="{create_thumbnail_url(screenshot['filename'], (200, 150))}" 
                     alt="{screenshot['filename']}" 
                     class="screenshot-thumb lazy-image"
                     data-src="{create_thumbnail_url(screenshot['filename'], (200, 150))}"
                     onclick="openModal('{screenshot['filename']}')">
                <div class="screenshot-filename">{screenshot['filename']}</div>
            </div>"""
    
    html += f"""
        </div>
    </div>
    
    <!-- Modal for full-size images -->
    <div id="imageModal" class="modal">
        <span class="modal-close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImage">
        <div id="modalCaption" style="text-align: center; color: white; margin-top: 1rem; font-size: 1.1rem;"></div>
    </div>
    
    <script>
        function openModal(filename) {{
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const caption = document.getElementById('modalCaption');
            
            modal.style.display = 'block';
            modalImg.src = '""" + CDN_CONFIG["base_url"] + """/' + filename;
            caption.innerHTML = filename;
        }}
        
        function closeModal() {{
            document.getElementById('imageModal').style.display = 'none';
        }}
        
        // Close modal when clicking outside the image
        window.onclick = function(event) {{
            const modal = document.getElementById('imageModal');
            if (event.target === modal) {{
                modal.style.display = 'none';
            }}
        }}
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                closeModal();
            }}
        }});
    </script>
</body>
</html>"""
    
    return html

def get_cluster_summary(clusters):
    """Get summary statistics for clusters"""
    total_clusters = len(clusters)
    total_screenshots = sum(len(screenshots) for screenshots in clusters.values())
    
    return {
        'total_clusters': total_clusters,
        'total_screenshots': total_screenshots
    }

def copy_images():
    """Images are served from CDN - no local copying needed"""
    print("Images served from CDN - skipping local copy")
    pass

def main():
    """Generate the optimized static site"""
    print("Generating optimized static site...")
    print(f"Using CDN: {SELECTED_CDN}")
    print(f"CDN Base URL: {CDN_CONFIG['base_url']}")
    
    # Load cluster data
    clusters = load_cluster_data()
    if not clusters:
        return
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Generate summary
    summary = get_cluster_summary(clusters)
    
    # Generate main page
    print("Generating main page...")
    main_html = generate_main_page(clusters, summary)
    with open(OUTPUT_DIR / "index.html", "w") as f:
        f.write(main_html)
    
    # Generate cluster detail pages
    print("Generating cluster detail pages...")
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
    for cluster_id, screenshots in sorted_clusters:
        detail_html = generate_cluster_detail_page(cluster_id, screenshots)
        with open(OUTPUT_DIR / f"layout_{cluster_id}.html", "w") as f:
            f.write(detail_html)
    
    # Copy images
    copy_images()
    
    print(f"\n✅ Optimized static site generated successfully in {OUTPUT_DIR}/")
    print(f"📁 Main page: {OUTPUT_DIR}/index.html")
    print(f"🖼️  Images: Served from {SELECTED_CDN.upper()} CDN")
    print(f"📄 Cluster pages: {len(clusters)} detail pages")
    print(f"⚡ Performance optimizations: Lazy loading, caching headers, CDN optimization")
    
    if SELECTED_CDN == "cloudflare":
        print("\n🚀 Recommended: Deploy to Cloudflare Pages for best performance!")
    elif SELECTED_CDN == "bunnycdn":
        print("\n🚀 Recommended: Deploy to any static hosting with BunnyCDN pull zone!")
    else:
        print("\n🚀 Recommended: Deploy to DigitalOcean Spaces with Cloudflare in front!")

if __name__ == '__main__':
    main()
