#!/usr/bin/env python3
"""
Debug Authentication Issue with Specific JWT Token
"""
import os
import sys
from pathlib import Path

# Add Django project to path
project_root = Path(__file__).parent.parent.parent / 'riskradar'
sys.path.insert(0, str(project_root))

# Load .env file
env_path = project_root / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riskradar.settings')
import django
django.setup()

from core.authentication import SupabaseJWTAuthentication
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User

def debug_authentication():
    """Debug authentication with the specific JWT token"""
    
    # Your specific token from the test output
    token = 'eyJhbGciOiJIUzI1NiIsImtpZCI6IjAxcStiVGNnQ0p4TFpiTmkiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2pmY3Bmb2VodGNsZG1hcHBrZHNtLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI4Y2VjYmEzMy1jNzY0LTQzOTQtOTAzMy03NDgxMzllNGNjMTciLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzQ5MTI0NzE2LCJpYXQiOjE3NDkxMjExMTYsImVtYWlsIjoiY2lhcmFuLmZpbm5lZ2FuQGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzQ5MTIxMTE2fV0sInNlc3Npb25faWQiOiI1ZTAzMmVhMi04MTBiLTQ4NDMtYjIxYi1jM2JmMTUzNGQ3NzQiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.X0dGxT1mfHEnYOweX_akFAKEM8tYsimdZj3L5z0snX0'
    
    print("=== Debug JWT Authentication ===")
    print(f"Token length: {len(token)}")
    print(f"Token preview: {token[:50]}...{token[-20:]}")
    
    # Test the authentication backend directly
    auth = SupabaseJWTAuthentication()
    factory = APIRequestFactory()
    
    # Create a fake request with the token
    request = factory.get('/api/v1/auth/status')
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    
    print(f"\n=== Testing Authentication Backend ===")
    
    # Try to authenticate
    try:
        result = auth.authenticate(request)
        print(f'✅ Authentication result: {result}')
        
        if result:
            user, token_payload = result
            print(f'✅ User: {user}')
            print(f'✅ User email: {user.email}')
            print(f'✅ User is_staff: {user.is_staff}')
            print(f'✅ Token payload keys: {list(token_payload.keys())}')
            print(f'✅ Token email: {token_payload.get("email")}')
            print(f'✅ Token sub: {token_payload.get("sub")}')
        else:
            print('❌ Authentication returned None')
            
    except Exception as e:
        print(f'❌ Authentication failed with error: {e}')
        import traceback
        traceback.print_exc()
    
    # Check if user exists in database
    print(f"\n=== Checking Database ===")
    try:
        user = User.objects.get(email='ciaran.finnegan@gmail.com')
        print(f'✅ User exists in database: {user}')
        print(f'✅ User ID: {user.id}')
        print(f'✅ User is_staff: {user.is_staff}')
        print(f'✅ User is_active: {user.is_active}')
    except User.DoesNotExist:
        print('❌ User does not exist in database')
        print('💡 User will be created during authentication')
    except Exception as e:
        print(f'❌ Error checking user: {e}')

def test_api_endpoint():
    """Test the actual API endpoint"""
    print(f"\n=== Testing API Endpoint ===")
    
    import requests
    
    token = 'eyJhbGciOiJIUzI1NiIsImtpZCI6IjAxcStiVGNnQ0p4TFpiTmkiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2pmY3Bmb2VodGNsZG1hcHBrZHNtLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI4Y2VjYmEzMy1jNzY0LTQzOTQtOTAzMy03NDgxMzllNGNjMTciLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzQ5MTI0NzE2LCJpYXQiOjE3NDkxMjExMTYsImVtYWlsIjoiY2lhcmFuLmZpbm5lZ2FuQGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzQ5MTIxMTE2fV0sInNlc3Npb25faWQiOiI1ZTAzMmVhMi04MTBiLTQ4NDMtYjIxYi1jM2JmMTUzNGQ3NzQiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.X0dGxT1mfHEnYOweX_akFAKEM8tYsimdZj3L5z0snX0'
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test local endpoint first
        response = requests.get('http://localhost:8000/api/v1/auth/status', headers=headers)
        print(f"Local endpoint status: {response.status_code}")
        print(f"Local endpoint response: {response.text}")
    except Exception as e:
        print(f"❌ Local endpoint error: {e}")
    
    try:
        # Test production endpoint
        response = requests.get('https://riskradar.dev.securitymetricshub.com/api/v1/auth/status', headers=headers)
        print(f"Production endpoint status: {response.status_code}")
        print(f"Production endpoint response: {response.text}")
    except Exception as e:
        print(f"❌ Production endpoint error: {e}")

if __name__ == "__main__":
    debug_authentication()
    test_api_endpoint() 