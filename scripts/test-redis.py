#!/usr/bin/env python3
"""Test Redis connection and caching"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
from cache import Cache

def test_redis():
    """Test Redis caching functionality"""
    print("\n🧪 Testing Redis Cache...")
    print("="*60)
    
    try:
        cache = Cache()
        
        # Test 1: Basic connection
        print("✅ Redis connected")
        
        # Test 2: Ping
        assert cache.ping(), "Ping failed"
        print("✅ Ping successful")
        
        # Test 3: Set and Get
        test_key = "test:property:123"
        test_data = {
            "address": "123 Test St",
            "city": "Test City",
            "price": 500000
        }
        
        cache.set(test_key, test_data, ttl=60)
        retrieved = cache.get(test_key)
        assert retrieved == test_data, "Data mismatch"
        print("✅ Set/Get working")
        
        # Test 4: Exists
        assert cache.exists(test_key), "Key should exist"
        print("✅ Exists check working")
        
        # Test 5: TTL
        ttl = cache.get_ttl(test_key)
        assert 50 < ttl <= 60, f"TTL unexpected: {ttl}"
        print(f"✅ TTL working ({ttl} seconds remaining)")
        
        # Test 6: Delete
        cache.delete(test_key)
        assert not cache.exists(test_key), "Key should be deleted"
        print("✅ Delete working")
        
        # Test 7: Stats
        stats = cache.get_stats()
        print(f"✅ Stats: {stats['keys']} keys, {stats['hit_rate']}% hit rate")
        
        # Cleanup
        cache.close()
        
        print("="*60)
        print("✅ All Redis tests passed!")
        print("")
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        print("")
        return False

if __name__ == "__main__":
    success = test_redis()
    sys.exit(0 if success else 1)
