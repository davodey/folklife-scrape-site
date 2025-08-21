#!/usr/bin/env python3
"""
Test script for the Festival Crawler
This script tests the crawler with minimal settings to ensure everything works
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from festival_crawler import FestivalCrawler


async def test_crawler():
    """Test the crawler with minimal settings"""
    print("🧪 Testing Festival Crawler...")
    
    # Create a test crawler with minimal settings
    test_crawler = FestivalCrawler(
        base_url="https://festival.si.edu",
        output_dir="test_screenshots"
    )
    
    try:
        print("✅ Starting test crawl (depth 1, homepage only)...")
        
        # Run with minimal depth for testing
        await test_crawler.run(max_depth=2, delay=2.0)
        
        print("✅ Test crawl completed successfully!")
        print(f"📁 Screenshots saved to: {test_crawler.output_dir}")
        print(f"📊 Total pages crawled: {len(test_crawler.visited_urls)}")
        
        # Save summary
        test_crawler.save_summary()
        
        print("\n🎉 Test completed successfully! The crawler is working properly.")
        print("You can now run the full crawler with: python festival_crawler.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Please check the error message and ensure all dependencies are installed.")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 Festival Crawler Test")
    print("=" * 40)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment may not be activated")
        print("   Run: source .venv/bin/activate")
        print()
    
    # Run test
    success = asyncio.run(test_crawler())
    
    if success:
        print("\n✅ All tests passed! You're ready to crawl the full website.")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        sys.exit(1) 