#!/usr/bin/env python3
"""
Check Environment Configuration
"""
import os
import sys
from pathlib import Path

# Add Django project to path
project_root = Path(__file__).parent.parent.parent / 'riskradar'
sys.path.insert(0, str(project_root))

# Load .env file if it exists
env_path = project_root / '.env'
if env_path.exists():
    print(f"Loading .env from: {env_path}")
    from dotenv import load_dotenv
    load_dotenv(env_path)
else:
    print(f"No .env file found at: {env_path}")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riskradar.settings')
import django
django.setup()

from django.conf import settings


def check_environment():
    """Check environment variable configuration"""
    
    print("=== Environment Variables ===")
    
    # List of important environment variables
    env_vars = [
        'DEBUG',
        'SECRET_KEY',
        'DATABASE_URL',
        'SUPABASE_PROJECT_ID',
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'SUPABASE_JWT_SECRET',
        'SUPABASE_SERVICE_ROLE_KEY',
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        django_value = getattr(settings, var, None)
        
        if var in ['SECRET_KEY', 'SUPABASE_JWT_SECRET', 'SUPABASE_SERVICE_ROLE_KEY']:
            # Show partial values for secrets
            env_display = f"{'SET' if value else 'NOT SET'} ({len(value) if value else 0} chars)"
            django_display = f"{'SET' if django_value else 'NOT SET'} ({len(django_value) if django_value else 0} chars)"
        else:
            env_display = value or 'NOT SET'
            django_display = django_value or 'NOT SET'
        
        print(f"{var}:")
        print(f"  Environment: {env_display}")
        print(f"  Django:      {django_display}")
        print()
    
    print("=== Django REST Framework Configuration ===")
    print(f"Authentication Classes: {settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES', [])}")
    print(f"Permission Classes: {settings.REST_FRAMEWORK.get('DEFAULT_PERMISSION_CLASSES', [])}")
    
    print("\n=== Database Configuration ===")
    db_config = settings.DATABASES.get('default', {})
    print(f"Engine: {db_config.get('ENGINE', 'NOT SET')}")
    print(f"Host: {db_config.get('HOST', 'NOT SET')}")
    print(f"Port: {db_config.get('PORT', 'NOT SET')}")
    print(f"Name: {db_config.get('NAME', 'NOT SET')}")
    
    print("\n=== JWT Secret Validation ===")
    jwt_secret = getattr(settings, 'SUPABASE_JWT_SECRET', None)
    if jwt_secret:
        print(f"✅ JWT Secret is configured ({len(jwt_secret)} characters)")
        print(f"Preview: {jwt_secret[:10]}...{jwt_secret[-10:]}")
        
        # Check if it looks like a proper JWT secret
        if len(jwt_secret) < 32:
            print("⚠️  Warning: JWT secret seems short (should be at least 32 characters)")
        
        if not all(c.isalnum() or c in '+/=' for c in jwt_secret):
            print("⚠️  Warning: JWT secret contains unexpected characters")
            
    else:
        print("❌ JWT Secret is NOT configured")
    

if __name__ == "__main__":
    check_environment() 