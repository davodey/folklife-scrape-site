#!/usr/bin/env python3
"""
Test script for the optimized static site generator
"""

import os
import sys
from pathlib import Path

def test_dependencies():
    """Test if all required dependencies are available"""
    print("🔍 Testing dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("❌ Python 3.6+ required")
        return False
    
    # Check required files
    required_files = [
        "layout_clusters_final.csv",
        "generate_static_site_optimized.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Required file not found: {file_path}")
            return False
    
    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Not in virtual environment - some dependencies may be missing")
    
    print("✅ All dependencies available")
    return True

def test_generator():
    """Test the static site generator"""
    print("\n🔧 Testing static site generator...")
    
    try:
        # Import the generator module
        sys.path.append('.')
        from generate_static_site_optimized import (
            load_cluster_data, 
            get_cluster_summary,
            create_thumbnail_url
        )
        
        # Test data loading
        clusters = load_cluster_data()
        if not clusters:
            print("❌ Failed to load cluster data")
            return False
        
        # Test summary generation
        summary = get_cluster_summary(clusters)
        if not summary:
            print("❌ Failed to generate summary")
            return False
        
        # Test URL generation
        test_url = create_thumbnail_url("test.png")
        if not test_url:
            print("❌ Failed to generate thumbnail URL")
            return False
        
        print(f"✅ Generator test passed!")
        print(f"   - Loaded {len(clusters)} clusters")
        print(f"   - Total screenshots: {summary['total_screenshots']}")
        print(f"   - Sample URL: {test_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Generator test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Optimized Static Site Generator")
    print("=" * 50)
    
    # Test dependencies
    if not test_dependencies():
        print("\n❌ Dependency test failed. Please fix issues above.")
        return False
    
    # Test generator
    if not test_generator():
        print("\n❌ Generator test failed. Please fix issues above.")
        return False
    
    print("\n🎉 All tests passed!")
    print("\n🚀 Ready to generate optimized static site!")
    print("   Run: python generate_static_site_optimized.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
