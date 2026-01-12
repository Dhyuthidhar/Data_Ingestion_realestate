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
        max_tokens: int = 4000
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
            system_prompt = """You are a thorough real estate research assistant with web search capabilities.

PRIMARY OBJECTIVE: Search the web and find accurate property data.

OUTPUT FLEXIBILITY:
- Preferred: Return structured JSON when you have the data
- Acceptable: Return findings in narrative format with field labels
- The system can parse multiple formats - focus on data quality first

SEARCH PROCESS:
1. Visit the specific property listing sites mentioned in the prompt (Zillow, Redfin, Realtor.com)
2. Extract actual data from those property pages
3. Include property-specific URLs in citations (e.g., zillow.com/homes/1148-Greenbrook...)
4. Use null for fields you genuinely cannot find after searching

CRITICAL: Your citations should include property-specific sites (Zillow, Redfin, Realtor.com), 
not generic JSON tutorial sites or documentation sites. If your response has all null values, 
it means you didn't search properly.

Format is less important than finding accurate data. We have robust parsing that can handle:
- Pure JSON: {"field": "value"}
- Structured text: "field: value"
- Narrative: "I found that the field is value..."

What matters most:
✅ SEARCH the property listing sites
✅ EXTRACT real data from those pages
✅ INCLUDE field names in your response
✅ CITE property-specific URLs

❌ DO NOT return all nulls without searching
❌ DO NOT cite generic tutorial or documentation sites
❌ DO NOT worry about perfect format - just find the data"""
        
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
                            {"role": "user", "content": f"SEARCH THE WEB and {prompt}"}  # Prepend SEARCH instruction
                        ],
                        "temperature": 0.1,  # Lower temperature for consistent JSON output
                        "max_tokens": 3500,  # Increased from default for complete responses
                        "return_citations": True,
                        "return_related_questions": False,
                        "search_recency_filter": "month"  # Prefer recent data
                        # NOTE: search_domain_filter removed - it prevents Perplexity from finding data
                    },
                    timeout=aiohttp.ClientTimeout(total=settings.RESEARCH_TIMEOUT)
                ) as response:
                    
                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Perplexity API error {response.status}: {text}")
                    
                    data = await response.json()
                    
                    # Extract AI response
                    ai_response = data['choices'][0]['message']['content']
                    citations = data.get('citations', [])
                    
                    # If citations are limited, extract URLs from response content
                    if len(citations) < 3:
                        import re
                        url_pattern = r'https?://[^\s\)\]"\'>]+'
                        found_urls = re.findall(url_pattern, ai_response)
                        # Add unique URLs not already in citations
                        for url in found_urls:
                            if url not in citations:
                                citations.append(url)
                    
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
                    
                    # Normalize response structure
                    result = self._normalize_response(result, citations, ai_response)
                    
                    return result
            
            except asyncio.TimeoutError:
                raise Exception(f"Perplexity research timed out ({settings.RESEARCH_TIMEOUT} seconds)")
            except Exception as e:
                raise Exception(f"Perplexity API error: {str(e)}")
    
    def _normalize_response(self, raw_result: dict, citations: list, ai_response: str) -> dict:
        """
        Normalize and validate response structure
        Ensures consistent format across all agent responses
        """
        # Add metadata
        raw_result['_citations'] = citations
        raw_result['_raw_response'] = ai_response
        raw_result['_model'] = self.model
        raw_result['_citation_count'] = len(citations)
        
        # Ensure response is a dict (not string or other type)
        if not isinstance(raw_result, dict):
            return {
                'error': 'invalid_response_type',
                'raw_response': str(raw_result),
                '_citations': citations,
                '_raw_response': ai_response,
                '_model': self.model
            }
        
        # If parsing failed, try to extract useful info from raw response
        if raw_result.get('error') == 'json_parse_failed':
            # Try to find JSON-like structures in the response
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response)
            if json_match:
                try:
                    import json
                    parsed = json.loads(json_match.group())
                    raw_result.update(parsed)
                    del raw_result['error']
                except:
                    pass  # Keep original error
        
        return raw_result
    
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
