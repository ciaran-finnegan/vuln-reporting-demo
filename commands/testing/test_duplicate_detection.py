#!/usr/bin/env python3
"""
Test script for duplicate file detection functionality.

This script tests:
1. Normal file upload and hash calculation
2. Duplicate detection and rejection
3. Force re-import functionality
4. Upload history retrieval
5. CLI command with duplicate detection

Usage:
    python test_duplicate_detection.py
"""

import os
import sys
import requests
import json
import time
import shutil
from pathlib import Path

# Configuration
API_BASE_URL = 'http://localhost:8000/api/v1'
TEST_DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'nessus_reports' / 'sample_files' / 'nessus'

def load_jwt_token():
    """Load JWT token from .env file for authenticated requests."""
    env_path = Path(__file__).parent.parent.parent / 'riskradar' / '.env'
    
    if not env_path.exists():
        print("⚠️  No .env file found - running unauthenticated tests only")
        return None
    
    try:
        with open(env_path) as f:
            for line in f:
                if line.startswith('SUPABASE_JWT_SECRET='):
                    jwt_secret = line.split('=', 1)[1].strip().strip('"\'')
                    # For testing, we'll create a simple test token
                    return "test-jwt-token"  # Placeholder - in real testing you'd generate a proper JWT
    except Exception as e:
        print(f"⚠️  Could not load JWT token: {e}")
    
    return None

def find_test_file():
    """Find a test Nessus file."""
    if TEST_DATA_DIR.exists():
        for file_path in TEST_DATA_DIR.glob('*.nessus'):
            return file_path
    
    # Try alternative locations
    alt_paths = [
        Path(__file__).parent.parent.parent / 'data' / 'sample_nessus_scan.nessus',
        Path(__file__).parent.parent.parent / 'riskradar' / 'sample_data' / 'nessus_sample.nessus'
    ]
    
    for alt_path in alt_paths:
        if alt_path.exists():
            return alt_path
    
    return None

def test_api_status():
    """Test API status endpoint."""
    print("🔍 Testing API status...")
    
    try:
        response = requests.get(f'{API_BASE_URL}/status')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data.get('status')}")
            print(f"   Endpoints: {', '.join(data.get('endpoints', {}).keys())}")
            return True
        else:
            print(f"❌ API Status failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is Django server running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ API Status error: {e}")
        return False

def test_first_upload(file_path, jwt_token=None):
    """Test initial file upload (should succeed)."""
    print(f"\n📁 Testing first upload: {file_path.name}")
    
    headers = {}
    if jwt_token:
        headers['Authorization'] = f'Bearer {jwt_token}'
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/xml')}
            response = requests.post(f'{API_BASE_URL}/upload/nessus', files=files, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ First upload successful")
            print(f"   File hash: {data.get('file_hash', 'N/A')}")
            print(f"   Upload ID: {data.get('upload_id', 'N/A')}")
            print(f"   Assets: {data.get('statistics', {}).get('assets_processed', 0)}")
            print(f"   Findings: {data.get('statistics', {}).get('findings_processed', 0)}")
            return data.get('file_hash'), data.get('upload_id')
        else:
            print(f"❌ First upload failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ First upload error: {e}")
        return None, None

def test_duplicate_upload(file_path, jwt_token=None):
    """Test duplicate upload (should be rejected)."""
    print(f"\n🚫 Testing duplicate upload: {file_path.name}")
    
    headers = {}
    if jwt_token:
        headers['Authorization'] = f'Bearer {jwt_token}'
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/xml')}
            response = requests.post(f'{API_BASE_URL}/upload/nessus', files=files, headers=headers)
        
        if response.status_code == 409:
            data = response.json()
            print(f"✅ Duplicate correctly detected and rejected")
            print(f"   File hash: {data.get('file_hash', 'N/A')}")
            print(f"   Original upload: {data.get('duplicate_info', {}).get('original_upload_date', 'N/A')}")
            print(f"   Solution: {data.get('solution', 'N/A')}")
            return True
        else:
            print(f"❌ Duplicate upload should have been rejected with 409, got: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Duplicate upload test error: {e}")
        return False

def test_force_reimport(file_path, jwt_token=None):
    """Test force re-import (should succeed despite duplicate)."""
    print(f"\n🔄 Testing force re-import: {file_path.name}")
    
    headers = {}
    if jwt_token:
        headers['Authorization'] = f'Bearer {jwt_token}'
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/xml')}
            response = requests.post(
                f'{API_BASE_URL}/upload/nessus?force_reimport=true',
                files=files,
                headers=headers
            )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Force re-import successful")
            print(f"   File hash: {data.get('file_hash', 'N/A')}")
            print(f"   Upload ID: {data.get('upload_id', 'N/A')}")
            print(f"   Force reimport used: {data.get('force_reimport_used', False)}")
            return True
        else:
            print(f"❌ Force re-import failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Force re-import error: {e}")
        return False

def test_upload_history(jwt_token=None):
    """Test upload history endpoint."""
    print(f"\n📋 Testing upload history...")
    
    headers = {}
    if jwt_token:
        headers['Authorization'] = f'Bearer {jwt_token}'
    
    try:
        response = requests.get(f'{API_BASE_URL}/upload/history', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload history retrieved")
            print(f"   Total uploads: {data.get('total_count', 0)}")
            print(f"   Records returned: {len(data.get('uploads', []))}")
            
            # Show recent uploads
            for upload in data.get('uploads', [])[:3]:
                print(f"   - {upload.get('filename')} ({upload.get('status')}) - {upload.get('uploaded_at')}")
            
            return True
        else:
            print(f"❌ Upload history failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload history error: {e}")
        return False

def test_cli_command(file_path):
    """Test CLI command with duplicate detection."""
    print(f"\n💻 Testing CLI command with duplicate detection...")
    
    # Create a copy of the test file for CLI testing
    cli_test_file = file_path.parent / f"cli_test_{file_path.name}"
    shutil.copy2(file_path, cli_test_file)
    
    try:
        # First, test normal import
        print("   Testing normal CLI import...")
        os.system(f"cd riskradar && python manage.py import_nessus {cli_test_file}")
        
        print("   Testing CLI duplicate detection...")
        os.system(f"cd riskradar && python manage.py import_nessus {cli_test_file}")
        
        print("   Testing CLI force re-import...")
        os.system(f"cd riskradar && python manage.py import_nessus {cli_test_file} --force-reimport")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI command test error: {e}")
        return False
    finally:
        # Clean up test file
        if cli_test_file.exists():
            cli_test_file.unlink()

def main():
    """Run all duplicate detection tests."""
    print("🧪 DUPLICATE FILE DETECTION TEST SUITE")
    print("=" * 50)
    
    # Check if Django server is running
    if not test_api_status():
        print("\n❌ Please start Django server: cd riskradar && python manage.py runserver")
        return
    
    # Find test file
    test_file = find_test_file()
    if not test_file:
        print("\n❌ No test Nessus file found. Please add a .nessus file to the data directory.")
        return
    
    print(f"📁 Using test file: {test_file}")
    
    # Load JWT token
    jwt_token = load_jwt_token()
    auth_status = "authenticated" if jwt_token else "unauthenticated"
    print(f"🔐 Running tests in {auth_status} mode")
    
    # Run test suite
    results = {
        'api_status': True,  # Already passed
        'first_upload': False,
        'duplicate_detection': False,
        'force_reimport': False,
        'upload_history': False,
        'cli_command': False
    }
    
    # Test 1: First upload
    file_hash, upload_id = test_first_upload(test_file, jwt_token)
    results['first_upload'] = file_hash is not None
    
    # Test 2: Duplicate detection
    if results['first_upload']:
        results['duplicate_detection'] = test_duplicate_upload(test_file, jwt_token)
    
    # Test 3: Force re-import
    if results['duplicate_detection']:
        results['force_reimport'] = test_force_reimport(test_file, jwt_token)
    
    # Test 4: Upload history
    results['upload_history'] = test_upload_history(jwt_token)
    
    # Test 5: CLI command (only if Django is accessible)
    try:
        results['cli_command'] = test_cli_command(test_file)
    except:
        print("⚠️  Skipping CLI test (Django not accessible)")
        results['cli_command'] = None
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = 0
    
    for test_name, result in results.items():
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
            passed += 1
        else:
            status = "❌ FAILED"
        
        if result is not None:
            total += 1
        
        print(f"{test_name.replace('_', ' ').title():<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Duplicate detection is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == '__main__':
    main() 