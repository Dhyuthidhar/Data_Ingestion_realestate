#!/usr/bin/env python3
"""
Integration tests for database and cache layers
Tests the complete data flow
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import json
from database import Database
from cache import Cache
from config import settings

def test_integration():
    """Test database and cache integration"""
    print("\n🧪 Integration Tests")
    print("="*60)
    
    # Sample property data
    test_property = {
        'property': {
            'address': '123 Test Avenue',
            'city': 'San Francisco',
            'state': 'CA'
        },
        'research': {
            'property_basics': {'price': 1200000, 'bedrooms': 3},
            'financials': {'price_per_sqft': 800},
            'neighborhood': {'walk_score': 95},
            'market_trends': {'median_price': 1150000},
            'soft_signals': {'sentiment': 'positive'}
        },
        'metadata': {
            'research_time_seconds': 45.2,
            'agents_used': 5,
            'cost_cents': 25,
            'quality': 'high'
        }
    }
    
    try:
        # Initialize
        db = Database()
        cache = Cache()
        print("✅ Database and cache connected\n")
        
        # Test 1: Save to database
        print("Test 1: Save to database")
        success = db.save_property(test_property)
        assert success, "Database save failed"
        print("✅ Saved to database\n")
        
        # Test 2: Retrieve from database
        print("Test 2: Retrieve from database")
        retrieved = db.get_property(
            test_property['property']['address'],
            test_property['property']['city'],
            test_property['property']['state']
        )
        assert retrieved is not None, "Property not found"
        assert retrieved['address'] == test_property['property']['address']
        print(f"✅ Retrieved property ID: {retrieved['id']}\n")
        
        # Test 3: Cache the data
        print("Test 3: Cache property data")
        cache_key = "property:123_Test_Avenue_San_Francisco_CA"
        cache.set(cache_key, test_property, ttl=300)  # 5 min for test
        assert cache.exists(cache_key)
        print("✅ Cached with 5-minute TTL\n")
        
        # Test 4: Retrieve from cache
        print("Test 4: Retrieve from cache")
        cached_data = cache.get(cache_key)
        assert cached_data is not None
        assert cached_data['property']['address'] == test_property['property']['address']
        print("✅ Cache hit successful\n")
        
        # Test 5: Database stats
        print("Test 5: Database statistics")
        db_stats = db.get_stats()
        print(f"   Total properties: {db_stats.get('total_properties', 0)}")
        print(f"   Unique markets: {db_stats.get('unique_markets', 0)}")
        print(f"   Avg research time: {db_stats.get('avg_research_time_seconds', 0):.2f}s")
        print("✅ Stats retrieved\n")
        
        # Test 6: Cache stats
        print("Test 6: Cache statistics")
        cache_stats = cache.get_stats()
        print(f"   Keys stored: {cache_stats['keys']}")
        print(f"   Hit rate: {cache_stats['hit_rate']}%")
        print(f"   Total hits: {cache_stats['hits']}")
        print("✅ Cache stats retrieved\n")
        
        # Test 7: Search functionality
        print("Test 7: Search properties")
        results = db.search_properties(city='San Francisco', state='CA')
        assert len(results) > 0, "No results found"
        print(f"✅ Found {len(results)} properties\n")
        
        # Test 8: Recent properties
        print("Test 8: Recent properties")
        recent = db.get_recent_properties(hours=24)
        print(f"✅ Found {len(recent)} recent properties\n")
        
        # Test 9: Cache TTL check
        print("Test 9: Cache TTL")
        ttl = cache.get_ttl(cache_key)
        assert ttl > 0, "TTL should be positive"
        print(f"✅ TTL remaining: {ttl} seconds\n")
        
        # Test 10: Complete flow simulation
        print("Test 10: Simulate API flow")
        # 1. Check cache first
        cache_result = cache.get(cache_key)
        if cache_result:
            print("   → Cache HIT (would save $0.025)")
        else:
            print("   → Cache MISS (would trigger research)")
        
        # 2. If miss, would research and save
        # 3. Cache the result
        cache.set(cache_key, test_property, ttl=settings.CACHE_TTL)
        print("✅ Flow simulation complete\n")
        
        # Cleanup
        cache.delete(cache_key)
        print("🧹 Cleaned up test data")
        
        db.close()
        cache.close()
        
        print("="*60)
        print("✅ All integration tests passed!")
        print("")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        print("")
        return False

if __name__ == "__main__":
    # Check if services are configured
    try:
        settings.validate()
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("Please set up .env file with database and API keys\n")
        sys.exit(1)
    
    success = test_integration()
    sys.exit(0 if success else 1)
