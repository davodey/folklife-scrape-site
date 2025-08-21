#!/usr/bin/env python3
"""
Smithsonian Festival Website Crawler
Crawls https://festival.si.edu and takes screenshots of all unique pages
"""

import asyncio
import os
import time
from urllib.parse import urljoin, urlparse
from pathlib import Path
import logging
from typing import Set, List, Dict, Any
import json

from playwright.async_api import async_playwright, Browser, Page
import requests
from bs4 import BeautifulSoup


class FestivalCrawler:
    def __init__(self, base_url: str = "https://folklife.si.edu", output_dir: str = "folklife-screens-x"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.visited_urls: Set[str] = set()
        self.url_mapping: Dict[str, str] = {}  # URL to filename mapping
        self.sitemap_data: Dict[str, Any] = {}  # Sitemap structure
        self.session = requests.Session()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def sanitize_filename(self, url: str) -> str:
        """Convert URL to a safe filename"""
        # Remove protocol and domain
        parsed = urlparse(url)
        path = parsed.path
        
        if not path or path == '/':
            path = 'homepage'
        
        # Remove leading slash and replace problematic characters
        filename = path.lstrip('/').replace('/', '_').replace('?', '_').replace('&', '_')
        filename = filename.replace('=', '_').replace('#', '_').replace('+', '_')
        
        # Limit length and ensure it ends with .png
        if len(filename) > 100:
            filename = filename[:100]
        
        if not filename.endswith('.png'):
            filename += '.png'
        
        return filename

    def is_valid_url(self, url: str) -> bool:
        """Check if URL should be crawled"""
        # Only crawl URLs from the same domain
        if not url.startswith(self.base_url):
            return False
        
        # Skip certain file types
        skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.xml', '.zip'}
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip search pages and certain URL patterns
        skip_patterns = [
            '/wp-admin', '/wp-content', '/wp-includes', '/feed', '/rss', '/sitemap',
            '/search', 'search?', 'Search?', 'Search/', 'search/', '?query=', '?JsonSearchModel='
        ]
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False
        
        return True

    def get_page_metadata(self, url: str, depth: int) -> Dict[str, Any]:
        """Extract metadata for sitemap entry"""
        parsed = urlparse(url)
        path = parsed.path
        
        # Determine page type based on URL structure
        page_type = "page"
        if path == "/" or path == "":
            page_type = "homepage"
        elif path.startswith("/blog"):
            page_type = "blog"
        elif path.startswith("/schedule"):
            page_type = "schedule"
        elif path.startswith("/visit"):
            page_type = "visit"
        elif path.startswith("/about-us"):
            page_type = "about"
        elif path.startswith("/2025"):
            page_type = "festival_program"
        elif path.startswith("/2024"):
            page_type = "festival_program"
        elif path.startswith("/2023"):
            page_type = "festival_program"
        elif "search" in path:
            page_type = "search"
        
        return {
            "url": url,
            "path": path,
            "page_type": page_type,
            "depth": depth,
            "screenshot": self.url_mapping.get(url, ""),
            "crawled_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "children": [],
            "parent": None,
            "images": []
        }

    async def get_page_links(self, page: Page) -> List[str]:
        """Extract all links from the current page"""
        try:
            # Wait for page to load with more flexible timeout
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=30000)
            except:
                self.logger.warning(f"Page load timeout for {page.url}, continuing anyway...")
            
            # Additional wait for dynamic content
            await asyncio.sleep(3)
            
            # Get all links
            links = await page.query_selector_all('a[href]')
            urls = []
            
            for link in links:
                try:
                    href = await link.get_attribute('href')
                    if href:
                        absolute_url = urljoin(self.base_url, href)
                        if self.is_valid_url(absolute_url):
                            urls.append(absolute_url)
                except Exception as e:
                    self.logger.debug(f"Error processing link: {e}")
                    continue
            
            return list(set(urls))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Error extracting links from {page.url}: {e}")
            return []

    async def get_page_images(self, page: Page) -> List[str]:
        """Extract all image URLs from the current page"""
        try:
            # Get all images
            images = await page.query_selector_all('img[src]')
            image_urls = []
            
            for img in images:
                try:
                    src = await img.get_attribute('src')
                    if src:
                        absolute_url = urljoin(self.base_url, src)
                        # Only include actual image files
                        if any(absolute_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                            image_urls.append(absolute_url)
                except Exception as e:
                    self.logger.debug(f"Error processing image: {e}")
                    continue
            
            return list(set(image_urls))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Error extracting images from {page.url}: {e}")
            return []

    async def take_screenshot(self, page: Page, url: str) -> str:
        """Take a screenshot of the current page"""
        try:
            # Wait for page to be fully loaded with more flexible approach
            try:
                await page.wait_for_load_state('networkidle', timeout=20000)
            except:
                self.logger.warning(f"Network idle timeout for {url}, taking screenshot anyway...")
            
            # Additional wait for dynamic content
            await asyncio.sleep(3)
            
            # Generate filename
            filename = self.sanitize_filename(url)
            filepath = self.output_dir / filename
            
            # Take screenshot
            await page.screenshot(
                path=str(filepath),
                full_page=True,
                type='png'
            )
            
            self.url_mapping[url] = filename
            self.logger.info(f"Screenshot saved: {filename} for {url}")
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot of {url}: {e}")
            return ""

    async def crawl_page(self, browser: Browser, url: str, depth: int = 0, max_depth: int = 3, parent_url: str = None):
        """Crawl a single page and its links"""
        if depth > max_depth or url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        self.logger.info(f"Crawling page {depth + 1}/{max_depth + 1}: {url}")
        
        # Add to sitemap
        page_data = self.get_page_metadata(url, depth)
        page_data["parent"] = parent_url
        self.sitemap_data[url] = page_data
        
        try:
            # Create new page context
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()
            
            # Navigate to page with more flexible timeout
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=45000)
            except Exception as e:
                self.logger.warning(f"Page navigation timeout for {url}: {e}")
                # Try to continue anyway
                pass
            
            # Take screenshot
            await self.take_screenshot(page, url)
            
            # Extract links and images
            links = await self.get_page_links(page)
            images = await self.get_page_images(page)
            
            # Update sitemap with children and images
            page_data["children"] = links
            page_data["images"] = images
            
            # Crawl new links if not at max depth
            if depth < max_depth:
                for link in links:
                    if link not in self.visited_urls:
                        await self.crawl_page(browser, link, depth + 1, max_depth, url)
            
            await context.close()
            
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {e}")

    def build_hierarchical_sitemap(self) -> Dict[str, Any]:
        """Build a hierarchical sitemap structure"""
        hierarchical = {
            "metadata": {
                "base_url": self.base_url,
                "total_pages": len(self.visited_urls),
                "crawled_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "crawler_version": "1.0.0"
            },
            "pages": {},
            "structure": {
                "homepage": None,
                "main_sections": {},
                "festival_programs": [],
                "blog_posts": [],
                "other_pages": []
            }
        }
        
        # Organize pages by type
        for url, page_data in self.sitemap_data.items():
            hierarchical["pages"][url] = page_data
            
            page_type = page_data["page_type"]
            if page_type == "homepage":
                hierarchical["structure"]["homepage"] = url
            elif page_type == "festival_program":
                hierarchical["structure"]["festival_programs"].append(url)
            elif page_type == "blog":
                hierarchical["structure"]["blog_posts"].append(url)
            elif page_type in ["schedule", "visit", "about"]:
                if page_type not in hierarchical["structure"]["main_sections"]:
                    hierarchical["structure"]["main_sections"][page_type] = []
                hierarchical["structure"]["main_sections"][page_type].append(url)
            else:
                hierarchical["structure"]["other_pages"].append(url)
        
        return hierarchical

    async def run(self, max_depth: int = 10, delay: float = 1.0):
        """Main crawling method"""
        self.logger.info(f"Starting crawl of {self.base_url}")
        self.logger.info(f"Max depth: {max_depth}, Delay between requests: {delay}s")
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            try:
                # Start crawling from the homepage
                await self.crawl_page(browser, self.base_url, max_depth=max_depth)
                
                # Save URL mapping
                mapping_file = self.output_dir / 'url_mapping.json'
                with open(mapping_file, 'w') as f:
                    json.dump(self.url_mapping, f, indent=2)
                
                # Save sitemap
                sitemap_file = self.output_dir / 'sitemap.json'
                hierarchical_sitemap = self.build_hierarchical_sitemap()
                with open(sitemap_file, 'w') as f:
                    json.dump(hierarchical_sitemap, f, indent=2)
                
                self.logger.info(f"Crawling completed! Screenshots saved to {self.output_dir}")
                self.logger.info(f"Total pages crawled: {len(self.visited_urls)}")
                self.logger.info(f"URL mapping saved to {mapping_file}")
                self.logger.info(f"Sitemap saved to {sitemap_file}")
                
            finally:
                await browser.close()

    def save_summary(self):
        """Save a summary of the crawling results"""
        summary = {
            'base_url': self.base_url,
            'total_pages': len(self.visited_urls),
            'visited_urls': list(self.visited_urls),
            'url_mapping': self.url_mapping,
            'sitemap_entries': len(self.sitemap_data),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        summary_file = self.output_dir / 'crawl_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Summary saved to {summary_file}")


async def main():
    """Main function"""
    crawler = FestivalCrawler()
    
    try:
        await crawler.run(max_depth=10, delay=1.0)
        crawler.save_summary()
        
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user")
        crawler.save_summary()
    except Exception as e:
        print(f"Error during crawling: {e}")
        crawler.save_summary()


if __name__ == "__main__":
    asyncio.run(main()) 