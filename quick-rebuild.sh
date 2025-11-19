#!/bin/bash
# Quick rebuild (uses cache) - faster for incremental changes

set -e

echo "⚡ Quick rebuild using cache..."

# Rebuild with cache
docker compose -f docker-compose.prod.yml build backend frontend

# Restart services
echo "🔄 Restarting services..."
docker compose -f docker-compose.prod.yml up -d --force-recreate

echo ""
echo "✅ Services restarted!"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "📝 Tailing logs (Ctrl+C to stop)..."
docker compose -f docker-compose.prod.yml logs -f --tail=50
