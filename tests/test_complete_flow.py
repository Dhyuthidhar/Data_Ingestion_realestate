#!/usr/bin/env python3
"""
Complete end-to-end flow test
Tests the entire system from API request to database storage
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import requests
from database import Database
from cache import Cache

API_URL = "http://localhost:5001"

def test_complete_flow():
    """Test complete property research flow"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║         Complete System Flow Test                         ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Initialize
    db = Database()
    cache = Cache()
    
    # Test property
    test_property = {
        'address': '1600 Pennsylvania Avenue',
        'city': 'Washington',
        'state': 'DC'
    }
    
    cache_key = f"property:{test_property['address'].replace(' ', '_')}_{test_property['city'].replace(' ', '_')}_{test_property['state']}"
    
    # Clean up any existing data
    print("🧹 Cleaning up previous test data...")
    cache.delete(cache_key)
    print("")
    
    # Test 1: Fresh research (cache miss)
    print("="*60)
    print("Test 1: Fresh Research (Cache Miss)")
    print("="*60)
    
    start = time.time()
    response = requests.get(
        f"{API_URL}/api/property",
        params=test_property,
        timeout=180
    )
    elapsed = time.time() - start
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    assert data['status'] == 'success'
    assert data['source'] == 'fresh_research'
    
    print(f"✅ Fresh research completed")
    print(f"   Time: {elapsed:.1f}s")
    print(f"   Agents: {data['data']['metadata']['agents_successful']}/5")
    print(f"   Cost: ${data['cost_cents']/100}")
    print("")
    
    # Verify cache
    print("Verifying cache...")
    cached_data = cache.get(cache_key)
    assert cached_data is not None, "Data not cached"
    print("✅ Data cached successfully")
    print("")
    
    # Verify database
    print("Verifying database...")
    db_data = db.get_property(
        test_property['address'],
        test_property['city'],
        test_property['state']
    )
    assert db_data is not None, "Data not saved to database"
    print("✅ Data saved to database")
    print("")
    
    # Test 2: Cache hit
    print("="*60)
    print("Test 2: Cache Hit")
    print("="*60)
    
    start = time.time()
    response = requests.get(
        f"{API_URL}/api/property",
        params=test_property
    )
    elapsed = time.time() - start
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['source'] in ['cache', 'cache_after_wait']
    
    print(f"✅ Cache hit confirmed")
    print(f"   Time: {elapsed*1000:.0f}ms")
    print(f"   Cost: $0.00 (saved $0.025)")
    print("")
    
    # Test 3: Statistics
    print("="*60)
    print("Test 3: System Statistics")
    print("="*60)
    
    response = requests.get(f"{API_URL}/api/stats")
    assert response.status_code == 200
    stats = response.json()
    
    print(f"✅ Statistics retrieved")
    print(f"   Total properties: {stats['database']['total_properties']}")
    print(f"   Cache keys: {stats['cache']['keys_stored']}")
    print(f"   Hit rate: {stats['cache']['hit_rate_percent']}%")
    print(f"   Cost saved: ${stats['cost_analysis']['cost_saved']}")
    print("")
    
    # Test 4: Search
    print("="*60)
    print("Test 4: Property Search")
    print("="*60)
    
    response = requests.get(
        f"{API_URL}/api/property/search",
        params={'state': test_property['state'], 'limit': 10}
    )
    assert response.status_code == 200
    search_results = response.json()
    
    print(f"✅ Search completed")
    print(f"   Results: {search_results['count']} properties")
    print("")
    
    # Test 5: Force refresh
    print("="*60)
    print("Test 5: Force Refresh (Skip Cache)")
    print("="*60)
    
    start = time.time()
    response = requests.get(
        f"{API_URL}/api/property",
        params={**test_property, 'force_refresh': 'true'},
        timeout=180
    )
    elapsed = time.time() - start
    
    assert response.status_code == 200
    data = response.json()
    assert data['source'] == 'fresh_research'
    
    print(f"✅ Force refresh worked")
    print(f"   Time: {elapsed:.1f}s")
    print(f"   Cost: ${data['cost_cents']/100}")
    print("")
    
    # Cleanup
    db.close()
    cache.close()
    
    print("="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60)
    print("")
    print("📊 Summary:")
    print(f"   ✅ Fresh research: Working ({elapsed:.1f}s)")
    print(f"   ✅ Cache system: Working (instant)")
    print(f"   ✅ Database: Working")
    print(f"   ✅ Search: Working")
    print(f"   ✅ Force refresh: Working")
    print("")
    
    return True

if __name__ == "__main__":
    try:
        success = test_complete_flow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        print("")
        sys.exit(1)
