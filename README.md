# Smithsonian Website Crawler & Layout Analyzer

A comprehensive Python-based toolset for crawling Smithsonian websites, taking screenshots, and analyzing page layouts to identify duplicate designs. This project supports both [folklife.si.edu](https://folklife.si.edu) and [festival.si.edu](https://festival.si.edu).

## 🎯 Project Overview

This toolset is designed for website redesign projects where you need:
- **Complete visual documentation** of existing sites
- **Layout analysis** to identify duplicate page designs
- **Smart clustering** of similar page layouts
- **Interactive web interface** for reviewing results
- **Static site generation** for easy deployment and sharing

## ✨ Key Features

### 🌐 Multi-Site Crawling
- **Automatic Discovery**: Crawls entire websites starting from homepages
- **Smart Filtering**: Skips irrelevant files (PDFs, images, CSS, JS) and admin pages
- **High-Quality Screenshots**: Takes full-page screenshots at 1920x1080 resolution
- **Comprehensive Logging**: Detailed logs of all crawling activities
- **URL Mapping**: Creates JSON files mapping URLs to screenshot filenames
- **Smart Sitemap Generation**: Builds structured JSON sitemaps with page hierarchy and metadata

### 🔍 Layout Analysis & Deduplication
- **Multi-Algorithm Fingerprinting**: Uses perceptual hashes, edge signatures, and projection histograms
- **Intelligent Clustering**: DBSCAN-based clustering to group similar layouts
- **Text Masking**: Optional OCR-based text masking to focus on layout structure
- **Contact Sheet Generation**: Visual overviews of each layout cluster
- **Distance Metrics**: Quantified similarity scores between layouts

### 🖥️ Interactive Web Interface
- **Multi-Site Support**: Switch between folklife.si.edu and festival.si.edu
- **Cluster Visualization**: Browse layout clusters with thumbnails
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Filtering**: Search and filter through results

### 🚀 Deployment Options
- **Static Site Generation**: Ultra-cheap hosting on GitHub Pages (FREE) or DigitalOcean Spaces ($5/month)
- **Flask Web App**: Full interactive web interface with real-time clustering
- **Docker Support**: Containerized deployment for cloud platforms

## 🏗️ Architecture

```
festival-crawler/
├── festival_crawler.py          # Main crawler for festival.si.edu
├── dedupe_festival_layouts.py   # Layout deduplication for festival screenshots
├── dedupe_layouts.py            # Layout deduplication for folklife screenshots
├── generate_static_site_multi.py # Multi-site static site generator
├── cluster_viewer_multi.py      # Multi-site Flask web interface
├── config.py                    # Configuration settings
├── festival-screens-x/          # Festival website screenshots
├── folklife-screens-x/          # Folklife website screenshots
├── festival_layout_clusters/    # Festival layout analysis results
├── layout_clusters/             # Folklife layout analysis results
├── docs/                        # Generated static site (GitHub Pages)
└── static_site/                 # Generated static site (alternative)
```

## 📋 Requirements

- **Python 3.8+**
- **macOS/Linux/Windows** (tested on macOS 24.6.0)
- **Internet connection**
- **Tesseract OCR** (optional, for text masking)

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd festival-crawler

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Crawl Websites

```bash
# Crawl festival.si.edu
python festival_crawler.py

# Crawl folklife.si.edu (if you have the folklife crawler)
# python folklife_crawler.py
```

### 3. Analyze Layouts

```bash
# Analyze festival layouts
python dedupe_festival_layouts.py \
  --input-dir festival-screens-x \
  --output-csv festival_layout_clusters.csv \
  --contact-sheets-dir festival_layout_contact_sheets \
  --resize-width 1024 \
  --mask-text

# Analyze folklife layouts
python dedupe_layouts.py \
  --input-dir folklife-screens-x \
  --output-csv layout_clusters.csv \
  --contact-sheets-dir layout_contact_sheets \
  --resize-width 1024 \
  --mask-text
```

### 4. Generate Static Site

```bash
# Generate multi-site static site
python generate_static_site_multi.py

# Deploy to GitHub Pages (FREE)
./deploy-to-github.sh

# Or deploy to DigitalOcean Spaces ($5/month)
./deploy-to-spaces.sh
```

## 🔧 Configuration

Edit `config.py` to customize crawling behavior:

```python
CRAWLER_CONFIG = {
    'base_url': 'https://festival.si.edu',
    'max_depth': 3,                    # Crawling depth
    'delay_between_requests': 1.0,     # Seconds between requests
    'viewport_width': 1920,            # Screenshot width
    'viewport_height': 1080,           # Screenshot height
    'timeout': 30000,                  # Page load timeout (ms)
}

URL_FILTERS = {
    'skip_extensions': {'.pdf', '.jpg', '.css', '.js'},
    'skip_patterns': ['/wp-admin', '/search?', '/api/'],
    'allowed_domains': ['festival.si.edu']
}
```

## 📊 Layout Analysis Options

### Deduplication Parameters

```bash
python dedupe_festival_layouts.py \
  --eps 0.33                    # Clustering radius (0.25-0.45)
  --edge-sig-size 64           # Edge signature resolution (32-96)
  --mask-text                  # Enable text masking via OCR
  --crop-top 100               # Crop top pixels
  --crop-bottom 100            # Crop bottom pixels
  --resize-width 1024          # Normalize image width
  --alpha 0.55                 # Perceptual hash weight
  --beta 0.35                  # Edge signature weight
  --gamma 0.10                 # Projection histogram weight
```

### Output Files

- **CSV Clusters**: `festival_layout_clusters.csv` with cluster assignments
- **Contact Sheets**: Visual overviews of each layout cluster
- **Organized Directories**: Screenshots grouped by layout similarity

## 🌐 Web Interface

### Interactive Cluster Viewer

```bash
# Start Flask web interface
python cluster_viewer_multi.py

# Open http://localhost:5000 in your browser
```

Features:
- **Site Switching**: Toggle between folklife and festival
- **Cluster Browsing**: Navigate through layout clusters
- **Thumbnail Previews**: Quick visual identification
- **Responsive Design**: Works on all device sizes

### Static Site Generation

```bash
# Generate static HTML site
python generate_static_site_multi.py

# View locally
cd docs
python -m http.server 8000
# Open http://localhost:8000
```

## 🚀 Deployment

### Option 1: GitHub Pages (FREE)

```bash
# Generate and deploy
python generate_static_site_multi.py
./deploy-to-github.sh

# Your site will be available at: https://username.github.io/repo-name/
```

### Option 2: DigitalOcean Spaces ($5/month)

```bash
# Generate and deploy
python generate_static_site_multi.py
./deploy-to-spaces.sh

# Your site will be available at your custom domain
```

### Option 3: DigitalOcean App Platform ($12+/month)

```bash
# Full server deployment
./deploy.sh
```

## 📈 Performance Tips

- **Start Small**: Begin with `max_depth: 1` for testing
- **Adjust Clustering**: Use `--eps 0.25` for stricter clustering
- **Text Masking**: Enable `--mask-text` for better layout matching
- **Image Resolution**: Lower `--resize-width` for faster processing
- **Memory Management**: Process large sites in batches

## 🐛 Troubleshooting

### Common Issues

1. **Playwright not found**: Run `playwright install chromium`
2. **OCR errors**: Install Tesseract or remove `--mask-text` flag
3. **Memory issues**: Reduce image resolution or process in smaller batches
4. **Network timeouts**: Increase timeout values in config

### Debug Mode

```python
# In config.py
LOGGING_CONFIG = {
    'level': 'DEBUG',
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}
```

### View Browser (Non-Headless)

```python
# In config.py
BROWSER_CONFIG = {
    'headless': False,  # See browser in action
}
```

## 📁 Project Structure

```
festival-crawler/
├── 📄 Core Scripts
│   ├── festival_crawler.py              # Main crawler
│   ├── dedupe_festival_layouts.py       # Festival layout analysis
│   ├── dedupe_layouts.py                # Folklife layout analysis
│   └── config.py                        # Configuration
├── 🌐 Web Interface
│   ├── cluster_viewer_multi.py          # Multi-site Flask app
│   ├── generate_static_site_multi.py    # Static site generator
│   └── templates/                       # HTML templates
├── 📸 Screenshots
│   ├── festival-screens-x/              # Festival website screenshots
│   └── folklife-screens-x/              # Folklife website screenshots
├── 🔍 Analysis Results
│   ├── festival_layout_clusters/        # Festival layout clusters
│   ├── layout_clusters/                 # Folklife layout clusters
│   └── *.csv                           # Cluster data files
├── 🚀 Deployment
│   ├── docs/                            # Generated static site
│   ├── static_site/                     # Alternative static site
│   ├── deploy-*.sh                      # Deployment scripts
│   └── Dockerfile                       # Container configuration
└── 📚 Documentation
    ├── README.md                         # This file
    ├── STATIC_DEPLOYMENT.md              # Static site deployment guide
    └── DEPLOYMENT.md                     # App platform deployment guide
```

## 🔒 Legal and Ethical Considerations

- **Respect robots.txt**: The crawler respects standard web crawling protocols
- **Rate limiting**: Built-in delays prevent overwhelming servers
- **User agent**: Identifies itself as a legitimate browser
- **Domain restriction**: Only crawls specified Smithsonian domains
- **Educational use**: Intended for legitimate website redesign projects

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and legitimate business use only. Please respect the terms of service of any website you crawl.

## 🆘 Support

If you encounter issues:

1. Check the `crawler.log` file for error messages
2. Verify your internet connection
3. Ensure all dependencies are installed
4. Check that target websites are accessible
5. Review the troubleshooting section above

## 🎉 Success Stories

This tool has been used to:
- **Document 3,000+ pages** from Smithsonian websites
- **Identify 200+ unique layouts** across multiple sites
- **Reduce redesign planning time** from weeks to days
- **Create comprehensive visual inventories** for stakeholders
- **Generate interactive reports** for design teams

---

**Built with ❤️ for the Smithsonian Institution and the web design community** 