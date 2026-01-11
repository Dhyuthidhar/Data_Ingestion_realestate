#!/usr/bin/env python3
"""
Environment configuration validator
Checks that all required settings are present and valid
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings

def check_environment():
    """Validate environment configuration"""
    print("\n🔍 Validating environment configuration...")
    print("")
    
    # Check critical settings
    checks = {
        'Perplexity API Key': settings.PERPLEXITY_API_KEY,
        'Database Password': settings.DB_PASSWORD,
        'Database Name': settings.DB_NAME,
        'Database User': settings.DB_USER
    }
    
    all_valid = True
    
    for name, value in checks.items():
        if value:
            print(f"  ✅ {name}: {'*' * 8}")
        else:
            print(f"  ❌ {name}: NOT SET")
            all_valid = False
    
    print("")
    settings.display_config()
    
    if not all_valid:
        print("\n❌ Configuration incomplete!")
        print("Please update your .env file with missing values")
        print("")
        return False
    
    print("\n✅ Configuration valid!")
    print("")
    return True

if __name__ == "__main__":
    try:
        success = check_environment()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
