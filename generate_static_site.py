#!/usr/bin/env python3
"""
Static Site Generator for folklife.si.edu Layouts Viewer
Generates static HTML files that can be hosted on DigitalOcean Spaces or GitHub Pages
"""

import os
import csv
import json
import base64
from pathlib import Path
from collections import defaultdict
from PIL import Image
import io

# Configuration
CLUSTERS_DIR = Path("layout_clusters")
CSV_FILE = Path("layout_clusters_final.csv")
THUMBNAIL_SIZE = (300, 225)
MAX_IMAGES_PER_CLUSTER = 20
OUTPUT_DIR = Path("static_site")

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

def create_thumbnail(image_path, size=THUMBNAIL_SIZE):
    """Create a thumbnail and return as base64 data URL"""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            
            # Create a copy to avoid modifying original
            img_copy = img.copy()
            
            # Resize maintaining aspect ratio
            img_copy.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convert to base64 for inline display
            buffer = io.BytesIO()
            img_copy.save(buffer, format='JPEG', quality=90)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        print(f"Warning: Could not create thumbnail for {image_path}: {e}")
        return None

def get_cluster_summary(clusters):
    """Generate summary statistics"""
    total_clusters = len(clusters)
    total_screenshots = sum(len(cluster) for cluster in clusters.values())
    
    return {
        'total_clusters': total_clusters,
        'total_screenshots': total_screenshots
    }

def generate_main_page(clusters, summary):
    """Generate the main index page"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>folklife.si.edu Layouts Viewer</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        
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
        .canonical-thumbnail {{ max-width: 100%; height: auto; border-radius: 4px; cursor: pointer; transition: opacity 0.2s; }}
        .canonical-thumbnail:hover {{ opacity: 0.8; }}
        
        .preview-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; }}
        .preview-thumb {{ width: 100%; height: auto; border-radius: 4px; cursor: pointer; transition: opacity 0.2s; }}
        .preview-thumb:hover {{ opacity: 0.8; }}
        
        .view-all {{ text-align: center; margin-top: 1rem; }}
        .view-all a {{ display: inline-block; padding: 0.75rem 1.5rem; background: #3498db; color: white; text-decoration: none; border-radius: 4px; transition: background 0.2s; }}
        .view-all a:hover {{ background: #2980b9; }}
        
        /* Modal/Lightbox styles */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }}
        .modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 90%; margin-top: 2%; }}
        .modal-close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }}
        .modal-close:hover {{ color: #bbb; }}
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

    for cluster_id, screenshots in clusters.items():
        # Find canonical image
        canonical = next((s for s in screenshots if s['canonical']), screenshots[0])
        
        # Create thumbnail for canonical
        canonical_thumbnail = create_thumbnail(f"folklife-screens-x/{canonical['filename']}")
        
        # Get preview thumbnails (up to 8)
        preview_screenshots = screenshots[:8]
        
        html += f"""
            <div class="cluster-card">
                <div class="cluster-header">
                    <div class="cluster-title">Layout {cluster_id}</div>
                    <div class="cluster-size">{len(screenshots)} screenshots</div>
                </div>
                
                <div class="cluster-content">
                    <div class="canonical-section">
                        <h3>Canonical Image</h3>"""
        
        if canonical_thumbnail:
            html += f"""
                        <img src="{canonical_thumbnail}" alt="{canonical['filename']}" class="canonical-thumbnail" 
                             onclick="openModal('{canonical['filename']}')">"""
        
        html += f"""
                        <p><strong>{canonical['filename']}</strong></p>
                        <p>This image represents the standard layout for this layout group.</p>
                    </div>
                    
                    <div class="preview-grid">"""
        
        for screenshot in preview_screenshots:
            thumbnail = create_thumbnail(f"folklife-screens-x/{screenshot['filename']}")
            if thumbnail:
                html += f"""
                        <img src="{thumbnail}" alt="{screenshot['filename']}" class="preview-thumb" 
                             title="{screenshot['filename']}" onclick="openModal('{screenshot['filename']}')">"""
        
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
            modalImg.src = 'images/' + filename;
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
    </script>
</body>
</html>"""
    
    return html

def generate_cluster_detail_page(cluster_id, screenshots):
    """Generate a detail page for a specific cluster"""
    # Find canonical image
    canonical = next((s for s in screenshots if s['canonical']), screenshots[0])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Layout {cluster_id} Details</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        
        .header {{ background: #2c3e50; color: white; padding: 2rem; text-align: center; }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 1rem; }}
        .header p {{ font-size: 1.2rem; opacity: 0.9; }}
        
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        
        .back-link {{ display: inline-block; margin-bottom: 2rem; color: #3498db; text-decoration: none; font-size: 1.1rem; }}
        .back-link:hover {{ text-decoration: underline; }}
        
        .cluster-info {{ background: white; border-radius: 8px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .canonical-section h3 {{ color: #2c3e50; margin-bottom: 1rem; }}
        .canonical-thumbnail {{ max-width: 300px; height: auto; border-radius: 4px; cursor: pointer; transition: opacity 0.2s; margin: 1rem 0; }}
        .canonical-thumbnail:hover {{ opacity: 0.8; }}
        
        .images-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 2rem; }}
        
        .image-card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .image-card img {{ width: 100%; height: auto; cursor: pointer; transition: opacity 0.2s; }}
        .image-card img:hover {{ opacity: 0.8; }}
        .image-info {{ padding: 1rem; }}
        .image-name {{ font-weight: bold; margin-bottom: 0.5rem; color: #2c3e50; }}
        .image-distance {{ color: #7f8c8d; font-size: 0.9rem; }}
        .canonical-badge {{ background: #27ae60; color: white; padding: 0.2rem 0.5rem; border-radius: 3px; font-size: 0.8rem; margin-left: 0.5rem; }}
        
        /* Modal/Lightbox styles */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }}
        .modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 90%; margin-top: 2%; }}
        .modal-close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }}
        .modal-close:hover {{ color: #bbb; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Layout {cluster_id} Details</h1>
        <p>{len(screenshots)} screenshots with similar layouts</p>
    </div>
    
    <div class="container">
        <a href="index.html" class="back-link">← Back to All Layouts</a>
        
        <div class="cluster-info">
            <div class="canonical-section">
                <h3>Canonical Image</h3>"""
    
    # Create thumbnail for canonical
    canonical_thumbnail = create_thumbnail(f"folklife-screens-x/{canonical['filename']}")
    if canonical_thumbnail:
        html += f"""
                <img src="{canonical_thumbnail}" alt="{canonical['filename']}" class="canonical-thumbnail" 
                     onclick="openModal('{canonical['filename']}')">"""
    
    html += f"""
                <p><strong>{canonical['filename']}</strong></p>
                <p>This image represents the standard layout for this layout group.</p>
            </div>
        </div>
        
        <div class="images-grid">"""
    
    for screenshot in screenshots:
        html += f"""
            <div class="image-card">
                <img src="images/{screenshot['filename']}" alt="{screenshot['filename']}" 
                     onclick="openModal('{screenshot['filename']}')">
                <div class="image-info">
                    <div class="image-name">
                        {screenshot['filename']}"""
        
        if screenshot['canonical']:
            html += '<span class="canonical-badge">Canonical</span>'
        
        html += f"""
                    </div>
                    <div class="image-distance">
                        Distance: {screenshot['distance']:.6f}
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
            modalImg.src = 'images/' + filename;
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
    </script>
</body>
</html>"""
    
    return html

def copy_images():
    """Copy images to the static site directory"""
    images_dir = OUTPUT_DIR / "images"
    images_dir.mkdir(exist_ok=True)
    
    source_dir = Path("folklife-screens-x")
    if not source_dir.exists():
        print(f"Warning: {source_dir} not found. Images will not be copied.")
        return
    
    print("Copying images...")
    for image_file in source_dir.glob("*.png"):
        dest_file = images_dir / image_file.name
        if not dest_file.exists():
            print(f"  Copying {image_file.name}")
            # Copy the file
            import shutil
            shutil.copy2(image_file, dest_file)

def main():
    """Generate the static site"""
    print("Generating static site...")
    
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
    for cluster_id, screenshots in clusters.items():
        detail_html = generate_cluster_detail_page(cluster_id, screenshots)
        with open(OUTPUT_DIR / f"layout_{cluster_id}.html", "w") as f:
            f.write(detail_html)
    
    # Copy images
    copy_images()
    
    print(f"\n✅ Static site generated successfully in {OUTPUT_DIR}/")
    print(f"📁 Main page: {OUTPUT_DIR}/index.html")
    print(f"🖼️  Images: {OUTPUT_DIR}/images/")
    print(f"📄 Cluster pages: {len(clusters)} detail pages")
    print("\n🚀 Deploy to DigitalOcean Spaces or GitHub Pages for cheap hosting!")

if __name__ == '__main__':
    main()
