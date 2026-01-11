"""
Perplexity AI agent for property research
Handles async API calls to Perplexity's sonar-pro model
"""
import aiohttp
import asyncio
import json
from typing import Dict, Optional, Any
from config import settings

class PerplexityPropertyAgent:
    """Base agent for Perplexity API interactions"""
    
    def __init__(self):
        """Initialize Perplexity agent"""
        self.api_key = settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = settings.PERPLEXITY_MODEL
        
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set in environment")
    
    async def research_async(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2500
    ) -> Dict[str, Any]:
        """
        Async research call to Perplexity API
        
        Args:
            prompt: User query/research request
            system_prompt: Optional system instructions
            temperature: Model temperature (0.0-1.0)
            max_tokens: Maximum response tokens
        
        Returns:
            Dict with parsed JSON response and citations
        
        Raises:
            Exception: On API errors or parsing failures
        """
        if not system_prompt:
            system_prompt = (
                "You are an expert real estate research analyst. "
                "Always return valid, parseable JSON with comprehensive data and citations. "
                "Be precise, factual, and include specific numbers when available."
            )
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "return_citations": True,
                        "search_recency_filter": "month"  # Recent data only
                    },
                    timeout=aiohttp.ClientTimeout(total=45)
                ) as response:
                    
                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Perplexity API error {response.status}: {text}")
                    
                    data = await response.json()
                    
                    # Extract AI response
                    ai_response = data['choices'][0]['message']['content']
                    citations = data.get('citations', [])
                    
                    # Parse JSON from response (handle markdown code blocks)
                    json_str = ai_response
                    if '```json' in json_str:
                        json_str = json_str.split('```json')[1].split('```')[0]
                    elif '```' in json_str:
                        json_str = json_str.split('```')[1].split('```')[0]
                    
                    try:
                        result = json.loads(json_str.strip())
                    except json.JSONDecodeError as e:
                        # If JSON parsing fails, return raw response
                        print(f"⚠️  JSON parsing failed: {e}")
                        print(f"Raw response: {ai_response[:200]}...")
                        result = {
                            "error": "json_parse_failed",
                            "raw_response": ai_response
                        }
                    
                    # Add metadata
                    result['_citations'] = citations
                    result['_raw_response'] = ai_response
                    result['_model'] = self.model
                    
                    return result
            
            except asyncio.TimeoutError:
                raise Exception("Perplexity research timed out (45 seconds)")
            except Exception as e:
                raise Exception(f"Perplexity API error: {str(e)}")
    
    def calculate_cost(self, num_calls: int = 1) -> float:
        """
        Calculate estimated API cost
        
        Args:
            num_calls: Number of API calls
        
        Returns:
            Estimated cost in USD
        """
        cost_per_call = 0.005  # $0.005 per call for sonar-pro
        return num_calls * cost_per_call
    
    async def test_connection(self) -> bool:
        """
        Test API connection with simple query
        
        Returns:
            bool: True if connection successful
        """
        try:
            result = await self.research_async(
                "What is 2+2? Respond with JSON: {\"answer\": number}",
                temperature=0.0,
                max_tokens=100
            )
            return 'answer' in result or '_raw_response' in result
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
