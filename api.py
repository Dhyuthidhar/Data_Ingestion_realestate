"""
Property Agentic Engine - REST API
Flask application integrating multi-agent research, caching, and database
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
import time
import traceback
from typing import Dict, Any

from collectors.multi_agent_system import MultiAgentResearchSystem
from database import Database
from cache import Cache
from config import settings

# Validate configuration before starting
try:
    settings.validate()
    print("\n" + "="*60)
    print("🚀 Property Agentic Engine API Starting...")
    print("="*60)
    settings.display_config()
except Exception as e:
    print(f"\n❌ Configuration error: {e}")
    print("Please check your .env file\n")
    exit(1)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize core systems
db = Database()
cache = Cache()
research_system = MultiAgentResearchSystem()

print("✅ All systems initialized")
print("="*60 + "\n")

# ============================================
# Health & Status Endpoints
# ============================================

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    Returns system health status
    """
    return jsonify({
        "status": "healthy",
        "service": "property-agentic-engine",
        "version": "1.0.0",
        "timestamp": time.time()
    }), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Detailed system status
    Returns configuration and system health
    """
    try:
        # Test database connection
        db_healthy = True
        try:
            db.get_stats()
        except:
            db_healthy = False
        
        # Test cache connection
        cache_healthy = cache.ping()
        
        return jsonify({
            "status": "operational",
            "systems": {
                "database": "healthy" if db_healthy else "unhealthy",
                "cache": "healthy" if cache_healthy else "unhealthy",
                "api": "healthy"
            },
            "configuration": {
                "max_agents": settings.MAX_AGENTS,
                "cache_ttl_hours": settings.CACHE_TTL / 3600,
                "model": settings.PERPLEXITY_MODEL,
                "environment": settings.ENVIRONMENT
            },
            "version": "1.0.0",
            "timestamp": time.time()
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    System statistics
    Returns database and cache metrics
    """
    try:
        # Database stats
        db_stats = db.get_stats()
        
        # Cache stats
        cache_stats = cache.get_stats()
        
        # Calculate metrics
        total_requests = cache_stats['hits'] + cache_stats['misses']
        cache_hit_rate = (
            (cache_stats['hits'] / total_requests * 100) 
            if total_requests > 0 else 0
        )
        
        # Calculate cost savings
        properties_researched = db_stats.get('total_properties', 0)
        total_cost_without_cache = properties_researched * 0.025
        cached_requests = cache_stats['hits']
        cost_saved = cached_requests * 0.025
        actual_cost = total_cost_without_cache - cost_saved
        
        return jsonify({
            "database": {
                "total_properties": db_stats.get('total_properties', 0),
                "unique_markets": db_stats.get('unique_markets', 0),
                "avg_research_time_seconds": round(
                    db_stats.get('avg_research_time_seconds', 0), 2
                ),
                "properties_today": db_stats.get('properties_today', 0),
                "properties_this_week": db_stats.get('properties_this_week', 0),
                "last_research": str(db_stats.get('last_research_timestamp', 'Never'))
            },
            "cache": {
                "keys_stored": cache_stats['keys'],
                "hit_rate_percent": round(cache_hit_rate, 2),
                "total_hits": cache_stats['hits'],
                "total_misses": cache_stats['misses'],
                "total_requests": total_requests
            },
            "cost_analysis": {
                "total_cost_without_cache": round(total_cost_without_cache, 2),
                "actual_cost_with_cache": round(actual_cost, 2),
                "cost_saved": round(cost_saved, 2),
                "savings_percent": round(
                    (cost_saved / total_cost_without_cache * 100) 
                    if total_cost_without_cache > 0 else 0, 2
                )
            },
            "system": {
                "cache_ttl_hours": settings.CACHE_TTL / 3600,
                "max_agents": settings.MAX_AGENTS,
                "cost_per_property": 0.025
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Failed to retrieve statistics",
            "message": str(e)
        }), 500

# ============================================
# Property Research Endpoints
# ============================================

@app.route('/api/research', methods=['POST'])
def research_property():
    """
    POST endpoint for property research (JSON body)
    
    Request body:
        {
            "address": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "force_refresh": false  // optional
        }
    
    Returns:
        Structured agent results with property data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "Invalid request",
                "message": "Request body must be JSON"
            }), 400
        
        address = data.get('address')
        city = data.get('city')
        state = data.get('state')
        force_refresh = data.get('force_refresh', False)
        
        # Validate required parameters
        if not all([address, city, state]):
            return jsonify({
                "error": "Missing required parameters",
                "required": ["address", "city", "state"],
                "example": {
                    "address": "1148 Greenbrook Drive",
                    "city": "Danville",
                    "state": "CA"
                }
            }), 400
        
        # Validate state code
        if len(state) != 2:
            return jsonify({
                "error": "Invalid state code",
                "message": "State must be a 2-letter code (e.g., 'NY', 'CA')"
            }), 400
        
        property_key = f"{address}, {city}, {state}"
        cache_key = f"property:{address.replace(' ', '_')}_{city.replace(' ', '_')}_{state}"
        
        print(f"\n{'='*60}")
        print(f"📍 Property Request: {property_key}")
        print(f"{'='*60}")
        
        # Check cache (unless force_refresh)
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                print(f"✅ Cache HIT: {property_key}")
                print(f"{'='*60}\n")
                
                return jsonify({
                    "status": "success",
                    "property": {
                        "address": address,
                        "city": city,
                        "state": state
                    },
                    "agents": cached.get('research', {}),
                    "metadata": cached.get('metadata', {}),
                    "source": "cache"
                }), 200
        
        print(f"🔬 Starting fresh research...")
        
        # Research with multi-agent system
        start_time = time.time()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        research_data = loop.run_until_complete(
            research_system.research_comprehensive(address, city, state)
        )
        
        loop.close()
        
        elapsed = time.time() - start_time
        
        # Build response
        complete_data = {
            "property": {
                "address": address,
                "city": city,
                "state": state,
                "full_address": property_key
            },
            "research": research_data,
            "metadata": {
                "researched_at": time.time(),
                "research_time_seconds": round(elapsed, 2),
                "agents_used": settings.MAX_AGENTS,
                "cost_cents": 2.5
            }
        }
        
        # Cache results
        cache.set(cache_key, complete_data, ttl=settings.CACHE_TTL)
        
        # Save to database
        try:
            db.save_property(complete_data)
        except Exception as e:
            print(f"⚠️  Database save failed: {e}")
        
        print(f"✅ Research complete in {elapsed:.1f}s")
        print(f"{'='*60}\n")
        
        return jsonify({
            "status": "success",
            "property": {
                "address": address,
                "city": city,
                "state": state
            },
            "agents": research_data,
            "metadata": complete_data['metadata'],
            "source": "fresh_research"
        }), 200
        
    except Exception as e:
        print(f"❌ Research failed: {e}")
        traceback.print_exc()
        
        return jsonify({
            "error": "Research failed",
            "message": str(e)
        }), 500

@app.route('/api/property', methods=['GET'])
def get_property():
    """
    Get comprehensive property research
    
    Query params:
        address (required): Street address
        city (required): City name
        state (required): 2-letter state code
        force_refresh (optional): Skip cache if 'true'
    
    Returns:
        Complete property research from 5 specialized agents
        
    Process:
        1. Check cache (if not force_refresh)
        2. If cache hit: Return cached data
        3. If cache miss: Research with multi-agent system
        4. Save to database and cache
        5. Return results
    """
    # Extract and validate parameters
    address = request.args.get('address')
    city = request.args.get('city')
    state = request.args.get('state')
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    # Validate required parameters
    if not all([address, city, state]):
        return jsonify({
            "error": "Missing required parameters",
            "required": ["address", "city", "state"],
            "optional": ["force_refresh"],
            "example": "/api/property?address=350 Fifth Avenue&city=New York&state=NY"
        }), 400
    
    # Validate state code
    if len(state) != 2:
        return jsonify({
            "error": "Invalid state code",
            "message": "State must be a 2-letter code (e.g., 'NY', 'CA')"
        }), 400
    
    property_key = f"{address}, {city}, {state}"
    cache_key = f"property:{address.replace(' ', '_')}_{city.replace(' ', '_')}_{state}"
    
    print(f"\n{'='*60}")
    print(f"📍 Property Request: {property_key}")
    print(f"{'='*60}")
    
    # Step 1: Check cache (unless force_refresh)
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            print(f"✅ Cache HIT: {property_key}")
            print(f"   Saved: $0.025 | Response: instant")
            print(f"{'='*60}\n")
            
            return jsonify({
                "status": "success",
                "data": cached,
                "source": "cache",
                "cache_age_hours": round(
                    (time.time() - cached.get('metadata', {}).get('researched_at', time.time())) / 3600, 
                    2
                ),
                "response_time_ms": 10,
                "cost_cents": 0
            }), 200
    
    print(f"🔬 Cache MISS: Starting research...")
    
    # Step 2: Check if another request is already researching this property (locking)
    lock_key = f"researching:{cache_key}"
    
    if cache.exists(lock_key):
        print(f"⏳ Another request is researching this property...")
        
        # Wait for other request to finish (up to 2 minutes)
        for i in range(120):
            time.sleep(1)
            cached = cache.get(cache_key)
            if cached:
                print(f"✅ Research completed by other request (waited {i+1}s)")
                print(f"{'='*60}\n")
                
                return jsonify({
                    "status": "success",
                    "data": cached,
                    "source": "cache_after_wait",
                    "wait_seconds": i + 1
                }), 200
        
        return jsonify({
            "error": "Research timeout",
            "message": "Property research took too long. Please try again."
        }), 504
    
    # Step 3: Acquire lock and start research
    cache.set(lock_key, "researching", ttl=settings.RESEARCH_TIMEOUT)
    
    try:
        start_time = time.time()
        
        # Launch multi-agent research (async)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        research_data = loop.run_until_complete(
            research_system.research_comprehensive(address, city, state)
        )
        
        loop.close()
        
        elapsed = time.time() - start_time
        
        # Build complete response
        complete_data = {
            "property": {
                "address": address,
                "city": city,
                "state": state,
                "full_address": property_key
            },
            "research": research_data,
            "metadata": {
                "researched_at": time.time(),
                "research_time_seconds": round(elapsed, 2),
                "research_quality": "comprehensive_multi_agent",
                "agents_used": settings.MAX_AGENTS,
                "agents_successful": research_data.get('_metadata', {}).get('agents_successful', 0),
                "agents_failed": research_data.get('_metadata', {}).get('agents_failed', 0),
                "data_freshness": "real_time",
                "cache_ttl_hours": settings.CACHE_TTL / 3600,
                "cost_cents": 2.5  # $0.025 = 2.5 cents
            }
        }
        
        # Step 4: Cache for 24 hours
        cache.set(cache_key, complete_data, ttl=settings.CACHE_TTL)
        print(f"   💾 Cached for 24 hours")
        
        # Step 5: Save to database (async, don't block response)
        try:
            db.save_property(complete_data)
            print(f"   💾 Saved to database")
        except Exception as e:
            print(f"   ⚠️  Database save failed (non-critical): {e}")
        
        print(f"✅ Research complete in {elapsed:.1f}s")
        print(f"   Cost: $0.025 | Agents: {complete_data['metadata']['agents_successful']}/5")
        print(f"{'='*60}\n")
        
        return jsonify({
            "status": "success",
            "data": complete_data,
            "source": "fresh_research",
            "research_time_seconds": round(elapsed, 2),
            "cost_cents": 2.5
        }), 200
        
    except Exception as e:
        print(f"❌ Research failed: {e}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        return jsonify({
            "error": "Research failed",
            "message": str(e),
            "property": property_key
        }), 500
        
    finally:
        # Always release lock
        cache.delete(lock_key)

@app.route('/api/property/search', methods=['GET'])
def search_properties():
    """
    Search properties by location
    
    Query params:
        city (optional): Filter by city
        state (optional): Filter by state
        limit (optional): Max results (default: 100)
    """
    city = request.args.get('city')
    state = request.args.get('state')
    limit = int(request.args.get('limit', 100))
    
    if limit > 1000:
        return jsonify({
            "error": "Limit too high",
            "message": "Maximum limit is 1000"
        }), 400
    
    try:
        results = db.search_properties(city=city, state=state, limit=limit)
        
        return jsonify({
            "status": "success",
            "results": results,
            "count": len(results),
            "filters": {
                "city": city,
                "state": state,
                "limit": limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Search failed",
            "message": str(e)
        }), 500

# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

# ============================================
# Main Entry Point
# ============================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎯 API Server Ready!")
    print("="*60)
    print("📡 Endpoints:")
    print("   GET  /health                - Health check")
    print("   GET  /api/status            - System status")
    print("   GET  /api/stats             - Statistics")
    print("   POST /api/research          - Property research (JSON body)")
    print("   GET  /api/property          - Property research (query params)")
    print("   GET  /api/property/search   - Search properties")
    print("="*60)
    print(f"🌐 Running on: http://{settings.FLASK_HOST}:{settings.FLASK_PORT}")
    print("="*60 + "\n")
    
    app.run(
        debug=settings.DEBUG,
        host=settings.FLASK_HOST,
        port=settings.FLASK_PORT
    )
