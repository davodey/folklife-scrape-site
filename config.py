"""
Configuration file for the Festival Crawler
Modify these settings as needed
"""

# Crawler Configuration
CRAWLER_CONFIG = {
    'base_url': 'https://festival.si.edu',
    'output_directory': 'screenshots',
    'max_depth': 3,  # How deep to crawl (0 = homepage only, 1 = homepage + direct links, etc.)
    'delay_between_requests': 1.0,  # Seconds to wait between requests
    'viewport_width': 1920,
    'viewport_height': 1080,
    'timeout': 30000,  # Page load timeout in milliseconds
    'wait_for_network_idle': 10000,  # Wait for network to be idle in milliseconds
    'additional_wait': 2,  # Additional seconds to wait for dynamic content
}

# Browser Configuration
BROWSER_CONFIG = {
    'headless': True,  # Set to False to see the browser in action
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'args': [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu'
    ]
}

# URL Filtering
URL_FILTERS = {
    'skip_extensions': {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.xml', '.zip', '.ico', '.svg'},
    'skip_patterns': [
        '/wp-admin',
        '/wp-content', 
        '/wp-includes',
        '/feed',
        '/rss',
        '/sitemap',
        '/api/',
        '/admin/',
        '/login',
        '/logout',
        '/register',
        '/search?',
        'mailto:',
        'tel:',
        'javascript:'
    ],
    'allowed_domains': ['festival.si.edu']  # Only crawl these domains
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'log_file': 'crawler.log'
} 