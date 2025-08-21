# Static Site Deployment Guide

This guide shows you how to deploy the folklife.si.edu Layouts Viewer as a static site for ultra-cheap hosting.

## 🎯 **Why Static Sites?**

- **💰 Ultra-cheap**: $5/month or less vs $12+/month for App Platform
- **⚡ Fast**: No server processing, just static files
- **🔒 Secure**: No server-side vulnerabilities
- **📈 Scalable**: CDN-backed, handles unlimited traffic
- **🌍 Global**: Fast loading worldwide

## 🚀 **Option 1: DigitalOcean Spaces (Recommended)**

### **Cost: $5/month for 250GB storage + $0.02/GB transfer**

#### **Step 1: Generate Static Site**
```bash
# Generate the static HTML files
python generate_static_site.py
```

This creates a `static_site/` directory with:
- `index.html` - Main overview page
- `layout_*.html` - Individual cluster detail pages  
- `images/` - All screenshot images

#### **Step 2: Create DigitalOcean Space**
1. Go to [DigitalOcean Spaces](https://cloud.digitalocean.com/spaces)
2. Click "Create a Space"
3. Choose a region close to your users
4. Set name (e.g., `folklife-layouts`)
5. Choose "Public" for public access
6. Click "Create Space"

#### **Step 3: Upload Files**
```bash
# Install s3cmd (macOS)
brew install s3cmd

# Configure s3cmd with your DigitalOcean credentials
s3cmd --configure

# Upload the static site
s3cmd sync static_site/ s3://your-space-name/ --acl-public
```

#### **Step 4: Enable CDN (Optional)**
1. In your Space settings, enable CDN
2. This gives you a custom domain like: `https://your-space-name.nyc3.cdn.digitaloceanspaces.com`

#### **Step 5: Custom Domain (Optional)**
1. Add your domain in DigitalOcean
2. Point DNS to your Space
3. Enable SSL (automatic with DigitalOcean)

## 🌐 **Option 2: GitHub Pages (FREE!)**

### **Cost: $0/month**

#### **Step 1: Create GitHub Repository**
1. Create a new repo: `folklife-layouts-viewer`
2. Make it public

#### **Step 2: Generate and Upload**
```bash
# Generate static site
python generate_static_site.py

# Initialize git in static_site directory
cd static_site
git init
git add .
git commit -m "Initial static site"

# Add remote and push
git remote add origin https://github.com/yourusername/folklife-layouts-viewer.git
git branch -M main
git push -u origin main
```

#### **Step 3: Enable GitHub Pages**
1. Go to repo Settings → Pages
2. Source: "Deploy from a branch"
3. Branch: `main` → `/ (root)`
4. Your site will be available at: `https://yourusername.github.io/folklife-layouts-viewer`

## 🔧 **Option 3: Netlify (FREE tier)**

### **Cost: $0/month for basic usage**

1. Go to [Netlify](https://netlify.com)
2. Drag and drop your `static_site/` folder
3. Get instant deployment with custom URL
4. Connect your domain for free SSL

## 📊 **Cost Comparison**

| Platform | Monthly Cost | Storage | Bandwidth | Features |
|----------|--------------|---------|-----------|----------|
| **GitHub Pages** | $0 | 1GB | Unlimited | Basic hosting |
| **Netlify** | $0 | 100GB | 100GB | Forms, functions |
| **DigitalOcean Spaces** | $5 | 250GB | $0.02/GB | CDN, custom domain |
| **DigitalOcean App Platform** | $12+ | N/A | N/A | Full server |

## 🎨 **Customization Options**

### **Change Colors/Theme**
Edit the CSS in `generate_static_site.py`:
```python
# Change header background
.header { background: #your-color; }

# Change button colors  
.view-all a { background: #your-color; }
```

### **Add Analytics**
Add Google Analytics or Plausible to track visitors:
```html
<!-- Add to HTML head section -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
```

### **Add Search**
Integrate with Algolia or similar for search functionality.

## 🚀 **Deployment Scripts**

### **DigitalOcean Spaces Auto-Deploy**
```bash
#!/bin/bash
# deploy-to-spaces.sh

echo "🚀 Deploying to DigitalOcean Spaces..."

# Generate static site
python generate_static_site.py

# Upload to Spaces
s3cmd sync static_site/ s3://your-space-name/ --acl-public --delete-removed

echo "✅ Deployed successfully!"
echo "🌐 Your site: https://your-space-name.nyc3.cdn.digitaloceanspaces.com"
```

### **GitHub Pages Auto-Deploy**
```bash
#!/bin/bash
# deploy-to-github.sh

echo "🚀 Deploying to GitHub Pages..."

# Generate static site
python generate_static_site.py

# Commit and push changes
cd static_site
git add .
git commit -m "Update static site $(date)"
git push

echo "✅ Deployed successfully!"
echo "🌐 Your site: https://yourusername.github.io/folklife-layouts-viewer"
```

## 🔍 **Testing Locally**

Before deploying, test your static site locally:
```bash
# Generate the site
python generate_static_site.py

# Serve locally with Python
cd static_site
python -m http.server 8000

# Open http://localhost:8000
```

## 📱 **Mobile Optimization**

The static site is already mobile-responsive with:
- Responsive grid layouts
- Touch-friendly navigation
- Optimized image loading
- Mobile-first CSS

## 🔒 **Security Considerations**

- **No server-side code** = No server vulnerabilities
- **Static files only** = Minimal attack surface
- **CDN protection** = DDoS protection included
- **HTTPS by default** on all platforms

## 📈 **Performance Benefits**

- **Instant loading** - No server processing
- **CDN caching** - Global fast access
- **Optimized images** - Thumbnails and full-size
- **Minimal JavaScript** - Fast rendering

## 🎯 **Recommended Setup**

1. **Start with GitHub Pages** (free) for testing
2. **Move to DigitalOcean Spaces** ($5/month) for production
3. **Add custom domain** for professional appearance
4. **Enable CDN** for global performance

## 🆘 **Troubleshooting**

### **Common Issues**

1. **Images not loading**: Check file paths in `images/` directory
2. **CSS not working**: Verify all HTML files have complete CSS
3. **Links broken**: Ensure all relative paths are correct
4. **Large file sizes**: Optimize images before upload

### **Support**

- **GitHub Pages**: Check repo settings and Actions logs
- **DigitalOcean Spaces**: Use Spaces dashboard for monitoring
- **Netlify**: Check deploy logs and build settings

---

**🎉 Result**: A professional, fast, and ultra-cheap static site that costs pennies per month instead of dollars!
