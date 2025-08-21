# Deploying to DigitalOcean App Platform

This guide will help you deploy the folklife.si.edu Layouts Viewer to DigitalOcean App Platform.

## Prerequisites

1. A DigitalOcean account
2. The `doctl` CLI tool installed and authenticated
3. Your GitHub repository containing this code

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository contains:
- `cluster_viewer.py` - The main Flask application
- `requirements.txt` - Python dependencies
- `Dockerfile` - For containerized deployment
- `do-app.yaml` - DigitalOcean App Platform configuration
- `Procfile` - Process definition
- `runtime.txt` - Python version specification

### 2. Update Configuration

Edit `do-app.yaml` and update:
- `repo`: Change `your-username/festival-crawler` to your actual GitHub repository
- `branch`: Ensure this matches your main branch name

### 3. Deploy Using doctl

```bash
# Create the app
doctl apps create --spec do-app.yaml

# Get your app ID
doctl apps list

# Deploy updates
doctl apps update <APP_ID> --spec do-app.yaml
```

### 4. Deploy Using DigitalOcean Console

1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect your GitHub repository
4. Select the repository and branch
5. DigitalOcean will auto-detect the Python app
6. Configure environment variables if needed
7. Deploy

## Environment Variables

The app will automatically use these environment variables:
- `PORT` - Automatically set by DigitalOcean
- `FLASK_ENV=production` - Set in the Dockerfile

## Data Requirements

**Important**: Before deploying, ensure you have:
1. Run the layout deduplication script to generate:
   - `layout_clusters_final.csv`
   - `layout_clusters/` directory with organized images
2. The `folklife-screens-x/` directory with your screenshots

## Custom Domain

To use a custom domain like `layouts.folklife.si.edu`:
1. Add your domain in DigitalOcean App Platform
2. Configure DNS records to point to the app
3. Set up SSL certificates (automatic with DigitalOcean)

## Monitoring

- View logs: `doctl apps logs <APP_ID>`
- Monitor performance in the DigitalOcean console
- Set up alerts for errors or high resource usage

## Troubleshooting

### Common Issues

1. **Port binding errors**: Ensure the app listens on `0.0.0.0` and uses `$PORT`
2. **Missing dependencies**: Check `requirements.txt` includes all needed packages
3. **File not found errors**: Verify data files are included in the repository
4. **Memory issues**: Consider upgrading to a larger instance size

### Debug Mode

For debugging, you can temporarily enable debug mode by modifying the Dockerfile:
```dockerfile
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
```

## Cost Optimization

- Start with `basic-xxs` instance size
- Monitor usage and scale as needed
- Consider using DigitalOcean's free tier for testing

## Security Notes

- The app runs in a containerized environment
- No direct database access required
- Static files are served through Flask
- Consider adding authentication if needed for production use
