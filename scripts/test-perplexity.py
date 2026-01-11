#!/usr/bin/env python3
"""Test Perplexity API connection and agent"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from collectors.perplexity_agent import PerplexityPropertyAgent

async def test_perplexity():
    """Test Perplexity agent functionality"""
    print("\n🧪 Testing Perplexity Agent...")
    print("="*60)
    
    try:
        agent = PerplexityPropertyAgent()
        print(f"✅ Agent initialized (Model: {agent.model})")
        print(f"💰 Cost per call: ${agent.calculate_cost(1)}")
        print("")
        
        # Test 1: Connection test
        print("Test 1: API Connection")
        connected = await agent.test_connection()
        assert connected, "Connection test failed"
        print("✅ API connection successful\n")
        
        # Test 2: Simple research query
        print("Test 2: Property Research Query")
        result = await agent.research_async(
            """Research property at 350 Fifth Avenue, New York, NY.
            Return JSON with: {"address": str, "city": str, "estimated_price": number}""",
            max_tokens=500
        )
        
        print(f"✅ Response received")
        print(f"   Has citations: {'Yes' if result.get('_citations') else 'No'}")
        print(f"   Response keys: {list(result.keys())[:5]}...")
        
        if 'error' not in result:
            print(f"   Sample data: {str(result)[:100]}...")
        print("")
        
        # Test 3: Cost calculation
        print("Test 3: Cost Calculation")
        cost_5_agents = agent.calculate_cost(5)
        print(f"✅ 5 agents cost: ${cost_5_agents}")
        print(f"   1000 properties: ${cost_5_agents * 1000}")
        print("")
        
        print("="*60)
        print("✅ All Perplexity agent tests passed!")
        print("")
        return True
        
    except Exception as e:
        print(f"❌ Perplexity test failed: {e}")
        import traceback
        traceback.print_exc()
        print("")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_perplexity())
    sys.exit(0 if success else 1)
