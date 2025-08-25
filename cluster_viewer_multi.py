#!/usr/bin/env python3
"""
Multi-Site Layout Cluster Viewer - Web UI for viewing screenshot clusters from multiple sites
Supports both folklife.si.edu and festival.si.edu
"""

from flask import Flask, render_template, jsonify, send_from_directory, request
import os
import json
import csv
from pathlib import Path
from collections import defaultdict
import base64
from PIL import Image
import io

app = Flask(__name__)

# Configuration for both sites
SITE_CONFIGS = {
    'folklife': {
        'name': 'folklife.si.edu',
        'display_name': 'Folklife Festival',
        'clusters_dir': Path("layout_clusters"),
        'csv_file': Path("layout_clusters_final.csv"),
        'images_dir': Path("folklife-screens-x"),
        'color': '#2c3e50'  # Dark blue
    },
    'festival': {
        'name': 'festival.si.edu', 
        'display_name': 'Smithsonian Festival',
        'clusters_dir': Path("festival_layout_clusters"),
        'csv_file': Path("festival_layout_clusters_strict.csv"),
        'images_dir': Path("festival-screens-x"),
        'color': '#8e44ad'  # Purple
    }
}

THUMBNAIL_SIZE = (300, 225)
MAX_IMAGES_PER_CLUSTER = 20

def get_current_site():
    """Get the currently selected site from query params or session"""
    site = request.args.get('site', 'folklife')
    if site not in SITE_CONFIGS:
        site = 'folklife'
    return site

def get_site_config(site=None):
    """Get configuration for a specific site"""
    if site is None:
        site = get_current_site()
    return SITE_CONFIGS[site]

def load_cluster_data(site):
    """Load cluster data from CSV for a specific site"""
    config = get_site_config(site)
    clusters = defaultdict(list)
    
    if not config['csv_file'].exists():
        return {}
    
    with open(config['csv_file'], 'r') as f:
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

def get_cluster_summary(site):
    """Get summary statistics for all clusters in a site"""
    clusters = load_cluster_data(site)
    
    # Convert site_config to JSON-serializable format
    site_config = get_site_config(site)
    json_safe_config = {
        'name': str(site_config['name']),
        'display_name': site_config['display_name'],
        'clusters_dir': str(site_config['clusters_dir']),
        'csv_file': str(site_config['csv_file']),
        'images_dir': str(site_config['images_dir']),
        'color': site_config['color']
    }
    
    summary = {
        'total_clusters': len(clusters),
        'total_screenshots': sum(len(cluster) for cluster in clusters.values()),
        'clusters': [],
        'site': site,
        'site_config': json_safe_config
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
            'screenshots': screenshots[:MAX_IMAGES_PER_CLUSTER],
            'has_more': len(screenshots) > MAX_IMAGES_PER_CLUSTER
        }
        
        summary['clusters'].append(cluster_info)
    
    return summary

@app.route('/')
def index():
    """Main page showing clusters for current site"""
    site = get_current_site()
    summary = get_cluster_summary(site)
    return render_template('index_multi.html', summary=summary, sites=SITE_CONFIGS)

@app.route('/api/clusters')
def api_clusters():
    """API endpoint for cluster data"""
    site = get_current_site()
    summary = get_cluster_summary(site)
    return jsonify(summary)

@app.route('/cluster/<cluster_id>')
def cluster_detail(cluster_id):
    """Detailed view of a specific cluster"""
    site = get_current_site()
    clusters = load_cluster_data(site)
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
    
    site_config = get_site_config(site)
    return render_template('cluster_detail_multi.html', 
                         cluster_id=cluster_id, 
                         cluster_data=cluster_data,
                         canonical=canonical,
                         site=site,
                         site_config=site_config,
                         sites=SITE_CONFIGS)

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve image files from the organized cluster directories"""
    site = get_current_site()
    config = get_site_config(site)
    
    # First try to find the image in the organized cluster directories
    clusters_dir = config['clusters_dir']
    if os.path.exists(clusters_dir):
        # Search through all cluster directories for the image
        for cluster_dir in os.listdir(clusters_dir):
            if cluster_dir.startswith('cluster_'):
                cluster_path = os.path.join(clusters_dir, cluster_dir)
                if os.path.isdir(cluster_path):
                    image_path = os.path.join(cluster_path, filename)
                    if os.path.exists(image_path):
                        try:
                            return send_from_directory(cluster_path, filename)
                        except Exception as e:
                            print(f"Error serving {filename} from {cluster_path}: {e}")
                            continue
    
    # Fallback to the original images directory if not found in clusters
    image_dirs = [
        str(config['images_dir']),
        f"./{config['images_dir']}",
        f"../{config['images_dir']}",
        f"/app/{config['images_dir']}"  # Docker path
    ]
    
    for img_dir in image_dirs:
        if os.path.exists(img_dir):
            try:
                return send_from_directory(img_dir, filename)
            except Exception as e:
                print(f"Error serving {filename} from {img_dir}: {e}")
                continue
    
    # If no directory found, return 404
    return f"Image not found in clusters or images directory for {site}. Filename: {filename}", 404

@app.route('/debug')
def debug_info():
    """Debug information for troubleshooting"""
    site = get_current_site()
    config = get_site_config(site)
    
    info = {
        'current_site': site,
        'working_directory': os.getcwd(),
        'available_directories': [d for d in os.listdir('.') if os.path.isdir(d)],
        'site_config': {
            'clusters_dir_exists': os.path.exists(config['clusters_dir']),
            'clusters_dir_path': os.path.abspath(config['clusters_dir']) if os.path.exists(config['clusters_dir']) else None,
            'csv_file_exists': os.path.exists(config['csv_file']),
            'csv_file_path': os.path.abspath(config['csv_file']) if os.path.exists(config['csv_file']) else None,
            'images_dir_exists': os.path.exists(config['images_dir']),
            'images_dir_path': os.path.abspath(config['images_dir']) if os.path.exists(config['images_dir']) else None,
        }
    }
    
    if os.path.exists(config['images_dir']):
        try:
            info['site_config']['images_dir_contents'] = os.listdir(config['images_dir'])[:10]
        except Exception as e:
            info['site_config']['images_dir_error'] = str(e)
    
    return jsonify(info)

@app.route('/api/cluster/<cluster_id>/thumbnails')
def cluster_thumbnails(cluster_id):
    """Get thumbnails for a specific cluster"""
    site = get_current_site()
    clusters = load_cluster_data(site)
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
    
    return jsonify({'thumbnails': thumbnails})

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Multi-Site Layout Cluster Viewer')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    print("Starting Multi-Site Layout Cluster Viewer...")
    print("Available sites:")
    for site_id, config in SITE_CONFIGS.items():
        print(f"  {site_id}: {config['display_name']} ({config['name']})")
        print(f"    Clusters: {config['clusters_dir']}")
        print(f"    CSV: {config['csv_file']}")
        print(f"    Images: {config['images_dir']}")
        print()
    
    print(f"Open http://{args.host}:{args.port} in your browser")
    print("Use ?site=folklife or ?site=festival to switch between sites")

    # Run the Flask app
    app.run(debug=args.debug, host=args.host, port=args.port)
