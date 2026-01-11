"""
Redis cache module for Property Agentic Engine
Implements 24-hour caching to minimize API costs
"""
import redis
import json
from typing import Optional, Dict, Any
from config import settings

class Cache:
    """Redis cache manager"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis.ping()
            print("✅ Redis connected")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except json.JSONDecodeError as e:
            print(f"Cache JSON decode error for key {key}: {e}")
            # Delete corrupted cache entry
            self.delete(key)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Data to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: from config)
            
        Returns:
            bool: Success status
        """
        try:
            ttl = ttl or settings.CACHE_TTL
            serialized = json.dumps(value)
            self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if key exists
        """
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
            
        Returns:
            bool: Success status
        """
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Redis pattern (e.g., 'property:*')
            
        Returns:
            int: Number of keys deleted
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0
    
    def get_ttl(self, key: str) -> int:
        """
        Get remaining TTL for key
        
        Args:
            key: Cache key
            
        Returns:
            int: Seconds until expiration (-1 if no expiry, -2 if doesn't exist)
        """
        try:
            return self.redis.ttl(key)
        except Exception as e:
            print(f"Cache TTL error: {e}")
            return -2
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics
        
        Returns:
            Dict with cache metrics
        """
        try:
            info = self.redis.info('stats')
            keyspace = self.redis.info('keyspace')
            
            # Extract key count
            db_info = keyspace.get(f'db{settings.REDIS_DB}', {})
            keys_count = db_info.get('keys', 0) if isinstance(db_info, dict) else 0
            
            return {
                'total_connections': info.get('total_connections_received', 0),
                'total_commands': info.get('total_commands_processed', 0),
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'keys': keys_count,
                'hit_rate': self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                )
            }
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {
                'hits': 0,
                'misses': 0,
                'keys': 0,
                'hit_rate': 0.0
            }
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)
    
    def flush_all(self) -> bool:
        """
        Flush all cache data (use with caution!)
        
        Returns:
            bool: Success status
        """
        try:
            self.redis.flushdb()
            print("⚠️  Cache flushed!")
            return True
        except Exception as e:
            print(f"Cache flush error: {e}")
            return False
    
    def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.redis.ping()
        except Exception as e:
            print(f"Redis ping failed: {e}")
            return False
    
    def close(self):
        """Close Redis connection"""
        try:
            self.redis.close()
            print("Redis connection closed")
        except:
            pass
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
