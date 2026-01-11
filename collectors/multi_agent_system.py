"""
Multi-Agent Research System
Coordinates 5 specialized Perplexity agents for comprehensive property research
"""
import asyncio
import time
from typing import Dict, Any
from collectors.perplexity_agent import PerplexityPropertyAgent
from config import settings

class MultiAgentResearchSystem:
    """Orchestrates multiple specialized research agents"""
    
    def __init__(self):
        """Initialize multi-agent system"""
        self.agent = PerplexityPropertyAgent()
        self.max_agents = settings.MAX_AGENTS
        
    async def research_comprehensive(
        self, 
        address: str, 
        city: str, 
        state: str
    ) -> Dict[str, Any]:
        """
        Deploy 5 specialized agents in parallel for comprehensive research
        
        Cost: 5 agents × $0.005 = $0.025 per property
        Time: ~45-90 seconds (parallel execution)
        
        Args:
            address: Property street address
            city: City name
            state: 2-letter state code
            
        Returns:
            Dict with research from all agents plus metadata
        """
        print(f"   🤖 Deploying {self.max_agents} specialized agents...")
        start_time = time.time()
        
        # Launch all agents in parallel
        tasks = [
            self.research_property_basics(address, city, state),
            self.research_financials(address, city, state),
            self.research_neighborhood(city, state),
            self.research_market_trends(city, state),
            self.research_soft_signals(city, state)
        ]
        
        # Execute all agents concurrently
        agents_data = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle failures gracefully
        results = {}
        agent_names = [
            'property_basics',
            'financial_analysis', 
            'neighborhood',
            'market_trends',
            'soft_signals'
        ]
        
        successful_agents = 0
        for i, data in enumerate(agents_data):
            agent_name = agent_names[i]
            
            if isinstance(data, Exception):
                print(f"   ⚠️  Agent {i+1} ({agent_name}) failed: {data}")
                results[agent_name] = {
                    "error": str(data),
                    "data": None,
                    "agent_status": "failed"
                }
            else:
                results[agent_name] = data
                results[agent_name]['agent_status'] = 'success'
                successful_agents += 1
                print(f"   ✅ Agent {i+1} ({agent_name}) complete")
        
        elapsed = time.time() - start_time
        
        # Add metadata
        results['_metadata'] = {
            'agents_deployed': self.max_agents,
            'agents_successful': successful_agents,
            'agents_failed': self.max_agents - successful_agents,
            'research_depth': 'comprehensive_multi_agent',
            'research_time_seconds': round(elapsed, 2),
            'cost_cents': self.max_agents * 0.5,  # $0.005 = 0.5 cents
            'timestamp': time.time()
        }
        
        print(f"   ⏱️  Research complete in {elapsed:.1f}s")
        print(f"   💰 Cost: $0.{results['_metadata']['cost_cents']:02.0f}")
        
        return results
    
    async def research_property_basics(
        self, 
        address: str, 
        city: str, 
        state: str
    ) -> Dict[str, Any]:
        """
        Agent 1: Property fundamentals
        Researches core property details, features, and specifications
        """
        prompt = f"""
Research comprehensive property basics for: {address}, {city}, {state}

Find and return as JSON:
{{
    "price": current listing or recent sale price (number or null),
    "bedrooms": number of bedrooms (number or null),
    "bathrooms": number of bathrooms (number or null),
    "square_feet": total square footage (number or null),
    "year_built": year property was built (number or null),
    "property_type": "single-family|condo|townhouse|multi-family|other",
    "lot_size_sqft": lot size in square feet (number or null),
    "parking_spaces": number of parking spaces (number or null),
    "price_history": [
        {{"date": "YYYY-MM", "price": number, "event": "sold|listed|price_change"}}
    ],
    "property_tax_annual": annual property tax (number or null),
    "hoa_fees_monthly": monthly HOA fees (number or null),
    "heating_cooling": "description of HVAC system",
    "recent_renovations": "description or null",
    "special_features": ["list of notable features"],
    "listing_status": "active|pending|sold|off_market",
    "days_on_market": number or null
}}

If any data unavailable, use null. Include only factual data with citations.
"""
        
        system_prompt = (
            "You are a property research specialist. "
            "Return ONLY valid JSON with comprehensive property data. "
            "Use null for unavailable data. Be precise with numbers."
        )
        
        return await self.agent.research_async(prompt, system_prompt)
    
    async def research_financials(
        self, 
        address: str, 
        city: str, 
        state: str
    ) -> Dict[str, Any]:
        """
        Agent 2: Financial analysis
        Analyzes investment potential, pricing, and financial metrics
        """
        prompt = f"""
Financial investment analysis for: {address}, {city}, {state}

Calculate and return as JSON:
{{
    "price_per_sqft": price per square foot (number or null),
    "neighborhood_avg_price_per_sqft": area average (number or null),
    "price_vs_market": "above_average|at_average|below_average",
    "estimated_rental_income_monthly": estimated rent (number or null),
    "estimated_cap_rate": capitalization rate percentage (number or null),
    "cash_on_cash_return_estimate": return percentage (number or null),
    "comparable_sales": [
        {{"address": "string", "price": number, "date": "YYYY-MM", "similarity": "high|medium|low"}}
    ],
    "appreciation_5yr_outlook": "bullish|neutral|bearish",
    "appreciation_history_10yr": 10-year appreciation percentage (number or null),
    "insurance_estimate_annual": estimated insurance cost (number or null),
    "maintenance_estimate_annual": estimated maintenance (number or null),
    "total_cost_ownership_monthly": total monthly cost (number or null),
    "investment_grade": "A|B|C|D|F",
    "value_assessment": "undervalued|fairly_valued|overvalued"
}}

Use null for unavailable data. Provide reasoning for grades.
"""
        
        system_prompt = (
            "You are a real estate investment analyst. "
            "Return ONLY valid JSON with financial analysis. "
            "Base estimates on comparable properties and market data."
        )
        
        return await self.agent.research_async(prompt, system_prompt)
    
    async def research_neighborhood(
        self, 
        city: str, 
        state: str
    ) -> Dict[str, Any]:
        """
        Agent 3: Neighborhood deep dive
        Researches schools, crime, walkability, amenities, demographics
        """
        prompt = f"""
Deep neighborhood analysis for: {city}, {state}

Research and return as JSON:
{{
    "schools": [
        {{"name": "string", "rating": number (1-10), "distance_miles": number, "type": "elementary|middle|high"}}
    ],
    "crime": {{
        "rating": "low|medium|high",
        "violent_crime_per_100k": number or null,
        "property_crime_per_100k": number or null,
        "vs_national_avg": "better|worse|similar"
    }},
    "walkability": {{
        "walk_score": number (0-100) or null,
        "transit_score": number (0-100) or null,
        "bike_score": number (0-100) or null
    }},
    "amenities": {{
        "grocery_stores_1mile": number or null,
        "restaurants_variety": "excellent|good|fair|limited",
        "parks_nearby": ["list of park names"],
        "shopping_centers": ["list"],
        "medical_facilities": ["list"]
    }},
    "commute": {{
        "to_downtown_minutes": average time (number or null),
        "to_airport_minutes": average time (number or null),
        "public_transit_options": ["bus|train|metro|light_rail"]
    }},
    "demographics": {{
        "median_age": number or null,
        "median_income": number or null,
        "diversity_index": "high|medium|low"
    }},
    "community_character": "description of neighborhood vibe",
    "future_development": "planned projects or changes"
}}
"""
        
        system_prompt = (
            "You are a neighborhood research specialist. "
            "Return ONLY valid JSON with comprehensive neighborhood data. "
            "Focus on quality of life factors."
        )
        
        return await self.agent.research_async(prompt, system_prompt)
    
    async def research_market_trends(
        self, 
        city: str, 
        state: str
    ) -> Dict[str, Any]:
        """
        Agent 4: Market analysis
        Analyzes current market conditions, trends, and forecasts
        """
        prompt = f"""
Real estate market trends for: {city}, {state}

Analyze and return as JSON:
{{
    "median_home_price_current": current median price (number or null),
    "median_price_12mo_ago": price 12 months ago (number or null),
    "price_trend_percent": year-over-year change (number or null),
    "price_trend_direction": "rising|stable|falling",
    "days_on_market_avg": average days (number or null),
    "inventory_months_supply": months of supply (number or null),
    "inventory_level": "low|balanced|high",
    "price_reductions_percent": percentage of listings with cuts (number or null),
    "market_type": "strong_sellers|sellers|balanced|buyers|strong_buyers",
    "forecast_12mo": "appreciation|stable|depreciation",
    "forecast_confidence": "high|medium|low",
    "seasonal_trends": "description of seasonal patterns",
    "competition_level": "high|medium|low",
    "best_time_to_buy": "recommendation",
    "market_momentum": "accelerating|stable|slowing"
}}
"""
        
        system_prompt = (
            "You are a real estate market analyst. "
            "Return ONLY valid JSON with market trend analysis. "
            "Use recent data and provide actionable insights."
        )
        
        return await self.agent.research_async(prompt, system_prompt)
    
    async def research_soft_signals(
        self, 
        city: str, 
        state: str
    ) -> Dict[str, Any]:
        """
        Agent 5: Economic soft signals
        Researches forward-looking indicators, corporate activity, innovation
        """
        prompt = f"""
Economic soft signals and forward-looking indicators for: {city}, {state}

Research comprehensively and return as JSON:
{{
    "corporate_employment": {{
        "major_employers": ["top 5 companies"],
        "recent_relocations_12mo": [
            {{"company": "string", "employees": number, "date": "YYYY-MM"}}
        ],
        "hiring_announcements": "summary",
        "layoff_activity": "low|medium|high",
        "avg_tech_salary": number or null,
        "job_growth_rate_yoy": percentage (number or null)
    }},
    "innovation_ecosystem": {{
        "vc_funding_last_year": amount in millions (number or null),
        "startups_founded_last_year": number or null,
        "tech_company_presence": "strong|moderate|weak",
        "university_research_strength": "strong|moderate|weak",
        "patent_filings_trend": "increasing|stable|decreasing"
    }},
    "infrastructure": {{
        "transportation_projects": ["list of announced projects"],
        "airport_expansion": "yes|no|planned",
        "public_transit_improvements": "description",
        "broadband_5g_rollout": "complete|in_progress|limited"
    }},
    "economic_indicators": {{
        "population_growth_5yr": percentage (number or null),
        "median_income_growth": percentage (number or null),
        "cost_of_living_trend": "rising_fast|rising|stable",
        "tax_policy_changes": "description or null"
    }},
    "sentiment_narrative": {{
        "media_tone": "positive|neutral|negative",
        "national_attention": "hot_market|emerging|stable|declining",
        "investor_sentiment": "bullish|neutral|bearish",
        "developer_activity": "very_active|active|moderate|low",
        "quality_of_life_ranking": number or null
    }},
    "risk_factors": ["list of potential concerns"],
    "opportunities": ["list of positive signals"],
    "overall_outlook": "very_positive|positive|neutral|concerning"
}}
"""
        
        system_prompt = (
            "You are an economic trends analyst specializing in real estate markets. "
            "Return ONLY valid JSON with forward-looking economic indicators. "
            "Focus on signals that predict future property value changes."
        )
        
        return await self.agent.research_async(prompt, system_prompt)
