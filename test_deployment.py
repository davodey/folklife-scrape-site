#!/usr/bin/env python3
"""
Test script to verify deployment is working correctly
"""

import os
import requests
import json

def test_deployment(base_url):
    """Test the deployment endpoints"""
    print(f"Testing deployment at: {base_url}")
    
    # Test main page
    try:
        response = requests.get(f"{base_url}/")
        print(f"Main page: {response.status_code}")
        if response.status_code == 200:
            print("✅ Main page loads successfully")
        else:
            print("❌ Main page failed to load")
    except Exception as e:
        print(f"❌ Error accessing main page: {e}")
    
    # Test debug endpoint
    try:
        response = requests.get(f"{base_url}/debug")
        print(f"Debug endpoint: {response.status_code}")
        if response.status_code == 200:
            debug_info = response.json()
            print("✅ Debug endpoint working")
            print(f"Working directory: {debug_info.get('working_directory')}")
            print(f"folklife-screens-x exists: {debug_info.get('folklife_screens_x_exists')}")
            print(f"Available directories: {debug_info.get('available_directories')}")
        else:
            print("❌ Debug endpoint failed")
    except Exception as e:
        print(f"❌ Error accessing debug endpoint: {e}")
    
    # Test image serving
    try:
        # Try to load a sample image
        response = requests.get(f"{base_url}/images/homepage.png")
        print(f"Image test: {response.status_code}")
        if response.status_code == 200:
            print("✅ Image serving working")
            print(f"Image size: {len(response.content)} bytes")
        else:
            print("❌ Image serving failed")
    except Exception as e:
        print(f"❌ Error testing image serving: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    test_deployment(base_url)
