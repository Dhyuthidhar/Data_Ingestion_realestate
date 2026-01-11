#!/bin/bash
set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Property Agentic Engine - Production Startup          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Validate configuration
echo "⚙️  Validating configuration..."
python scripts/check-env.py
if [ $? -ne 0 ]; then
    exit 1
fi

# Check services
echo ""
echo "🔍 Checking services..."

# Check PostgreSQL
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running!"
    exit 1
fi
echo "✅ PostgreSQL: Running"

# Check Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running!"
    exit 1
fi
echo "✅ Redis: Running"

echo ""
echo "🚀 Starting API server..."
echo "   Host: ${FLASK_HOST:-0.0.0.0}"
echo "   Port: ${FLASK_PORT:-5001}"
echo "   Environment: ${ENVIRONMENT:-development}"
echo ""

# Start with gunicorn for production
if [ "$ENVIRONMENT" = "production" ]; then
    gunicorn -w 4 -b ${FLASK_HOST:-0.0.0.0}:${FLASK_PORT:-5001} api:app
else
    python api.py
fi
