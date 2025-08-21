#!/usr/bin/env python3
"""
Layout Cluster Viewer - Web UI for viewing screenshot clusters
"""

from flask import Flask, render_template, jsonify, send_from_directory
import os
import json
import csv
from pathlib import Path
from collections import defaultdict
import base64
from PIL import Image
import io

app = Flask(__name__)

# Configuration
CLUSTERS_DIR = Path("layout_clusters")
CSV_FILE = Path("layout_clusters_final.csv")
THUMBNAIL_SIZE = (300, 225)  # width, height - increased for better quality
MAX_IMAGES_PER_CLUSTER = 20  # Limit for performance

def load_cluster_data():
    """Load cluster data from CSV and organize by clusters"""
    clusters = defaultdict(list)
    
    if not CSV_FILE.exists():
        return {}
    
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cluster_id = row['cluster_id']
            clusters[cluster_id].append({
                'filename': row['filename'],
                'path': row['path'],
                'canonical': row['canonical'],
                'distance': float(row['distance_to_canonical'])
            })
    
    # Sort clusters by size (largest first)
    return dict(sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True))

def create_thumbnail(image_path, size=THUMBNAIL_SIZE):
    """Create a thumbnail from an image file"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
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
        print(f"Error creating thumbnail for {image_path}: {e}")
        return None

def get_cluster_summary():
    """Get summary statistics for all clusters"""
    clusters = load_cluster_data()
    
    summary = {
        'total_clusters': len(clusters),
        'total_screenshots': sum(len(cluster) for cluster in clusters.values()),
        'clusters': []
    }
    
    for cluster_id, screenshots in clusters.items():
        # Find canonical image
        canonical = None
        for screenshot in screenshots:
            if screenshot['filename'] == screenshot['canonical']:
                canonical = screenshot
                break
        
        if not canonical:
            canonical = screenshots[0]  # Fallback
        
        # Create thumbnail for canonical
        canonical_thumb = create_thumbnail(canonical['path'])
        
        cluster_info = {
            'id': cluster_id,
            'size': len(screenshots),
            'canonical': canonical,
            'canonical_thumbnail': canonical_thumb,
            'screenshots': screenshots[:MAX_IMAGES_PER_CLUSTER],  # Limit for performance
            'has_more': len(screenshots) > MAX_IMAGES_PER_CLUSTER
        }
        
        summary['clusters'].append(cluster_info)
    
    return summary

@app.route('/')
def index():
    """Main page showing all clusters"""
    summary = get_cluster_summary()
    return render_template('index.html', summary=summary)

@app.route('/api/clusters')
def api_clusters():
    """API endpoint for cluster data"""
    summary = get_cluster_summary()
    return jsonify(summary)

@app.route('/cluster/<cluster_id>')
def cluster_detail(cluster_id):
    """Detailed view of a specific cluster"""
    clusters = load_cluster_data()
    if cluster_id not in clusters:
        return "Cluster not found", 404
    
    cluster_data = clusters[cluster_id]
    canonical = None
    for screenshot in cluster_data:
        if screenshot['filename'] == screenshot['canonical']:
            canonical = screenshot
            break
    
    if not canonical:
        canonical = cluster_data[0]
    
    return render_template('cluster_detail.html', 
                         cluster_id=cluster_id, 
                         cluster_data=cluster_data,
                         canonical=canonical)

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve image files"""
    return send_from_directory('folklife-screens-x', filename)

@app.route('/api/cluster/<cluster_id>/thumbnails')
def cluster_thumbnails(cluster_id):
    """Get thumbnails for a specific cluster"""
    clusters = load_cluster_data()
    if cluster_id not in clusters:
        return jsonify({'error': 'Cluster not found'}), 404
    
    cluster_data = clusters[cluster_id]
    thumbnails = []
    
    for screenshot in cluster_data[:MAX_IMAGES_PER_CLUSTER]:
        thumb = create_thumbnail(screenshot['path'])
        if thumb:
            thumbnails.append({
                'filename': screenshot['filename'],
                'path': screenshot['path'],
                'thumbnail': thumb,
                'distance': screenshot['distance']
            })
    
    return jsonify({
        'cluster_id': cluster_id,
        'thumbnails': thumbnails,
        'total': len(cluster_data)
    })

def create_templates():
    """Create basic HTML templates"""
    
    # Main template
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>folklife.si.edu Layouts Viewer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 2rem; text-align: center; }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
        .stats { background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
        .stat-item { text-align: center; }
        .stat-number { font-size: 2rem; font-weight: bold; color: #3498db; }
        .stat-label { color: #7f8c8d; margin-top: 0.5rem; }
        .clusters-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 2rem; }
        .cluster-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .cluster-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }
        .cluster-header { background: #ecf0f1; padding: 1rem; border-bottom: 1px solid #ddd; }
        .cluster-title { font-size: 1.2rem; font-weight: bold; color: #2c3e50; margin-bottom: 0.5rem; }
        .cluster-size { color: #7f8c8d; font-size: 0.9rem; }
        .canonical-image { width: 100%; height: 150px; object-fit: cover; }
        .cluster-preview { padding: 1rem; }
        .preview-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin-top: 1rem; }
        .preview-thumb { width: 100%; height: 40px; object-fit: cover; border-radius: 4px; }
        .view-all { text-align: center; margin-top: 1rem; }
        .view-btn { background: #3498db; color: white; padding: 0.5rem 1rem; text-decoration: none; border-radius: 4px; display: inline-block; }
        .view-btn:hover { background: #2980b9; }
        .loading { text-align: center; padding: 2rem; color: #7f8c8d; }
        
        /* Modal/Lightbox styles */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }
        .modal-content { margin: auto; display: block; max-width: 90%; max-height: 90%; margin-top: 2%; }
        .modal-close { position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }
        .modal-close:hover { color: #bbb; }
        .clickable { cursor: pointer; transition: opacity 0.2s; }
        .clickable:hover { opacity: 0.8; }
    </style>
</head>
<body>
    <div class="header">
        <h1>folklife.si.edu Layouts Viewer</h1>
        <p>Visual overview of {{ summary.total_clusters }} unique layouts from {{ summary.total_screenshots }} screenshots</p>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">{{ summary.total_clusters }}</div>
                    <div class="stat-label">Unique Layouts</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ summary.total_screenshots }}</div>
                    <div class="stat-label">Total Screenshots</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ "%.1f"|format(summary.total_screenshots / summary.total_clusters) }}</div>
                    <div class="stat-label">Avg per Cluster</div>
                </div>
            </div>
        </div>
        
        <div class="clusters-grid">
            {% for cluster in summary.clusters %}
            <div class="cluster-card">
                <div class="cluster-header">
                    <div class="cluster-title">Layout {{ cluster.id }}</div>
                    <div class="cluster-size">{{ cluster.size }} screenshots</div>
                </div>
                
                {% if cluster.canonical_thumbnail %}
                <img src="{{ cluster.canonical_thumbnail }}" alt="Canonical" class="canonical-image clickable" 
                     onclick="openModal('{{ cluster.canonical.path }}', '{{ cluster.canonical.filename }}')">
                {% endif %}
                
                <div class="cluster-preview">
                    <div><strong>Canonical:</strong> {{ cluster.canonical.filename }}</div>
                    
                    {% if cluster.screenshots %}
                    <div class="preview-grid">
                        {% for screenshot in cluster.screenshots[:8] %}
                        <img src="/images/{{ screenshot.filename }}" alt="{{ screenshot.filename }}" class="preview-thumb clickable" 
                             title="{{ screenshot.filename }}" onclick="openModal('{{ screenshot.path }}', '{{ screenshot.filename }}')">
                        {% endfor %}
                    </div>
                    {% endif %}
                    
                    {% if cluster.has_more %}
                    <div class="view-all">
                        <a href="/cluster/{{ cluster.id }}" class="view-btn">View All {{ cluster.size }} Images</a>
                    </div>
                    {% else %}
                    <div class="view-all">
                        <a href="/cluster/{{ cluster.id }}" class="view-btn">View Details</a>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <!-- Modal for full-size images -->
    <div id="imageModal" class="modal">
        <span class="modal-close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImage">
        <div id="modalCaption" style="text-align: center; color: white; margin-top: 1rem; font-size: 1.1rem;"></div>
    </div>
    
    <script>
        function openModal(imagePath, filename) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const caption = document.getElementById('modalCaption');
            
            modal.style.display = 'block';
            modalImg.src = '/images/' + filename;
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
    
    # Cluster detail template
    detail_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Layout {{ cluster_id }} Details</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 1.5rem; }
        .header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; }
        .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
        .back-link { color: #3498db; text-decoration: none; margin-bottom: 1rem; display: inline-block; }
        .back-link:hover { text-decoration: underline; }
        .cluster-info { background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .canonical-section { background: #ecf0f1; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .images-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
        .image-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .image-card img { width: 100%; height: 200px; object-fit: cover; }
        .image-info { padding: 1rem; }
        .image-name { font-weight: bold; margin-bottom: 0.5rem; word-break: break-all; }
        .image-distance { color: #7f8c8d; font-size: 0.9rem; }
        .canonical-badge { background: #27ae60; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 0.5rem; }
        
        /* Modal/Lightbox styles */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }
        .modal-content { margin: auto; display: block; max-width: 90%; max-height: 90%; margin-top: 2%; }
        .modal-close { position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }
        .modal-close:hover { color: #bbb; }
        .clickable { cursor: pointer; transition: opacity 0.2s; }
        .clickable:hover { opacity: 0.8; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Layout {{ cluster_id }} Details</h1>
        <p>{{ cluster_data|length }} screenshots with similar layouts</p>
    </div>
    
    <div class="container">
        <a href="/" class="back-link">← Back to All Layouts</a>
        
        <div class="cluster-info">
            <div class="canonical-section">
                <h3>Canonical Image</h3>
                <img src="/images/{{ canonical.filename }}" alt="{{ canonical.filename }}" 
                     class="canonical-thumbnail clickable" 
                     onclick="openModal('{{ canonical.path }}', '{{ canonical.filename }}')"
                     style="max-width: 300px; height: auto; border-radius: 4px; margin: 1rem 0;">
                <p><strong>{{ canonical.filename }}</strong></p>
                <p>This image represents the standard layout for this layout group.</p>
            </div>
        </div>
        
        <div class="images-grid">
            {% for screenshot in cluster_data %}
            <div class="image-card">
                <img src="/images/{{ screenshot.filename }}" alt="{{ screenshot.filename }}" 
                     class="clickable" onclick="openModal('{{ screenshot.path }}', '{{ screenshot.filename }}')">
                <div class="image-info">
                    <div class="image-name">
                        {{ screenshot.filename }}
                        {% if screenshot.filename == screenshot.canonical %}
                        <span class="canonical-badge">Canonical</span>
                        {% endif %}
                    </div>
                    <div class="image-distance">
                        Distance: {{ "%.6f"|format(screenshot.distance) }}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <!-- Modal for full-size images -->
    <div id="imageModal" class="modal">
        <span class="modal-close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImage">
        <div id="modalCaption" style="text-align: center; color: white; margin-top: 1rem; font-size: 1.1rem;"></div>
    </div>
    
    <script>
        function openModal(imagePath, filename) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const caption = document.getElementById('modalCaption');
            
            modal.style.display = 'block';
            modalImg.src = '/images/' + filename;
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
    
    # Write templates
    with open("templates/index.html", "w") as f:
        f.write(index_html)
    
    with open("templates/cluster_detail.html", "w") as f:
        f.write(detail_html)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='folklife.si.edu Layouts Viewer')
    parser.add_argument('--generate-templates-only', action='store_true', 
                       help='Generate HTML templates and exit')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Create templates directory if it doesn't exist
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Create basic templates
    create_templates()
    
    if args.generate_templates_only:
        print("Templates generated successfully")
        exit(0)
    
    print("Starting folklife.si.edu Layouts Viewer...")
    print(f"Clusters directory: {CLUSTERS_DIR}")
    print(f"CSV file: {CSV_FILE}")
    print(f"Open http://{args.host}:{args.port} in your browser")
    
    # Run the Flask app
    app.run(debug=args.debug, host=args.host, port=args.port)
