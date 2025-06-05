#!/usr/bin/env python3
"""
Test admin endpoints locally with proper JWT authentication
"""

import requests
import json
import os
import jwt
import time
from dotenv import load_dotenv

# Load environment variables from local riskradar directory
load_dotenv(dotenv_path='../../riskradar/.env')

# Local API base URL
API_BASE = "http://localhost:8000/api/v1"

# Get Supabase JWT secret from environment
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')

def generate_admin_jwt():
    """Generate an admin JWT token"""
    if not SUPABASE_JWT_SECRET:
        print("❌ SUPABASE_JWT_SECRET not found in environment")
        return None
    
    payload = {
        'sub': 'admin-test-user-123',
        'email': 'admin@riskradar.com', 
        'aud': 'authenticated',
        'role': 'authenticated',
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600,  # 1 hour expiry
        'user_metadata': {
            'is_staff': True,
            'is_superuser': True
        }
    }
    
    try:
        token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm='HS256')
        return token
    except Exception as e:
        print(f"❌ Failed to generate JWT: {e}")
        return None

def test_endpoint_with_auth(endpoint, token, description):
    """Test an endpoint with authentication"""
    print(f"\n🔍 Testing {description}")
    print(f"Endpoint: {endpoint}")
    
    if not token:
        print("❌ No valid token available")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            data = response.json()
            if isinstance(data, dict):
                print(f"Response keys: {list(data.keys())}")
                # Print first few items if it's a list
                if isinstance(data.get('logs'), list) and data['logs']:
                    print(f"First log entry: {json.dumps(data['logs'][0], indent=2)}")
                elif 'total_logs_24h' in data:
                    print(f"Health metrics: {json.dumps(data, indent=2)}")
            elif isinstance(data, list):
                print(f"Returned {len(data)} items")
                if data:
                    print(f"First item: {json.dumps(data[0], indent=2)}")
        elif response.status_code == 403:
            print("❌ FORBIDDEN - User lacks admin permissions")
            print(f"Response: {response.text}")
        elif response.status_code == 401:
            print("❌ UNAUTHORIZED - Token invalid or expired")
            print(f"Response: {response.text}")
        else:
            print(f"❌ ERROR - Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Local Django server not running")
        print("💡 Run: cd ../../riskradar && python manage.py runserver")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_auth_profile(token):
    """Test the auth profile endpoint to verify token works"""
    print(f"\n🔍 Testing Authentication Profile")
    print(f"Endpoint: /auth/profile")
    
    if not token:
        print("❌ No valid token available")
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f"{API_BASE}/auth/profile", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token is valid!")
            data = response.json()
            print(f"User: {data.get('user', {}).get('email', 'Unknown')}")
            print(f"Is Admin: {data.get('permissions', {}).get('is_admin', False)}")
            return True
        else:
            print(f"❌ Token validation failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Local Django server not running")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def check_local_server():
    """Check if local Django server is running"""
    try:
        response = requests.get(f"{API_BASE}/status", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🔐 Testing Risk Radar Admin Endpoints (LOCAL)")
    print("=" * 55)
    
    # Check if server is running
    if not check_local_server():
        print("❌ Local Django server is not running")
        print("💡 Start it with: cd ../../riskradar && python manage.py runserver")
        exit(1)
    
    print("✅ Local Django server is running")
    
    # Generate admin token
    print("\n🔑 Generating admin JWT token...")
    admin_token = generate_admin_jwt()
    
    if not admin_token:
        print("❌ Cannot proceed without valid JWT token")
        exit(1)
    
    print(f"✅ Generated token (first 50 chars): {admin_token[:50]}...")
    
    # Test authentication first
    if not test_auth_profile(admin_token):
        print("❌ Token validation failed, skipping admin endpoint tests")
        exit(1)
    
    # Test admin endpoints
    admin_endpoints = [
        ("/logs/", "System Logs"),
        ("/logs/health/", "System Health Metrics"),
        ("/logs/analytics/error-rate/", "Error Rate Analytics"),
        ("/logs/analytics/by-source/", "Logs by Source"),
        ("/logs/analytics/top-errors/", "Top Errors"),
    ]
    
    print(f"\n📊 Testing {len(admin_endpoints)} admin endpoints...")
    
    for endpoint, description in admin_endpoints:
        test_endpoint_with_auth(endpoint, admin_token, description)
    
    print(f"\n✅ Local admin endpoint testing complete!") 