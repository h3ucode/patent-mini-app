#!/bin/bash
echo "🧹 Cleaning up Docker resources..."
docker-compose down -v
docker system prune -f

echo "🏗️  Rebuilding containers..."
docker-compose build --no-cache

echo "🚀 Starting services..."
docker-compose up -d