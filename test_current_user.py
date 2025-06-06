#!/usr/bin/env python3
"""
Test script to check current user admin status and provide instructions for making users admin.
Run this script to see your current authentication status.
"""

import requests
import json

def test_user_status():
    """Test the current user's authentication status"""
    
    print("🔍 Risk Radar User Admin Status Checker")
    print("=" * 50)
    
    # You need to get your JWT token from the browser dev tools
    print("\n📋 Instructions:")
    print("1. Go to https://riskradar.dev.securitymetricshub.com")
    print("2. Open browser Developer Tools (F12)")
    print("3. Go to Application > Local Storage or Session Storage")
    print("4. Look for your Supabase token (usually starts with 'eyJ')")
    print("5. Copy that token and paste it here when prompted")
    
    token = input("\n🔑 Paste your JWT token here: ").strip()
    
    if not token:
        print("❌ No token provided. Exiting.")
        return
    
    # Test authentication status
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        print("\n🔍 Testing authentication status...")
        response = requests.get(
            'https://riskradar.dev.securitymetricshub.com/api/v1/auth/profile',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            permissions = data.get('permissions', {})
            
            print(f"\n✅ Authentication successful!")
            print(f"📧 Email: {user.get('email')}")
            print(f"👤 Name: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
            print(f"🛡️  Is Admin: {permissions.get('is_admin', False)}")
            print(f"📊 Can View Logs: {permissions.get('can_view_logs', False)}")
            print(f"⬆️  Can Upload: {permissions.get('can_upload', False)}")
            
            if not permissions.get('is_admin', False):
                print("\n⚠️  ISSUE FOUND: You are not an admin user!")
                print("This is why you're getting 403 Forbidden errors on admin endpoints.")
                print_admin_instructions()
            else:
                print("\n🎉 You have admin access! Admin endpoints should work.")
                
        elif response.status_code == 401:
            print("\n❌ Authentication failed!")
            print("Your token is invalid or expired.")
            print("Please get a fresh token from Supabase.")
            
        elif response.status_code == 403:
            print("\n❌ Access forbidden!")
            print("Your token is valid but you don't have the required permissions.")
            print_admin_instructions()
            
        else:
            print(f"\n❌ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: {e}")
        print("Make sure the server is running and accessible.")

def print_admin_instructions():
    """Print instructions for making a user admin"""
    print("\n" + "="*60)
    print("🔧 HOW TO MAKE A USER ADMIN IN SUPABASE")
    print("="*60)
    
    print("\n1. 🌐 Go to your Supabase Dashboard:")
    print("   https://supabase.com/dashboard")
    
    print("\n2. 📁 Select your Risk Radar project")
    
    print("\n3. 👥 Go to Authentication > Users")
    
    print("\n4. 🔍 Find your user (ciaran.finnegan@gmail.com)")
    
    print("\n5. ✏️  Click on your user to edit")
    
    print("\n6. 📝 In the 'User Metadata' section, add this JSON:")
    print("   {")
    print('     "is_staff": true,')
    print('     "is_superuser": false,')
    print('     "first_name": "Ciaran",')
    print('     "last_name": "Finnegan"')
    print("   }")
    
    print("\n7. 💾 Click 'Update User'")
    
    print("\n8. 🔄 Log out and log back in to get a new JWT token")
    
    print("\n9. ✅ Test again with this script")
    
    print("\n" + "="*60)
    print("📋 ALTERNATIVE: Using Supabase CLI")
    print("="*60)
    
    print("\nIf you have Supabase CLI installed:")
    print("1. supabase login")
    print("2. supabase projects list")
    print("3. supabase link --project-ref YOUR_PROJECT_REF")
    print("4. Update user metadata via SQL in dashboard")
    
    print("\n💡 IMPORTANT NOTES:")
    print("- Setting is_staff=true gives access to admin endpoints")
    print("- Setting is_superuser=true gives Django superuser privileges")
    print("- Changes take effect immediately but require new JWT token")
    print("- You can also do this via the Supabase SQL editor")

def decode_jwt_info(token):
    """Show JWT token information without validating signature"""
    try:
        import base64
        
        # Split the token
        parts = token.split('.')
        if len(parts) != 3:
            print("❌ Invalid JWT token format")
            return
            
        # Decode payload (add padding if needed)
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        
        decoded = base64.urlsafe_b64decode(payload)
        payload_data = json.loads(decoded)
        
        print("\n🔍 JWT Token Information:")
        print(f"📧 Email: {payload_data.get('email', 'Not found')}")
        print(f"🆔 Subject: {payload_data.get('sub', 'Not found')}")
        print(f"👥 Role: {payload_data.get('role', 'Not found')}")
        
        user_metadata = payload_data.get('user_metadata', {})
        if user_metadata:
            print("📊 User Metadata:")
            for key, value in user_metadata.items():
                print(f"  {key}: {value}")
        else:
            print("⚠️  No user_metadata found - this is why admin access fails!")
            
    except Exception as e:
        print(f"❌ Could not decode token: {e}")

if __name__ == "__main__":
    test_user_status() 