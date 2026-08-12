#!/bin/bash
# Build script for Render.com deployment

set -e

echo "🔨 HATSS Build Script for Render.com"
echo "===================================="

# Detect if this is frontend or backend build
if [ -f "frontend/package.json" ]; then
    echo "📦 Detected: Frontend + Backend project"
    
    # Build Frontend
    echo ""
    echo "🏗️  Building Frontend..."
    cd frontend
    npm install --production
    npm run build
    cd ..
    
    # Build Backend
    echo ""
    echo "🏗️  Building Backend..."
    cd backend
    pip install --upgrade pip
    pip install -e .
    pip install gunicorn
    cd ..
    
    echo ""
    echo "✅ Build completed successfully!"
    
elif [ -f "package.json" ]; then
    # Frontend-only build
    echo "📦 Detected: Frontend project"
    echo "🏗️  Building Frontend..."
    
    npm install --production
    npm run build
    
    echo ""
    echo "✅ Build completed successfully!"
    
elif [ -f "pyproject.toml" ]; then
    # Backend-only build
    echo "📦 Detected: Backend project"
    echo "🏗️  Building Backend..."
    
    pip install --upgrade pip
    pip install -e .
    pip install gunicorn
    
    echo ""
    echo "✅ Build completed successfully!"
    
else
    echo "❌ Error: Could not detect project type"
    exit 1
fi
