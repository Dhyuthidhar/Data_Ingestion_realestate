"""
Database module for Property Agentic Engine
Handles PostgreSQL connections and operations
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from typing import Dict, List, Optional
from config import settings

class Database:
    """PostgreSQL database manager"""
    
    def __init__(self):
        """Initialize database connection"""
        try:
            self.conn = psycopg2.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD
            )
            self.conn.autocommit = False
            print("✅ Database connected")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def save_property(self, data: Dict) -> bool:
        """
        Save or update property research data
        
        Args:
            data: Dictionary with structure:
                {
                    'property': {'address', 'city', 'state'},
                    'research': {...},
                    'metadata': {'research_time_seconds', 'agents_used', 'cost'}
                }
        
        Returns:
            bool: Success status
        """
        cur = self.conn.cursor()
        
        try:
            # Extract fields
            property_info = data.get('property', {})
            research = data.get('research', {})
            metadata = data.get('metadata', {})
            
            # Insert or update
            cur.execute("""
                INSERT INTO properties (
                    address, city, state,
                    research_data,
                    research_time_seconds,
                    agents_used,
                    research_cost_cents,
                    data_quality
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (address, city, state) 
                DO UPDATE SET
                    research_data = EXCLUDED.research_data,
                    research_time_seconds = EXCLUDED.research_time_seconds,
                    agents_used = EXCLUDED.agents_used,
                    research_cost_cents = EXCLUDED.research_cost_cents,
                    data_quality = EXCLUDED.data_quality,
                    updated_at = NOW()
                RETURNING id;
            """, (
                property_info.get('address'),
                property_info.get('city'),
                property_info.get('state'),
                json.dumps(research),
                metadata.get('research_time_seconds'),
                metadata.get('agents_used', 5),
                metadata.get('cost_cents', 25),
                metadata.get('quality', 'high')
            ))
            
            property_id = cur.fetchone()[0]
            self.conn.commit()
            
            print(f"   💾 Saved to database (ID: {property_id})")
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"   ❌ Database save failed: {e}")
            return False
        finally:
            cur.close()
    
    def get_property(self, address: str, city: str, state: str) -> Optional[Dict]:
        """
        Get property by location
        
        Args:
            address: Street address
            city: City name
            state: 2-letter state code
            
        Returns:
            Dict with property data or None if not found
        """
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cur.execute("""
                SELECT 
                    id,
                    address,
                    city,
                    state,
                    research_data,
                    research_time_seconds,
                    agents_used,
                    research_cost_cents,
                    data_quality,
                    created_at,
                    updated_at
                FROM properties 
                WHERE address = %s AND city = %s AND state = %s
            """, (address, city, state))
            
            result = cur.fetchone()
            return dict(result) if result else None
            
        except Exception as e:
            print(f"Database query error: {e}")
            return None
        finally:
            cur.close()
    
    def get_stats(self) -> Dict:
        """
        Get system statistics
        
        Returns:
            Dict with database statistics
        """
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cur.execute("SELECT * FROM property_stats;")
            stats = cur.fetchone()
            return dict(stats) if stats else {}
        except Exception as e:
            print(f"Stats query error: {e}")
            return {}
        finally:
            cur.close()
    
    def search_properties(
        self, 
        city: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search properties by location
        
        Args:
            city: Filter by city (optional)
            state: Filter by state (optional)
            limit: Maximum results to return
            
        Returns:
            List of property dictionaries
        """
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            query = "SELECT * FROM properties WHERE 1=1"
            params = []
            
            if city:
                query += " AND city = %s"
                params.append(city)
            
            if state:
                query += " AND state = %s"
                params.append(state)
            
            query += " ORDER BY updated_at DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            results = cur.fetchall()
            
            return [dict(r) for r in results]
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
        finally:
            cur.close()
    
    def get_recent_properties(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """
        Get recently researched properties
        
        Args:
            hours: How many hours back to look
            limit: Maximum results
            
        Returns:
            List of recent properties
        """
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cur.execute("""
                SELECT * FROM properties
                WHERE created_at > NOW() - INTERVAL '%s hours'
                ORDER BY created_at DESC
                LIMIT %s
            """, (hours, limit))
            
            results = cur.fetchall()
            return [dict(r) for r in results]
            
        except Exception as e:
            print(f"Recent query error: {e}")
            return []
        finally:
            cur.close()
    
    def delete_property(self, property_id: int) -> bool:
        """Delete property by ID"""
        cur = self.conn.cursor()
        
        try:
            cur.execute("DELETE FROM properties WHERE id = %s", (property_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Delete error: {e}")
            return False
        finally:
            cur.close()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
