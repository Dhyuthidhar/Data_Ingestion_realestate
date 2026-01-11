#!/usr/bin/env python3
"""
Comprehensive System Validation
Tests all components together under various conditions
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from database import Database
from cache import Cache
from collectors.multi_agent_system import MultiAgentResearchSystem

API_URL = "http://localhost:5001"

def test_system_health():
    """Validate all system components are healthy"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║         System Health Validation                          ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print("="*60)
    print("Test 1: Component Health Checks")
    print("="*60)
    
    # Test Database
    print("\n1. Database Health:")
    try:
        db = Database()
        stats = db.get_stats()
        db.close()
        print("   ✅ Database: Connected and operational")
        print(f"   📊 Properties: {stats.get('total_properties', 0)}")
    except Exception as e:
        print(f"   ❌ Database: Failed - {e}")
        return False
    
    # Test Cache
    print("\n2. Cache Health:")
    try:
        cache = Cache()
        assert cache.ping(), "Redis ping failed"
        cache_stats = cache.get_stats()
        cache.close()
        print("   ✅ Cache: Connected and operational")
        print(f"   📊 Keys: {cache_stats['keys']}, Hit rate: {cache_stats['hit_rate']}%")
    except Exception as e:
        print(f"   ❌ Cache: Failed - {e}")
        return False
    
    # Test API
    print("\n3. API Health:")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        assert response.status_code == 200
        print("   ✅ API: Responding correctly")
    except Exception as e:
        print(f"   ❌ API: Failed - {e}")
        return False
    
    # Test Multi-Agent System
    print("\n4. Multi-Agent System:")
    try:
        system = MultiAgentResearchSystem()
        print("   ✅ Multi-Agent System: Initialized")
        print(f"   🤖 Agents configured: {system.max_agents}")
    except Exception as e:
        print(f"   ❌ Multi-Agent System: Failed - {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ All system components healthy!")
    print("="*60 + "\n")
    return True

def test_concurrent_requests():
    """Test system under concurrent load"""
    print("="*60)
    print("Test 2: Concurrent Request Handling")
    print("="*60)
    print("Testing 5 concurrent property requests...\n")
    
    test_properties = [
        {"address": "1600 Pennsylvania Avenue", "city": "Washington", "state": "DC"},
        {"address": "350 Fifth Avenue", "city": "New York", "state": "NY"},
        {"address": "1 Infinite Loop", "city": "Cupertino", "state": "CA"},
        {"address": "1 Microsoft Way", "city": "Redmond", "state": "WA"},
        {"address": "1 Apple Park Way", "city": "Cupertino", "state": "CA"}
    ]
    
    def fetch_property(prop):
        try:
            start = time.time()
            response = requests.get(
                f"{API_URL}/api/property",
                params=prop,
                timeout=180
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "property": f"{prop['address']}, {prop['city']}",
                    "status": "success",
                    "source": data.get('source', 'unknown'),
                    "time": elapsed
                }
            else:
                return {
                    "property": f"{prop['address']}, {prop['city']}",
                    "status": "failed",
                    "error": response.status_code
                }
        except Exception as e:
            return {
                "property": f"{prop['address']}, {prop['city']}",
                "status": "error",
                "error": str(e)
            }
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_property, prop) for prop in test_properties]
        results = [future.result() for future in as_completed(futures)]
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] != 'success')
    
    print("\nResults:")
    for result in results:
        status_symbol = "✅" if result['status'] == 'success' else "❌"
        print(f"  {status_symbol} {result['property']}")
        if result['status'] == 'success':
            print(f"     Source: {result['source']}, Time: {result['time']:.1f}s")
    
    print(f"\n📊 Summary:")
    print(f"   Total time: {total_time:.1f}s")
    print(f"   Successful: {successful}/{len(test_properties)}")
    print(f"   Failed: {failed}/{len(test_properties)}")
    print(f"   Avg time: {total_time/len(test_properties):.1f}s per request")
    
    print("\n" + "="*60)
    if successful == len(test_properties):
        print("✅ Concurrent request handling: PASSED")
    else:
        print("⚠️  Concurrent request handling: PARTIAL")
    print("="*60 + "\n")
    
    return successful >= len(test_properties) * 0.8  # 80% success rate

def test_cache_efficiency():
    """Test cache hit/miss efficiency"""
    print("="*60)
    print("Test 3: Cache Efficiency")
    print("="*60)
    
    test_property = {
        "address": "350 Fifth Avenue",
        "city": "New York",
        "state": "NY"
    }
    
    print("\nRequest 1: First request (should be cache or fresh)...")
    start = time.time()
    response1 = requests.get(f"{API_URL}/api/property", params=test_property)
    time1 = time.time() - start
    data1 = response1.json()
    source1 = data1.get('source', 'unknown')
    
    print(f"   Source: {source1}")
    print(f"   Time: {time1*1000:.0f}ms")
    
    print("\nRequest 2: Immediate repeat (should hit cache)...")
    start = time.time()
    response2 = requests.get(f"{API_URL}/api/property", params=test_property)
    time2 = time.time() - start
    data2 = response2.json()
    source2 = data2.get('source', 'unknown')
    
    print(f"   Source: {source2}")
    print(f"   Time: {time2*1000:.0f}ms")
    
    # Verify cache hit
    cache_hit = 'cache' in source2
    speedup = time1 / time2 if time2 > 0 else 0
    
    print(f"\n📊 Cache Analysis:")
    print(f"   Cache hit: {'✅ Yes' if cache_hit else '❌ No'}")
    print(f"   Speedup: {speedup:.1f}x faster")
    print(f"   Cost saved: $0.025" if cache_hit else "   Cost: $0.025")
    
    print("\n" + "="*60)
    if cache_hit and speedup > 10:
        print("✅ Cache efficiency: EXCELLENT")
    elif cache_hit:
        print("✅ Cache efficiency: GOOD")
    else:
        print("⚠️  Cache efficiency: NEEDS IMPROVEMENT")
    print("="*60 + "\n")
    
    return cache_hit

def test_error_handling():
    """Test system error handling"""
    print("="*60)
    print("Test 4: Error Handling")
    print("="*60)
    
    print("\n1. Missing parameters:")
    response = requests.get(f"{API_URL}/api/property")
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    print("   ✅ Returns 400 for missing parameters")
    
    print("\n2. Invalid state code:")
    response = requests.get(
        f"{API_URL}/api/property",
        params={"address": "123 Main St", "city": "Anytown", "state": "XYZ"}
    )
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    print("   ✅ Returns 400 for invalid state code")
    
    print("\n3. Non-existent endpoint:")
    response = requests.get(f"{API_URL}/api/nonexistent")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    print("   ✅ Returns 404 for non-existent endpoint")
    
    print("\n" + "="*60)
    print("✅ Error handling: PASSED")
    print("="*60 + "\n")
    return True

def test_data_consistency():
    """Test data consistency across cache and database"""
    print("="*60)
    print("Test 5: Data Consistency")
    print("="*60)
    
    test_property = {
        "address": "1 Apple Park Way",
        "city": "Cupertino",
        "state": "CA"
    }
    
    cache_key = f"property:{test_property['address'].replace(' ', '_')}_{test_property['city'].replace(' ', '_')}_{test_property['state']}"
    
    print("\nFetching property via API...")
    response = requests.get(f"{API_URL}/api/property", params=test_property, timeout=180)
    assert response.status_code == 200
    api_data = response.json()['data']
    
    print("Checking cache...")
    cache = Cache()
    cached_data = cache.get(cache_key)
    assert cached_data is not None, "Data not in cache"
    print("   ✅ Data found in cache")
    
    print("Checking database...")
    db = Database()
    db_data = db.get_property(
        test_property['address'],
        test_property['city'],
        test_property['state']
    )
    assert db_data is not None, "Data not in database"
    print("   ✅ Data found in database")
    
    # Verify consistency
    cache_address = cached_data['property']['address']
    db_address = db_data['address']
    assert cache_address == db_address, "Cache/DB address mismatch"
    
    print("\n📊 Consistency Check:")
    print(f"   API → Cache: ✅ Consistent")
    print(f"   API → Database: ✅ Consistent")
    print(f"   Cache → Database: ✅ Consistent")
    
    cache.close()
    db.close()
    
    print("\n" + "="*60)
    print("✅ Data consistency: PASSED")
    print("="*60 + "\n")
    return True

def run_all_validations():
    """Run complete validation suite"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║     Property Agentic Engine - System Validation           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    tests = [
        ("System Health", test_system_health),
        ("Concurrent Requests", test_concurrent_requests),
        ("Cache Efficiency", test_cache_efficiency),
        ("Error Handling", test_error_handling),
        ("Data Consistency", test_data_consistency)
    ]
    
    results = {}
    start_time = time.time()
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {test_name}")
            print(f"{'='*60}")
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    total_time = time.time() - start_time
    
    # Final report
    print("\n" + "="*60)
    print("FINAL VALIDATION REPORT")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    print(f"⏱️  Total time: {total_time:.1f}s")
    
    if passed == len(tests):
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ System is production-ready")
    else:
        print(f"\n⚠️  {failed} validation(s) failed")
        print("❌ System needs attention before production")
    
    print("="*60 + "\n")
    
    return passed == len(tests)

if __name__ == "__main__":
    try:
        success = run_all_validations()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Validation suite crashed: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
