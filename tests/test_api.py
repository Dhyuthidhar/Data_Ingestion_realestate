#!/usr/bin/env python3
"""
Comprehensive API tests
Tests complete request/response flow
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import time

API_URL = "http://localhost:5001"

def test_health():
    """Test health endpoint"""
    print("\n🧪 Test 1: Health Check")
    print("="*60)
    
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert data['status'] == 'healthy', "Service not healthy"
    
    print("✅ Health check passed")
    print(f"   Service: {data['service']}")
    print(f"   Version: {data['version']}")

def test_status():
    """Test status endpoint"""
    print("\n🧪 Test 2: System Status")
    print("="*60)
    
    response = requests.get(f"{API_URL}/api/status")
    assert response.status_code == 200
    
    data = response.json()
    assert data['status'] == 'operational'
    assert data['systems']['database'] == 'healthy'
    assert data['systems']['cache'] == 'healthy'
    
    print("✅ Status check passed")
    print(f"   Database: {data['systems']['database']}")
    print(f"   Cache: {data['systems']['cache']}")
    print(f"   Max agents: {data['configuration']['max_agents']}")

def test_stats():
    """Test stats endpoint"""
    print("\n🧪 Test 3: Statistics")
    print("="*60)
    
    response = requests.get(f"{API_URL}/api/stats")
    assert response.status_code == 200
    
    data = response.json()
    print("✅ Statistics retrieved")
    print(f"   Properties: {data['database']['total_properties']}")
    print(f"   Cache hit rate: {data['cache']['hit_rate_percent']}%")
    print(f"   Cost saved: ${data['cost_analysis']['cost_saved']}")

def test_property_research():
    """Test property research endpoint"""
    print("\n🧪 Test 4: Property Research (Real API Call)")
    print("="*60)
    print("⚠️  This will cost $0.025 and take ~15 seconds")
    
    # Test property
    params = {
        'address': '350 Fifth Avenue',
        'city': 'New York',
        'state': 'NY'
    }
    
    print(f"Researching: {params['address']}, {params['city']}, {params['state']}")
    
    start = time.time()
    response = requests.get(f"{API_URL}/api/property", params=params, timeout=180)
    elapsed = time.time() - start
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert data['status'] == 'success'
    
    print(f"✅ Property research completed")
    print(f"   Source: {data['source']}")
    print(f"   Time: {elapsed:.1f}s")
    
    if data['source'] == 'fresh_research':
        print(f"   Agents successful: {data['data']['metadata']['agents_successful']}/5")
        print(f"   Cost: ${data['cost_cents']/100}")
    else:
        print(f"   Cache age: {data.get('cache_age_hours', 0):.1f} hours")
        print(f"   Cost: $0.00 (cached)")

def test_property_cache():
    """Test that second request hits cache"""
    print("\n🧪 Test 5: Cache Hit")
    print("="*60)
    
    params = {
        'address': '350 Fifth Avenue',
        'city': 'New York',
        'state': 'NY'
    }
    
    start = time.time()
    response = requests.get(f"{API_URL}/api/property", params=params)
    elapsed = time.time() - start
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['source'] in ['cache', 'cache_after_wait'], f"Expected cache hit, got {data['source']}"
    
    print(f"✅ Cache hit confirmed")
    print(f"   Response time: {elapsed*1000:.0f}ms")
    print(f"   Cost: $0.00 (saved $0.025)")

def test_search():
    """Test search endpoint"""
    print("\n🧪 Test 6: Property Search")
    print("="*60)
    
    response = requests.get(f"{API_URL}/api/property/search?city=New York&state=NY&limit=10")
    assert response.status_code == 200
    
    data = response.json()
    print(f"✅ Search completed")
    print(f"   Results: {data['count']} properties")

def run_all_tests():
    """Run complete test suite"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║          API Integration Test Suite                       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    tests = [
        ("Health Check", test_health),
        ("System Status", test_status),
        ("Statistics", test_stats),
        ("Property Research", test_property_research),
        ("Cache Hit", test_property_cache),
        ("Property Search", test_search)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All API tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")
    
    print("="*60 + "\n")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}\n")
        sys.exit(1)
