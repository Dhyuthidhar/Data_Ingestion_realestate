#!/usr/bin/env python3
"""
Test extraction accuracy across multiple properties
Monitors data extraction performance for multi-agent system
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors.multi_agent_system import MultiAgentResearchSystem

TEST_PROPERTIES = [
    ("1148 Greenbrook Drive", "Danville", "CA"),
    # Add more test properties as needed
    # ("350 Fifth Avenue", "New York", "NY"),
    # ("1600 Pennsylvania Avenue", "Washington", "DC"),
]

# Expected fields per agent
EXPECTED_FIELDS = {
    'property_records_ownership': [
        'parcel_number', 'property_tax_annual', 'hoa_monthly', 
        'hoa_association_name', 'owner_name', 'purchase_date',
        'mortgage_amount', 'lender_name'
    ],
    'property_details_market': [
        'bedrooms', 'bathrooms', 'square_feet', 'year_built',
        'lot_size_sqft', 'property_type', 'current_status',
        'last_sold_price', 'last_sold_date', 'price_per_sqft'
    ],
    'neighborhood_location': [
        'schools', 'walk_score', 'transit_score', 'bike_score',
        'flood_zone', 'crime_rate_per_100k', 'median_household_income',
        'safety_rating'
    ],
    'financial_inference_estimates': [
        'rent_estimate_low', 'rent_estimate_high', 'gross_yield_pct',
        'insurance_annual_estimate', 'maintenance_annual_estimate'
    ],
    'economic_growth_signals': [
        'major_employers', 'population_growth_pct', 'unemployment_rate_pct',
        'employment_growth'
    ]
}

async def test_extraction_accuracy():
    """Test extraction accuracy across multiple properties"""
    system = MultiAgentResearchSystem()
    
    results = {
        'total_properties': len(TEST_PROPERTIES),
        'properties': [],
        'overall_stats': {
            'total_fields_expected': 0,
            'total_fields_extracted': 0,
            'extraction_rate': 0.0
        }
    }
    
    print("\n" + "=" * 80)
    print("📊 EXTRACTION ACCURACY TEST")
    print("=" * 80)
    
    for address, city, state in TEST_PROPERTIES:
        print(f"\n🏠 Testing: {address}, {city}, {state}")
        print("-" * 80)
        
        result = await system.research_comprehensive(address, city, state)
        
        # Analyze extraction for each agent
        property_result = {
            'address': f"{address}, {city}, {state}",
            'agents': {},
            'total_expected': 0,
            'total_extracted': 0,
            'extraction_rate': 0.0
        }
        
        for agent_name, expected_fields in EXPECTED_FIELDS.items():
            if agent_name in result:
                agent_data = result[agent_name]
                structured_data = agent_data.get('structured_data', {})
                
                # Count extracted fields (excluding 'confidence')
                extracted_fields = [f for f in structured_data.keys() if f != 'confidence']
                extracted_count = len(extracted_fields)
                expected_count = len(expected_fields)
                
                # Calculate extraction rate
                extraction_rate = (extracted_count / expected_count * 100) if expected_count > 0 else 0
                
                # Identify missing fields
                missing_fields = [f for f in expected_fields if f not in extracted_fields]
                
                agent_result = {
                    'expected_count': expected_count,
                    'extracted_count': extracted_count,
                    'extraction_rate': extraction_rate,
                    'extracted_fields': extracted_fields,
                    'missing_fields': missing_fields,
                    'status': agent_data.get('agent_status', 'unknown'),
                    'citations': agent_data.get('citation_count', 0),
                    'confidence': agent_data.get('confidence', 'UNKNOWN')
                }
                
                property_result['agents'][agent_name] = agent_result
                property_result['total_expected'] += expected_count
                property_result['total_extracted'] += extracted_count
                
                # Print agent summary
                status_icon = '✅' if agent_result['status'] == 'success' else '❌'
                print(f"\n{status_icon} {agent_name}:")
                print(f"   Extracted: {extracted_count}/{expected_count} ({extraction_rate:.1f}%)")
                print(f"   Citations: {agent_result['citations']}")
                print(f"   Confidence: {agent_result['confidence']}")
                
                if extracted_fields:
                    print(f"   ✓ Found: {', '.join(extracted_fields[:5])}")
                    if len(extracted_fields) > 5:
                        print(f"           + {len(extracted_fields) - 5} more...")
                
                if missing_fields:
                    print(f"   ✗ Missing: {', '.join(missing_fields[:5])}")
                    if len(missing_fields) > 5:
                        print(f"              + {len(missing_fields) - 5} more...")
        
        # Calculate overall extraction rate for this property
        if property_result['total_expected'] > 0:
            property_result['extraction_rate'] = (
                property_result['total_extracted'] / property_result['total_expected'] * 100
            )
        
        results['properties'].append(property_result)
        
        print(f"\n{'─' * 80}")
        print(f"Property Total: {property_result['total_extracted']}/{property_result['total_expected']} "
              f"({property_result['extraction_rate']:.1f}%)")
    
    # Calculate overall statistics
    total_expected = sum(p['total_expected'] for p in results['properties'])
    total_extracted = sum(p['total_extracted'] for p in results['properties'])
    
    results['overall_stats']['total_fields_expected'] = total_expected
    results['overall_stats']['total_fields_extracted'] = total_extracted
    
    if total_expected > 0:
        results['overall_stats']['extraction_rate'] = (total_extracted / total_expected * 100)
    
    # Print overall summary
    print("\n" + "=" * 80)
    print("📊 OVERALL EXTRACTION STATISTICS")
    print("=" * 80)
    
    print(f"\n📋 Total Fields:")
    print(f"   Expected: {total_expected}")
    print(f"   Extracted: {total_extracted}")
    print(f"   Extraction Rate: {results['overall_stats']['extraction_rate']:.1f}%")
    
    # Agent-level averages
    print(f"\n📊 By Agent (Average across all properties):")
    agent_stats = {}
    for agent_name in EXPECTED_FIELDS.keys():
        extracted_counts = []
        expected_counts = []
        for prop in results['properties']:
            if agent_name in prop['agents']:
                extracted_counts.append(prop['agents'][agent_name]['extracted_count'])
                expected_counts.append(prop['agents'][agent_name]['expected_count'])
        
        if expected_counts:
            avg_extracted = sum(extracted_counts) / len(extracted_counts)
            avg_expected = sum(expected_counts) / len(expected_counts)
            avg_rate = (avg_extracted / avg_expected * 100) if avg_expected > 0 else 0
            
            agent_stats[agent_name] = {
                'avg_extracted': avg_extracted,
                'avg_expected': avg_expected,
                'avg_rate': avg_rate
            }
            
            print(f"   • {agent_name}: {avg_extracted:.1f}/{avg_expected:.1f} ({avg_rate:.1f}%)")
    
    # Performance assessment
    print(f"\n🎯 PERFORMANCE ASSESSMENT:")
    overall_rate = results['overall_stats']['extraction_rate']
    
    if overall_rate >= 80:
        grade = "✅ EXCELLENT"
        assessment = "Extraction performing above target"
    elif overall_rate >= 70:
        grade = "✅ GOOD"
        assessment = "Extraction meeting minimum target"
    elif overall_rate >= 50:
        grade = "⚠️  NEEDS IMPROVEMENT"
        assessment = "Extraction below target - review prompts and patterns"
    else:
        grade = "❌ POOR"
        assessment = "Extraction significantly below target - major fixes needed"
    
    print(f"   Grade: {grade}")
    print(f"   Assessment: {assessment}")
    print(f"   Target: 80%+ extraction rate")
    
    # Save detailed results
    output_file = 'extraction_accuracy_report.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed report saved to: {output_file}")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    print("\n🚀 Starting Extraction Accuracy Test...")
    result = asyncio.run(test_extraction_accuracy())
    print("\n✅ Test complete!\n")
