# Smithsonian Festival Website Crawler

A Python-based website crawler that automatically crawls [https://festival.si.edu](https://festival.si.edu) and takes screenshots of all unique pages. Perfect for website redesign projects where you need visual documentation of the current site.

## Features

- **Automatic Discovery**: Crawls the entire website starting from the homepage
- **Smart Filtering**: Skips irrelevant files (PDFs, images, CSS, JS) and admin pages
- **High-Quality Screenshots**: Takes full-page screenshots at 1920x1080 resolution
- **Comprehensive Logging**: Detailed logs of all crawling activities
- **URL Mapping**: Creates a JSON file mapping URLs to screenshot filenames
- **Smart Sitemap Generation**: Builds a structured JSON sitemap with page hierarchy and metadata
- **Page Classification**: Automatically categorizes pages by type (homepage, blog, schedule, etc.)
- **Image URL Extraction**: Captures all image URLs found on each page
- **Search Page Filtering**: Automatically skips search results and query-based URLs
- **Configurable**: Easy to customize crawling depth, delays, and filters
- **Respectful Crawling**: Includes delays between requests to be respectful to the server

## Requirements

- Python 3.8+
- macOS (tested on macOS 24.6.0)
- Internet connection

## Installation

1. **Activate your virtual environment** (if you haven't already):
   ```bash
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

## Usage

### Basic Usage

Run the crawler with default settings:
```bash
python festival_crawler.py
```

### Configuration

Edit `config.py` to customize:
- **Crawling depth**: How many levels deep to crawl (default: 10)
- **Output directory**: Where to save screenshots (default: `screenshots/`)
- **Viewport size**: Screenshot resolution (default: 1920x1080)
- **Delays**: Time between requests (default: 1 second)
- **URL filters**: What to skip during crawling

### Output

The crawler will create:
- `folklife-screens-x/` directory with all page screenshots
- `sitemap.json` comprehensive sitemap with page hierarchy and metadata
- `url_mapping.json` mapping URLs to filenames
- `crawl_summary.json` with crawling statistics
- `crawler.log` with detailed logging

## How It Works

1. **Start**: Begins at the homepage (https://festival.si.edu)
2. **Discover**: Finds all links on each page
3. **Filter**: Removes irrelevant URLs (PDFs, admin pages, etc.)
4. **Screenshot**: Takes a full-page screenshot of each unique page
5. **Recurse**: Follows links to discover more pages (up to max depth)
6. **Document**: Creates comprehensive mapping and summary files

## Customization

### Change Crawling Depth

In `config.py`:
```python
CRAWLER_CONFIG = {
    'max_depth': 2,  # Only crawl 2 levels deep
    # ... other settings
}
```

### Change Screenshot Resolution

In `config.py`:
```python
CRAWLER_CONFIG = {
    'viewport_width': 1366,
    'viewport_height': 768,
    # ... other settings
}
```

### Add Custom URL Filters

In `config.py`:
```python
URL_FILTERS = {
    'skip_patterns': [
        '/wp-admin',
        '/wp-content',
        '/custom-pattern',  # Add your custom pattern
        # ... other patterns
    ]
}
```

## Troubleshooting

### Common Issues

1. **Playwright not found**: Run `playwright install chromium`
2. **Permission errors**: Ensure you have write access to the output directory
3. **Memory issues**: Reduce `max_depth` or add longer delays
4. **Network timeouts**: Increase timeout values in config

### Debug Mode

Set logging to DEBUG in `config.py`:
```python
LOGGING_CONFIG = {
    'level': 'DEBUG',
    # ... other settings
}
```

### View Browser (Non-Headless Mode)

Set `headless: False` in `config.py` to see the browser in action:
```python
BROWSER_CONFIG = {
    'headless': False,
    # ... other settings
}
```

## Performance Tips

- **Reduce depth**: Start with `max_depth: 1` for testing
- **Increase delays**: Use longer delays if the server is slow
- **Monitor memory**: Large sites may require more RAM
- **Check logs**: Review `crawler.log` for any issues

## Legal and Ethical Considerations

- **Respect robots.txt**: The crawler respects standard web crawling protocols
- **Rate limiting**: Built-in delays prevent overwhelming the server
- **User agent**: Identifies itself as a legitimate browser
- **Domain restriction**: Only crawls the specified domain

## Support

If you encounter issues:
1. Check the `crawler.log` file for error messages
2. Verify your internet connection
3. Ensure all dependencies are installed
4. Check that the target website is accessible

## License

This project is for educational and legitimate business use only. Please respect the terms of service of any website you crawl. 