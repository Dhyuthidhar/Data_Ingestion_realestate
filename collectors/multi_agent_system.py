"""
Multi-Agent Research System - EXPERT OPTIMIZED FOR PERPLEXITY SONAR PRO
Conversational prompts that work WITH model strengths, not against them
"""
import asyncio
import time
import re
from typing import Dict, Any
from datetime import datetime
from collectors.perplexity_agent import PerplexityPropertyAgent
from config import settings

class MultiAgentResearchSystem:
    """Orchestrates multiple specialized research agents with expert-optimized prompts"""
    
    def __init__(self):
        """Initialize multi-agent system"""
        self.agent = PerplexityPropertyAgent()
        self.max_agents = settings.MAX_AGENTS
    
    def _extract_json_from_response(self, response: str, agent_name: str) -> dict:
        """
        Extract and validate JSON from agent response, handling common formatting issues.
        
        Args:
            response: Raw response string from agent
            agent_name: Name of agent for logging
            
        Returns:
            Parsed JSON dict or None if extraction fails
        """
        import json
        import logging
        
        logger = logging.getLogger(__name__)
        
        if not response or not response.strip():
            logger.error(f"❌ {agent_name}: Empty response received")
            return None
        
        # Remove leading/trailing whitespace
        response = response.strip()
        
        # Try direct JSON parsing first
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning(f"⚠️ {agent_name}: Direct JSON parsing failed, trying extraction...")
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                extracted = json_match.group(1)
                logger.info(f"✓ {agent_name}: Extracted JSON from markdown block")
                return json.loads(extracted)
            except json.JSONDecodeError:
                logger.warning(f"⚠️ {agent_name}: Markdown-extracted JSON invalid")
        
        # Try to find JSON object anywhere in the response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            try:
                extracted = json_match.group(0)
                logger.info(f"✓ {agent_name}: Found JSON object in response")
                return json.loads(extracted)
            except json.JSONDecodeError:
                logger.warning(f"⚠️ {agent_name}: Found JSON-like object but parsing failed")
        
        # Log failure with response preview
        logger.error(f"❌ {agent_name}: Could not extract valid JSON")
        logger.error(f"   Response preview: {response[:200]}...")
        return None
    
    def _parse_dual_format_response(self, response: dict, agent_name: str, address: str = "") -> dict:
        """
        Parse agent response with JSON enforcement.
        Priority: JSON extraction -> fallback to regex extraction
        """
        import json
        import logging
        
        logger = logging.getLogger(__name__)
        
        content = response.get('_raw_response', '')
        citations = response.get('_citations', [])
        
        result = {
            'structured_data': {},
            'detailed_analysis': '',
            'parse_success': False,
            'parse_method': 'none',
            'citations': citations,
            'citation_count': len(citations),
            'agent': agent_name
        }
        
        # Define expected fields per agent
        AGENT_FIELDS = {
            'property_records_ownership': ['last_sold_price', 'last_sold_date', 'property_tax_annual',
                                          'hoa_monthly', 'listing_status', 'days_on_market'],
            'property_details_market': ['bedrooms', 'bathrooms', 'square_feet', 'year_built',
                                       'lot_size_sqft', 'property_type', 'current_status',
                                       'last_sold_price', 'last_sold_date', 'price_per_sqft'],
            'neighborhood_location': ['walk_score', 'transit_score', 'bike_score',
                                     'elementary_school', 'elementary_rating',
                                     'middle_school', 'middle_rating',
                                     'high_school', 'high_rating',
                                     'crime_rate', 'nearby_amenities'],
            'financial_inference_estimates': ['rent_estimate_monthly', 'annual_rental_income', 'gross_yield_pct',
                                             'property_insurance_annual', 'maintenance_annual_estimate',
                                             'estimate_confidence', 'calculation_basis'],
            'economic_growth_signals': ['major_employers', 'employment_growth_trend', 'population_growth_pct',
                                       'unemployment_rate', 'key_industries', 'economic_outlook',
                                       'data_recency', 'confidence', 'source_quality']
        }
        
        # Try JSON extraction using the helper method
        extracted_json = self._extract_json_from_response(content, agent_name)
        
        if extracted_json is not None:
            result['structured_data'] = extracted_json
            result['parse_method'] = 'json_extraction'
            result['parse_success'] = True
            result['detailed_analysis'] = f"JSON data extracted successfully from {agent_name}"
            
            # Validate expected fields are present
            expected_fields = AGENT_FIELDS.get(agent_name, [])
            if expected_fields:
                actual_fields = set(extracted_json.keys())
                missing_fields = set(expected_fields) - actual_fields
                
                if missing_fields:
                    logger.warning(f"⚠️ Agent {agent_name}: Missing fields: {missing_fields}")
                    # Add missing fields as null
                    for field in missing_fields:
                        result['structured_data'][field] = None
                
                # Log success metrics
                non_null_fields = sum(1 for v in result['structured_data'].values() if v is not None and v != 'confidence')
                logger.info(f"✅ Agent {agent_name}: {non_null_fields}/{len(expected_fields)} fields populated")
        else:
            # Fallback: conversational text extraction
            logger.warning(f"⚠️ Agent {agent_name}: JSON extraction failed, falling back to regex")
            result['detailed_analysis'] = content
            result['structured_data'] = self._extract_key_metrics_from_text(content, agent_name, address)
            result['parse_method'] = 'text_extraction_fallback'
            result['parse_success'] = True
        
        # Add confidence scoring
        if len(citations) >= 5:
            result['structured_data']['confidence'] = 'HIGH'
        elif len(citations) <= 1:
            result['structured_data']['confidence'] = 'LOW'
        else:
            result['structured_data']['confidence'] = result['structured_data'].get('confidence', 'MEDIUM')
        
        # Legacy compatibility: add raw_analysis for backward compatibility
        result['raw_analysis'] = result['detailed_analysis']
        result['confidence'] = result['structured_data'].get('confidence', 'MEDIUM')
        
        return result
    
    def _extract_key_metrics_from_text(self, text: str, agent_name: str, address: str = "") -> dict:
        """
        Fallback: Extract structured data from conversational text using regex.
        Updated for new accessibility-based agent architecture with validation.
        """
        import os
        data = {}
        
        # Enable debug logging
        DEBUG = os.getenv('DEBUG_EXTRACTION', 'false').lower() == 'true'
        
        if DEBUG:
            print(f"\n   🔍 Extracting from {agent_name}...")
            print(f"   📝 Text length: {len(text)} chars")
        
        if agent_name == 'property_records_ownership':
            # ═══════════════════════════════════════════════════════════
            # PARCEL NUMBER - Multiple patterns with validation
            # ═══════════════════════════════════════════════════════════
            parcel_patterns = [
                r'(?:parcel|APN)(?:\s+number)?[:\s]+(\d{3}[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d)',
                r'(?:parcel|APN)[:\s]+([0-9]{3}-[0-9]{3}-[0-9]{3}-[0-9])',
                r'parcel\s*(?:number|#|ID)?\s*:?\s*([\d\-]{10,})'
            ]
            for pattern in parcel_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    parcel = match.group(1).strip()
                    # Validate: should have 3-4 digit groups
                    if len(parcel.replace('-', '').replace(' ', '')) >= 10:
                        data['parcel_number'] = parcel
                        if DEBUG:
                            print(f"   ✓ Parcel: {parcel}")
                        break
            
            # ═══════════════════════════════════════════════════════════
            # PROPERTY TAX - Multiple patterns with strict validation
            # ═══════════════════════════════════════════════════════════
            tax_patterns = [
                r'property\s+tax[:\s]+\$?([\d,]+)\s*(?:annual|per year|yearly)?',
                r'annual\s+(?:property\s+)?tax[:\s]+\$?([\d,]+)',
                r'tax[:\s]+\$?([\d,]{5,})\s*(?:annual|per year)',
                r'\$?([\d,]{5,})\s*(?:property tax|annual tax)'
            ]
            for pattern in tax_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    tax_str = match.group(1).replace(',', '')
                    tax_value = int(tax_str)
                    # VALIDATION: Property tax should be $2,000 - $100,000 for CA
                    if 2000 <= tax_value <= 100000:
                        data['property_tax_annual'] = tax_value
                        if DEBUG:
                            print(f"   ✓ Property tax: ${tax_value}")
                        break
                    elif tax_value < 2000 and DEBUG:
                        print(f"   ⚠️  Rejected property_tax: ${tax_value} (too low, likely wrong match)")
            
            # ═══════════════════════════════════════════════════════════
            # HOA FEES - Multiple patterns with validation
            # ═══════════════════════════════════════════════════════════
            hoa_patterns = [
                r'\$(\d+)\s*(?:per\s*month|/month|monthly).*?HOA',
                r'HOA.*?\$(\d+)\s*(?:per\s*month|/month|monthly)',
                r'HOA\s*(?:fee|dues)?[:\s]+\$(\d+)',
                r'association\s*fee[:\s]+\$(\d+)\s*(?:per\s*month|monthly)'
            ]
            for pattern in hoa_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    hoa_value = int(match.group(1))
                    # VALIDATION: HOA should be $50 - $1000/month typically
                    if 50 <= hoa_value <= 1000:
                        data['hoa_monthly'] = hoa_value
                        if DEBUG:
                            print(f"   ✓ HOA: ${hoa_value}/month")
                        break
            
            # ═══════════════════════════════════════════════════════════
            # HOA ASSOCIATION NAME
            # ═══════════════════════════════════════════════════════════
            hoa_name_patterns = [
                r'([A-Z][\w\s]+)\s*HOA',
                r'HOA[:\s]+([A-Z][\w\s]+)',
                r'([A-Z][\w\s]+)\s*(?:Homeowners|Home Owners)\s*Association'
            ]
            for pattern in hoa_name_patterns:
                match = re.search(pattern, text)
                if match:
                    hoa_name = match.group(1).strip()
                    # Validation: reasonable length
                    if 5 <= len(hoa_name) <= 50:
                        data['hoa_association_name'] = hoa_name
                        if DEBUG:
                            print(f"   ✓ HOA name: {hoa_name}")
                        break
            
            # ═══════════════════════════════════════════════════════════
            # OWNER NAME - Multiple patterns with validation
            # ═══════════════════════════════════════════════════════════
            owner_patterns = [
                r'(?:current\s+)?owner[:\s]+([A-Z][a-z]+\s+[A-Z][\w\s]+)',
                r'buyer[:\s]+([A-Z][a-z]+\s+[A-Z][\w\s]+)',
                r'(?:owned by|purchased by)[:\s]+([A-Z][a-z]+\s+[A-Z][\w\s]+)'
            ]
            for pattern in owner_patterns:
                match = re.search(pattern, text)
                if match:
                    name = match.group(1).strip()
                    # VALIDATION: Reject county names, generic terms
                    invalid_terms = ['County', 'Contra Costa', 'Assessor', 'Tax', 'Public', 
                                    'Record', 'LLC', 'Inc', 'Corp', 'Trust', 'Fees', 'Association']
                    if not any(term in name for term in invalid_terms):
                        # Additional validation: should be 2-4 words
                        word_count = len(name.split())
                        if 2 <= word_count <= 4:
                            data['owner_name'] = name
                            if DEBUG:
                                print(f"   ✓ Owner: {name}")
                            break
                    elif DEBUG:
                        print(f"   ⚠️  Rejected owner_name: '{name}' (invalid term)")
            
            # ═══════════════════════════════════════════════════════════
            # PURCHASE DATE
            # ═══════════════════════════════════════════════════════════
            purchase_date_match = re.search(r'purchased?\s*(?:in|on)?\s*([A-Z][a-z]+\s+\d{4}|\d{1,2}/\d{1,2}/\d{4}|\d{4})', text, re.IGNORECASE)
            if purchase_date_match:
                data['purchase_date'] = purchase_date_match.group(1)
                if DEBUG:
                    print(f"   ✓ Purchase date: {purchase_date_match.group(1)}")
            
            # ═══════════════════════════════════════════════════════════
            # MORTGAGE AMOUNT - Multiple patterns with validation
            # ═══════════════════════════════════════════════════════════
            mortgage_patterns = [
                r'mortgage.*?\$?([\d,\.]+)\s*million',
                r'loan\s*amount[:\s]+\$?([\d,]+)',
                r'original\s*(?:loan|mortgage)[:\s]+\$?([\d,]+)',
                r'deed\s*of\s*trust.*?\$?([\d,]+)'
            ]
            for pattern in mortgage_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    # Check if in millions
                    if 'million' in match.group(0).lower():
                        amount = float(amount_str) * 1000000
                    else:
                        amount = float(amount_str)
                    # VALIDATION: Mortgage should be $100k - $10M for this area
                    if 100000 <= amount <= 10000000:
                        data['mortgage_amount'] = int(amount)
                        if DEBUG:
                            print(f"   ✓ Mortgage: ${int(amount):,}")
                        break
            
            # ═══════════════════════════════════════════════════════════
            # LENDER NAME
            # ═══════════════════════════════════════════════════════════
            lender_match = re.search(r'lender\s*:?\s*([A-Z][\w\s&]+(?:Bank|Mortgage|Financial|Credit Union))', text, re.IGNORECASE)
            if lender_match:
                data['lender_name'] = lender_match.group(1).strip()
                if DEBUG:
                    print(f"   ✓ Lender: {lender_match.group(1).strip()}")
        
        elif agent_name == 'property_details_market':
            # Extract property basics
            bed_match = re.search(r'(\d+)\s*bed', text, re.IGNORECASE)
            if bed_match:
                data['bedrooms'] = int(bed_match.group(1))
            
            bath_match = re.search(r'(\d+(?:\.\d+)?)\s*bath', text, re.IGNORECASE)
            if bath_match:
                data['bathrooms'] = float(bath_match.group(1))
            
            sqft_match = re.search(r'([\d,]+)\s*(?:sq\s*ft|square\s*feet)', text, re.IGNORECASE)
            if sqft_match:
                data['square_feet'] = int(sqft_match.group(1).replace(',', ''))
            
            year_match = re.search(r'built\s+(?:in\s+)?(\d{4})', text, re.IGNORECASE)
            if year_match:
                data['year_built'] = int(year_match.group(1))
            
            # Lot size
            lot_match = re.search(r'([\d,]+)\s*(?:sq\s*ft|square\s*feet)\s*lot', text, re.IGNORECASE)
            if lot_match:
                data['lot_size_sqft'] = int(lot_match.group(1).replace(',', ''))
            
            # Property type
            if 'single-family' in text.lower() or 'single family' in text.lower():
                data['property_type'] = 'single-family'
            elif 'condo' in text.lower():
                data['property_type'] = 'condo'
            elif 'townhouse' in text.lower() or 'townhome' in text.lower():
                data['property_type'] = 'townhouse'
            
            # Current status
            if 'for sale' in text.lower():
                data['current_status'] = 'for sale'
            elif 'sold' in text.lower() or 'off market' in text.lower():
                data['current_status'] = 'sold'
            elif 'pending' in text.lower():
                data['current_status'] = 'pending'
            
            # Sale price and date
            sale_patterns = [
                r'sold.*?(?:for|at|price)\s*\$([\d,\.]+)\s*(?:million|M)?.*?(?:in|on)\s*([A-Z][a-z]+\s+\d{4})',
                r'\$([\d,\.]+)\s*(?:million|M)?.*?sold.*?([A-Z][a-z]+\s+\d{4})'
            ]
            for pattern in sale_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    price_str = match.group(1).replace(',', '')
                    if 'million' in match.group(0).lower() or 'M' in match.group(0):
                        data['last_sold_price'] = float(price_str) * 1000000
                    else:
                        data['last_sold_price'] = float(price_str)
                    data['last_sold_date'] = match.group(2)
                    break
            
            # Price per sqft
            ppsf_match = re.search(r'\$(\d+)\s*(?:per|/)\s*(?:sq\s*ft|square\s*foot)', text, re.IGNORECASE)
            if ppsf_match:
                data['price_per_sqft'] = int(ppsf_match.group(1))
            
            # Days on market
            dom_match = re.search(r'(\d+)\s*days\s*on\s*market', text, re.IGNORECASE)
            if dom_match:
                data['days_on_market'] = int(dom_match.group(1))
        
        elif agent_name == 'neighborhood_location':
            # ═══════════════════════════════════════════════════════════
            # SCHOOL NAMES AND RATINGS - Structured extraction
            # ═══════════════════════════════════════════════════════════
            # Pattern 1: Exact format "School Name, GreatSchools Rating: X/10"
            school_pattern = r'([A-Z][\w\s]+(?:Elementary|Middle|High)(?:\s+School)?)[,:\s]+.*?GreatSchools\s+Rating[:\s]+(\d+)/10'
            school_matches = re.findall(school_pattern, text, re.IGNORECASE)
            
            # Pattern 2: Fallback for "School Name...X/10" format
            if not school_matches:
                school_pattern = r'([A-Z][\w\s]+(?:Elementary|Middle|High)(?:\s+School)?)[,:\s]+.*?(\d+)/10'
                school_matches = re.findall(school_pattern, text)
            
            # Pattern 3: Handle ranges like "8–9/10" - extract first number
            if not school_matches:
                school_pattern = r'([A-Z][\w\s]+(?:Elementary|Middle|High)(?:\s+School)?)[,:\s]+.*?(\d+)(?:–\d+)?/10'
                school_matches = re.findall(school_pattern, text)
            
            if school_matches:
                schools = []
                for school_name, rating in school_matches:
                    schools.append({
                        'name': school_name.strip(),
                        'rating': int(rating)
                    })
                data['schools'] = schools
                if DEBUG:
                    print(f"   ✓ Schools: {len(schools)} extracted")
                    for school in schools:
                        print(f"      - {school['name']}: {school['rating']}/10")
            
            # ═══════════════════════════════════════════════════════════
            # WALK SCORE - Multiple patterns
            # ═══════════════════════════════════════════════════════════
            walk_patterns = [
                r'Walk\s*Score[:\s]+(\d+)',
                r'Walkability[:\s]+(\d+)/100',
                r'walk\s*score.*?(\d+)/100'
            ]
            for pattern in walk_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    score = int(match.group(1))
                    if 0 <= score <= 100:  # Validation
                        data['walk_score'] = score
                        if DEBUG:
                            print(f"   ✓ Walk Score: {score}")
                        break
            
            # ═══════════════════════════════════════════════════════════
            # TRANSIT SCORE
            # ═══════════════════════════════════════════════════════════
            transit_patterns = [
                r'Transit\s*Score[:\s]+(\d+)',
                r'transit.*?(\d+)/100'
            ]
            for pattern in transit_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    score = int(match.group(1))
                    if 0 <= score <= 100:
                        data['transit_score'] = score
                        if DEBUG:
                            print(f"   ✓ Transit Score: {score}")
                        break
            
            # ═══════════════════════════════════════════════════════════
            # BIKE SCORE
            # ═══════════════════════════════════════════════════════════
            bike_patterns = [
                r'Bike\s*Score[:\s]+(\d+)',
                r'bike.*?(\d+)/100'
            ]
            for pattern in bike_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    score = int(match.group(1))
                    if 0 <= score <= 100:
                        data['bike_score'] = score
                        if DEBUG:
                            print(f"   ✓ Bike Score: {score}")
                        break
            
            # ═══════════════════════════════════════════════════════════
            # FLOOD ZONE/RISK
            # ═══════════════════════════════════════════════════════════
            flood_patterns = [
                r'Flood\s*(?:Factor|Risk)[:\s]+(Minimal|Moderate|Major|Severe)',
                r'FEMA\s*Zone[:\s]+([A-Z]+)',
                r'flood.*?(minimal|moderate|major|severe)',
            ]
            for pattern in flood_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data['flood_zone'] = match.group(1).capitalize()
                    if DEBUG:
                        print(f"   ✓ Flood zone: {match.group(1).capitalize()}")
                    break
            
            # Extract crime rate
            crime_match = re.search(r'crime\s*rate.*?(\d+)\s*per\s*100,?000', text, re.IGNORECASE)
            if crime_match:
                data['crime_rate_per_100k'] = int(crime_match.group(1))
            
            # Safety rating
            if 'very safe' in text.lower() or 'low crime' in text.lower():
                data['safety_rating'] = 'high'
            elif 'unsafe' in text.lower() or 'high crime' in text.lower():
                data['safety_rating'] = 'low'
            else:
                data['safety_rating'] = 'medium'
            
            # Demographics
            income_match = re.search(r'median\s*(?:household)?\s*income.*?\$([\d,]+)', text, re.IGNORECASE)
            if income_match:
                data['median_household_income'] = int(income_match.group(1).replace(',', ''))
        
        elif agent_name == 'financial_inference_estimates':
            # Extract rent estimates
            rent_patterns = [
                r'\$(\d+,?\d*)\s*(?:-|to)\s*\$(\d+,?\d*).*?(?:rent|per\s*month)',
                r'rent.*?\$(\d+,?\d*)\s*(?:-|to)\s*\$(\d+,?\d*)'
            ]
            for pattern in rent_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data['rent_estimate_low'] = int(match.group(1).replace(',', ''))
                    data['rent_estimate_high'] = int(match.group(2).replace(',', ''))
                    break
            
            # Single rent estimate
            if 'rent_estimate_low' not in data:
                single_rent_match = re.search(r'rent.*?\$(\d+,?\d*)\s*(?:per\s*month|monthly)', text, re.IGNORECASE)
                if single_rent_match:
                    data['rent_estimate_monthly'] = int(single_rent_match.group(1).replace(',', ''))
            
            # Extract yield/cap rate
            yield_patterns = [
                r'(\d+(?:\.\d+)?)\s*%.*?(?:yield|cap\s*rate)',
                r'(?:yield|cap\s*rate).*?(\d+(?:\.\d+)?)\s*%'
            ]
            for pattern in yield_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data['gross_yield_pct'] = float(match.group(1))
                    break
            
            # Extract insurance estimate
            insurance_match = re.search(r'insurance.*?\$(\d+,?\d*)\s*(?:per\s*year|annually)', text, re.IGNORECASE)
            if insurance_match:
                data['insurance_annual_estimate'] = int(insurance_match.group(1).replace(',', ''))
            
            # Extract maintenance estimate
            maintenance_match = re.search(r'maintenance.*?\$(\d+,?\d*)\s*(?:per\s*year|annually)', text, re.IGNORECASE)
            if maintenance_match:
                data['maintenance_annual_estimate'] = int(maintenance_match.group(1).replace(',', ''))
            
            # Extract cash-on-cash return
            coc_match = re.search(r'cash[\-\s]on[\-\s]cash.*?(\d+(?:\.\d+)?)\s*%', text, re.IGNORECASE)
            if coc_match:
                data['cash_on_cash_return_pct'] = float(coc_match.group(1))
        
        elif agent_name == 'economic_growth_signals':
            # Extract major employers
            employers = []
            for match in re.finditer(r'([A-Z][\w\s&]+(?:Inc|Corp|Company|LLC)).*?(\d+,?\d*)\s*employees', text):
                employers.append({
                    'name': match.group(1).strip(),
                    'employee_count': int(match.group(2).replace(',', ''))
                })
            if employers:
                data['major_employers'] = employers
            
            # Extract population growth
            pop_growth_match = re.search(r'population\s*growth.*?(\d+(?:\.\d+)?)\s*%', text, re.IGNORECASE)
            if pop_growth_match:
                data['population_growth_pct'] = float(pop_growth_match.group(1))
            
            # Extract unemployment rate
            unemployment_match = re.search(r'unemployment.*?(\d+(?:\.\d+)?)\s*%', text, re.IGNORECASE)
            if unemployment_match:
                data['unemployment_rate_pct'] = float(unemployment_match.group(1))
            
            # Employment growth
            if 'growing' in text.lower() or 'strong.*job' in text.lower():
                data['employment_growth'] = 'strong'
            elif 'declining' in text.lower() or 'weak' in text.lower():
                data['employment_growth'] = 'weak'
            else:
                data['employment_growth'] = 'moderate'
        
        
        return data
    
    async def research_comprehensive(
        self, 
        address: str, 
        city: str, 
        state: str
    ) -> Dict[str, Any]:
        """
        Deploy 5 specialized agents with expert-optimized conversational prompts
        
        OPTIMIZATION STRATEGY:
        - Conversational, not instructional language
        - Human-centric framing (buyer perspective)
        - Search-triggering questions
        - Natural output with smart parsing
        - Permission to fail gracefully (MLS limitations)
        """
        start_time = time.time()
        full_address = f"{address}, {city}, {state}"
        
        print(f"\n🤖 Deploying {self.max_agents} specialized agents...")
        print(f"📍 Property: {full_address}")
        print(f"⚡ Using expert-optimized conversational prompts")
        
        # AGENT 1: Property Sale & Tax Facts (HIGH CONFIDENCE PUBLIC DATA)
        agent1_task = asyncio.create_task(
            self.agent.research_async(
                prompt=f"""OBJECTIVE: Research easily accessible property facts for {full_address}

SEARCH THESE SITES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Zillow.com → Property page → "Tax History" section for property tax
2. Redfin.com → Property details → Check for HOA information
3. Look at "Sale History" section for last sold information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FIND THESE FACTS (all available on listing sites):

📌 last_sold_price - Last sale price (e.g., 2408000)
📌 last_sold_date - Last sale date (format: YYYY-MM-DD, e.g., "2022-05-16")
📌 property_tax_annual - Annual property tax if shown (e.g., 22303)
📌 hoa_monthly - Monthly HOA fee if mentioned (e.g., 150, or null if none)
📌 listing_status - Current status (e.g., "Sold", "Active", "Off Market", "Pending")
📌 days_on_market - Days on market if currently listed (or last listing duration)

NOTE: We're focusing on data that's prominently displayed on listing sites. 
Fields requiring county database access (parcel number, owner name, mortgage details) 
will be handled by a separate premium data source in the future.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (flexible - like Agent 2):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION 1 - JSON (preferred):
{{
  "last_sold_price": 2408000,
  "last_sold_date": "2022-05-16",
  "property_tax_annual": 22303,
  "hoa_monthly": 150,
  "listing_status": "Sold",
  "days_on_market": 12
}}

OPTION 2 - Structured list:
- last_sold_price: 2408000
- last_sold_date: 2022-05-16
- property_tax_annual: 22303
- hoa_monthly: 150
- listing_status: Sold
- days_on_market: 12

OPTION 3 - Natural narrative:
According to Zillow, the property last_sold_price was $2,408,000 on 2022-05-16 (last_sold_date). The property_tax_annual is $22,303. The hoa_monthly fee is $150. The listing_status is Sold and it was on the market for 12 days_on_market.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIORITY: Find the data - format is secondary.

✅ SEARCH the property listing sites
✅ EXTRACT real data from those pages
✅ INCLUDE field names in your response
✅ CITE property-specific URLs

Current date: January 2026""",
                system_prompt=f"""You are a thorough real estate research assistant for {full_address}.

PRIMARY OBJECTIVE: Search the web and find accurate property data.

OUTPUT FLEXIBILITY:
- Preferred: Return structured JSON when you have the data
- Acceptable: Return findings in narrative format with field labels
- The system can parse multiple formats - focus on data quality first

SEARCH PROCESS:
1. Visit Zillow.com, Redfin.com, Realtor.com for the specific property
2. Extract actual data from property listing pages
3. Include property-specific URLs in citations
4. Use null for fields you genuinely cannot find

CRITICAL: Your citations should include property-specific sites (Zillow, Redfin, Realtor.com), 
not generic tutorial sites. If your response has all null values, it means you 
didn't search properly.

Format is less important than finding accurate data. We have robust parsing that can 
handle JSON, structured text, or narrative responses."""
            )
        )
        
        # AGENT 2: Property Details & Market Data (HIGH CONFIDENCE PUBLIC DATA)
        agent2_task = asyncio.create_task(
            self.agent.research_async(
                prompt=f"""OBJECTIVE: Research property details and market data for {full_address}

SEARCH THESE SITES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Zillow.com → Search "{full_address}" → Property page → Basic details, price history
2. Redfin.com → Search "{full_address}" → Property details → Home facts, market data
3. Realtor.com → Search "{full_address}" → Property overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FIND THESE DETAILS:
📌 bedrooms - Number of bedrooms (e.g., 4)
📌 bathrooms - Number of bathrooms (can be decimal like 2.5 or 3.0)
📌 square_feet - Interior square footage (e.g., 3192)
📌 lot_size_sqft - Lot size in square feet (e.g., 9500)
📌 year_built - Year the property was built (e.g., 1973)
📌 property_type - Type: Single Family, Condo, Townhouse, etc.
📌 current_status - Current status: For Sale, Sold, Off Market, Pending
📌 last_sold_price - Last sale price (e.g., 2410000)
📌 last_sold_date - Last sale date in YYYY-MM-DD format (e.g., 2022-05-15)
📌 price_per_sqft - Price per square foot (calculate if needed)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (flexible - choose what works):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION 1 - JSON (preferred):
{{
  "bedrooms": 4,
  "bathrooms": 3.0,
  "square_feet": 3192,
  "year_built": 1973,
  "lot_size_sqft": 9500,
  "property_type": "Single Family",
  "current_status": "Sold",
  "last_sold_price": 2410000,
  "last_sold_date": "2022-05-15",
  "price_per_sqft": 755
}}

OPTION 2 - Structured list:
Property details for {full_address}:
- bedrooms: 4
- bathrooms: 3.0
- square_feet: 3192
- year_built: 1973
- lot_size_sqft: 9500
- property_type: Single Family
- current_status: Sold
- last_sold_price: 2410000
- last_sold_date: 2022-05-15
- price_per_sqft: 755

OPTION 3 - Natural narrative:
According to Zillow, this property has 4 bedrooms and 3.0 bathrooms. The square_feet is 3,192 and it was built in 1973 (year_built). The lot_size_sqft is 9,500. It's a Single Family home (property_type). The current_status is Sold - it last_sold_price for $2,410,000 on 2022-05-15 (last_sold_date), which works out to about 755 price_per_sqft.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIORITY: Find actual data from property websites. Format is secondary.

✅ SEARCH the property listing sites
✅ EXTRACT real data from those pages
✅ INCLUDE field names in your response
✅ CITE property-specific URLs

❌ DO NOT return all nulls
❌ DO NOT skip the web search
❌ Format flexibility - we can parse various formats

Current date: January 2026""",
                system_prompt=f"""You are a thorough real estate research assistant for {full_address}.

PRIMARY OBJECTIVE: Search the web and find accurate property data.

OUTPUT FLEXIBILITY:
- Preferred: Return structured JSON when you have the data
- Acceptable: Return findings in narrative format with field labels
- The system can parse multiple formats - focus on data quality first

SEARCH PROCESS:
1. Visit Zillow.com, Redfin.com, Realtor.com for the specific property
2. Extract actual data from property listing pages
3. Include property-specific URLs in citations
4. Use null for fields you genuinely cannot find

CRITICAL: Your citations should include property-specific sites (Zillow, Redfin, Realtor.com), 
not generic tutorial sites. If your response has all null values, it means you 
didn't search properly.

Format is less important than finding accurate data. We have robust parsing that can 
handle JSON, structured text, or narrative responses."""
            )
        )
        
        # AGENT 3: Neighborhood & Location Analysis (HIGH CONFIDENCE PUBLIC DATA)
        agent3_task = asyncio.create_task(
            self.agent.research_async(
                prompt=f"""OBJECTIVE: Research neighborhood and location data for {full_address}

SEARCH THESE SITES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. GreatSchools.org → Search by address → Find nearby schools with ratings
2. WalkScore.com → Search address → Get Walk/Transit/Bike scores
3. Redfin or Zillow → Check neighborhood section for crime, amenities
4. Google Maps → Search "{full_address}" → Look at nearby amenities
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FIND THIS NEIGHBORHOOD DATA:

📌 walk_score - Walk Score (0-100) from WalkScore.com
📌 transit_score - Transit Score (0-100) from WalkScore.com  
📌 bike_score - Bike Score (0-100) from WalkScore.com

📌 elementary_school - Nearest elementary school name
📌 elementary_rating - School rating (e.g., 8)
📌 middle_school - Nearest middle school name
📌 middle_rating - School rating (e.g., 9)
📌 high_school - Nearest high school name
📌 high_rating - School rating (e.g., 7)

📌 crime_rate - Crime rate description (e.g., "Low", "Below Average", "Average")
📌 nearby_amenities - List 3-5 key nearby amenities (parks, shopping, restaurants)

SEARCH STRATEGY:
1. Visit WalkScore.com first for scores (very reliable)
2. Then GreatSchools.org for school ratings
3. Check listing site neighborhood sections for crime/amenities
4. Google Maps can help identify nearby amenities

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (flexible like Agent 2):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION 1 - JSON (preferred):
{{
  "walk_score": 24,
  "transit_score": 20,
  "bike_score": 35,
  "elementary_school": "Greenbrook Elementary School",
  "elementary_rating": 8,
  "middle_school": "Charlotte Wood Middle School",
  "middle_rating": 9,
  "high_school": "Monte Vista High School", 
  "high_rating": 7,
  "crime_rate": "Low",
  "nearby_amenities": ["Danville Town Center (1.2 miles)", "Iron Horse Trail (0.5 miles)", "Rose Garden Shopping Center (2 miles)"]
}}

OPTION 2 - Structured list:
- walk_score: 24
- transit_score: 20
- bike_score: 35
- elementary_school: Greenbrook Elementary School
- elementary_rating: 8
- middle_school: Charlotte Wood Middle School
- middle_rating: 9
- high_school: Monte Vista High School
- high_rating: 7
- crime_rate: Low
- nearby_amenities: Danville Town Center (1.2 miles), Iron Horse Trail (0.5 miles), Rose Garden Shopping Center (2 miles)

OPTION 3 - Natural narrative:
According to WalkScore.com, the walk_score is 24, transit_score is 20, and bike_score is 35. From GreatSchools.org, the elementary_school is Greenbrook Elementary School with an elementary_rating of 8. The middle_school is Charlotte Wood Middle School with a middle_rating of 9. The high_school is Monte Vista High School with a high_rating of 7. The crime_rate is Low. Nearby amenities include Danville Town Center (1.2 miles), Iron Horse Trail (0.5 miles), and Rose Garden Shopping Center (2 miles).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIORITY: Accurate data from reliable sources. Format is secondary.

✅ SEARCH WalkScore.com for scores (very reliable)
✅ SEARCH GreatSchools.org for school info
✅ INCLUDE field names in your response
✅ CITE specific URLs

Current date: January 2026""",
                system_prompt=f"""You are a thorough neighborhood research assistant for {full_address}.

PRIMARY OBJECTIVE: Search the web and find accurate neighborhood data.

OUTPUT FLEXIBILITY:
- Preferred: Return structured JSON when you have the data
- Acceptable: Return findings in narrative format with field labels
- The system can parse multiple formats - focus on data quality first

SEARCH PROCESS:
1. Visit WalkScore.com for walk/transit/bike scores (very reliable source)
2. Visit GreatSchools.org for school names and ratings
3. Check Zillow/Redfin neighborhood sections for crime and amenities
4. Use Google Maps to identify nearby amenities

CRITICAL: Your citations should include specialized sites (WalkScore.com, GreatSchools.org), 
not generic tutorial sites. If your response has all null values, it means you 
didn't search properly.

Format is less important than finding accurate data. We have robust parsing that can 
handle JSON, structured text, or narrative responses."""
            )
        )
        
        # AGENT 4: Financial Inference & Estimates (MODERATE CONFIDENCE - ESTIMATES ONLY)
        agent4_task = asyncio.create_task(
            self.agent.research_async(
                prompt=f"""OBJECTIVE: Estimate financial metrics for {full_address}

⚠️ IMPORTANT: These are ESTIMATES based on market data, not exact figures.

SEARCH THESE SOURCES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Zillow.com → "Rent Zestimate" (rental estimate)
2. Rentometer.com → Comparable rental data for area
3. Redfin or Zillow → Current estimated home value
4. Insurance comparison sites → Regional insurance rates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CALCULATE THESE ESTIMATES:

📌 rent_estimate_monthly - Monthly rental estimate
   METHOD 1: Check Zillow "Rent Zestimate"
   METHOD 2: Find 3-5 comparable rentals in same neighborhood
   METHOD 3: Calculate 0.8-1.0% of home value per month
   Example: For $2.4M home → $4,800-5,000/month range

📌 annual_rental_income - Yearly rental income (rent_estimate_monthly × 12)

📌 gross_yield_pct - Gross rental yield percentage
   FORMULA: (annual_rental_income / current_home_value) × 100
   Example: ($60,000 / $2,400,000) × 100 = 2.5%

📌 property_insurance_annual - Annual property insurance estimate
   METHOD: $3-6 per $1,000 of home value (varies by state/risk)
   California: ~$4/1000 (higher in fire zones)
   Example: $2,400,000 × 0.004 = $9,600/year

📌 maintenance_annual_estimate - Annual maintenance estimate  
   RULE: 1-2% of home value
   Newer homes (post-2000): 1%
   Older homes (pre-1990): 1.5-2%
   Example: $2,400,000 × 0.015 = $36,000/year

CALCULATION STEPS:
1. Get current home value (Zillow/Redfin estimate)
2. Find rental comparables or Rent Zestimate
3. Calculate gross yield using formula
4. Estimate insurance based on home value and location
5. Estimate maintenance based on home value and age

SHOW YOUR WORK: Include calculation basis in response so users understand estimates.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (flexible):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION 1 - JSON (preferred):
{{
  "rent_estimate_monthly": 5000,
  "annual_rental_income": 60000,
  "gross_yield_pct": 2.5,
  "property_insurance_annual": 9600,
  "maintenance_annual_estimate": 36000,
  "estimate_confidence": "MEDIUM",
  "calculation_basis": "Based on Zillow Rent Zestimate of $5,000/mo and Redfin home value estimate of $2.4M"
}}

OPTION 2 - Structured with calculations:
- rent_estimate_monthly: 5000 (from Zillow Rent Zestimate)
- annual_rental_income: 60000 (5000 × 12)
- gross_yield_pct: 2.5 (calculated: 60000 / 2400000 × 100)
- property_insurance_annual: 9600 (estimated at $4 per $1000 of value)
- maintenance_annual_estimate: 36000 (1.5% of home value for 1973 home)
- estimate_confidence: MEDIUM
- calculation_basis: Based on Zillow Rent Zestimate and Redfin value estimate

OPTION 3 - Narrative with methodology:
Based on my research, the rent_estimate_monthly is approximately $5,000 according to Zillow's Rent Zestimate. This gives an annual_rental_income of $60,000. With the current home value around $2.4M, the gross_yield_pct is 2.5%. For property_insurance_annual, I estimate $9,600 (typical California rate of $4 per $1,000 of value). The maintenance_annual_estimate is $36,000 (1.5% of value for a 1973-built home).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIORITY: Reasonable estimates with clear methodology. Show your calculations.

✅ SEARCH for Rent Zestimate and comparable rentals
✅ CALCULATE yields and costs using standard formulas
✅ EXPLAIN your calculation methodology
✅ CITE sources for estimates

Current date: January 2026""",
                system_prompt=f"""You are a thorough real estate financial analyst for {full_address}.

PRIMARY OBJECTIVE: Provide reasonable financial estimates with clear methodology.

⚠️ IMPORTANT: You are providing ESTIMATES, not actual data.

OUTPUT FLEXIBILITY:
- Preferred: Return structured JSON with estimates and calculation basis
- Acceptable: Return findings in narrative format with field labels and methodology
- The system can parse multiple formats - focus on reasonable estimates first

SEARCH PROCESS:
1. Visit Zillow.com for Rent Zestimate and home value estimate
2. Search for comparable rental properties in the area
3. Use standard real estate formulas for insurance and maintenance
4. Include your calculation methodology in the response

ESTIMATION GUIDELINES:
- Rental: 0.7-1.2% of home value per month (suburban areas typically lower)
- Gross yield: 1.5-4% for residential properties (lower in expensive areas)
- Insurance: $3-8 per $1,000 of home value (California ~$4-5)
- Maintenance: 1-2% of home value annually (older homes higher)

CRITICAL: Show your work. Include calculation basis so users understand how estimates were derived.

Format is less important than providing reasonable estimates with clear methodology."""
            )
        )
        
        # AGENT 5: Economic & Growth Signals (DEEP RESEARCH - MARKET INTELLIGENCE)
        agent5_task = asyncio.create_task(
            self.agent.research_async(
                prompt=f"""OBJECTIVE: Research economic growth indicators for the {city}, {state} area using DEEP RESEARCH mode for comprehensive analysis.

⚠️ IMPORTANT: This requires multi-step research synthesizing data from authoritative government and economic sources.

AUTHORITATIVE DATA SOURCES TO PRIORITIZE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. U.S. Bureau of Labor Statistics (BLS.gov) - Employment & unemployment data
2. U.S. Census Bureau (Census.gov) - Population & demographic trends
3. State Labor Department - {state} employment statistics
4. Local Economic Development Agency - {city} economic reports
5. Regional business journals - Major employer news
6. LinkedIn Economic Graph - Employment trends by region
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESEARCH THESE ECONOMIC INDICATORS:

📌 major_employers - Top 5-10 major employers in the area
   FIND: Companies with 500+ employees headquartered or with major presence
   SOURCES: Chamber of Commerce, Business journals, Economic development sites
   FORMAT: List with company name and brief description
   Example: ["Apple Inc. (tech, 25,000+ employees)", "Kaiser Permanente (healthcare, 8,000 employees)"]

📌 employment_growth_trend - Employment growth direction
   FIND: Is employment growing, stable, or declining?
   SOURCES: BLS area employment statistics, state labor data
   TIMEFRAME: Last 3-5 years
   FORMAT: "Growing" | "Stable" | "Declining" with percentage if available
   Example: "Growing (+3.2% over 3 years)"

📌 population_growth_pct - Population growth rate
   FIND: Population change percentage over recent years
   SOURCES: U.S. Census Bureau, state demographic data
   TIMEFRAME: Last 5-10 years
   FORMAT: Percentage (e.g., 8.5 for 8.5% growth)
   Example: 8.5

📌 unemployment_rate - Current unemployment rate
   FIND: Most recent unemployment rate for the area
   SOURCES: BLS Local Area Unemployment Statistics
   FORMAT: Percentage (e.g., 3.2 for 3.2% unemployment)
   Example: 3.2

📌 key_industries - Top 3-5 industries driving the local economy
   FIND: Major industry sectors in the area
   SOURCES: Economic development reports, BLS industry data
   FORMAT: List of industries
   Example: ["Technology", "Healthcare", "Professional Services", "Education"]

📌 economic_outlook - Overall economic health assessment
   FIND: Expert assessments of economic trends
   SOURCES: Economic development agencies, regional Fed reports
   FORMAT: "Strong" | "Moderate" | "Weak" with supporting details
   Example: "Strong - driven by tech sector growth and low unemployment"

RESEARCH METHODOLOGY:
1. Start with government sources (BLS, Census) for hard data
2. Cross-reference with state/local sources for context
3. Check business journals for major employer updates
4. Synthesize into coherent economic picture
5. Include timeframes and data recency

DEEP RESEARCH MODE: Use multi-step reasoning to:
- Connect employment trends with industry growth
- Understand demographic shifts impacting economy
- Identify leading vs lagging indicators
- Provide context for economic data

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (flexible):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION 1 - JSON (preferred):
{{
  "major_employers": [
    "Apple Inc. (technology, headquarters)",
    "Kaiser Permanente (healthcare, 8,000+ employees)",
    "Chevron (energy, regional office)"
  ],
  "employment_growth_trend": "Growing (+3.2% over 3 years)",
  "population_growth_pct": 8.5,
  "unemployment_rate": 3.2,
  "key_industries": ["Technology", "Healthcare", "Professional Services"],
  "economic_outlook": "Strong - tech sector growth, low unemployment, population influx",
  "data_recency": "2024-2025 data",
  "confidence": "HIGH",
  "source_quality": "Government statistics (BLS, Census) + regional reports"
}}

OPTION 2 - Research synthesis:
Based on deep research of authoritative sources:

major_employers: Apple Inc. (technology headquarters), Kaiser Permanente (healthcare, 8,000+ employees), Chevron (energy regional office)

employment_growth_trend: Growing (+3.2% over 3 years according to BLS data)

population_growth_pct: 8.5% (Census Bureau 2015-2023 data)

unemployment_rate: 3.2% (BLS December 2025)

key_industries: Technology, Healthcare, Professional Services

economic_outlook: Strong - driven by tech sector growth and low unemployment

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIORITY: Authoritative sources and clear data provenance. Show data recency.

✅ SEARCH government sources (BLS, Census) for hard data
✅ SYNTHESIZE across multiple authoritative sources
✅ PROVIDE context and trends, not just raw numbers
✅ CITE sources with .gov domains when possible

Current date: January 2026""",
                system_prompt=f"""You are an expert economic research analyst specializing in regional economic analysis for {city}, {state}.

PRIMARY OBJECTIVE: Conduct deep, multi-step research to gather authoritative economic data about the specified area.

RESEARCH STANDARDS:
- Prioritize government sources (BLS.gov, Census.gov, Federal Reserve)
- Synthesize data across multiple authoritative sources
- Provide context and trends, not just raw numbers
- Include data recency and source quality indicators
- Use multi-step reasoning to connect economic indicators

OUTPUT FLEXIBILITY:
- Preferred: Structured JSON with comprehensive data and source indicators
- Acceptable: Detailed research narrative with clear field labels
- Critical: High-quality authoritative sources in citations

QUALITY OVER SPEED: Take time to find accurate, authoritative data from government and academic sources.

This is supplementary market intelligence - focus on research quality and authoritative sources."""
            )
        )
        
        # Collect tasks (NEW ARCHITECTURE: Accessibility-based)
        tasks = {
            'property_records_ownership': agent1_task,
            'property_details_market': agent2_task,
            'neighborhood_location': agent3_task,
            'financial_inference_estimates': agent4_task,
            'economic_growth_signals': agent5_task
        }
        
        # Execute with timeout
        done, pending = await asyncio.wait(
            tasks.values(),
            timeout=settings.RESEARCH_TIMEOUT,
            return_when=asyncio.ALL_COMPLETED
        )
        
        # Cancel any still-running tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Parse each agent's dual-format response
        results = {}
        agent_names = list(tasks.keys())
        successful_agents = 0
        
        for i, (name, task) in enumerate(tasks.items()):
            if task in done:
                try:
                    raw_result = task.result()
                    parsed = self._parse_dual_format_response(raw_result, name, address)
                    results[name] = parsed
                    results[name]['agent_status'] = 'success'
                    successful_agents += 1
                    # Classify data quality
                    quality_label = 'HIGH CONFIDENCE' if name in ['property_records_ownership', 'property_details_market', 'neighborhood_location'] else 'ESTIMATES'
                    print(f"   ✅ Agent {i+1} ({name}): Success ({parsed['citation_count']} citations, [{quality_label}])")
                except Exception as e:
                    print(f"   ❌ Agent {i+1} ({name}): Failed - {e}")
                    results[name] = {
                        'error': str(e),
                        'agent_status': 'failed',
                        'confidence': 'LOW',
                        'structured_data': {},
                        'detailed_analysis': ''
                    }
            else:
                print(f"   ⏱️  Agent {i+1} ({name}): Timeout")
                results[name] = {
                    'error': 'timeout',
                    'agent_status': 'timeout',
                    'confidence': 'LOW',
                    'structured_data': {},
                    'detailed_analysis': ''
                }
        
        elapsed = time.time() - start_time
        
        # Add metadata
        results['_metadata'] = {
            'property_address': full_address,
            'research_time_seconds': round(elapsed, 2),
            'agents_successful': successful_agents,
            'agents_failed': self.max_agents - successful_agents,
            'total_agents': self.max_agents,
            'cost_cents': self.max_agents * 0.5,
            'timestamp': datetime.now().isoformat(),
            'prompt_strategy': 'conversational_expert_optimized',
            'timeout_enforced': elapsed >= (settings.RESEARCH_TIMEOUT - 0.5)
        }
        
        print(f"   ⏱️  Research complete in {elapsed:.1f}s")
        print(f"   💰 Cost: $0.{results['_metadata']['cost_cents']:02.0f}")
        print(f"   📊 Success rate: {successful_agents}/{self.max_agents} agents")
        
        return results
