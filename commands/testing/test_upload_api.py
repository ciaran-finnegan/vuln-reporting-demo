#!/usr/bin/env python3
"""
Test script for the Django Upload API
Tests various scenarios including successful uploads, error handling, and validation
"""

import requests
import json
import os
import jwt
import time
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api/v1"

# Load environment variables
from dotenv import load_dotenv

# Load .env file from riskradar directory (adjust path since we're in commands/testing/)
load_dotenv(dotenv_path='../../riskradar/.env')

# Get Supabase JWT secret from environment
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')
if not SUPABASE_JWT_SECRET:
    print("⚠️  SUPABASE_JWT_SECRET not found in environment variables")
    print("💡 Make sure riskradar/.env file exists with SUPABASE_JWT_SECRET set")
    SUPABASE_JWT_SECRET = None

def generate_test_jwt(user_email="test@example.com", user_id="test-user-123"):
    """Generate a test JWT token that mimics Supabase format"""
    payload = {
        'sub': user_id,  # Supabase user ID
        'email': user_email,
        'aud': 'authenticated',
        'role': 'authenticated',
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600,  # Expires in 1 hour
        'user_metadata': {
            'first_name': 'Test',
            'last_name': 'User'
        }
    }
    
    try:
        token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm='HS256')
        return token
    except Exception as e:
        print(f"⚠️ Could not generate JWT token: {e}")
        print("💡 Make sure to update SUPABASE_JWT_SECRET in this script")
        return None

def test_api_status():
    """Test the API status endpoint"""
    print("🔍 Testing API status...")
    response = requests.get(f"{API_BASE}/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_upload_info():
    """Test the upload info endpoint"""
    print("📋 Testing upload info...")
    response = requests.get(f"{API_BASE}/upload/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_nessus_upload(file_path):
    """Test uploading a Nessus file"""
    print(f"📤 Testing Nessus upload: {os.path.basename(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE}/upload/nessus", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print("✅ Upload successful!")
        print(f"Filename: {data['filename']}")
        print(f"File size: {data['file_size']:,} bytes")
        print(f"Assets processed: {data['statistics']['assets_processed']}")
        print(f"Vulnerabilities processed: {data['statistics']['vulnerabilities_processed']}")
        print(f"Findings processed: {data['statistics']['findings_processed']}")
        print(f"Assets created: {data['parser_details']['assets_created']}")
        print(f"Vulnerabilities created: {data['parser_details']['vulnerabilities_created']}")
        print(f"Findings created: {data['parser_details']['findings_created']}")
        if data['statistics']['errors']:
            print(f"⚠️  Errors: {len(data['statistics']['errors'])}")
    else:
        print(f"❌ Upload failed: {response.text}")
    print()

def test_authenticated_upload(file_path, token):
    """Test uploading a Nessus file with authentication"""
    print(f"🔐 Testing authenticated Nessus upload: {os.path.basename(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    if not token:
        print("❌ No valid token provided")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE}/upload/nessus", files=files, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print("✅ Authenticated upload successful!")
        print(f"Filename: {data['filename']}")
        print(f"Uploaded by: {data.get('uploaded_by', 'Anonymous')}")
        print(f"Authentication: {data.get('authenticated', 'No')}")
    else:
        print(f"❌ Upload failed: {response.text}")
    print()

def test_invalid_token_upload(file_path):
    """Test uploading with an invalid token"""
    print(f"🚫 Testing upload with invalid token: {os.path.basename(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    # Use an invalid token
    headers = {'Authorization': 'Bearer invalid-token-12345'}
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE}/upload/nessus", files=files, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 403:
        print("✅ Correctly rejected invalid token")
    else:
        print(f"Response: {response.json()}")
    print()

def test_invalid_file():
    """Test uploading an invalid file"""
    print("🚫 Testing invalid file upload...")
    
    # Create a temporary text file
    with open('/tmp/test.txt', 'w') as f:
        f.write("This is not a Nessus file")
    
    with open('/tmp/test.txt', 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE}/upload/nessus", files=files)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Clean up
    os.unlink('/tmp/test.txt')
    print()

def test_no_file():
    """Test uploading without a file"""
    print("❌ Testing upload without file...")
    response = requests.post(f"{API_BASE}/upload/nessus")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

if __name__ == "__main__":
    print("🚀 Testing Risk Radar Upload API with Authentication")
    print("=" * 60)
    
    # Test basic endpoints
    test_api_status()
    test_upload_info()
    
    # Test unauthenticated upload
    nessus_file = "../../data/nessus_reports/sample_files/nessus/nessus_v_unknown.nessus"
    print("📤 UNAUTHENTICATED UPLOAD TEST")
    print("-" * 30)
    test_nessus_upload(nessus_file)
    
    # Test authenticated upload
    print("🔐 AUTHENTICATION TESTS")
    print("-" * 30)
    test_token = generate_test_jwt()
    if test_token:
        test_authenticated_upload(nessus_file, test_token)
    
    # Test invalid token
    test_invalid_token_upload(nessus_file)
    
    # Test error scenarios
    print("🚫 ERROR SCENARIO TESTS")
    print("-" * 30)
    test_invalid_file()
    test_no_file()
    
    print("✅ All authentication tests completed!")
    print("\n💡 Tips:")
    print("- Update SUPABASE_JWT_SECRET in this script with your actual secret to test authentication")
    print("- The API currently allows both authenticated and unauthenticated uploads")
    print("- Authentication adds user context but doesn't restrict access (MVP design)") 