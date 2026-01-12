#!/usr/bin/env python3
"""
Search-Enabled Accuracy Test
Tests that agents are actually searching the web for real data
"""
import asyncio
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from collectors.multi_agent_system import MultiAgentResearchSystem

async def test_search_accuracy():
    """Test that agents are searching the web and returning real data"""
    system = MultiAgentResearchSystem()
    
    test_property = ("1148 Greenbrook Drive", "Danville", "CA")
    
    print("\n" + "="*70)
    print("🔍 SEARCH-ENABLED ACCURACY TEST")
    print("="*70)
    print("\nTesting: Web search enforcement and citation requirements")
    print(f"Property: {test_property[0]}, {test_property[1]}, {test_property[2]}")
    print("\nExpected Improvements:")
    print("  ✅ Agents SEARCH the web (not just generate responses)")
    print("  ✅ Real property data from Zillow/Redfin (not generic estimates)")
    print("  ✅ Verified comparable sales with actual addresses")
    print("  ✅ Citations with source URLs for all claims")
    print("  ✅ Data confidence levels based on source verification")
    print("  ✅ Address verification before reporting data")
    print("="*70)
    
    start = time.time()
    result = await system.research_comprehensive(*test_property)
    elapsed = time.time() - start
    
    print(f"\n{'='*70}")
    print("📊 RESULTS ANALYSIS")
    print("="*70)
    
    # Agent 1: Property Basics
    print("\n🏠 AGENT 1: Property Basics")
    basics = result.get('property_basics', {})
    
    address_verified = basics.get('address_verified')
    sources_checked = basics.get('sources_checked', [])
    citations = basics.get('_citations', [])
    confidence = basics.get('data_confidence', 'UNKNOWN')
    
    print(f"   Address Verified: {address_verified}")
    print(f"   Sources Checked: {len(sources_checked)} sources")
    if sources_checked:
        for source in sources_checked[:3]:
            print(f"      - {source}")
    print(f"   Citations Found: {len(citations)} citations")
    print(f"   Data Confidence: {confidence}")
    
    if basics.get('current_price'):
        print(f"   ✅ Current Price: ${basics['current_price']:,}")
    if basics.get('bedrooms'):
        print(f"   ✅ Bedrooms: {basics['bedrooms']}")
    if basics.get('bathrooms'):
        print(f"   ✅ Bathrooms: {basics['bathrooms']}")
    if basics.get('square_feet'):
        print(f"   ✅ Square Feet: {basics['square_feet']:,}")
    
    # Agent 2: Financial Analysis
    print("\n💰 AGENT 2: Financial Analysis")
    financials = result.get('financial_analysis', {})
    
    comps = financials.get('comparable_sales', [])
    rentals = financials.get('rental_comparables', [])
    
    print(f"   Comparable Sales Found: {len(comps)}")
    for i, comp in enumerate(comps[:3], 1):
        comp_addr = comp.get('address', 'Unknown')
        comp_price = comp.get('sale_price', 0)
        comp_url = comp.get('source_url', 'No URL')
        print(f"      {i}. {comp_addr}: ${comp_price:,}")
        if comp_url != 'No URL':
            print(f"         Source: {comp_url[:60]}...")
    
    print(f"   Rental Comparables Found: {len(rentals)}")
    for i, rental in enumerate(rentals[:2], 1):
        rental_addr = rental.get('address', 'Unknown')
        rental_price = rental.get('monthly_rent', 0)
        print(f"      {i}. {rental_addr}: ${rental_price:,}/mo")
    
    # Agent 3: Neighborhood
    print("\n🏘️  AGENT 3: Neighborhood Intelligence")
    neighborhood = result.get('neighborhood', {})
    
    schools = neighborhood.get('schools', {})
    walkability = neighborhood.get('walkability', {})
    crime = neighborhood.get('crime', {})
    
    if schools:
        elem = schools.get('elementary', {})
        if elem.get('name'):
            print(f"   Elementary: {elem.get('name')} (Rating: {elem.get('rating', 'N/A')}/10)")
        high = schools.get('high', {})
        if high.get('name'):
            print(f"   High School: {high.get('name')} (Rating: {high.get('rating', 'N/A')}/10)")
    
    if walkability:
        walk_score = walkability.get('walk_score', 'N/A')
        print(f"   Walk Score: {walk_score}")
    
    if crime:
        safety = crime.get('safety_grade', 'N/A')
        print(f"   Safety Grade: {safety}")
    
    # Agent 4: Market Trends
    print("\n📈 AGENT 4: Market Trends")
    market = result.get('market_trends', {})
    
    city_market = market.get('city_market', {})
    if city_market:
        median = city_market.get('median_price_current', 0)
        yoy = city_market.get('yoy_price_change_percent', 0)
        if median:
            print(f"   Median Price: ${median:,}")
        if yoy:
            print(f"   YoY Change: {yoy:+.1f}%")
    
    forecast = market.get('forecast_6_12mo', {})
    if forecast:
        direction = forecast.get('price_direction', 'unknown')
        print(f"   Forecast: {direction}")
    
    # Agent 5: Economic Signals
    print("\n🏢 AGENT 5: Economic Soft Signals")
    signals = result.get('soft_signals', {})
    
    employers = signals.get('major_employers', [])
    if employers:
        print(f"   Major Employers: {len(employers)} found")
        for emp in employers[:3]:
            name = emp.get('name', 'Unknown')
            count = emp.get('employees', 0)
            if name != 'Unknown':
                print(f"      - {name}: {count:,} employees")
    
    innovation = signals.get('innovation', {})
    if innovation:
        vc_funding = innovation.get('vc_funding_12mo', 0)
        if vc_funding:
            print(f"   VC Funding (12mo): ${vc_funding:,}")
    
    # Overall Metadata
    print(f"\n{'='*70}")
    print("⏱️  PERFORMANCE METRICS")
    print("="*70)
    metadata = result.get('_metadata', {})
    print(f"   Research Time: {elapsed:.1f}s")
    print(f"   Agents Successful: {metadata.get('agents_successful', 0)}/5")
    print(f"   Agents Failed: {metadata.get('agents_failed', 0)}/5")
    print(f"   Cost: $0.{metadata.get('cost_cents', 0):02.0f}")
    
    # Verification Summary
    print(f"\n{'='*70}")
    print("✅ VERIFICATION SUMMARY")
    print("="*70)
    
    checks = []
    
    # Check 1: Address verification
    if address_verified:
        checks.append("✅ Address verified for exact property")
    else:
        checks.append("❌ Address verification failed or not found")
    
    # Check 2: Sources checked
    if len(sources_checked) >= 2:
        checks.append(f"✅ Multiple sources checked ({len(sources_checked)})")
    else:
        checks.append(f"⚠️  Limited sources checked ({len(sources_checked)})")
    
    # Check 3: Citations present
    total_citations = len(citations)
    if total_citations >= 3:
        checks.append(f"✅ Citations provided ({total_citations} URLs)")
    else:
        checks.append(f"⚠️  Limited citations ({total_citations} URLs)")
    
    # Check 4: Comparable sales
    if len(comps) >= 3:
        checks.append(f"✅ Comparable sales found ({len(comps)} properties)")
    else:
        checks.append(f"⚠️  Limited comps ({len(comps)} properties)")
    
    # Check 5: Real addresses in comps
    real_comps = sum(1 for c in comps if c.get('address') and len(c.get('address', '')) > 10)
    if real_comps >= 2:
        checks.append(f"✅ Real property addresses in comps ({real_comps})")
    else:
        checks.append(f"⚠️  Generic or missing comp addresses ({real_comps})")
    
    # Check 6: Data confidence
    if confidence in ['HIGH', 'MEDIUM']:
        checks.append(f"✅ Data confidence: {confidence}")
    else:
        checks.append(f"⚠️  Data confidence: {confidence}")
    
    for check in checks:
        print(f"   {check}")
    
    # Final Assessment
    passed = sum(1 for c in checks if c.startswith("✅"))
    total = len(checks)
    
    print(f"\n{'='*70}")
    if passed >= 5:
        print(f"🎉 EXCELLENT! Search-enabled agents working correctly ({passed}/{total})")
        print("   Agents are searching the web and returning verified data.")
    elif passed >= 3:
        print(f"✅ GOOD! Search improvements detected ({passed}/{total})")
        print("   Some agents are searching, but more verification needed.")
    else:
        print(f"⚠️  NEEDS IMPROVEMENT ({passed}/{total})")
        print("   Agents may not be searching the web effectively.")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(test_search_accuracy())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user\n")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
