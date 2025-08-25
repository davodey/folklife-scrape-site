#!/usr/bin/env python3
"""
Multi-Site Static Site Generator for Layouts Viewer
Generates static HTML files for both folklife.si.edu and festival.si.edu
Outputs to docs/ directory for GitHub Pages deployment
"""

import os
import csv
import json
import base64
from pathlib import Path
from collections import defaultdict
from PIL import Image
import io

# Site configurations
SITE_CONFIGS = {
    'folklife': {
        'name': 'folklife',
        'display_name': 'Folklife',
        'clusters_dir': Path("layout_clusters"),
        'csv_file': Path("layout_clusters_final.csv"),
        'images_dir': Path("folklife-screens-x"),
        'color': '#2c3e50',
        'description': 'folklife.si.edu'
    },
    'festival': {
        'name': 'festival',
        'display_name': 'Festival',
        'clusters_dir': Path("festival_layout_clusters"),
        'csv_file': Path("festival_layout_clusters_strict.csv"),
        'images_dir': Path("festival-screens-x"),
        'color': '#8e44ad',
        'description': 'festival.si.edu'
    }
}

# Configuration
THUMBNAIL_SIZE = (300, 225)
MAX_IMAGES_PER_CLUSTER = 20
OUTPUT_DIR = Path("docs")
SPACES_CDN_BASE = "https://quotient.nyc3.cdn.digitaloceanspaces.com"

def load_cluster_data(site):
    """Load cluster data from CSV for a specific site"""
    site_config = SITE_CONFIGS[site]
    csv_file = site_config['csv_file']
    
    if not csv_file.exists():
        print(f"Error: {csv_file} not found for {site}. Run the deduplication script first.")
        return None
    
    clusters = defaultdict(list)
    with open(csv_file, 'r') as f:
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

def get_cluster_summary(clusters, site):
    """Generate summary statistics for a site"""
    total_clusters = len(clusters)
    total_screenshots = sum(len(cluster) for cluster in clusters.values())
    
    return {
        'site': site,
        'site_config': SITE_CONFIGS[site],
        'total_clusters': total_clusters,
        'total_screenshots': total_screenshots,
        'clusters': clusters
    }

def generate_main_page(summary, site_configs):
    """Generate the main index page with site switching"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{summary['site_config']['display_name']} Layouts Viewer</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        
        /* Site Toggle Toolbar */
        .site-toolbar {{ 
            background: #34495e; 
            padding: 1rem 2rem; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .site-toggle {{ display: flex; gap: 0.5rem; }}
        .site-btn {{ 
            padding: 0.75rem 1.5rem; 
            border: 2px solid white; 
            border-radius: 6px; 
            cursor: pointer; 
            font-weight: 500; 
            transition: all 0.2s;
            text-decoration: none;
            display: inline-block;
            background: transparent;
            color: white;
        }}
        .site-btn.active {{ 
            background: rgba(255, 255, 255, 0.2); 
            color: white; 
            border-color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        .site-btn:not(.active) {{ 
            background: transparent; 
            color: white; 
            border-color: rgba(255, 255, 255, 0.7);
        }}
        .site-btn:hover:not(.active) {{ 
            background: rgba(255, 255, 255, 0.1); 
            border-color: white;
            transform: translateY(-1px);
        }}
        .site-info {{ color: white; font-size: 0.9rem; opacity: 0.8; }}
        
        .header {{ 
            background: {summary['site_config']['color']}; 
            color: white; 
            padding: 2rem; 
            text-align: center; 
        }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .header p {{ font-size: 1.1rem; opacity: 0.9; }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
        .stats {{ background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }}
        .stat-item {{ text-align: center; }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: {summary['site_config']['color']}; }}
        .stat-label {{ color: #7f8c8d; margin-top: 0.5rem; }}
        
        .clusters-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 2rem; }}
        .cluster-card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s; }}
        .cluster-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }}
        .cluster-header {{ background: #ecf0f1; padding: 1rem; border-bottom: 1px solid #ddd; }}
        .cluster-title {{ font-size: 1.2rem; font-weight: bold; color: #2c3e50; margin-bottom: 0.5rem; }}
        .cluster-size {{ color: #7f8c8d; font-size: 0.9rem; }}
        .canonical-image {{ 
            width: 100%; 
            height: 150px; 
            object-fit: cover; 
            transition: opacity 0.3s ease;
        }}
        .canonical-image.loading {{ opacity: 0.3; }}
        .canonical-image.loaded {{ opacity: 1; }}
        
        .cluster-preview {{ padding: 1rem; }}
        .preview-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin-top: 1rem; }}
        .preview-thumb {{ 
            width: 100%; 
            height: 40px; 
            object-fit: cover; 
            border-radius: 4px; 
            transition: opacity 0.3s ease;
        }}
        .preview-thumb.loading {{ opacity: 0.3; }}
        .preview-thumb.loaded {{ opacity: 1; }}
        
        /* Skeleton loading states */
        .skeleton {{ 
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
            border-radius: 4px;
        }}
        
        @keyframes loading {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
        
        .image-container {{ position: relative; }}
        .loading-overlay {{ 
            position: absolute; 
            top: 0; 
            left: 0; 
            right: 0; 
            bottom: 0; 
            background: #f8f9fa; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: #6c757d; 
            font-size: 0.8rem;
            border-radius: 4px;
        }}
        .loading-overlay.skeleton {{ 
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }}
        .loading-overlay.failed {{ 
            background: #dc3545; 
            color: white; 
            font-weight: bold; 
            font-size: 1.1rem; 
        }}
        .loading-overlay.loaded {{ 
            display: none; 
        }}
        .view-all {{ text-align: center; margin-top: 1rem; }}
        .view-btn {{ 
            background: {summary['site_config']['color']}; 
            color: white; 
            padding: 0.5rem 1rem; 
            text-decoration: none; 
            border-radius: 4px; 
            display: inline-block; 
            transition: background 0.2s;
        }}
        .view-btn:hover {{ opacity: 0.9; }}
        
        /* Modal/Lightbox styles */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }}
        .modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 90%; margin-top: 2%; }}
        .modal-close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }}
        .modal-close:hover {{ color: #bbb; }}
        .clickable {{ cursor: pointer; transition: opacity 0.2s; }}
        .clickable:hover {{ opacity: 0.8; }}
    </style>
</head>
<body>
    <!-- Site Toggle Toolbar -->
    <div class="site-toolbar">
        <div class="site-toggle">
            <a href="index.html" class="site-btn{' active' if summary['site'] == 'folklife' else ''}">
                {site_configs['folklife']['display_name']}
            </a>
            <a href="index_festival.html" class="site-btn{' active' if summary['site'] == 'festival' else ''}">
                {site_configs['festival']['display_name']}
            </a>
        </div>
        <div class="site-info">
            Currently viewing: {summary['site_config']['display_name']}
        </div>
    </div>
    
            <div class="header">
            <h1>{summary['site_config']['display_name']} Layouts Viewer</h1>
            <p>Visual overview of {summary['total_clusters']} unique layouts from {summary['total_screenshots']} screenshots</p>
            <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">
                💡 <strong>How it works:</strong> Each cluster groups screenshots with similar visual layouts. 
                Images are sorted by similarity to the "canonical" (most representative) image.
            </p>
        </div>
    
    <div class="container">
        <div class="stats">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">{summary['total_clusters']}</div>
                    <div class="stat-label">Unique Layouts</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{summary['total_screenshots']}</div>
                    <div class="stat-label">Total Screenshots</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{summary['total_screenshots'] / summary['total_clusters']:.1f}</div>
                    <div class="stat-label">Avg per Cluster</div>
                </div>
            </div>
        </div>
        
        <div class="clusters-grid">"""
    
    # Sort clusters by size (largest first)
    sorted_clusters = sorted(summary['clusters'].items(), key=lambda x: len(x[1]), reverse=True)
    
    for cluster_id, screenshots in sorted_clusters:
        # Find canonical image
        canonical = next((s for s in screenshots if s['canonical']), screenshots[0])
        
        # Get preview images (up to 8)
        preview_images = screenshots[:8]
        
        html += f"""
            <div class="cluster-card">
                <div class="cluster-header">
                    <div class="cluster-title">Layout {cluster_id}</div>
                    <div class="cluster-size">{len(screenshots)} screenshots</div>
                </div>
                
                <div class="image-container">
                    <div class="loading-overlay skeleton" id="loading-{cluster_id}-canonical">
                        <span>Loading...</span>
                    </div>
                    <img src="{SPACES_CDN_BASE}/{canonical['filename']}" 
                         alt="Canonical" 
                         class="canonical-image clickable loading" 
                         onclick="openModal('{canonical['filename']}')"
                         onload="imageLoaded(this, 'loading-{cluster_id}-canonical')"
                         onerror="imageError(this, 'loading-{cluster_id}-canonical')">
                </div>
                
                <div class="cluster-preview">
                    <div><strong>Canonical:</strong> {canonical['filename']}</div>
                    
                    <div class="preview-grid">"""
        
        for i, screenshot in enumerate(preview_images):
            html += f"""
                        <div class="image-container">
                            <div class="loading-overlay skeleton" id="loading-{cluster_id}-preview-{i}">
                                <span>...</span>
                            </div>
                            <img src="{SPACES_CDN_BASE}/{screenshot['filename']}" 
                                 alt="{screenshot['filename']}" 
                                 class="preview-thumb clickable loading" 
                                 title="{screenshot['filename']}" 
                                 onclick="openModal('{screenshot['filename']}')"
                                 onload="imageLoaded(this, 'loading-{cluster_id}-preview-{i}')"
                                 onerror="imageError(this, 'loading-{cluster_id}-preview-{i}')">
                        </div>"""
        
        html += f"""
                    </div>
                    
                    <div class="view-all">
                        <a href="layout_{summary['site']}_{cluster_id}.html" class="view-btn">View All {len(screenshots)} Images</a>
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
            modalImg.src = 'https://quotient.nyc3.cdn.digitaloceanspaces.com/' + filename;
            caption.innerHTML = filename;
        }
        
        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }
        
        function imageLoaded(img, loadingId) {
            // Hide loading overlay and show image
            const loadingOverlay = document.getElementById(loadingId);
            if (loadingOverlay) {
                loadingOverlay.classList.remove('skeleton');
                loadingOverlay.classList.add('loaded');
            }
            img.classList.remove('loading');
            img.classList.add('loaded');
        }
        
        function imageError(img, loadingId) {
            // Show error state with red background and "Failed" text
            const loadingOverlay = document.getElementById(loadingId);
            if (loadingOverlay) {
                loadingOverlay.classList.remove('skeleton');
                loadingOverlay.classList.add('failed');
                loadingOverlay.innerHTML = '<span>Failed</span>';
            }
            img.style.display = 'none';
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

def generate_cluster_detail_page(cluster_id, screenshots, site, site_config):
    """Generate a cluster detail page"""
    # Sort screenshots by distance (0.0 first)
    sorted_screenshots = sorted(screenshots, key=lambda x: x['distance'])
    
    # Find canonical image
    canonical = next((s for s in screenshots if s['canonical']), screenshots[0])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_config['display_name']} - Layout {cluster_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        
        /* Site Toggle Toolbar */
        .site-toolbar {{ 
            background: #34495e; 
            padding: 1rem 2rem; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .site-toggle {{ display: flex; gap: 0.5rem; }}
        .site-btn {{ 
            padding: 0.75rem 1.5rem; 
            border: 2px solid white; 
            border-radius: 6px; 
            cursor: pointer; 
            font-weight: 500; 
            transition: all 0.2s;
            text-decoration: none;
            display: inline-block;
            background: transparent;
            color: white;
        }}
        .site-btn.active {{ 
            background: rgba(255, 255, 255, 0.2); 
            color: white; 
            border-color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        .site-btn:not(.active) {{ 
            background: transparent; 
            color: white; 
            border-color: rgba(255, 255, 255, 0.7);
        }}
        .site-btn:hover:not(.active) {{ 
            background: rgba(255, 255, 255, 0.1); 
            border-color: white;
            transform: translateY(-1px);
        }}
        .site-info {{ color: white; font-size: 0.9rem; opacity: 0.8; }}
        
        .header {{ 
            background: {site_config['color']}; 
            color: white; 
            padding: 2rem; 
            text-align: center; 
        }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .header p {{ font-size: 1.1rem; opacity: 0.9; }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
        .back-link {{ margin-bottom: 2rem; }}
        .back-btn {{ 
            background: {site_config['color']}; 
            color: white; 
            padding: 0.75rem 1.5rem; 
            text-decoration: none; 
            border-radius: 6px; 
            display: inline-block;
            transition: opacity 0.2s;
        }}
        .back-btn:hover {{ opacity: 0.9; }}
        
        .cluster-info {{ background: white; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .cluster-header {{ display: flex; align-items: center; gap: 2rem; margin-bottom: 2rem; }}
        .canonical-image {{ width: 200px; height: 150px; object-fit: cover; border-radius: 8px; }}
        .cluster-details h2 {{ color: #2c3e50; margin-bottom: 1rem; }}
        .cluster-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem; }}
        .stat-item {{ text-align: center; }}
        .stat-number {{ font-size: 1.5rem; font-weight: bold; color: {site_config['color']}; }}
        .stat-label {{ color: #7f8c8d; font-size: 0.9rem; }}
        
        .images-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }}
        .image-card {{ 
            background: white; 
            border-radius: 8px; 
            overflow: hidden; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
            transition: transform 0.2s; 
        }}
        .image-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }}
        .image-card img {{ width: 100%; height: 200px; object-fit: cover; cursor: pointer; transition: opacity 0.2s; }}
        .image-card img:hover {{ opacity: 0.8; }}
        .image-info {{ padding: 1rem; }}
        .image-name {{ font-weight: bold; color: #2c3e50; margin-bottom: 0.5rem; word-break: break-word; }}
        .canonical-badge {{ 
            background: {site_config['color']}; 
            color: white; 
            padding: 0.25rem 0.5rem; 
            border-radius: 4px; 
            font-size: 0.8rem; 
            margin-left: 0.5rem; 
        }}
        .image-distance {{ color: #7f8c8d; font-size: 0.9rem; }}
        
        /* User feedback styles */
        .feedback-section {{ 
            background: #f8f9fa; 
            border: 1px solid #dee2e6; 
            border-radius: 8px; 
            padding: 1rem; 
            margin-top: 1rem; 
        }}
        .feedback-title {{ 
            font-weight: bold; 
            color: #495057; 
            margin-bottom: 0.5rem; 
        }}
        .feedback-buttons {{ 
            display: flex; 
            gap: 0.5rem; 
            flex-wrap: wrap; 
        }}
        .feedback-btn {{ 
            background: #6c757d; 
            color: white; 
            border: none; 
            padding: 0.25rem 0.5rem; 
            border-radius: 4px; 
            font-size: 0.8rem; 
            cursor: pointer; 
            transition: background 0.2s; 
        }}
        .feedback-btn:hover {{ background: #5a6268; }}
        .feedback-btn.flag {{ background: #dc3545; }}
        .feedback-btn.flag:hover {{ background: #c82333; }}
        .feedback-btn.correct {{ background: #28a745; }}
        .feedback-btn.correct:hover {{ background: #218838; }}
        .feedback-form {{ 
            display: none; 
            margin-top: 1rem; 
            padding: 1rem; 
            background: white; 
            border-radius: 6px; 
            border: 1px solid #ced4da; 
        }}
        .feedback-form.show {{ display: block; }}
        .feedback-form textarea {{ 
            width: 100%; 
            min-height: 80px; 
            padding: 0.5rem; 
            border: 1px solid #ced4da; 
            border-radius: 4px; 
            margin-bottom: 0.5rem; 
            font-family: inherit; 
        }}
        .feedback-form button {{ 
            background: #007bff; 
            color: white; 
            border: none; 
            padding: 0.5rem 1rem; 
            border-radius: 4px; 
            cursor: pointer; 
        }}
        .feedback-form button:hover {{ background: #0056b3; }}
        .similarity-warning {{ 
            background: #fff3cd; 
            border: 1px solid #ffeaa7; 
            color: #856404; 
            padding: 0.5rem; 
            border-radius: 4px; 
            margin-bottom: 0.5rem; 
            font-size: 0.9rem; 
        }}
        
        /* Loading overlay styles */
        .image-container {{ position: relative; }}
        .loading-overlay {{ 
            position: absolute; 
            top: 0; 
            left: 0; 
            right: 0; 
            bottom: 0; 
            background: #f8f9fa; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: #6c757d; 
            font-size: 0.8rem;
            border-radius: 4px;
        }}
        .loading-overlay.skeleton {{ 
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }}
        .loading-overlay.failed {{ 
            background: #dc3545; 
            color: white; 
            font-weight: bold; 
            font-size: 1.1rem; 
        }}
        .loading-overlay.loaded {{ 
            display: none; 
        }}
        
        @keyframes loading {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
        
        /* Modal/Lightbox styles */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }}
        .modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 90%; margin-top: 2%; }}
        .modal-close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }}
        .modal-close:hover {{ color: #bbb; }}
    </style>
</head>
<body>
    <!-- Site Toggle Toolbar -->
    <div class="site-toolbar">
        <div class="site-toggle">
            <a href="index.html" class="site-btn{' active' if site == 'folklife' else ''}">
                {SITE_CONFIGS['folklife']['display_name']}
            </a>
            <a href="index_festival.html" class="site-btn{' active' if site == 'festival' else ''}">
                {SITE_CONFIGS['festival']['display_name']}
            </a>
        </div>
        <div class="site-info">
            Currently viewing: {site_config['display_name']}
        </div>
    </div>
    
    <div class="header">
        <h1>{site_config['display_name']} - Layout {cluster_id}</h1>
        <p>Detailed view of {len(screenshots)} screenshots in this layout cluster</p>
    </div>
    
    <div class="container">
        <div class="back-link">
            <a href="{'index.html' if site == 'folklife' else f'index_{site}.html'}" class="back-btn">← Back to All Layouts</a>
        </div>
        
        <div class="cluster-info">
            <div class="cluster-header">
                <div class="image-container">
                    <div class="loading-overlay skeleton" id="loading-{cluster_id}-canonical">
                        <span>Loading...</span>
                    </div>
                    <img src="{SPACES_CDN_BASE}/{canonical['filename']}" alt="Canonical" class="canonical-image clickable" 
                         onclick="openModal('{canonical['filename']}')"
                         onload="imageLoaded(this, 'loading-{cluster_id}-canonical')"
                         onerror="imageError(this, 'loading-{cluster_id}-canonical')">
                </div>
                <div class="cluster-details">
                    <h2>Layout {cluster_id}</h2>
                    <p><strong>Canonical Image:</strong> {canonical['filename']}</p>
                    <p style="font-size: 0.9rem; color: #666; margin: 0.5rem 0;">
                        💡 <strong>Canonical:</strong> The most representative image for this layout. 
                        Other images are sorted by how similar they are to this one.
                    </p>
                    <div class="cluster-stats">
                        <div class="stat-item">
                            <div class="stat-number">{len(screenshots)}</div>
                            <div class="stat-label">Total Screenshots</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{len(screenshots):.1f}</div>
                            <div class="stat-label">Avg per Layout</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- User Feedback Section -->
            <div class="feedback-section">
                <div class="feedback-title">🤔 Found a misclassified image?</div>
                <p style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                    Help improve our layout detection by flagging images that don't belong here or suggesting new layouts.
                </p>
                <div class="feedback-buttons">
                    <button class="feedback-btn flag" onclick="showFeedbackForm('flag', '{cluster_id}')">
                        🚩 Flag for Review
                    </button>
                    <button class="feedback-btn correct" onclick="showFeedbackForm('correct', '{cluster_id}')">
                        ✏️ Suggest New Layout
                    </button>
                </div>
                
                <div id="feedback-form-{cluster_id}" class="feedback-form">
                    <textarea id="feedback-text-{cluster_id}" placeholder="Please describe why this image should be reviewed or what new layout it represents..."></textarea>
                    <button onclick="submitFeedback('{cluster_id}', '{site}')">Submit Feedback</button>
                </div>
            </div>
        </div>
        
        <div class="images-grid">"""
    
    for screenshot in sorted_screenshots:
        similarity = 100 - (screenshot['distance'] * 100)
        needs_review = similarity < 80
        
        html += f"""
            <div class="image-card">
                <div class="image-container">
                    <div class="loading-overlay skeleton" id="loading-{cluster_id}-{screenshot['filename'].replace('.', '_')}">
                        <span>Loading...</span>
                    </div>
                    <img src="{SPACES_CDN_BASE}/{screenshot['filename']}" alt="{screenshot['filename']}" 
                         onclick="openModal('{screenshot['filename']}')"
                         onload="imageLoaded(this, 'loading-{cluster_id}-{screenshot['filename'].replace('.', '_')}')"
                         onerror="imageError(this, 'loading-{cluster_id}-{screenshot['filename'].replace('.', '_')}')">
                </div>
                <div class="image-info">
                    <div class="image-name">
                        {screenshot['filename']}"""
        
        if screenshot['canonical']:
            html += f"""
                        <span class="canonical-badge">Canonical</span>"""
        
        html += f"""
                    </div>
                    <div class="image-distance">
                        Similarity: {similarity:.1f}%
                    </div>"""
        
        if needs_review:
            html += f"""
                    <div class="similarity-warning">
                        ⚠️ <strong>Review Recommended:</strong> This image has low similarity and may need human review.
                    </div>"""
        
        html += f"""
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
            modalImg.src = 'https://quotient.nyc3.cdn.digitaloceanspaces.com/' + filename;
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
        
        // Image loading functions
        function imageLoaded(img, loadingId) {
            // Hide loading overlay and show image
            const loadingOverlay = document.getElementById(loadingId);
            if (loadingOverlay) {
                loadingOverlay.classList.remove('skeleton');
                loadingOverlay.classList.add('loaded');
            }
            img.classList.remove('loading');
            img.classList.add('loaded');
        }
        
        function imageError(img, loadingId) {
            // Show error state with red background and "Failed" text
            const loadingOverlay = document.getElementById(loadingId);
            if (loadingOverlay) {
                loadingOverlay.classList.remove('skeleton');
                loadingOverlay.classList.add('failed');
                loadingOverlay.innerHTML = '<span>Failed</span>';
            }
            img.style.display = 'none';
        }
        
        // Feedback system functions
        function showFeedbackForm(type, clusterId) {
            const form = document.getElementById(`feedback-form-${clusterId}`);
            const textarea = document.getElementById(`feedback-text-${clusterId}`);
            
            // Clear previous content
            textarea.value = '';
            
            // Show form
            form.classList.add('show');
            
            // Focus on textarea
            textarea.focus();
        }
        
        function submitFeedback(clusterId, site) {
            const textarea = document.getElementById(`feedback-text-${clusterId}`);
            const feedback = textarea.value.trim();
            
            if (!feedback) {
                alert('Please provide feedback before submitting.');
                return;
            }
            
            // Here you would typically send this to your backend
            // For now, we'll just show a success message
            alert('Thank you for your feedback! This will be reviewed by our team.');
            
            // Hide the form
            document.getElementById(`feedback-form-${clusterId}`).classList.remove('show');
            
            // In a real implementation, you would:
            // 1. Send feedback to your backend API
            // 2. Store it in a database
            // 3. Create a review queue for human moderators
            // 4. Potentially create new layout buckets
            console.log('Feedback submitted:', {
                clusterId: clusterId,
                site: site,
                feedback: feedback,
                timestamp: new Date().toISOString()
            });
        }
    </script>
</body>
</html>"""
    
    return html

def main():
    """Generate the multi-site static site"""
    print("🚀 Generating Multi-Site Static Site...")
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Generate site for each site
    for site in SITE_CONFIGS:
        print(f"\n📁 Generating {site} site...")
        
        # Load cluster data
        clusters = load_cluster_data(site)
        if not clusters:
            print(f"⚠️  Skipping {site} - no data found")
            continue
        
        # Generate summary
        summary = get_cluster_summary(clusters, site)
        
        # Generate main page
        print(f"  📄 Generating main page...")
        main_html = generate_main_page(summary, SITE_CONFIGS)
        
        # Save main page with site-specific name
        if site == 'folklife':
            main_filename = "index.html"
        else:
            main_filename = f"index_{site}.html"
        
        with open(OUTPUT_DIR / main_filename, "w") as f:
            f.write(main_html)
        
        # Generate cluster detail pages
        print(f"  🖼️  Generating {len(clusters)} cluster detail pages...")
        sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
        
        for cluster_id, screenshots in sorted_clusters:
            detail_html = generate_cluster_detail_page(cluster_id, screenshots, site, SITE_CONFIGS[site])
            detail_filename = f"layout_{site}_{cluster_id}.html"
            
            with open(OUTPUT_DIR / detail_filename, "w") as f:
                f.write(detail_html)
    
    print(f"\n✅ Multi-site static site generated successfully in {OUTPUT_DIR}/")
    print(f"📁 Main pages: index.html (folklife), index_festival.html")
    print(f"🖼️  Images: Served from DigitalOcean Spaces CDN")
    print(f"📄 Cluster pages: Generated for both sites")
    print("\n🚀 Deploy to GitHub Pages or DigitalOcean Spaces for hosting!")
    print(f"🌐 Folklife: index.html")
    print(f"🎪 Festival: index_festival.html")

if __name__ == '__main__':
    main()
