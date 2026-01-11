#!/bin/bash
set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Property Agentic Engine - Complete Setup              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Step 1: Install dependencies
echo "📦 Step 1: Installing dependencies..."
./scripts/install.sh
echo ""

# Step 2: Check configuration
echo "⚙️  Step 2: Checking configuration..."
python scripts/check-env.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Configuration invalid. Please update .env file"
    exit 1
fi
echo ""

# Step 3: Setup database
echo "🗄️  Step 3: Setting up PostgreSQL database..."
./scripts/setup-db.sh
echo ""

# Step 4: Test database
echo "🧪 Step 4: Testing database connection..."
python scripts/test-db.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Database test failed"
    exit 1
fi
echo ""

# Step 5: Test Redis
echo "🧪 Step 5: Testing Redis cache..."
python scripts/test-redis.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Redis test failed"
    exit 1
fi
echo ""

# Step 6: Run integration tests
echo "🧪 Step 6: Running integration tests..."
python tests/test_integration.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Integration tests failed"
    exit 1
fi
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 ✅ SETUP COMPLETE!                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 All systems ready!"
echo ""
echo "📊 System Status:"
echo "   ✅ Dependencies installed"
echo "   ✅ Configuration valid"
echo "   ✅ PostgreSQL database initialized"
echo "   ✅ Redis cache connected"
echo "   ✅ Integration tests passed"
echo ""
echo "🚀 Next Steps:"
echo "   1. Proceed to Task 3: Multi-Agent AI System"
echo "   2. Or test manually: python api.py"
echo ""
