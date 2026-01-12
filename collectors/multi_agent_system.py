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
    
    def _parse_dual_format_response(self, response: dict, agent_name: str, address: str = "") -> dict:
        """
        Parse dual-format response with structured data and detailed analysis.
        Supports three formats:
        1. Dual format with delimiters (---STRUCTURED_DATA--- and ---DETAILED_ANALYSIS---)
        2. Pure JSON
        3. Conversational text (fallback to regex extraction)
        """
        import json
        
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
        
        # Try dual-format parsing first
        structured_match = re.search(
            r'---STRUCTURED_DATA---\s*(\{.*?\})\s*---END_STRUCTURED_DATA---',
            content,
            re.DOTALL
        )
        analysis_match = re.search(
            r'---DETAILED_ANALYSIS---\s*(.*?)\s*---END_DETAILED_ANALYSIS---',
            content,
            re.DOTALL
        )
        
        if structured_match:
            try:
                result['structured_data'] = json.loads(structured_match.group(1))
                result['parse_method'] = 'dual_format_structured'
                result['parse_success'] = True
            except json.JSONDecodeError:
                pass
        
        if analysis_match:
            result['detailed_analysis'] = analysis_match.group(1).strip()
            if not result['parse_success']:
                result['parse_method'] = 'dual_format_analysis_only'
                result['parse_success'] = True
        
        # If dual format failed, try pure JSON
        if not result['parse_success']:
            try:
                parsed_json = json.loads(content)
                result['structured_data'] = parsed_json
                result['detailed_analysis'] = content
                result['parse_method'] = 'full_json'
                result['parse_success'] = True
            except json.JSONDecodeError:
                pass
        
        # Fallback: conversational text extraction
        if not result['parse_success']:
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
        """
        data = {}
        
        if agent_name == 'property_basics':
            # Extract price
            price_match = re.search(r'\$([\d,]+(?:\.\d+)?(?:\s*(?:million|M))?)', text)
            if price_match:
                price_str = price_match.group(1).replace(',', '')
                if 'million' in price_match.group(0).lower() or 'M' in price_match.group(0):
                    data['last_sold_price'] = float(price_str.replace('million', '').replace('M', '').strip()) * 1000000
                else:
                    data['last_sold_price'] = float(price_str)
            
            # Extract beds/baths
            bed_match = re.search(r'(\d+)\s*bed', text, re.IGNORECASE)
            if bed_match:
                data['bedrooms'] = int(bed_match.group(1))
            
            bath_match = re.search(r'(\d+(?:\.\d+)?)\s*bath', text, re.IGNORECASE)
            if bath_match:
                data['bathrooms'] = float(bath_match.group(1))
            
            # Square footage
            sqft_match = re.search(r'([\d,]+)\s*(?:sq\s*ft|square\s*feet)', text, re.IGNORECASE)
            if sqft_match:
                data['square_feet'] = int(sqft_match.group(1).replace(',', ''))
            
            # Year built
            year_match = re.search(r'built\s+(?:in\s+)?(\d{4})', text, re.IGNORECASE)
            if year_match:
                data['year_built'] = int(year_match.group(1))
            
            # Address verification
            if address:
                address_lower = address.lower().replace(' ', '').replace('-', '')
                text_lower = text.lower().replace(' ', '').replace('-', '')
                data['address_verified'] = address_lower in text_lower
            
            # Property status
            if 'for sale' in text.lower():
                data['current_status'] = 'for sale'
            elif 'sold' in text.lower() or 'off market' in text.lower():
                data['current_status'] = 'sold'
            else:
                data['current_status'] = 'unknown'
        
        elif agent_name == 'financial_analysis':
            # Extract yield
            yield_match = re.search(r'(\d+(?:\.\d+)?)\s*%.*?(?:yield|return)', text, re.IGNORECASE)
            if yield_match:
                data['gross_yield_pct'] = float(yield_match.group(1))
            
            # Extract rent estimates
            rent_match = re.search(r'\$(\d+,?\d*)\s*(?:-|to)\s*\$(\d+,?\d*).*?(?:rent|month)', text, re.IGNORECASE)
            if rent_match:
                data['rent_estimate_low'] = int(rent_match.group(1).replace(',', ''))
                data['rent_estimate_high'] = int(rent_match.group(2).replace(',', ''))
            
            # Price per sqft
            ppsf_match = re.search(r'\$(\d+).*?(?:per|/)\s*(?:sq\s*ft|square\s*foot)', text, re.IGNORECASE)
            if ppsf_match:
                data['price_per_sqft'] = int(ppsf_match.group(1))
        
        elif agent_name == 'neighborhood_intelligence':
            # Extract walk score
            walk_match = re.search(r'walk\s*score.*?(\d+)', text, re.IGNORECASE)
            if walk_match:
                data['walk_score'] = int(walk_match.group(1))
            
            # Safety rating
            if 'very safe' in text.lower() or 'low crime' in text.lower():
                data['safety_rating'] = 'high'
            elif 'unsafe' in text.lower() or 'high crime' in text.lower():
                data['safety_rating'] = 'low'
            else:
                data['safety_rating'] = 'medium'
        
        elif agent_name == 'market_trends':
            # Market type
            if "seller's market" in text.lower() or 'seller market' in text.lower():
                data['market_type'] = 'seller'
            elif "buyer's market" in text.lower() or 'buyer market' in text.lower():
                data['market_type'] = 'buyer'
            else:
                data['market_type'] = 'balanced'
            
            # Days on market
            dom_match = re.search(r'(\d+)\s*days.*?(?:on\s*market|DOM)', text, re.IGNORECASE)
            if dom_match:
                data['days_on_market'] = int(dom_match.group(1))
        
        elif agent_name == 'economic_soft_signals':
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
        
        # AGENT 1: Property Basics (Conversational)
        agent1_task = asyncio.create_task(
            self.agent.research_async(
                prompt=f"""I'm looking at buying {full_address}. Can you help me find current information about this property?

I need to know:
- Is it currently for sale? If so, what's the asking price?
- If not for sale, what did it last sell for and when?
- How many bedrooms and bathrooms does it have?
- What's the square footage?
- What year was it built?
- What type of property is it (house, condo, townhome)?

Please search real estate websites like Zillow, Redfin, and Realtor.com to find this information. 

Give me specific numbers with your sources - I need accurate data to make a buying decision.""",
                system_prompt=f"""You are a real estate research assistant helping a buyer research {full_address}.

CRITICAL INSTRUCTIONS:
1. Search the web immediately for this property on Zillow, Redfin, Realtor.com
2. Find the EXACT property listing or sale record
3. Extract specific numbers (beds, baths, sqft, price, year)
4. Cite which website you found each piece of data on
5. If you can't find the property, say "I couldn't find this property on major real estate sites"

Return your findings in natural language with embedded citations. Include a "data_confidence" assessment (HIGH/MEDIUM/LOW) based on how many sources confirmed the data."""
            )
        )
        
        # AGENT 2: Financial Analysis (MLS-Aware)
        agent2_task = asyncio.create_task(
            self.agent.research_async(
                prompt=f"""I'm analyzing the investment potential of {full_address}.

Can you help me understand:

**Recent Sales in the Area:**
- What have similar homes sold for recently within 0.5 miles?
- Are prices going up or down in this neighborhood?
- What's the typical price per square foot?

**Rental Market:**
- What do similar properties rent for in this area?
- Is this a good rental market?
- What's the typical rent-to-price ratio?

**Investment Potential:**
- Is this neighborhood appreciating?
- What's driving the local real estate market?
- Any red flags I should know about?

Search Zillow, Redfin, and rental sites to give me a realistic assessment.""",
                system_prompt="""You are a real estate investment analyst.

IMPORTANT: You may not be able to find detailed "sold" data because:
- MLS data is restricted to licensed agents
- Public sites often hide recent sale details
- This is normal and NOT your failure

INSTEAD, focus on what IS publicly available:
1. CURRENT listings of similar properties (gives price range)
2. Price trends mentioned in market reports
3. Rental listings on Zillow, Apartments.com, Craigslist
4. Neighborhood price discussions in forums/articles

Be honest about what you CAN and CANNOT find. Say: "Detailed sold comps require MLS access, but based on current listings in the area, similar homes are priced between $X-Y"

Provide useful context even without perfect data."""
            )
        )
        
        # AGENT 3: Neighborhood Intelligence (Personal Framing)
        agent3_task = asyncio.create_task(
            self.agent.research_async(
                prompt=f"""I'm considering moving to the neighborhood around {full_address}.

Can you tell me about:

**Schools:**
- Which schools would my kids attend at this address?
- What are their ratings on GreatSchools?
- Are they considered good schools?

**Getting Around:**
- How walkable is this neighborhood?
- Can I walk to restaurants, stores, parks?
- What's the Walk Score if available?
- Is public transit accessible?

**Safety:**
- How safe is this neighborhood?
- What's the crime rate compared to the rest of {city}?

**The Neighborhood Vibe:**
- What's it like to live here?
- What amenities are nearby (parks, shopping, dining)?
- Who typically lives in this area (families, young professionals, retirees)?

Give me an honest assessment with sources.""",
                system_prompt=f"""You are a neighborhood expert helping someone evaluate {full_address}.

SEARCH STRATEGY:
1. Search "schools near {address}" and look for GreatSchools ratings
2. Search "{address} walk score" to find walkability data
3. Search "{city} {state} crime rate by neighborhood"  
4. Search "{city} {state} neighborhoods" for character/demographics

CRITICAL: Use specific websites:
- GreatSchools.org for school data
- WalkScore.com for walkability
- NeighborhoodScout.com for crime stats
- Local news sites for neighborhood character

Provide a balanced, honest assessment. Mention both pros and cons."""
            )
        )
        
        # AGENT 4: Market Trends (Expert Search Strategy)
        agent4_task = asyncio.create_task(
            self.agent.research_async(
                prompt=f"""I'm trying to understand the real estate market in {city}, {state} right now.

**Current Market:**
- Are home prices going up, down, or staying flat?
- How long do homes typically sit on the market?
- Is it a buyer's market or seller's market?

**Future Outlook:**
- Where do experts think the market is headed?
- Any economic factors I should know about?
- Good time to buy or should I wait?

**This Specific Area:**
- How does {city} compare to other markets?
- What makes this market unique?

Search recent real estate market reports and local news.""",
                system_prompt=f"""You are a real estate market analyst for {city}, {state}.

SEARCH TERMS TO USE:
- "{city} {state} real estate market 2025"
- "{city} housing market trends"
- "{city} home prices forecast"
- "{city} inventory levels"

SOURCES TO PRIORITIZE:
- Redfin market reports
- Zillow market research
- Local news articles about housing
- National Association of Realtors data

Synthesize multiple sources into a clear market assessment. Cite specific data points (median prices, DOM, inventory) when available."""
            )
        )
        
        # AGENT 5: Economic Signals (Forward-Looking)
        agent5_task = asyncio.create_task(
            self.agent.research_async(
                prompt=f"""I'm researching {city}, {state} as a place to invest in real estate.

**Job Market & Economy:**
- What are the major employers?
- Are companies moving in or leaving?
- Is the job market growing?

**Growth & Development:**
- Is the population growing?
- Any major infrastructure projects (transit, highways)?
- New business districts or developments?

**Investment Climate:**
- Do investors see this area as hot or cooling off?
- What's the buzz about {city} in real estate circles?
- Any concerning trends?

Search for recent news, business journals, and economic reports.""",
                system_prompt=f"""You are an economic research analyst focused on {city}, {state}.

SEARCH QUERIES TO RUN:
- "{city} {state} major employers 2025"
- "{city} companies relocating"
- "{city} population growth"
- "{city} development projects"
- "{city} real estate investment outlook"

SOURCES:
- Business journals (local)
- Chamber of Commerce data
- Census data
- Local news about economic development
- Real estate investment forums/blogs

Focus on forward-looking indicators that affect real estate values."""
            )
        )
        
        # Collect tasks
        tasks = {
            'property_basics': agent1_task,
            'financial_analysis': agent2_task,
            'neighborhood_intelligence': agent3_task,
            'market_trends': agent4_task,
            'economic_soft_signals': agent5_task
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
                    print(f"   ✅ Agent {i+1} ({name}): Success ({parsed['citation_count']} citations, parsed: {parsed['parse_method']})")
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
