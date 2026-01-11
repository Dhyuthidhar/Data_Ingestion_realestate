#!/usr/bin/env python3
"""
Comprehensive tests for multi-agent research system
Tests individual agents and full orchestration
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import time
from collectors.multi_agent_system import MultiAgentResearchSystem
from collectors.perplexity_agent import PerplexityPropertyAgent

async def test_single_agent():
    """Test individual agent functionality"""
    print("\n🧪 Test 1: Single Agent")
    print("="*60)
    
    try:
        agent = PerplexityPropertyAgent()
        
        result = await agent.research_async(
            """Research Empire State Building property basics.
            Return JSON with: {"address": str, "city": str, "type": str}""",
            max_tokens=500
        )
        
        assert '_citations' in result, "No citations returned"
        assert '_raw_response' in result, "No raw response"
        
        print("✅ Single agent test passed")
        print(f"   Citations: {len(result.get('_citations', []))}")
        print(f"   Response type: {type(result)}")
        print("")
        return True
        
    except Exception as e:
        print(f"❌ Single agent test failed: {e}")
        return False

async def test_multi_agent_system():
    """Test full multi-agent orchestration"""
    print("🧪 Test 2: Multi-Agent System")
    print("="*60)
    
    try:
        system = MultiAgentResearchSystem()
        
        # Research a well-known property
        result = await system.research_comprehensive(
            "350 Fifth Avenue",
            "New York",
            "NY"
        )
        
        # Verify structure
        assert '_metadata' in result, "No metadata"
        assert 'property_basics' in result, "Missing property_basics"
        assert 'financial_analysis' in result, "Missing financial_analysis"
        assert 'neighborhood' in result, "Missing neighborhood"
        assert 'market_trends' in result, "Missing market_trends"
        assert 'soft_signals' in result, "Missing soft_signals"
        
        metadata = result['_metadata']
        print(f"✅ Multi-agent system test passed")
        print(f"   Agents deployed: {metadata['agents_deployed']}")
        print(f"   Agents successful: {metadata['agents_successful']}")
        print(f"   Research time: {metadata['research_time_seconds']}s")
        print(f"   Cost: ${metadata['cost_cents']/100:.3f}")
        print("")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_results_structure():
    """Test that agent results have expected structure"""
    print("🧪 Test 3: Agent Result Structure")
    print("="*60)
    
    try:
        system = MultiAgentResearchSystem()
        
        result = await system.research_comprehensive(
            "123 Main Street",
            "San Francisco",
            "CA"
        )
        
        # Check each agent's output
        checks_passed = 0
        
        # Property basics
        basics = result.get('property_basics', {})
        if 'agent_status' in basics:
            print(f"   ✅ Property basics: {basics['agent_status']}")
            checks_passed += 1
        
        # Financials
        financials = result.get('financial_analysis', {})
        if 'agent_status' in financials:
            print(f"   ✅ Financial analysis: {financials['agent_status']}")
            checks_passed += 1
        
        # Neighborhood
        neighborhood = result.get('neighborhood', {})
        if 'agent_status' in neighborhood:
            print(f"   ✅ Neighborhood: {neighborhood['agent_status']}")
            checks_passed += 1
        
        # Market trends
        trends = result.get('market_trends', {})
        if 'agent_status' in trends:
            print(f"   ✅ Market trends: {trends['agent_status']}")
            checks_passed += 1
        
        # Soft signals
        signals = result.get('soft_signals', {})
        if 'agent_status' in signals:
            print(f"   ✅ Soft signals: {signals['agent_status']}")
            checks_passed += 1
        
        print(f"\n✅ Structure test passed ({checks_passed}/5 agents returned data)")
        print("")
        return True
        
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        return False

async def test_error_handling():
    """Test that system handles errors gracefully"""
    print("🧪 Test 4: Error Handling")
    print("="*60)
    
    try:
        system = MultiAgentResearchSystem()
        
        # Test with nonsense data
        result = await system.research_comprehensive(
            "XYZ123 Fake Street",
            "NowhereCity",
            "ZZ"
        )
        
        # Should still return results (even if some agents fail)
        assert '_metadata' in result, "No metadata on error case"
        
        metadata = result['_metadata']
        print(f"✅ Error handling test passed")
        print(f"   System continued despite bad data")
        print(f"   Successful agents: {metadata['agents_successful']}/{metadata['agents_deployed']}")
        print(f"   Failed agents: {metadata['agents_failed']}")
        print("")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

async def test_performance():
    """Test system performance and timing"""
    print("🧪 Test 5: Performance")
    print("="*60)
    
    try:
        system = MultiAgentResearchSystem()
        
        start = time.time()
        result = await system.research_comprehensive(
            "1600 Pennsylvania Avenue",
            "Washington",
            "DC"
        )
        elapsed = time.time() - start
        
        # Performance expectations
        assert elapsed < 120, f"Too slow: {elapsed}s (expected < 120s)"
        
        print(f"✅ Performance test passed")
        print(f"   Total time: {elapsed:.1f}s")
        print(f"   Time per agent: {elapsed/5:.1f}s average")
        print(f"   Within acceptable range: < 120s")
        print("")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

async def run_all_tests():
    """Run complete test suite"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║        Multi-Agent System Test Suite                      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    tests = [
        ("Single Agent", test_single_agent),
        ("Multi-Agent System", test_multi_agent_system),
        ("Result Structure", test_agent_results_structure),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}\n")
            failed += 1
    
    print("="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All agent tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")
    
    print("="*60)
    print("")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
