#!/usr/bin/env python3
"""Test database connection and schema"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from config import settings

def test_database():
    """Test database connection and schema"""
    print("\n🧪 Testing Database Connection...")
    print("="*60)
    
    try:
        # Connect
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        print(f"✅ Connected to: {settings.DB_NAME}")
        
        cur = conn.cursor()
        
        # Test 1: Check if properties table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'properties'
            );
        """)
        table_exists = cur.fetchone()[0]
        print(f"{'✅' if table_exists else '❌'} Properties table exists")
        
        # Test 2: Check indexes
        cur.execute("""
            SELECT COUNT(*) FROM pg_indexes 
            WHERE tablename = 'properties';
        """)
        index_count = cur.fetchone()[0]
        print(f"✅ Indexes created: {index_count}")
        
        # Test 3: Check view
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.views 
                WHERE table_name = 'property_stats'
            );
        """)
        view_exists = cur.fetchone()[0]
        print(f"{'✅' if view_exists else '❌'} property_stats view exists")
        
        # Test 4: Query stats view
        cur.execute("SELECT * FROM property_stats;")
        stats = cur.fetchone()
        print(f"✅ Current stats: {stats[0]} properties")
        
        cur.close()
        conn.close()
        
        print("="*60)
        print("✅ Database tests passed!")
        print("")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        print("")
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
