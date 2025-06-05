#!/usr/bin/env python3
"""
Test JWT Authentication - Debug Script
"""
import os
import sys
import requests
import json
from pathlib import Path

# Add Django project to path
project_root = Path(__file__).parent.parent.parent / 'riskradar'
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riskradar.settings')
import django
django.setup()

from django.conf import settings


def test_jwt_auth():
    """Test JWT authentication with detailed debugging"""
    
    # Check environment variables
    print("=== Environment Check ===")
    jwt_secret = getattr(settings, 'SUPABASE_JWT_SECRET', None)
    print(f"SUPABASE_JWT_SECRET: {'SET' if jwt_secret else 'NOT SET'}")
    if jwt_secret:
        print(f"JWT Secret length: {len(jwt_secret)}")
        print(f"JWT Secret preview: {jwt_secret[:10]}...{jwt_secret[-5:]}")
    
    supabase_url = getattr(settings, 'SUPABASE_URL', None)
    print(f"SUPABASE_URL: {supabase_url}")
    
    # Test endpoints
    base_url = "https://riskradar.dev.securitymetricshub.com"
    # base_url = "http://localhost:8000"  # Uncomment for local testing
    
    print(f"\n=== Testing Endpoints ===")
    print(f"Base URL: {base_url}")
    
    # Test unauthenticated endpoint
    print("\n1. Testing unauthenticated endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test upload info endpoint (should work without auth)
    print("\n2. Testing upload info endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/upload/info")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test auth status endpoint without token
    print("\n3. Testing auth status without token...")
    try:
        response = requests.get(f"{base_url}/api/v1/auth/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with JWT token (you'll need to provide this)
    jwt_token = input("\nEnter your JWT token (or press Enter to skip): ").strip()
    
    if jwt_token:
        print("\n=== Testing with JWT Token ===")
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        
        # Test auth status with token
        print("\n4. Testing auth status with token...")
        try:
            response = requests.get(f"{base_url}/api/v1/auth/status", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
            else:
                print(f"Error response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test auth profile with token
        print("\n5. Testing auth profile with token...")
        try:
            response = requests.get(f"{base_url}/api/v1/auth/profile", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
            else:
                print(f"Error response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test admin endpoint (logs)
        print("\n6. Testing admin endpoint (logs)...")
        try:
            response = requests.get(f"{base_url}/api/v1/logs/?limit=5", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
            else:
                print(f"Error response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Decode JWT token locally for debugging
    if jwt_token and jwt_secret:
        print("\n=== Local JWT Debugging ===")
        try:
            import jwt
            
            # Decode without verification
            unverified = jwt.decode(jwt_token, options={"verify_signature": False})
            print(f"Unverified payload: {json.dumps(unverified, indent=2)}")
            
            # Try to decode with verification
            try:
                verified = jwt.decode(
                    jwt_token,
                    jwt_secret,
                    algorithms=['HS256'],
                    audience='authenticated'
                )
                print("✅ JWT signature verification PASSED")
                print(f"Verified payload: {json.dumps(verified, indent=2)}")
            except jwt.InvalidSignatureError:
                print("❌ JWT signature verification FAILED")
                print("This means the SUPABASE_JWT_SECRET is incorrect")
            except jwt.ExpiredSignatureError:
                print("❌ JWT token has EXPIRED")
            except jwt.InvalidAudienceError:
                print("❌ JWT audience is invalid")
            except Exception as e:
                print(f"❌ JWT verification failed: {e}")
                
        except ImportError:
            print("PyJWT not available for local testing")
        except Exception as e:
            print(f"Error decoding JWT: {e}")
    

if __name__ == "__main__":
    test_jwt_auth() 