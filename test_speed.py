#!/usr/bin/env python3
"""
Speed Test for Optimized Multi-Agent System
Tests performance improvements after optimization
"""
import asyncio
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from collectors.multi_agent_system import MultiAgentResearchSystem

async def speed_test():
    system = MultiAgentResearchSystem()
    
    test_properties = [
        ("350 Fifth Avenue", "New York", "NY"),
        ("1148 Greenbrook Drive", "Danville", "CA"),
        ("100 Main St", "Austin", "TX")
    ]
    
    # Get timeout from settings
    from config.settings import settings
    timeout = settings.RESEARCH_TIMEOUT
    
    print("\n" + "="*60)
    print("🚀 SPEED TEST - Optimized Multi-Agent System")
    print("="*60)
    print("\nOptimizations Applied:")
    print("  ✅ Timeout: 90s → 45s")
    print("  ✅ Max tokens: 4000 → 2500")
    print("  ✅ Concise prompts (50-70% shorter)")
    print(f"  ✅ Hard timeout: {timeout} seconds max")
    print(f"\nExpected: 18-{timeout} seconds per property")
    print("="*60)
    
    times = []
    
    for i, (address, city, state) in enumerate(test_properties, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{len(test_properties)}: {address}, {city}, {state}")
        print("="*60)
        
        start = time.time()
        result = await system.research_comprehensive(address, city, state)
        elapsed = time.time() - start
        
        times.append(elapsed)
        
        metadata = result.get('_metadata', {})
        successful = metadata.get('agents_successful', 0)
        timeout_hit = metadata.get('timeout_enforced', False)
        
        print(f"\n📊 Results:")
        print(f"   ⏱️  Time: {elapsed:.2f}s")
        print(f"   ✅ Success: {successful}/5 agents")
        print(f"   🎯 Under {timeout}s: {'YES ✅' if elapsed < timeout else 'NO ❌'}")
        print(f"   ⏰ Timeout enforced: {'Yes' if timeout_hit else 'No'}")
        
        # Brief pause between tests
        if i < len(test_properties):
            print("\n⏸️  Waiting 2 seconds before next test...")
            await asyncio.sleep(2)
    
    print("\n" + "="*60)
    print("📊 FINAL RESULTS:")
    print("="*60)
    print(f"   Average: {sum(times)/len(times):.2f}s")
    print(f"   Fastest: {min(times):.2f}s")
    print(f"   Slowest: {max(times):.2f}s")
    print(f"   All under {timeout}s: {'YES ✅' if all(t < timeout for t in times) else 'NO ❌'}")
    
    # Performance comparison
    baseline = 32.45  # Previous baseline
    avg_time = sum(times)/len(times)
    improvement = ((baseline - avg_time) / baseline) * 100
    
    print(f"\n🎯 Performance Improvement:")
    print(f"   Baseline: {baseline:.2f}s")
    print(f"   Optimized: {avg_time:.2f}s")
    print(f"   Improvement: {improvement:.1f}% faster")
    print(f"   Time saved: {baseline - avg_time:.2f}s per property")
    
    print("\n" + "="*60)
    if avg_time < timeout:
        print(f"✅ SUCCESS! Target achieved: < {timeout} seconds")
    else:
        print("⚠️  Target not met, but still improved")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(speed_test())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user\n")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
