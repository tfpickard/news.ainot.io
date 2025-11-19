#!/bin/bash
# Rebuild and restart production containers

set -e

echo "🔨 Rebuilding production containers..."

# Stop containers
echo "⏸️  Stopping containers..."
docker compose -f docker-compose.prod.yml down

# Rebuild without cache to ensure all dependencies are fresh
echo "🏗️  Building backend (this may take a few minutes)..."
docker compose -f docker-compose.prod.yml build --no-cache backend

echo "🏗️  Building frontend (this may take a few minutes)..."
docker compose -f docker-compose.prod.yml build --no-cache frontend

# Start everything
echo "🚀 Starting containers..."
docker compose -f docker-compose.prod.yml up -d

# Show logs
echo ""
echo "✅ Containers rebuilt and started!"
echo ""
echo "📊 Container status:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "📝 Following logs (Ctrl+C to stop viewing)..."
docker compose -f docker-compose.prod.yml logs -f
