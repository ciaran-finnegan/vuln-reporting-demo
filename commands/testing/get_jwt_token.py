#!/usr/bin/env python3
"""
Get JWT Token from Supabase - Authentication Script
"""
import os
import sys
import requests
import json
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

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riskradar.settings')
import django
django.setup()

from django.conf import settings


def get_jwt_token():
    """Get JWT token from Supabase via API"""
    
    supabase_url = getattr(settings, 'SUPABASE_URL', None)
    supabase_anon_key = getattr(settings, 'SUPABASE_ANON_KEY', None)
    
    if not supabase_url or not supabase_anon_key:
        print("❌ Supabase URL or ANON KEY not configured")
        return None
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Anon Key: {supabase_anon_key[:20]}...")
    
    # Get user credentials
    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required")
        return None
    
    # Sign in to Supabase
    auth_url = f"{supabase_url}/auth/v1/token?grant_type=password"
    
    headers = {
        'apikey': supabase_anon_key,
        'Authorization': f'Bearer {supabase_anon_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'email': email,
        'password': password
    }
    
    print(f"\n🔐 Attempting to sign in to Supabase...")
    
    try:
        response = requests.post(auth_url, headers=headers, json=data)
        
        if response.status_code == 200:
            auth_data = response.json()
            access_token = auth_data.get('access_token')
            
            if access_token:
                print("✅ Successfully authenticated!")
                print(f"JWT Token: {access_token}")
                print(f"\nToken length: {len(access_token)} characters")
                print(f"Token preview: {access_token[:50]}...{access_token[-20:]}")
                
                # Show user info
                user = auth_data.get('user', {})
                print(f"\nUser Info:")
                print(f"  Email: {user.get('email')}")
                print(f"  ID: {user.get('id')}")
                print(f"  Created: {user.get('created_at')}")
                
                # Test the token
                print(f"\n🧪 Testing token with Risk Radar API...")
                test_token(access_token)
                
                return access_token
            else:
                print("❌ No access token in response")
                print(f"Response: {auth_data}")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get('error_description', error_data.get('msg', 'Unknown error'))
                print(f"Error: {error_msg}")
                
                if 'Invalid login credentials' in error_msg:
                    print("\n💡 Tips:")
                    print("  - Check your email and password")
                    print("  - Make sure the user exists in Supabase")
                    print("  - Try creating a user in the Supabase dashboard first")
    
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
    
    return None


def test_token(token):
    """Test the JWT token with Risk Radar API"""
    
    base_url = "https://riskradar.dev.securitymetricshub.com"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test auth status
    try:
        response = requests.get(f"{base_url}/api/v1/auth/status", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Auth Status: {data}")
        else:
            print(f"❌ Auth Status Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing auth status: {e}")
    
    # Test auth profile
    try:
        response = requests.get(f"{base_url}/api/v1/auth/profile", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Auth Profile: {data}")
        else:
            print(f"❌ Auth Profile Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing auth profile: {e}")


def create_test_user():
    """Create a test user in Supabase (requires service role key)"""
    
    supabase_url = getattr(settings, 'SUPABASE_URL', None)
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not service_key:
        print("❌ SUPABASE_SERVICE_ROLE_KEY not found")
        print("💡 You can find this in your Supabase dashboard under Settings → API")
        return
    
    email = input("Enter email for new user: ").strip()
    password = input("Enter password for new user: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required")
        return
    
    # Create user via admin API
    admin_url = f"{supabase_url}/auth/v1/admin/users"
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'email': email,
        'password': password,
        'email_confirm': True
    }
    
    try:
        response = requests.post(admin_url, headers=headers, json=data)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User created successfully!")
            print(f"User ID: {user_data.get('id')}")
            print(f"Email: {user_data.get('email')}")
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error creating user: {e}")


if __name__ == "__main__":
    print("=== Supabase JWT Token Generator ===")
    print()
    print("Options:")
    print("1. Sign in with existing user")
    print("2. Create new test user (requires service role key)")
    print()
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        token = get_jwt_token()
        if token:
            print(f"\n📋 Copy this token for testing:")
            print(f"{token}")
    elif choice == "2":
        create_test_user()
        print("\nAfter creating the user, run this script again and choose option 1")
    else:
        print("Invalid choice") 