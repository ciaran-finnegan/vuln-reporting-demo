#!/usr/bin/env python3
"""
Simple test script to verify analytics endpoints are working.
"""

import requests
import json
import jwt
import time
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:8001"
ENDPOINTS_TO_TEST = [
    "/api/v1/logs/analytics/by-level/?timeRange=24h",
    "/api/v1/logs/analytics/error-rate/?timeRange=24h", 
    "/api/v1/logs/analytics/by-source/?timeRange=24h",
    "/api/v1/logs/analytics/top-errors/?timeRange=24h&limit=5",
    "/api/v1/logs/health/"
]

def generate_test_jwt():
    """Generate a test JWT token for admin user"""
    # Use a test secret (replace with actual SUPABASE_JWT_SECRET for real testing)
    secret = "test-secret-key-for-development-only"
    
    payload = {
        'sub': 'admin-test-user-123',
        'email': 'admin@test.com',
        'aud': 'authenticated',
        'role': 'authenticated',
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600,  # 1 hour
        'user_metadata': {
            'is_staff': True,
            'is_superuser': True
        }
    }
    
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token

def test_endpoints():
    """Test all analytics endpoints"""
    print("🔍 Testing Log Analytics Endpoints")
    print("=" * 50)
    
    # Generate test JWT
    token = generate_test_jwt()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"🔑 Using test JWT token")
    print()
    
    for endpoint in ENDPOINTS_TO_TEST:
        url = BASE_URL + endpoint
        print(f"📊 Testing: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                
                # Show some sample data
                if 'data' in data:
                    print(f"   📈 Data points: {len(data['data'])}")
                    if data['data']:
                        print(f"   📝 Sample: {data['data'][0]}")
                elif 'total_logs_24h' in data:
                    print(f"   📊 Total logs (24h): {data['total_logs_24h']}")
                    print(f"   ⚠️  Error rate: {data['error_rate']}%")
                
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   💬 Response: {response.text[:100]}...")
                
        except requests.ConnectionError:
            print(f"   ❌ Connection failed - is Django server running on port 8001?")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()

def check_server():
    """Check if Django server is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/status", timeout=5)
        if response.status_code == 200:
            print("✅ Django server is running")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Cannot connect to Django server")
        print("   Run: cd riskradar && python manage.py runserver 8001")
        return False

if __name__ == "__main__":
    if check_server():
        test_endpoints()
    else:
        print("\n⚠️  Start the Django server first:")
        print("   cd riskradar && python manage.py runserver 8001") 