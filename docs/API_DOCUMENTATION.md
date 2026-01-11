# Property Agentic Engine - API Documentation

## Overview

The Property Agentic Engine provides a REST API for comprehensive real estate property research using 5 specialized AI agents powered by Perplexity AI.

**Base URL:** `http://localhost:5001` (development)

**Architecture:** Multi-agent AI system with 24-hour caching and persistent storage.

**Cost:** $0.025 per property (fresh research) | $0.00 (cached)

---

## Authentication

Currently, the API does not require authentication. Future versions may implement API key authentication.

---

## Endpoints

### 1. Health Check

**GET** `/health` 

Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "property-agentic-engine",
  "version": "1.0.0",
  "timestamp": 1705066800.123
}
```

**Status Codes:**
- `200 OK`: Service is healthy

---

### 2. System Status

**GET** `/api/status` 

Detailed system status including component health.

**Response:**
```json
{
  "status": "operational",
  "systems": {
    "database": "healthy",
    "cache": "healthy",
    "api": "healthy"
  },
  "configuration": {
    "max_agents": 5,
    "cache_ttl_hours": 24.0,
    "model": "sonar-pro",
    "environment": "development"
  },
  "version": "1.0.0",
  "timestamp": 1705066800.123
}
```

**Status Codes:**
- `200 OK`: System operational
- `500 Internal Server Error`: System issues

---

### 3. Statistics

**GET** `/api/stats` 

System statistics including database, cache, and cost analysis.

**Response:**
```json
{
  "database": {
    "total_properties": 150,
    "unique_markets": 25,
    "avg_research_time_seconds": 11.5,
    "properties_today": 12,
    "properties_this_week": 45,
    "last_research": "2025-01-11 14:45:00"
  },
  "cache": {
    "keys_stored": 120,
    "hit_rate_percent": 82.5,
    "total_hits": 850,
    "total_misses": 180,
    "total_requests": 1030
  },
  "cost_analysis": {
    "total_cost_without_cache": 3.75,
    "actual_cost_with_cache": 0.65,
    "cost_saved": 3.10,
    "savings_percent": 82.67
  },
  "system": {
    "cache_ttl_hours": 24.0,
    "max_agents": 5,
    "cost_per_property": 0.025
  }
}
```

**Status Codes:**
- `200 OK`: Statistics retrieved
- `500 Internal Server Error`: Failed to retrieve stats

---

### 4. Property Research (Main Endpoint)

**GET** `/api/property` 

Research comprehensive property information using 5 specialized AI agents.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| address | string | Yes | Street address |
| city | string | Yes | City name |
| state | string | Yes | 2-letter state code |
| force_refresh | boolean | No | Skip cache (default: false) |

**Example Request:**
```bash
GET /api/property?address=350%20Fifth%20Avenue&city=New%20York&state=NY
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "property": {
      "address": "350 Fifth Avenue",
      "city": "New York",
      "state": "NY",
      "full_address": "350 Fifth Avenue, New York, NY"
    },
    "research": {
      "property_basics": {
        "price": 2500000,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "square_feet": 1800,
        "year_built": 1931,
        "property_type": "condo",
        "...": "..."
      },
      "financial_analysis": {
        "price_per_sqft": 1389,
        "investment_grade": "B+",
        "...": "..."
      },
      "neighborhood": {
        "schools": [...],
        "crime": {...},
        "walkability": {...},
        "...": "..."
      },
      "market_trends": {
        "median_home_price_current": 1200000,
        "price_trend_direction": "rising",
        "...": "..."
      },
      "soft_signals": {
        "corporate_employment": {...},
        "innovation_ecosystem": {...},
        "...": "..."
      },
      "_metadata": {
        "agents_deployed": 5,
        "agents_successful": 5,
        "research_depth": "comprehensive_multi_agent"
      }
    },
    "metadata": {
      "researched_at": 1705066800.123,
      "research_time_seconds": 11.2,
      "agents_successful": 5,
      "agents_failed": 0,
      "data_freshness": "real_time",
      "cache_ttl_hours": 24.0,
      "cost_cents": 2.5
    }
  },
  "source": "fresh_research",
  "research_time_seconds": 11.2,
  "cost_cents": 2.5
}
```

**Response (Cached):**
```json
{
  "status": "success",
  "data": {...},
  "source": "cache",
  "cache_age_hours": 2.5,
  "response_time_ms": 7,
  "cost_cents": 0
}
```

**Status Codes:**
- `200 OK`: Property research successful
- `400 Bad Request`: Missing or invalid parameters
- `500 Internal Server Error`: Research failed
- `504 Gateway Timeout`: Research timed out (>2 minutes)

**Performance:**
- Fresh research: 10-15 seconds, $0.025
- Cached response: <100ms, $0.00
- Cache TTL: 24 hours

---

### 5. Property Search

**GET** `/api/property/search` 

Search previously researched properties by location.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| city | string | No | Filter by city |
| state | string | No | Filter by state |
| limit | integer | No | Max results (default: 100, max: 1000) |

**Example Request:**
```bash
GET /api/property/search?city=New%20York&state=NY&limit=10
```

**Response:**
```json
{
  "status": "success",
  "results": [
    {
      "id": 1,
      "address": "350 Fifth Avenue",
      "city": "New York",
      "state": "NY",
      "research_data": {...},
      "created_at": "2025-01-11T14:30:00",
      "updated_at": "2025-01-11T14:30:00"
    },
    ...
  ],
  "count": 10,
  "filters": {
    "city": "New York",
    "state": "NY",
    "limit": 10
  }
}
```

**Status Codes:**
- `200 OK`: Search successful
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Search failed

---

## Response Structure

### Property Research Data

Each property research includes 5 specialized agent reports:

**1. Property Basics**
- Price, bedrooms, bathrooms, square footage
- Year built, property type, lot size
- Price history, property tax, HOA fees
- Listing status, days on market

**2. Financial Analysis**
- Price per sqft, market comparison
- Investment metrics (cap rate, cash-on-cash return)
- Comparable sales analysis
- Cost of ownership estimates
- Investment grade rating

**3. Neighborhood**
- Schools with ratings and distances
- Crime statistics
- Walkability, transit, and bike scores
- Nearby amenities
- Demographics and community character

**4. Market Trends**
- Current median prices and trends
- Price forecasts
- Inventory levels and days on market
- Market type (buyer's/seller's market)
- Best time to buy recommendations

**5. Soft Signals**
- Corporate employment trends
- Innovation ecosystem strength
- Infrastructure projects
- Population and income growth
- Investment sentiment and outlook

---

## Error Responses

All errors follow this structure:
```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

**Common Errors:**

- `400 Bad Request`: Missing or invalid parameters
- `404 Not Found`: Endpoint does not exist
- `500 Internal Server Error`: Server-side error
- `504 Gateway Timeout`: Request timeout

---

## Rate Limiting

Currently no rate limiting is enforced. Future versions may implement:
- 100 requests per hour per IP
- 1000 property researches per day per API key

---

## Best Practices

1. **Cache First**: Check cache before forcing fresh research
2. **Use force_refresh sparingly**: Only when data must be current
3. **Handle errors gracefully**: Implement retry logic with exponential backoff
4. **Monitor costs**: Track API usage and cache hit rates
5. **Batch requests**: Use search endpoint for multiple properties

---

## Examples

### Python
```python
import requests

# Property research
response = requests.get(
    "http://localhost:5001/api/property",
    params={
        "address": "350 Fifth Avenue",
        "city": "New York",
        "state": "NY"
    },
    timeout=180
)

data = response.json()
if data['status'] == 'success':
    property_info = data['data']
    print(f"Price: ${property_info['research']['property_basics']['price']}")
```

### cURL
```bash
# Property research
curl "http://localhost:5001/api/property?address=350%20Fifth%20Avenue&city=New%20York&state=NY"

# Force refresh
curl "http://localhost:5001/api/property?address=350%20Fifth%20Avenue&city=New%20York&state=NY&force_refresh=true"

# Search properties
curl "http://localhost:5001/api/property/search?state=NY&limit=20"

# Statistics
curl "http://localhost:5001/api/stats"
```

### JavaScript
```javascript
// Property research
fetch('http://localhost:5001/api/property?' + new URLSearchParams({
  address: '350 Fifth Avenue',
  city: 'New York',
  state: 'NY'
}))
.then(response => response.json())
.then(data => {
  if (data.status === 'success') {
    console.log('Property:', data.data.property);
    console.log('Source:', data.source);
  }
})
.catch(error => console.error('Error:', error));
```

---

## Support

For issues or questions:
- GitHub Issues: [Your Repository]
- Email: [Your Email]
- Documentation: This file

---

## Changelog

### Version 1.0.0 (2025-01-11)
- Initial release
- 5 specialized AI agents
- 24-hour caching system
- PostgreSQL persistence
- Complete REST API

---
