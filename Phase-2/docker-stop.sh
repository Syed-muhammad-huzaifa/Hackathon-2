#!/bin/bash
set -e

echo "🛑 Stopping TaskFlow services..."

docker-compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "To remove volumes (⚠️  deletes database data):"
echo "  docker-compose down -v"
