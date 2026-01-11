#!/bin/bash
set -e

echo "🗄️  Setting up PostgreSQL database..."
echo ""

DB_NAME="property_agentic_db"
DB_USER=${DB_USER:-$(whoami)}

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running!"
    echo "Start it with: brew services start postgresql  # Mac"
    echo "             or: sudo systemctl start postgresql  # Linux"
    exit 1
fi

echo "✅ PostgreSQL is running"
echo ""

# Check if database exists
if psql -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "⚠️  Database '$DB_NAME' already exists"
    read -p "Drop and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Dropping existing database..."
        dropdb -U $DB_USER $DB_NAME
    else
        echo "Using existing database..."
    fi
fi

# Create database if it doesn't exist
if ! psql -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "📦 Creating database: $DB_NAME"
    createdb -U $DB_USER $DB_NAME
fi

echo ""
echo "📋 Initializing schema..."
psql -U $DB_USER -d $DB_NAME -f init_db.sql

echo ""
echo "✅ Database setup complete!"
echo ""
echo "📊 Database Information:"
echo "   Name: $DB_NAME"
echo "   User: $DB_USER"
echo "   Tables: properties"
echo "   Indexes: 6 indexes created"
echo "   Views: property_stats"
echo ""
echo "🧪 Test connection:"
echo "   psql -U $DB_USER -d $DB_NAME -c 'SELECT * FROM property_stats;'"
