"""
Test script for new accessibility-based agent architecture
Tests 5 agents: property_records_ownership, property_details_market, 
neighborhood_location, financial_inference_estimates, economic_growth_signals
"""
import asyncio
import json
from collectors.multi_agent_system import MultiAgentResearchSystem

async def test_new_agent_architecture():
    """Test the new 5-agent architecture with data accessibility separation"""
    system = MultiAgentResearchSystem()
    
    print("=" * 80)
    print("🧪 TESTING NEW 5-AGENT ARCHITECTURE")
    print("=" * 80)
    print("\n📋 Architecture Overview:")
    print("  Tier 1 - HIGH CONFIDENCE PUBLIC DATA (90-95% success):")
    print("    • Agent 1: property_records_ownership")
    print("    • Agent 2: property_details_market")
    print("    • Agent 3: neighborhood_location")
    print("\n  Tier 2 - ESTIMATES & INFERENCE (60-70% success):")
    print("    • Agent 4: financial_inference_estimates")
    print("    • Agent 5: economic_growth_signals")
    print("\n" + "=" * 80)
    
    # Test property
    test_address = '1148 Greenbrook Drive'
    test_city = 'Danville'
    test_state = 'CA'
    
    print(f"\n🏠 Test Property: {test_address}, {test_city}, {test_state}")
    print("=" * 80)
    
    # Run comprehensive research
    result = await system.research_comprehensive(
        test_address,
        test_city,
        test_state
    )
    
    # Display results by tier
    print("\n" + "=" * 80)
    print("📊 TIER 1: HIGH CONFIDENCE PUBLIC DATA")
    print("=" * 80)
    
    tier1_agents = ['property_records_ownership', 'property_details_market', 'neighborhood_location']
    
    for agent_name in tier1_agents:
        if agent_name in result:
            agent_data = result[agent_name]
            print(f"\n{'─' * 80}")
            print(f"🔍 {agent_name.upper().replace('_', ' ')}")
            print(f"{'─' * 80}")
            
            # Status
            status = agent_data.get('agent_status', 'unknown')
            status_icon = '✅' if status == 'success' else '❌'
            print(f"{status_icon} Status: {status}")
            
            if status == 'success':
                # Parse method
                parse_method = agent_data.get('parse_method', 'unknown')
                print(f"📝 Parse Method: {parse_method}")
                
                # Citations
                citation_count = agent_data.get('citation_count', 0)
                print(f"📚 Citations: {citation_count}")
                
                # Confidence
                confidence = agent_data.get('confidence', 'UNKNOWN')
                print(f"🎯 Confidence: {confidence}")
                
                # Structured data
                if 'structured_data' in agent_data and agent_data['structured_data']:
                    print(f"\n📋 Structured Data Extracted:")
                    for key, value in agent_data['structured_data'].items():
                        if key != 'confidence':
                            print(f"  • {key}: {value}")
                else:
                    print(f"\n⚠️  No structured data extracted")
                
                # Show snippet of detailed analysis
                if 'detailed_analysis' in agent_data and agent_data['detailed_analysis']:
                    analysis = agent_data['detailed_analysis']
                    snippet = analysis[:200] + "..." if len(analysis) > 200 else analysis
                    print(f"\n💬 Analysis Preview:")
                    print(f"  {snippet}")
            else:
                error = agent_data.get('error', 'Unknown error')
                print(f"❌ Error: {error}")
    
    print("\n" + "=" * 80)
    print("📈 TIER 2: ESTIMATES & INFERENCE")
    print("=" * 80)
    print("⚠️  NOTE: These are ESTIMATES, not actual data")
    print("=" * 80)
    
    tier2_agents = ['financial_inference_estimates', 'economic_growth_signals']
    
    for agent_name in tier2_agents:
        if agent_name in result:
            agent_data = result[agent_name]
            print(f"\n{'─' * 80}")
            print(f"📊 {agent_name.upper().replace('_', ' ')}")
            print(f"{'─' * 80}")
            
            # Status
            status = agent_data.get('agent_status', 'unknown')
            status_icon = '✅' if status == 'success' else '❌'
            print(f"{status_icon} Status: {status}")
            
            if status == 'success':
                # Parse method
                parse_method = agent_data.get('parse_method', 'unknown')
                print(f"📝 Parse Method: {parse_method}")
                
                # Citations
                citation_count = agent_data.get('citation_count', 0)
                print(f"📚 Citations: {citation_count}")
                
                # Confidence
                confidence = agent_data.get('confidence', 'UNKNOWN')
                print(f"🎯 Confidence: {confidence} (ESTIMATES)")
                
                # Structured data
                if 'structured_data' in agent_data and agent_data['structured_data']:
                    print(f"\n📋 Estimated Data:")
                    for key, value in agent_data['structured_data'].items():
                        if key != 'confidence':
                            print(f"  • {key}: {value} [ESTIMATED]")
                else:
                    print(f"\n⚠️  No estimates extracted")
                
                # Show snippet of detailed analysis
                if 'detailed_analysis' in agent_data and agent_data['detailed_analysis']:
                    analysis = agent_data['detailed_analysis']
                    snippet = analysis[:200] + "..." if len(analysis) > 200 else analysis
                    print(f"\n💬 Analysis Preview:")
                    print(f"  {snippet}")
            else:
                error = agent_data.get('error', 'Unknown error')
                print(f"❌ Error: {error}")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("📊 SUMMARY STATISTICS")
    print("=" * 80)
    
    metadata = result.get('_metadata', {})
    
    print(f"\n⏱️  Performance:")
    print(f"  • Total Time: {metadata.get('research_time_seconds', 0):.1f}s")
    print(f"  • Timeout Enforced: {metadata.get('timeout_enforced', False)}")
    
    print(f"\n💰 Cost:")
    print(f"  • Total Cost: ${metadata.get('cost_cents', 0) / 100:.3f}")
    print(f"  • Cost per Agent: ${metadata.get('cost_cents', 0) / 100 / 5:.4f}")
    
    print(f"\n✅ Success Rates:")
    total_agents = metadata.get('total_agents', 5)
    successful = metadata.get('agents_successful', 0)
    failed = metadata.get('agents_failed', 0)
    print(f"  • Total Agents: {total_agents}")
    print(f"  • Successful: {successful} ({successful/total_agents*100:.0f}%)")
    print(f"  • Failed: {failed} ({failed/total_agents*100:.0f}%)")
    
    # Tier-specific success rates
    tier1_success = sum(1 for name in tier1_agents if result.get(name, {}).get('agent_status') == 'success')
    tier2_success = sum(1 for name in tier2_agents if result.get(name, {}).get('agent_status') == 'success')
    
    print(f"\n📊 By Tier:")
    print(f"  • Tier 1 (High Confidence): {tier1_success}/3 ({tier1_success/3*100:.0f}%)")
    print(f"  • Tier 2 (Estimates): {tier2_success}/2 ({tier2_success/2*100:.0f}%)")
    
    # Citation statistics
    total_citations = sum(result.get(name, {}).get('citation_count', 0) for name in tier1_agents + tier2_agents)
    tier1_citations = sum(result.get(name, {}).get('citation_count', 0) for name in tier1_agents)
    tier2_citations = sum(result.get(name, {}).get('citation_count', 0) for name in tier2_agents)
    
    print(f"\n📚 Citations:")
    print(f"  • Total Citations: {total_citations}")
    print(f"  • Tier 1 Citations: {tier1_citations}")
    print(f"  • Tier 2 Citations: {tier2_citations}")
    print(f"  • Average per Agent: {total_citations/total_agents:.1f}")
    
    # Data extraction statistics
    print(f"\n📋 Data Extraction:")
    for agent_name in tier1_agents + tier2_agents:
        if agent_name in result and result[agent_name].get('agent_status') == 'success':
            structured_count = len(result[agent_name].get('structured_data', {}))
            parse_method = result[agent_name].get('parse_method', 'unknown')
            print(f"  • {agent_name}: {structured_count} fields ({parse_method})")
    
    print("\n" + "=" * 80)
    print("🎯 ARCHITECTURE VALIDATION")
    print("=" * 80)
    
    # Validate expected improvements
    print(f"\n✅ Expected Outcomes:")
    print(f"  • Tier 1 agents (90-95% success): {'✅ PASS' if tier1_success >= 2 else '❌ FAIL'} ({tier1_success}/3)")
    print(f"  • Tier 2 agents (60-70% success): {'✅ PASS' if tier2_success >= 1 else '❌ FAIL'} ({tier2_success}/2)")
    print(f"  • Total time < 60s: {'✅ PASS' if metadata.get('research_time_seconds', 999) < 60 else '❌ FAIL'}")
    print(f"  • Cost = $0.025: {'✅ PASS' if abs(metadata.get('cost_cents', 0) - 2.5) < 0.1 else '❌ FAIL'}")
    print(f"  • Total citations > 15: {'✅ PASS' if total_citations > 15 else '❌ FAIL'} ({total_citations})")
    
    # Overall assessment
    overall_pass = (
        tier1_success >= 2 and
        tier2_success >= 1 and
        metadata.get('research_time_seconds', 999) < 60 and
        total_citations > 15
    )
    
    print(f"\n{'=' * 80}")
    if overall_pass:
        print("🎉 ARCHITECTURE REFACTOR: ✅ SUCCESS")
        print("New accessibility-based agent system is working as expected!")
    else:
        print("⚠️  ARCHITECTURE REFACTOR: NEEDS REVIEW")
        print("Some agents may need prompt or extraction pattern adjustments.")
    print("=" * 80)
    
    # Save full results to JSON
    output_file = 'test_new_agents_results.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n💾 Full results saved to: {output_file}")
    
    return result

if __name__ == "__main__":
    print("\n🚀 Starting New Agent Architecture Test...")
    result = asyncio.run(test_new_agent_architecture())
    print("\n✅ Test complete!\n")
