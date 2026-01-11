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
        
        OPTIMIZED: 25-second hard timeout for faster responses
        
        Cost: 5 agents × $0.005 = $0.025 per property
        Time: ~18-25 seconds (parallel execution with timeout)
        
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
        tasks = {
            'property_basics': self.research_property_basics(address, city, state),
            'financial_analysis': self.research_financials(address, city, state),
            'neighborhood': self.research_neighborhood(city, state),
            'market_trends': self.research_market_trends(city, state),
            'soft_signals': self.research_soft_signals(city, state)
        }
        
        # Wait for agents with 25-second hard timeout
        done, pending = await asyncio.wait(
            tasks.values(),
            timeout=25,  # Hard cutoff at 25 seconds
            return_when=asyncio.ALL_COMPLETED
        )
        
        # Cancel any still-running tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Collect results
        results = {}
        agent_names = list(tasks.keys())
        
        successful_agents = 0
        for i, (name, task) in enumerate(tasks.items()):
            if task in done:
                try:
                    data = task.result()
                    results[name] = data
                    results[name]['agent_status'] = 'success'
                    successful_agents += 1
                    print(f"   ✅ Agent {i+1} ({name}) complete")
                except Exception as e:
                    print(f"   ⚠️  Agent {i+1} ({name}) failed: {e}")
                    results[name] = {
                        "error": str(e),
                        "data": None,
                        "agent_status": "failed"
                    }
            else:
                print(f"   ⏱️  Agent {i+1} ({name}) timeout - skipped")
                results[name] = {
                    "error": "timeout",
                    "data": None,
                    "agent_status": "timeout"
                }
        
        elapsed = time.time() - start_time
        
        # Add metadata
        results['_metadata'] = {
            'agents_deployed': self.max_agents,
            'agents_successful': successful_agents,
            'agents_failed': self.max_agents - successful_agents,
            'research_depth': 'comprehensive_multi_agent',
            'research_time_seconds': round(elapsed, 2),
            'cost_cents': self.max_agents * 0.5,  # $0.005 = 0.5 cents
            'timestamp': time.time(),
            'timeout_enforced': elapsed >= 24.5  # True if we hit timeout
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
Research: {address}, {city}, {state}

Return JSON:
{{
    "price": current listing/sale price,
    "bedrooms": number,
    "bathrooms": number,
    "square_feet": number,
    "year_built": number,
    "property_type": type,
    "lot_size_sqft": number,
    "parking_spaces": number,
    "price_history": [last 2 sales with dates],
    "property_tax_annual": number,
    "hoa_fees_monthly": number or null
}}

Be concise. Use null if unavailable.
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
Financial analysis: {address}, {city}, {state}

Return JSON:
{{
    "price_per_sqft": number,
    "neighborhood_avg_ppsf": number,
    "estimated_rent_monthly": number,
    "cap_rate_estimate": percentage,
    "comparable_sales": [3 recent similar properties],
    "appreciation_outlook_5yr": "bullish|neutral|bearish",
    "investment_grade": "A|B|C|D"
}}

Focus on key metrics only.
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
Neighborhood: {city}, {state}

Return JSON:
{{
    "schools": [top 3 with ratings/distance],
    "crime": {{"rating": "low|medium|high", "vs_national": "better|worse"}},
    "walkability": {{"walk_score": 0-100, "transit_score": 0-100}},
    "amenities": {{"grocery": count, "restaurants": "excellent|good|fair", "parks": [names]}},
    "commute_downtown_min": number,
    "demographics": {{"median_age": number, "median_income": number}}
}}

Be brief.
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
Market: {city}, {state}

Return JSON:
{{
    "median_price_current": number,
    "price_trend_12mo": percentage,
    "days_on_market_avg": number,
    "inventory_level": "low|balanced|high",
    "market_type": "sellers|balanced|buyers",
    "forecast_12mo": "appreciation|stable|depreciation"
}}

Key metrics only.
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
Economic signals: {city}, {state}

Return JSON:
{{
    "major_employers": [top 5],
    "recent_relocations": [companies with employee counts],
    "job_growth_yoy": percentage,
    "vc_funding_last_year": amount,
    "population_growth_5yr": percentage,
    "sentiment": {{"media_tone": "positive|neutral|negative", "investor_outlook": "bullish|neutral|bearish"}},
    "infrastructure_projects": [key projects]
}}

Focus on actionable signals.
"""
        
        system_prompt = (
            "You are an economic trends analyst specializing in real estate markets. "
            "Return ONLY valid JSON with forward-looking economic indicators. "
            "Focus on signals that predict future property value changes."
        )
        
        return await self.agent.research_async(prompt, system_prompt)
