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

### Detect Duplicate Layouts in Screenshots

After you have screenshots (e.g., in `folklife-screens-x/`), you can cluster duplicates by page layout using the included script:

```bash
python dedupe_layouts.py \
  --input-dir folklife-screens-x \
  --output-csv layout_clusters.csv \
  --contact-sheets-dir layout_contact_sheets \
  --resize-width 1024 \
  --crop-top 0 --crop-bottom 0 \
  --mask-text
```

What it does:
- Normalizes images to a common width and optional top/bottom crop
- Optionally masks text via OCR so content doesn't affect similarity
- Computes multiple layout fingerprints (perceptual hashes + edge/block signatures)
- Clusters near-duplicate layouts and writes a CSV labeling canonical vs. duplicates
- Optionally creates contact sheets per cluster for quick visual review

Flags you may want to tweak:
- `--eps`: clustering radius on the combined distance (lower = stricter). Try 0.25–0.45.
- `--edge-sig-size`: resolution of the edge signature (32–96). Larger is slower, more precise.
- `--mask-text`: enable to de-emphasize differing content; requires Tesseract (optional).
- `--crop-top` / `--crop-bottom`: remove fixed browser/UI bars if present.

Outputs:
- `layout_clusters.csv`: columns `cluster_id`, `canonical`, `filename`, `path`, `distance_to_canonical`
- `layout_contact_sheets/`: one JPG per cluster (if `--contact-sheets-dir` set)

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

## Deployment Options

### 🚀 **Option 1: Static Site (Recommended - Ultra Cheap!)**

**Cost: $0-5/month vs $12+/month for App Platform**

Generate a static HTML site that can be hosted on:
- **GitHub Pages**: FREE
- **DigitalOcean Spaces**: $5/month for 250GB
- **Netlify**: FREE tier

#### **Quick Deploy to GitHub Pages (FREE)**
```bash
# Generate static site
python generate_static_site.py

# Deploy to GitHub Pages
./deploy-to-github.sh
```

#### **Quick Deploy to DigitalOcean Spaces ($5/month)**
```bash
# Generate static site
python generate_static_site.py

# Deploy to DigitalOcean Spaces
./deploy-to-spaces.sh
```

#### **Test Locally First**
```bash
# Generate and test locally
python generate_static_site.py
cd static_site
python -m http.server 8000
# Open http://localhost:8000
```

### 🖥️ **Option 2: DigitalOcean App Platform**

**Cost: $12+/month**

For full server functionality (not recommended for cost reasons).

#### **Quick Deploy**
1. **Install doctl CLI tool**:
   ```bash
   # macOS
   brew install doctl
   ```

2. **Authenticate with DigitalOcean**:
   ```bash
   doctl auth init
   ```

3. **Deploy using the script**:
   ```bash
   ./deploy.sh
   ```

### 📁 **Deployment Files**

#### **Static Site (Recommended)**
- `generate_static_site.py` - Static site generator
- `deploy-to-github.sh` - GitHub Pages deployment
- `deploy-to-spaces.sh` - DigitalOcean Spaces deployment
- `STATIC_DEPLOYMENT.md` - Detailed static site guide

#### **App Platform**
- `Dockerfile` - Container configuration
- `do-app.yaml` - DigitalOcean App Platform spec
- `Procfile` - Process definition
- `runtime.txt` - Python version
- `deploy.sh` - Automated deployment script
- `DEPLOYMENT.md` - Detailed App Platform guide

## 💰 **Cost Comparison**

| Option | Monthly Cost | Storage | Bandwidth | Best For |
|--------|--------------|---------|-----------|----------|
| **GitHub Pages** | $0 | 1GB | Unlimited | Testing, personal projects |
| **DigitalOcean Spaces** | $5 | 250GB | $0.02/GB | **Production, professional use** |
| **DigitalOcean App Platform** | $12+ | N/A | N/A | Full server features |

**🎯 Recommendation**: Use the static site option for massive cost savings!

## License

This project is for educational and legitimate business use only. Please respect the terms of service of any website you crawl. 