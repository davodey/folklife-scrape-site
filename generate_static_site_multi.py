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

def load_url_mapping(site):
    """Load URL mapping for a specific site"""
    site_config = SITE_CONFIGS[site]
    url_mapping_file = site_config['images_dir'] / 'url_mapping.json'
    
    if not url_mapping_file.exists():
        print(f"Warning: {url_mapping_file} not found for {site}")
        return {}
    
    try:
        with open(url_mapping_file, 'r') as f:
            url_mapping = json.load(f)
        # Reverse the mapping to go from filename to URL
        filename_to_url = {v: k for k, v in url_mapping.items()}
        return filename_to_url
    except Exception as e:
        print(f"Error loading URL mapping for {site}: {e}")
        return {}

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

def calculate_cluster_importance(cluster_size, avg_distance, site_type, canonical_filename, cluster_id):
    """Calculate importance score for a cluster based on multiple factors"""
    
    # Base importance from cluster size (but cap it to avoid overvaluing large clusters)
    size_score = min(cluster_size / 15.0, 1.0)  # Normalize to 0-1, cap at 15+ screenshots
    
    # Distance score (closer to canonical = more important)
    distance_score = 1.0 - min(avg_distance, 1.0)
    
    # Layout type importance - identify truly important layouts
    layout_importance = 0.0
    layout_reason = ""
    is_critical_page = False
    
    # Check for homepage and main navigation layouts (ALWAYS high priority)
    if any(keyword in canonical_filename.lower() for keyword in ['homepage', 'index', 'main', 'navigation']):
        layout_importance = 1.0
        layout_reason = "Critical page type (homepage/navigation)"
        is_critical_page = True
    # Check for top-level navigation categories (ALWAYS high priority)
    elif any(keyword in canonical_filename.lower() for keyword in ['magazine', 'research', 'cultural', 'education', 'archives', 'about']):
        layout_importance = 1.0
        layout_reason = "Critical page type (top-level navigation)"
        is_critical_page = True
    # Check for Festival-specific navigation categories (ALWAYS high priority)
    elif any(keyword in canonical_filename.lower() for keyword in ['festival', 'visit', 'learn', 'schedule', 'sponsors']):
        layout_importance = 1.0
        layout_reason = "Critical page type (top-level navigation)"
        is_critical_page = True
    # Check for program/schedule layouts
    elif any(keyword in canonical_filename.lower() for keyword in ['schedule', 'program', 'events', 'festival']):
        layout_importance = 0.9
        layout_reason = "Important page type (program/schedule)"
    # Check for visitor information
    elif any(keyword in canonical_filename.lower() for keyword in ['visit', 'visitor', 'information', 'directions']):
        layout_importance = 0.8
        layout_reason = "Important page type (visitor info)"
    # Check for about pages
    elif any(keyword in canonical_filename.lower() for keyword in ['about', 'mission', 'history']):
        layout_importance = 0.7
        layout_reason = "Important page type (about/mission)"
    # Check for blog/content pages
    elif any(keyword in canonical_filename.lower() for keyword in ['blog', 'news', 'article', 'story']):
        layout_importance = 0.6
        layout_reason = "Content page type (blog/article)"
    # Check for archive/historical pages
    elif any(keyword in canonical_filename.lower() for keyword in ['archive', 'past', 'history', 'legacy']):
        layout_importance = 0.5
        layout_reason = "Archive page type (historical)"
    # Check for utility pages
    elif any(keyword in canonical_filename.lower() for keyword in ['search', 'contact', 'legal', 'privacy']):
        layout_importance = 0.4
        layout_reason = "Utility page type (search/contact)"
    # Default for other pages
    else:
        layout_importance = 0.3
        layout_reason = "Standard page type"
    
    # Site-specific importance (festival might be more important than folklife)
    site_multiplier = 1.1 if site_type == 'festival' else 1.0
    
    # For critical pages (homepage, navigation), force high priority
    if is_critical_page:
        importance = 0.85  # Force high priority
    else:
        # Combined importance score (0-1)
        # Weight: Layout type (50%), Size (25%), Consistency (15%), Site (10%)
        importance = (
            layout_importance * 0.5 + 
            size_score * 0.25 + 
            distance_score * 0.15
        ) * site_multiplier
    
    # Ensure importance is within bounds
    importance = max(0.0, min(1.0, importance))
    
    # Convert to importance level
    if importance >= 0.7:
        level = 'high'
    elif importance >= 0.4:
        level = 'medium'
    else:
        level = 'low'
    
    # Create explanation for the importance level
    if level == 'high':
        if is_critical_page:
            explanation = f"High priority: {layout_reason}"
        elif layout_importance >= 0.9:
            explanation = f"High priority: {layout_reason}"
        elif size_score >= 0.8:
            explanation = f"High priority: Frequently used layout ({cluster_size} similar pages)"
        else:
            explanation = f"High priority: {layout_reason} + good consistency"
    elif level == 'medium':
        if layout_importance >= 0.7:
            explanation = f"Medium priority: {layout_reason}"
        elif size_score >= 0.6:
            explanation = f"Medium priority: Moderately used layout ({cluster_size} similar pages)"
        else:
            explanation = f"Medium priority: {layout_reason}"
    else:
        if cluster_size == 1:
            explanation = f"Low priority: Unique layout (single page)"
        else:
            explanation = f"Low priority: {layout_reason} + limited usage"
    
    return level, importance, explanation

def generate_main_page(summary, site_configs):
    """Generate the main index page with site switching and importance filtering"""
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
        
        /* Importance Filter Bar */
        .importance-filter {{ 
            background: white; 
            padding: 1.5rem; 
            border-radius: 8px; 
            margin-bottom: 2rem; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        .filter-label {{ 
            font-weight: 600; 
            color: #495057; 
            margin-right: 0.5rem;
        }}
        .filter-buttons {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
        .filter-btn {{ 
            padding: 0.5rem 1rem; 
            border: 2px solid #dee2e6; 
            border-radius: 6px; 
            background: white; 
            color: #6c757d; 
            cursor: pointer; 
            font-weight: 500; 
            transition: all 0.2s;
            font-size: 0.9rem;
        }}
        .filter-btn:hover {{ 
            border-color: {summary['site_config']['color']}; 
            color: {summary['site_config']['color']};
        }}
        .filter-btn.active {{ 
            background: {summary['site_config']['color']}; 
            color: white; 
            border-color: {summary['site_config']['color']};
        }}
        .filter-btn.count {{ 
            background: #f8f9fa; 
            border-color: #ced4da;
            color: #495057;
        }}
        
        .stats {{ background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }}
        .stat-item {{ text-align: center; }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: {summary['site_config']['color']}; }}
        .stat-label {{ color: #7f8c8d; margin-top: 0.5rem; }}
        
        .clusters-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); 
            gap: 3rem; 
            padding: 1rem 0;
        }}
        .cluster-card {{ 
            background: white; 
            border-radius: 20px; 
            overflow: hidden; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.08); 
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            position: relative;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}
        .cluster-card:hover {{ 
            transform: translateY(-8px) scale(1.02); 
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            border-color: rgba(0,0,0,0.1);
        }}
        
        /* Importance Label */
        .importance-label {{ 
            position: absolute; 
            top: 1rem; 
            right: 1rem; 
            padding: 0.25rem 0.75rem; 
            border-radius: 20px; 
            font-size: 0.75rem; 
            font-weight: 700; 
            text-transform: uppercase; 
            letter-spacing: 0.5px;
            z-index: 10;
        }}
        .importance-label.high {{ 
            background: #dc3545; 
            color: white; 
            box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
        }}
        .importance-label.medium {{ 
            background: #fd7e14; 
            color: white; 
            box-shadow: 0 2px 8px rgba(253, 126, 20, 0.3);
        }}
        .importance-label.low {{ 
            background: #6c757d; 
            color: white; 
            box-shadow: 0 2px 8px rgba(108, 117, 125, 0.3);
        }}
        
        .cluster-header-top {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 1rem 1.5rem 0.75rem 1.5rem;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            position: relative;
        }}
        .cluster-header-top::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, {summary['site_config']['color']}, {summary['site_config']['color']}dd);
        }}
        .cluster-explanation {{
            font-size: 0.95rem;
            font-weight: 500;
            color: #6c757d;
            margin-top: 0.25rem;
            line-height: 1.4;
        }}
        
        .cluster-main-content {{
            display: flex;
            flex-direction: column;
            flex: 1;
        }}
        
        .cluster-image-section {{
            padding: 1rem 1.5rem;
            background: #fafbfc;
        }}
        
        .cluster-info-section {{
            padding: 1rem 1.5rem 1.5rem 1.5rem;
            background: white;
            display: flex;
            flex-direction: column;
            flex: 1;
        }}
        
        .cluster-header {{ 
            margin-bottom: 1rem;
        }}
        .cluster-title {{ 
            font-size: 1.4rem; 
            font-weight: 700; 
            color: #1a1a1a; 
            margin-bottom: 0.5rem; 
            letter-spacing: -0.02em;
            line-height: 1.3;
        }}
        .cluster-size {{ 
            color: #6c757d; 
            font-size: 0.9rem; 
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .canonical-image {{ 
            width: 100%; 
            height: 220px; 
            object-fit: cover; 
            transition: transform 0.3s ease;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }}
        .cluster-card:hover .canonical-image {{
            transform: scale(1.02);
        }}
        .cluster-preview {{ 
            margin-bottom: 1.25rem;
            padding-top: 0.75rem;
            border-top: 1px solid #f1f3f4;
        }}
        .preview-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); 
            gap: 0.75rem; 
            max-width: 100%;
            margin-top: 0.75rem;
        }}
        .preview-thumb {{ 
            width: 100%; 
            height: 60px; 
            object-fit: cover; 
            border-radius: 8px; 
            transition: transform 0.2s ease;
            cursor: pointer;
            border: 2px solid transparent;
        }}
        .preview-thumb:hover {{
            transform: scale(1.05);
            border-color: {summary['site_config']['color']};
        }}
        .cluster-actions {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid #f1f3f4;
        }}
        .view-btn {{ 
            background: {summary['site_config']['color']}; 
            color: white; 
            padding: 0.875rem 1.5rem; 
            border-radius: 8px; 
            text-decoration: none; 
            font-weight: 600; 
            text-align: center; 
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        .view-btn:hover {{ 
            transform: translateY(-2px); 
            box-shadow: 0 4px 16px rgba(0,0,0,0.25);
        }}
        .canonical-page-link {{ 
            background: #f8f9fa; 
            color: #495057; 
            padding: 0.75rem 1.25rem; 
            border-radius: 8px; 
            text-decoration: none; 
            font-weight: 500; 
            text-align: center; 
            transition: all 0.2s ease;
            border: 1px solid #e9ecef;
        }}
        .canonical-page-link:hover {{ 
            background: #e9ecef; 
            border-color: #dee2e6;
        }}
        
        .cluster-header {{ 
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
            padding: 2rem; 
            border-bottom: 1px solid rgba(0,0,0,0.05);
            position: relative;
        }}
        .cluster-header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, {summary['site_config']['color']}, {summary['site_config']['color']}dd);
        }}
        .cluster-title {{ 
            font-size: 1.5rem; 
            font-weight: 700; 
            color: #1a1a1a; 
            margin-bottom: 0.75rem; 
            letter-spacing: -0.02em;
        }}
        .cluster-size {{ 
            color: #6c757d; 
            font-size: 1rem; 
            font-weight: 500; 
            opacity: 0.8;
        }}
        .canonical-image {{ 
            width: 100%; 
            height: 220px; 
            object-fit: cover; 
            transition: transform 0.3s ease;
        }}
        .cluster-card:hover .canonical-image {{
            transform: scale(1.05);
        }}
        .cluster-preview {{ 
            padding: 2.5rem; 
            background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
        }}
        .preview-grid {{ 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 1rem; 
            margin: 2rem 0; 
            padding: 1.5rem;
            background: rgba(255,255,255,0.7);
            border-radius: 16px;
            border: 1px solid rgba(0,0,0,0.05);
        }}
        .preview-thumb {{ 
            width: 100%; 
            height: 60px; 
            object-fit: cover; 
            border-radius: 12px;
            border: 2px solid rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .preview-thumb:hover {{
            transform: scale(1.1);
            border-color: {summary['site_config']['color']};
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}
        .view-all {{ 
            text-align: center; 
            margin-top: 2rem; 
            display: flex;
            flex-direction: column;
            gap: 1rem;
            align-items: center;
        }}
        .view-btn {{ 
            background: linear-gradient(135deg, {summary['site_config']['color']}, {summary['site_config']['color']}dd); 
            color: white; 
            padding: 1rem 2.5rem; 
            text-decoration: none; 
            border-radius: 16px; 
            display: inline-block; 
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            font-weight: 600;
            font-size: 1rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            border: none;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }}
        .view-btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }}
        .view-btn:hover::before {{
            left: 100%;
        }}
        .view-btn:hover {{ 
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.25);
            background: linear-gradient(135deg, {summary['site_config']['color']}dd, {summary['site_config']['color']});
        }}
        .view-btn:active {{ 
            transform: translateY(0);
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }}
        .loading {{ text-align: center; padding: 2rem; color: #7f8c8d; }}
        
        /* Hidden cards for filtering */
        .cluster-card.hidden {{ display: none; }}
        
        /* Skeleton Loading */
        .skeleton {{
            animation: skeleton-loading 1.5s ease-in-out infinite;
        }}
        
        @keyframes skeleton-loading {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}
        
        .skeleton .canonical-image {{
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: skeleton-shimmer 1.5s infinite;
        }}
        
        @keyframes skeleton-shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {{
            .importance-filter {{ flex-direction: column; align-items: stretch; }}
            .filter-buttons {{ justify-content: center; }}
            .clusters-grid {{ grid-template-columns: 1fr; }}
        }}
        
        /* Modal styles */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }}
        .modal-content {{
            margin: auto;
            display: block;
            width: 90%;
            max-width: 1200px;
            max-height: 90vh;
            object-fit: contain;
        }}
        .modal-close {{
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
        .modal-close:hover {{
            color: #bbb;
        }}
        
        /* Clickable elements */
        .clickable {{
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .clickable:hover {{
            opacity: 0.9;
        }}
        
        /* Canonical page link styles */
        .canonical-page-link {{
            display: inline-block;
            padding: 0.875rem 2rem;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            color: #495057;
            text-decoration: none;
            border-radius: 16px;
            font-size: 0.95rem;
            border: 2px solid rgba(0,0,0,0.05);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            font-weight: 600;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            position: relative;
            overflow: hidden;
        }}
        .canonical-page-link::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0,0,0,0.05), transparent);
            transition: left 0.5s;
        }}
        .canonical-page-link:hover::before {{
            left: 100%;
        }}
        .canonical-page-link:hover {{
            background: linear-gradient(135deg, #e9ecef, #dee2e6);
            color: #212529;
            border-color: rgba(0,0,0,0.1);
            text-decoration: none;
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }}
        
        /* Enhanced container spacing */
        .container {{
            max-width: 1600px; 
            margin: 0 auto; 
            padding: 3rem 2rem; 
        }}
        
        /* Enhanced stats styling */
        .stats {{
            background: linear-gradient(135deg, #ffffff, #f8f9fa); 
            padding: 3rem; 
            border-radius: 24px; 
            margin-bottom: 3rem; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
        }}
        .stats-grid {{
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 2rem; 
        }}
        .stat-item {{
            text-align: center; 
            padding: 1.5rem;
            background: rgba(255,255,255,0.7);
            border-radius: 16px;
            border: 1px solid rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }}
        .stat-item:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2.5rem; 
            font-weight: 800; 
            color: {summary['site_config']['color']}; 
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }}
        .stat-label {{
            color: #6c757d; 
            margin-top: 0.5rem; 
            font-weight: 600;
            font-size: 1rem;
        }}
        
        /* Modal/Lightbox styles */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }}
        .modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 90%; margin-top: 2%; }}
        .modal-close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }}
        .modal-close:hover {{ color: #bbb; }}
        .clickable {{ cursor: pointer; transition: opacity 0.2s; }}
        .clickable:hover {{ opacity: 0.8; }}
        
        /* URL link styles */
        .image-url-link {{
            display: inline-block;
            margin-top: 0.5rem;
            padding: 0.5rem 0.75rem;
            background: #f8f9fa;
            color: #495057;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.85rem;
            border: 1px solid #e9ecef;
            transition: all 0.2s ease;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .image-url-link:hover {{
            background: #e9ecef;
            color: #212529;
            border-color: #dee2e6;
            text-decoration: none;
        }}
        .url-icon {{
            margin-right: 0.5rem;
            opacity: 0.7;
        }}
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
            <strong>Importance levels</strong> are calculated based on cluster size and layout consistency.
        </p>
    </div>
    
    <div class="container">
        <!-- Importance Filter Bar -->
        <div class="importance-filter">
            <div class="filter-label">Filter by Importance:</div>
            <div class="filter-buttons">
                <button class="filter-btn active" data-filter="all" onclick="filterByImportance('all')">
                    All Layouts
                </button>
                <button class="filter-btn" data-filter="high" onclick="filterByImportance('high')">
                    🔴 High Priority
                </button>
                <button class="filter-btn" data-filter="medium" onclick="filterByImportance('medium')">
                    🟠 Medium Priority
                </button>
                <button class="filter-btn" data-filter="low" onclick="filterByImportance('low')">
                    ⚫ Low Priority
                </button>
            </div>
            <div class="filter-btn count" id="filterCount">
                Showing all {summary['total_clusters']} layouts
            </div>
        </div>
        
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
        
        <!-- Importance Calculation Info -->
        <div class="stats" style="margin-bottom: 1rem;">
            <h3 style="margin-bottom: 1rem; color: #495057;">How Importance is Calculated</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; font-size: 0.9rem;">
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; border-left: 4px solid #dc3545;">
                    <strong>🔴 High Priority (≥0.7):</strong> Homepage, navigation, program schedules, visitor info
                </div>
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; border-left: 4px solid #fd7e14;">
                    <strong>🟠 Medium Priority (0.4-0.69):</strong> About pages, blog posts, content pages
                </div>
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; border-left: 4px solid #6c757d;">
                    <strong>⚫ Low Priority (<0.4):</strong> Archive pages, utility pages, less critical layouts
                </div>
            </div>
            <p style="margin-top: 1rem; font-size: 0.85rem; color: #6c757d;">
                <strong>Formula:</strong> Layout Type (50%) + Cluster Size (25%) + Consistency (15%) + Site Priority (10%)
            </p>
        </div>
        
        <div class="clusters-grid">"""
    
    # Load URL mapping for this site
    url_mapping = load_url_mapping(summary['site'])
    
    # Sort clusters by size (largest first) and calculate importance
    sorted_clusters = []
    for cluster_id, screenshots in summary['clusters'].items():
        # Calculate average distance for importance scoring
        avg_distance = sum(s['distance'] for s in screenshots) / len(screenshots)
        
        # Find canonical image for importance calculation
        canonical = next((s for s in screenshots if s['canonical']), screenshots[0])
        
        importance_level, importance_score, explanation = calculate_cluster_importance(
            len(screenshots), avg_distance, summary['site'], canonical['filename'], cluster_id
        )
        
        sorted_clusters.append({
            'cluster_id': cluster_id,
            'screenshots': screenshots,
            'importance_level': importance_level,
            'importance_score': importance_score,
            'explanation': explanation
        })
    
    # Sort by importance score first, then by size
    sorted_clusters.sort(key=lambda x: (x['importance_score'], len(x['screenshots'])), reverse=True)
    
    # Generate cluster cards
    for cluster_data in sorted_clusters:
        cluster_id = cluster_data['cluster_id']
        screenshots = cluster_data['screenshots']
        importance_level = cluster_data['importance_level']
        importance_score = cluster_data['importance_score']
        explanation = cluster_data['explanation']
        
        # Get canonical image (first image with canonical=True)
        canonical = next((s for s in screenshots if s['canonical']), screenshots[0])
        
        # Get preview images (up to MAX_IMAGES_PER_CLUSTER)
        preview_images = screenshots[:MAX_IMAGES_PER_CLUSTER]
        
        # Get canonical URL if available
        canonical_url = url_mapping.get(canonical['filename'], '')
        
        html += f"""
            <div class="cluster-card skeleton" data-importance="{importance_level}">
                <div class="cluster-header-top">
                    <div class="importance-label {importance_level}">{importance_level.upper()}</div>
                    <div class="cluster-explanation">
                        {explanation}
                    </div>
                </div>
                
                <div class="cluster-main-content">
                    <div class="cluster-image-section">
                        <img src="{SPACES_CDN_BASE}/{summary['site']}/{canonical['filename']}" 
                             alt="Canonical" 
                             class="canonical-image clickable" 
                             onclick="openModal('{canonical['filename']}', '{summary['site']}')">
                    </div>
                    
                    <div class="cluster-info-section">
                        <div class="cluster-header">
                            <div class="cluster-title">Layout {cluster_id}: {canonical['filename'].replace('.png', '').replace('_', ' ').title()}</div>
                            <div class="cluster-size">{len(screenshots)} screenshots</div>
                        </div>
                        
                        <div class="cluster-preview">
                            <div class="preview-grid">"""
        
        for screenshot in preview_images:
            html += f"""
                                <img src="{SPACES_CDN_BASE}/{summary['site']}/{screenshot['filename']}" 
                                     alt="{screenshot['filename']}" 
                                     class="preview-thumb clickable" 
                                     title="{screenshot['filename']}" 
                                     onclick="openModal('{screenshot['filename']}', '{summary['site']}')">"""
        
        html += f"""
                            </div>
                        </div>
                        
                        <div class="cluster-actions">
                            <a href="layout_{summary['site']}_{cluster_id}.html" class="view-btn">View All {len(screenshots)} Images</a>"""
        
        # Add canonical page link if available
        if canonical_url:
            html += f"""
                            <a href="{canonical_url}" target="_blank" class="canonical-page-link">🔗 View Source Page</a>"""
        
        html += f"""
                        </div>
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
        function openModal(filename, site) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const caption = document.getElementById('modalCaption');
            
            modal.style.display = 'block';
            modalImg.src = 'https://quotient.nyc3.cdn.digitaloceanspaces.com/' + site + '/' + filename;
            caption.innerHTML = filename;
        }
        
        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }
        
        function filterByImportance(importance) {
            const cards = document.querySelectorAll('.cluster-card');
            const filterBtns = document.querySelectorAll('.filter-btn');
            let visibleCount = 0;
            let totalScreenshots = 0;
            
            // Update active filter button
            filterBtns.forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.filter === importance) {
                    btn.classList.add('active');
                }
            });
            
            // Filter cards and count screenshots
            cards.forEach(card => {
                if (importance === 'all' || card.dataset.importance === importance) {
                    card.classList.remove('hidden');
                    visibleCount++;
                    
                    // Extract screenshot count from the cluster-size text
                    const sizeText = card.querySelector('.cluster-size').textContent;
                    const screenshotMatch = sizeText.match(/(\\d+)\\s+screenshots/);
                    if (screenshotMatch) {
                        totalScreenshots += parseInt(screenshotMatch[1]);
                    }
                } else {
                    card.classList.add('hidden');
                }
            });
            
            // Update count display
            const countElement = document.getElementById('filterCount');
            if (importance === 'all') {
                countElement.textContent = `Showing all ${cards.length} layouts`;
            } else {
                countElement.textContent = `Showing ${visibleCount} ${importance} priority layouts`;
            }
            
            // Update stats widget
            updateStatsWidget(visibleCount, totalScreenshots);
        }
        
        function updateStatsWidget(visibleLayouts, visibleScreenshots) {
            // Update Unique Layouts count
            const uniqueLayoutsElement = document.querySelector('.stat-number');
            if (uniqueLayoutsElement) {
                uniqueLayoutsElement.textContent = visibleLayouts;
            }
            
            // Update Total Screenshots count
            const totalScreenshotsElements = document.querySelectorAll('.stat-number');
            if (totalScreenshotsElements.length > 1) {
                totalScreenshotsElements[1].textContent = visibleScreenshots;
            }
            
            // Update Average per Cluster
            const avgPerClusterElements = document.querySelectorAll('.stat-number');
            if (avgPerClusterElements.length > 2) {
                const avgPerCluster = visibleLayouts > 0 ? (visibleScreenshots / visibleLayouts).toFixed(1) : '0.0';
                avgPerClusterElements[2].textContent = avgPerCluster;
            }
            
            // Update header description
            const headerDescription = document.querySelector('.header p');
            if (headerDescription) {
                const totalLayouts = document.querySelectorAll('.cluster-card').length;
                const totalScreenshots = Array.from(document.querySelectorAll('.cluster-size')).reduce((sum, el) => {
                    const match = el.textContent.match(/(\d+)\s+screenshots/);
                    return sum + (match ? parseInt(match[1]) : 0);
                }, 0);
                
                if (visibleLayouts === totalLayouts) {
                    headerDescription.textContent = `Visual overview of ${totalLayouts} unique layouts from ${totalScreenshots} screenshots`;
                } else {
                    headerDescription.textContent = `Visual overview of ${visibleLayouts} visible layouts from ${visibleScreenshots} screenshots (filtered from ${totalLayouts} total layouts)`;
                }
            }
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
        
        // Remove skeleton loading when images load
        document.addEventListener('DOMContentLoaded', function() {
            const images = document.querySelectorAll('.canonical-image, .preview-thumb');
            images.forEach(img => {
                if (img.complete) {
                    img.closest('.cluster-card').classList.remove('skeleton');
                } else {
                    img.addEventListener('load', function() {
                        this.closest('.cluster-card').classList.remove('skeleton');
                    });
                }
            });
        });
    </script>
</body>
</html>"""
    
    return html

def generate_cluster_detail_page(cluster_id, screenshots, site, site_config):
    """Generate a detailed page for a specific cluster"""
    # Sort screenshots by distance (canonical first, then by similarity)
    sorted_screenshots = sorted(screenshots, key=lambda x: (not x['canonical'], x['distance']))
    canonical = next((s for s in screenshots if s['canonical']), screenshots[0])
    
    # Load URL mapping for this site
    url_mapping = load_url_mapping(site)
    
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
        
        .container {{ max-width: 1600px; margin: 0 auto; padding: 3rem 2rem; }}
        .back-link {{ margin-bottom: 3rem; }}
        .back-btn {{ 
            background: linear-gradient(135deg, {site_config['color']}, {site_config['color']}dd); 
            color: white; 
            padding: 1rem 2.5rem; 
            text-decoration: none; 
            border-radius: 16px; 
            display: inline-block;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            font-weight: 600;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            position: relative;
            overflow: hidden;
        }}
        .back-btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }}
        .back-btn:hover::before {{
            left: 100%;
        }}
        .back-btn:hover {{ 
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.25);
            background: linear-gradient(135deg, {site_config['color']}dd, {site_config['color']});
        }}
        
        .cluster-info {{ 
            background: linear-gradient(135deg, #ffffff, #f8f9fa); 
            padding: 3rem; 
            border-radius: 24px; 
            margin-bottom: 3rem; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
        }}
        .cluster-header {{ 
            display: flex; 
            align-items: flex-start; 
            gap: 3rem; 
            margin-bottom: 2.5rem; 
        }}
        .canonical-image {{ 
            width: 300px; 
            height: 220px; 
            object-fit: cover; 
            border-radius: 20px;
            border: 2px solid rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        }}
        .canonical-image:hover {{
            transform: scale(1.05);
            box-shadow: 0 12px 32px rgba(0,0,0,0.15);
        }}
        .cluster-details h2 {{ 
            color: #1a1a1a; 
            margin-bottom: 1.5rem; 
            font-size: 2.2rem; 
            font-weight: 800;
            letter-spacing: -0.02em;
        }}
        .cluster-stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
            gap: 1.5rem; 
            margin-top: 2rem; 
        }}
        .stat-item {{ 
            text-align: center; 
            padding: 1.5rem;
            background: rgba(255,255,255,0.8);
            border-radius: 16px;
            border: 1px solid rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }}
        .stat-item:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        }}
        .stat-number {{ 
            font-size: 2rem; 
            font-weight: 800; 
            color: {site_config['color']}; 
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }}
        .stat-label {{ 
            color: #6c757d; 
            font-size: 1rem; 
            font-weight: 600;
        }}
        
        .images-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); 
            gap: 2rem; 
        }}
        .image-card {{ 
            background: linear-gradient(135deg, #ffffff, #f8f9fa); 
            border-radius: 20px; 
            overflow: hidden; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.08); 
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            position: relative;
        }}
        .image-card:hover {{ 
            transform: translateY(-6px) scale(1.02); 
            box-shadow: 0 16px 48px rgba(0,0,0,0.15);
            border-color: rgba(0,0,0,0.1);
        }}
        .image-card img {{ 
            width: 100%; 
            height: 240px; 
            object-fit: cover; 
            cursor: pointer; 
            transition: all 0.3s ease; 
        }}
        .image-card:hover img {{ 
            transform: scale(1.05);
        }}
        .image-info {{ 
            padding: 2rem; 
            background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
        }}
        .image-name {{ 
            font-weight: 700; 
            color: #1a1a1a; 
            margin-bottom: 1rem; 
            word-break: break-word; 
            line-height: 1.5;
            font-size: 1.1rem;
        }}
        .canonical-badge {{ 
            background: linear-gradient(135deg, {site_config['color']}, {site_config['color']}dd); 
            color: white; 
            padding: 0.5rem 1rem; 
            border-radius: 12px; 
            font-size: 0.85rem; 
            margin-left: 0.75rem; 
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .image-distance {{ 
            color: #6c757d; 
            font-size: 1rem; 
            margin-bottom: 1rem; 
            font-weight: 500;
        }}
        
        /* URL link styles */
        .image-url-link {{
            display: inline-block;
            padding: 0.5rem 0.75rem;
            background: #f8f9fa;
            color: #495057;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.85rem;
            border: 1px solid #e9ecef;
            transition: all 0.2s ease;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            margin-top: 0.5rem;
        }}
        .image-url-link:hover {{
            background: #e9ecef;
            color: #212529;
            border-color: #dee2e6;
            text-decoration: none;
        }}
        .url-icon {{
            margin-right: 0.5rem;
            opacity: 0.7;
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
            <a href="{'index.html' if site == 'folklife' else f'index_{site}.html'}" class="site-btn{' active' if site == 'folklife' else ''}">
                {SITE_CONFIGS['folklife']['display_name']}
            </a>
            <a href="{'index.html' if site == 'festival' else f'index_{site}.html'}" class="site-btn{' active' if site == 'festival' else ''}">
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
                <img src="{SPACES_CDN_BASE}/{site}/{canonical['filename']}" alt="Canonical" class="canonical-image clickable" 
                     onclick="openModal('{canonical['filename']}', '{site}')">
                <div class="cluster-details">
                    <h2>Layout {cluster_id}</h2>"""
    
    # Add URL link for canonical image if available
    canonical_url = url_mapping.get(canonical['filename'], '')
    if canonical_url:
        html += f"""
                    <a href="{canonical_url}" target="_blank" class="image-url-link">
                        <span class="url-icon">🔗</span>View Source Page
                    </a>"""
    
    html += f"""
                    
                    <div class="cluster-stats">
                        <div class="stat-item">
                            <div class="stat-number">{len(screenshots)}</div>
                            <div class="stat-label">Total Screenshots</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{len(screenshots)}</div>
                            <div class="stat-label">Images in Layout</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="images-grid">"""
    
    for screenshot in sorted_screenshots:
        similarity = 100 - (screenshot['distance'] * 100)
        
        html += f"""
            <div class="image-card">
                <img src="{SPACES_CDN_BASE}/{site}/{screenshot['filename']}" alt="{screenshot['filename']}" 
                     onclick="openModal('{screenshot['filename']}', '{site}')">
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
        
        # Add URL link if available
        screenshot_url = url_mapping.get(screenshot['filename'], '')
        if screenshot_url:
            html += f"""
                    <a href="{screenshot_url}" target="_blank" class="image-url-link">
                        <span class="url-icon">🔗</span>View Source Page
                    </a>"""
        
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
        function openModal(filename, site) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const caption = document.getElementById('modalCaption');
            
            modal.style.display = 'block';
            modalImg.src = 'https://quotient.nyc3.cdn.digitaloceanspaces.com/' + site + '/' + filename;
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

def main():
    """Main execution function"""
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Generate pages for each site
    for site_name in SITE_CONFIGS:
        print(f"Generating site: {site_name}")
        
        # Load cluster data
        clusters = load_cluster_data(site_name)
        if clusters is None:
            continue
        
        # Generate summary
        summary = get_cluster_summary(clusters, site_name)
        
        # Generate main index page
        main_html = generate_main_page(summary, SITE_CONFIGS)
        
        # Save main page
        if site_name == 'folklife':
            output_file = OUTPUT_DIR / 'index.html'
        else:
            output_file = OUTPUT_DIR / f'index_{site_name}.html'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(main_html)
        print(f"Generated: {output_file}")
        
        # Generate cluster detail pages
        for cluster_id, screenshots in clusters.items():
            detail_html = generate_cluster_detail_page(cluster_id, screenshots, site_name, SITE_CONFIGS[site_name])
            
            output_file = OUTPUT_DIR / f'layout_{site_name}_{cluster_id}.html'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(detail_html)
            print(f"Generated: {output_file}")
    
    print("Site generation complete!")

if __name__ == "__main__":
    main()
