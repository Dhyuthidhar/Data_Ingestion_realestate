"""
Configuration management for Property Agentic Engine
Loads settings from .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Application configuration from environment variables"""
    
    # Perplexity AI
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    PERPLEXITY_MODEL = os.getenv('PERPLEXITY_MODEL', 'sonar-pro')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'property_agentic_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # Application
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Multi-Agent System
    MAX_AGENTS = int(os.getenv('MAX_AGENTS', 5))
    RESEARCH_TIMEOUT = int(os.getenv('RESEARCH_TIMEOUT', 120))
    CACHE_TTL = int(os.getenv('CACHE_TTL', 86400))  # 24 hours
    
    # Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = {
            'PERPLEXITY_API_KEY': cls.PERPLEXITY_API_KEY,
            'DB_PASSWORD': cls.DB_PASSWORD
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(f"❌ Missing required configuration: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def get_db_url(cls):
        """Get PostgreSQL connection URL"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def display_config(cls):
        """Display current configuration (masked)"""
        print("="*60)
        print("⚙️  CONFIGURATION")
        print("="*60)
        print(f"Environment: {cls.ENVIRONMENT}")
        print(f"Debug Mode: {cls.DEBUG}")
        print(f"Max Agents: {cls.MAX_AGENTS}")
        print(f"Cache TTL: {cls.CACHE_TTL / 3600} hours")
        print(f"Perplexity Model: {cls.PERPLEXITY_MODEL}")
        print(f"Database: {cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}")
        print(f"Redis: {cls.REDIS_HOST}:{cls.REDIS_PORT}")
        print("="*60)

# Create singleton instance
settings = Config()
