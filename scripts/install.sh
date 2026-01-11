#!/bin/bash
set -e

echo "📦 Installing dependencies for property-agentic-engine..."
echo ""

# Check if venv is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

echo ""
echo "📥 Installing production dependencies..."
pip install -r requirements.txt

echo ""
echo "🛠️  Installing development dependencies..."
pip install -r requirements-dev.txt

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "📊 Installed packages:"
pip list | grep -E "flask|redis|psycopg2|aiohttp|pytest"
