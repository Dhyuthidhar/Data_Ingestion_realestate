#!/usr/bin/env python3

"""
Quick Manual Test Script for Property Agentic Engine
Run this to test specific addresses
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:5001"

# Test addresses
TEST_ADDRESSES = [
    {"address": "350 Fifth Avenue", "city": "New York", "state": "NY", "name": "Empire State Building"},
    {"address": "1 Apple Park Way", "city": "Cupertino", "state": "CA", "name": "Apple Park"},
    {"address": "1600 Pennsylvania Avenue", "city": "Washington", "state": "DC", "name": "White House"},
    {"address": "1 Microsoft Way", "city": "Redmond", "state": "WA", "name": "Microsoft HQ"},
    {"address": "1148 Greenbrook Drive", "city": "Danville", "state": "CA", "name": "Danville Property"},
]


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def check_api_health():
    """Check if API is running and healthy"""
    print_header("🏥 Checking API Health")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API is healthy!")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API!")
        print("\n💡 Make sure API server is running:")
        print("   cd /Users/sssd/Documents/data_ingres_realestate/property-agentic-engine")
        print("   source venv/bin/activate")
        print("   python api.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_single_address(address_data, force_refresh=False):
    """Test property research for a specific address"""
    
    name = address_data.get('name', 'Property')
    address = address_data['address']
    city = address_data['city']
    state = address_data['state']
    
    print_header(f"🏠 Testing: {name}")
    print(f"Address: {address}, {city}, {state}")
    
    # Build request
    params = {
        "address": address,
        "city": city,
        "state": state
    }
    
    if force_refresh:
        params["force_refresh"] = "true"
        print("⚡ Forcing fresh research (bypassing cache)...")
    
    # Make request
    print("\n⏳ Sending request to API...")
    print(f"   This will take 11-15 seconds for fresh research")
    print(f"   Or <100ms if cached")
    
    start_time = time.time()
    
    try:
        response = requests.get(f"{API_URL}/api/property", params=params, timeout=120)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Print results
            print(f"\n✅ SUCCESS!")
            print(f"\n📊 Summary:")
            print(f"   Response time: {elapsed:.2f} seconds")
            print(f"   Source: {data.get('source', 'unknown')}")
            print(f"   Cost: ${data.get('cost_cents', 0)/100:.2f}")
            
            # Get research data
            research = data.get('data', {}).get('research', {})
            metadata = research.get('_metadata', {})
            
            print(f"\n🤖 Agent Results:")
            print(f"   Successful agents: {metadata.get('agents_successful', 0)}/5")
            print(f"   Failed agents: {metadata.get('agents_failed', 0)}")
            print(f"   Total research time: {metadata.get('total_time_seconds', 0):.2f}s")
            print(f"   Cost: ${metadata.get('cost_cents', 0)/100:.2f}")
            
            # Check each agent
            print(f"\n📝 Data Available:")
            agents = {
                'property_basics': '🏡 Property Basics',
                'financial_analysis': '💰 Financial Analysis',
                'neighborhood': '🏘️  Neighborhood Info',
                'market_trends': '📈 Market Trends',
                'soft_signals': '🎯 Soft Signals'
            }
            
            for key, label in agents.items():
                if key in research:
                    status = research[key].get('agent_status', 'unknown')
                    emoji = '✅' if status == 'success' else '❌'
                    citations = len(research[key].get('citations', []))
                    print(f"   {emoji} {label}: {status} ({citations} citations)")
            
            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_result_{name.replace(' ', '_')}_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Full response saved to: {filename}")
            
            # Show sample data
            if 'property_basics' in research and research['property_basics'].get('agent_status') == 'success':
                basics_data = research['property_basics'].get('data', {})
                if basics_data:
                    print(f"\n📋 Sample Data (Property Basics):")
                    # Show first 500 chars
                    sample = str(basics_data)[:500]
                    print(f"   {sample}...")
            
            return True
            
        else:
            print(f"\n❌ FAILED!")
            print(f"   Status code: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n❌ REQUEST TIMEOUT!")
        print(f"   The request took longer than 120 seconds")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_cache_performance():
    """Test cache hit performance"""
    
    print_header("🚀 Testing Cache Performance")
    
    address = TEST_ADDRESSES[0]  # Use Empire State Building
    
    print("This test will:")
    print("1. Make first request (likely fresh research: ~11-15s)")
    print("2. Make second request (should hit cache: <100ms)")
    print("3. Compare performance\n")
    
    # First request
    print("━" * 70)
    print("1️⃣  FIRST REQUEST (Fresh or Cached)")
    print("━" * 70)
    time.sleep(1)
    result1 = test_single_address(address)
    
    if not result1:
        print("\n⚠️  First request failed, skipping cache test")
        return
    
    # Wait a bit
    print("\n⏸️  Waiting 3 seconds...")
    time.sleep(3)
    
    # Second request
    print("━" * 70)
    print("2️⃣  SECOND REQUEST (Should Hit Cache)")
    print("━" * 70)
    time.sleep(1)
    result2 = test_single_address(address)
    
    if result2:
        print("\n✅ Cache test complete!")
        print("   If second request was <100ms, cache is working perfectly!")


def test_multiple_addresses():
    """Test multiple addresses"""
    
    print_header("🏘️  Testing Multiple Addresses")
    print(f"Testing {len(TEST_ADDRESSES)} properties...\n")
    
    results = []
    
    for i, addr in enumerate(TEST_ADDRESSES, 1):
        print(f"\n{'━' * 70}")
        print(f"Property {i}/{len(TEST_ADDRESSES)}")
        print(f"{'━' * 70}")
        
        success = test_single_address(addr)
        results.append({
            'name': addr.get('name'),
            'success': success
        })
        
        # Brief pause between requests
        if i < len(TEST_ADDRESSES):
            print("\n⏸️  Waiting 2 seconds before next request...")
            time.sleep(2)
    
    # Summary
    print_header("📊 Test Summary")
    successful = sum(1 for r in results if r['success'])
    print(f"Total tests: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print(f"\nResults:")
    for r in results:
        emoji = '✅' if r['success'] else '❌'
        print(f"  {emoji} {r['name']}")


def interactive_test():
    """Interactive address testing"""
    
    print_header("🔍 Custom Address Test")
    
    print("Enter property details to research:\n")
    
    address = input("Street address: ").strip()
    city = input("City: ").strip()
    state = input("State (2 letters, e.g., NY): ").strip().upper()
    
    if not address or not city or not state:
        print("\n❌ All fields are required!")
        return
    
    if len(state) != 2:
        print("\n❌ State must be 2 letters (e.g., NY, CA)")
        return
    
    address_data = {
        "address": address,
        "city": city,
        "state": state,
        "name": f"{address}, {city}"
    }
    
    test_single_address(address_data)


def main():
    """Main menu"""
    
    print("\n" + "="*70)
    print("  🏠 Property Agentic Engine - Manual Testing Tool")
    print("="*70)
    print(f"\nAPI URL: {API_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check API health first
    if not check_api_health():
        print("\n⚠️  API is not available. Please start the API server first.")
        return
    
    # Main menu
    while True:
        print("\n" + "─"*70)
        print("Select test:")
        print("─"*70)
        print("1. Test Empire State Building (350 Fifth Ave, NY)")
        print("2. Test Danville Property (1148 Greenbrook Dr, CA)")
        print("3. Test multiple famous addresses")
        print("4. Test cache performance")
        print("5. Test custom address (your choice)")
        print("6. Test system status")
        print("7. View statistics")
        print("0. Exit")
        print("─"*70)
        
        choice = input("\nEnter choice (0-7): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        elif choice == "1":
            test_single_address(TEST_ADDRESSES[0])
        elif choice == "2":
            test_single_address(TEST_ADDRESSES[4])  # Danville property
        elif choice == "3":
            test_multiple_addresses()
        elif choice == "4":
            test_cache_performance()
        elif choice == "5":
            interactive_test()
        elif choice == "6":
            # Test system status
            print_header("📊 System Status")
            try:
                response = requests.get(f"{API_URL}/api/status", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(json.dumps(data, indent=2))
                else:
                    print(f"❌ Status code: {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")
        elif choice == "7":
            # View statistics
            print_header("📈 Statistics")
            try:
                response = requests.get(f"{API_URL}/api/stats", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(json.dumps(data, indent=2))
                else:
                    print(f"❌ Status code: {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ Invalid choice, please try again")
        
        # Ask to continue
        if choice != "0":
            print("\n" + "─"*70)
            cont = input("Press Enter to continue or 'q' to quit: ").strip().lower()
            if cont == 'q':
                print("\n👋 Goodbye!")
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
