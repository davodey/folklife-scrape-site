#!/bin/bash

# Deploy to DigitalOcean App Platform
# Usage: ./deploy.sh [app-name]

set -e

APP_NAME=${1:-"folklife-layouts-viewer"}

echo "🚀 Deploying $APP_NAME to DigitalOcean App Platform..."

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl is not installed. Please install it first:"
    echo "   https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if user is authenticated
if ! doctl account get &> /dev/null; then
    echo "❌ Please authenticate with DigitalOcean first:"
    echo "   doctl auth init"
    exit 1
fi

       # Check if app exists
       if doctl apps list | grep -q "$APP_NAME"; then
           echo "📝 Updating existing app: $APP_NAME"
           APP_ID=$(doctl apps list --format ID,Name --no-header | grep "$APP_NAME" | awk '{print $1}')
           doctl apps update "$APP_ID" --spec do-app.yaml
           echo "✅ App updated successfully!"
       else
           echo "🆕 Creating new app: $APP_NAME"
           doctl apps create --spec do-app.yaml
           echo "✅ App created successfully!"
       fi
       
       echo ""
       echo "🔄 Waiting for app to be ready..."
       sleep 30
       
       # Get app info
       APP_ID=$(doctl apps list --format ID,Name --no-header | grep "$APP_NAME" | awk '{print $1}')
       APP_URL=$(doctl apps get "$APP_ID" --format URL --no-header)
       
       echo ""
       echo "🧪 Testing deployment..."
       python test_deployment.py "$APP_URL"

echo ""
echo "🌐 Your app should be available at:"
echo "   https://$APP_NAME-xxxxx.ondigitalocean.app"
echo ""
echo "📊 To monitor your app:"
echo "   doctl apps list"
echo "   doctl apps logs <APP_ID>"
