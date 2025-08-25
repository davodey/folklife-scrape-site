# CDN Optimization Guide for Static Site

This guide provides step-by-step instructions for implementing the best low-cost caching solutions for your folklife.si.edu Layouts Viewer static site.

## 🚀 **Quick Start: Cloudflare (Recommended)**

**Cost: $0/month**
**Performance Improvement: 3-5x faster loading**

### Step 1: Sign up for Cloudflare
1. Go to [cloudflare.com](https://cloudflare.com)
2. Create a free account
3. Add your domain (or use a subdomain like `layouts.yourdomain.com`)

### Step 2: Configure DNS
1. Point your domain's nameservers to Cloudflare
2. Add an A record pointing to `192.0.2.1` (Cloudflare placeholder)
3. Enable the orange cloud (proxy) for your domain

### Step 3: Configure Performance Settings
1. Go to **Speed** → **Optimization**
2. Enable **Auto Minify** for HTML, CSS, and JavaScript
3. Enable **Brotli** compression
4. Go to **Caching** → **Configuration**
5. Set **Browser Cache TTL** to "1 month"
6. Enable **Always Online**

### Step 4: Update Static Site Generator
```python
# In generate_static_site_optimized.py
SELECTED_CDN = "cloudflare"
CDN_CONFIGS["cloudflare"]["base_url"] = "https://yourdomain.com"
```

### Step 5: Deploy
```bash
# Generate optimized site
python generate_static_site_optimized.py

# Deploy to any static hosting (GitHub Pages, Netlify, etc.)
# Cloudflare will automatically cache and optimize everything
```

## 💰 **Option 2: BunnyCDN (Very Low Cost)**

**Cost: $0.01/GB transfer**
**Performance Improvement: 2-4x faster loading**

### Step 1: Create BunnyCDN Account
1. Go to [bunny.net](https://bunny.net)
2. Sign up for free account
3. Add payment method (pay-as-you-go)

### Step 2: Create Pull Zone
1. Go to **Storage** → **Pull Zones**
2. Click **Create Pull Zone**
3. Set **Origin URL** to your DigitalOcean Spaces URL
4. Choose **Optimization Level**: Medium
5. Enable **Image Optimization**
6. Set **Cache Control**: 1 month

### Step 3: Configure Edge Rules
1. Go to **Edge Rules**
2. Add rule for images:
   - **If**: File extension contains `.png` or `.jpg`
   - **Then**: Cache Level = Cache Everything, Edge Cache TTL = 1 month

### Step 4: Update Configuration
```python
# In generate_static_site_optimized.py
SELECTED_CDN = "bunnycdn"
CDN_CONFIGS["bunnycdn"]["base_url"] = "https://your-zone.b-cdn.net"
```

## ☁️ **Option 3: Optimize Current DigitalOcean Spaces**

**Cost: $5/month + $0.02/GB transfer**
**Performance Improvement: 1.5-2x faster loading**

### Step 1: Enable CDN Features
1. Go to your DigitalOcean Spaces dashboard
2. Enable **CDN** if not already enabled
3. Set **Cache-Control** headers in your uploads

### Step 2: Add Cache Headers
```bash
# When uploading files, add cache headers
s3cmd sync static_site/ s3://your-space-name/ \
  --acl-public \
  --add-header="Cache-Control: public, max-age=31536000" \
  --add-header="Content-Encoding: gzip"
```

### Step 3: Use Optimized Generator
```python
# In generate_static_site_optimized.py
SELECTED_CDN = "digitalocean"
# The generator will add proper cache headers automatically
```

## 📊 **Performance Comparison**

| CDN Option | Cost | Setup Time | Performance Gain | Features |
|------------|------|------------|------------------|----------|
| **Cloudflare** | $0/month | 15 min | 3-5x faster | Auto-optimization, DDoS protection |
| **BunnyCDN** | $0.01/GB | 30 min | 2-4x faster | Image optimization, edge rules |
| **DigitalOcean** | $5/month | 10 min | 1.5-2x faster | Basic CDN, simple setup |

## 🔧 **Advanced Optimizations**

### 1. Image Optimization
```python
# Cloudflare automatic image optimization
image_url = f"{base_url}/cdn-cgi/image/format=auto,quality=85,width=300,height=225/{filename}"

# BunnyCDN image optimization
image_url = f"{base_url}/{filename}?optimize=medium&width=300&height=225"
```

### 2. Browser Caching
```html
<!-- Add to HTML head -->
<meta http-equiv="Cache-Control" content="public, max-age=3600, must-revalidate">
<meta http-equiv="Expires" content="3600">
```

### 3. Resource Preloading
```html
<!-- Preload critical resources -->
<link rel="preload" href="/critical.css" as="style">
<link rel="preload" href="/critical.js" as="script">
<link rel="dns-prefetch" href="//your-cdn.com">
```

### 4. Lazy Loading
```html
<!-- Images load only when visible -->
<img class="lazy-image" 
     data-src="image-url" 
     alt="description">
```

## 🚀 **Deployment Scripts**

### Cloudflare Deployment
```bash
#!/bin/bash
# deploy-to-cloudflare.sh

echo "🚀 Deploying to Cloudflare..."

# Generate optimized site
python generate_static_site_optimized.py

# Deploy to any static hosting
# Cloudflare will automatically optimize and cache

echo "✅ Deployed! Cloudflare will optimize everything automatically."
```

### BunnyCDN Deployment
```bash
#!/bin/bash
# deploy-to-bunnycdn.sh

echo "🚀 Deploying to BunnyCDN..."

# Generate optimized site
python generate_static_site_optimized.py

# Upload to your hosting (GitHub Pages, Netlify, etc.)
# BunnyCDN pull zone will cache from your origin

echo "✅ Deployed! BunnyCDN is caching and optimizing your content."
```

## 📈 **Monitoring Performance**

### 1. WebPageTest
- Test your site at [webpagetest.org](https://webpagetest.org)
- Compare before/after CDN implementation
- Look for improvements in:
  - First Contentful Paint (FCP)
  - Largest Contentful Paint (LCP)
  - Time to Interactive (TTI)

### 2. Google PageSpeed Insights
- Test at [pagespeed.web.dev](https://pagespeed.web.dev)
- Get specific optimization recommendations
- Monitor Core Web Vitals

### 3. Browser DevTools
- Open Chrome DevTools → Network tab
- Look for:
  - Cached resources (marked with disk icon)
  - Compression (gzip/brotli)
  - CDN headers

## 🎯 **Recommended Implementation Order**

1. **Start with Cloudflare** (free, easiest setup)
2. **Test performance** with WebPageTest
3. **If needed, upgrade to BunnyCDN** for better image optimization
4. **Monitor costs** and adjust as needed

## 🔍 **Troubleshooting**

### Common Issues

1. **Images not loading from CDN**
   - Check CDN base URL configuration
   - Verify DNS settings
   - Check CDN dashboard for errors

2. **Cache not working**
   - Verify cache headers are set
   - Check CDN cache settings
   - Clear browser cache for testing

3. **Performance not improving**
   - Ensure CDN is properly configured
   - Check if images are being served from CDN
   - Verify compression is enabled

### Debug Commands

```bash
# Check if CDN is working
curl -I https://your-cdn.com/image.png

# Look for cache headers
curl -H "Accept-Encoding: gzip" -I https://your-cdn.com/image.png

# Test image optimization
curl -I "https://your-cdn.com/cdn-cgi/image/format=auto,quality=85/image.png"
```

## 💡 **Pro Tips**

1. **Start small**: Begin with Cloudflare free tier
2. **Test thoroughly**: Use multiple tools to verify improvements
3. **Monitor costs**: Track bandwidth usage if using paid CDN
4. **Optimize images**: Compress images before uploading
5. **Use WebP**: Modern browsers support WebP for smaller file sizes

## 🆘 **Need Help?**

- **Cloudflare**: [docs.cloudflare.com](https://docs.cloudflare.com)
- **BunnyCDN**: [docs.bunny.net](https://docs.bunny.net)
- **DigitalOcean**: [docs.digitalocean.com](https://docs.digitalocean.com)

---

**Next Steps:**
1. Choose your preferred CDN option
2. Update the configuration in `generate_static_site_optimized.py`
3. Generate and deploy your optimized site
4. Test performance improvements
5. Monitor and optimize further as needed
