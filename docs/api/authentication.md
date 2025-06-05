# Authentication Guide

## Overview
Risk Radar uses Supabase JWT tokens for authentication. Users authenticate via the frontend, and the JWT token is sent to API endpoints.

## Getting a Token

### Method 1: Browser (Development)
1. Log into the Risk Radar app at [https://riskradar.dev.securitymetricshub.com](https://riskradar.dev.securitymetricshub.com)
2. Open browser dev tools (F12)
3. Go to Application → Local Storage
4. Find your Supabase session
5. Copy the `access_token` value

### Method 2: Programmatic Access
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password'
})

// Get token
const token = data.session.access_token
```

### Method 3: Supabase Dashboard (Admin)
1. Go to your Supabase project dashboard
2. Navigate to Authentication → Users
3. Click on a user → "Generate JWT"
4. Copy the generated token

## Using Tokens

### cURL Example
```bash
curl -H "Authorization: Bearer your-token-here" \
  https://riskradar.dev.securitymetricshub.com/api/v1/auth/profile
```

### Python Example
```python
import requests

headers = {
    'Authorization': 'Bearer your-token-here',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://riskradar.dev.securitymetricshub.com/api/v1/auth/profile',
    headers=headers
)

if response.status_code == 200:
    user_data = response.json()
    print(f"User: {user_data['user']['email']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### JavaScript Example
```javascript
const token = 'your-jwt-token-here';

const response = await fetch('https://riskradar.dev.securitymetricshub.com/api/v1/auth/profile', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

if (response.ok) {
  const userData = await response.json();
  console.log('User:', userData.user.email);
} else {
  console.error('Authentication failed:', response.status);
}
```

## Token Format

JWT tokens are base64-encoded strings with three parts separated by dots:
```
header.payload.signature
```

Example token structure:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNjQwOTk1MjAwLCJzdWIiOiJ1c2VyLWlkLTEyMyIsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsInJvbGUiOiJhdXRoZW50aWNhdGVkIn0.signature
```

The payload contains:
- `aud`: Audience (should be "authenticated")
- `exp`: Expiration timestamp
- `sub`: User ID
- `email`: User email
- `role`: User role

## Token Validation

Risk Radar validates tokens by:
1. Checking the signature using the Supabase JWT secret
2. Verifying the audience is "authenticated"
3. Ensuring the token hasn't expired
4. Creating or updating Django user records

## Token Expiry

- **Default Expiry**: Tokens expire after 1 hour
- **Refresh Handling**: Frontend should refresh tokens automatically
- **Error Response**: 401 Unauthorized when token expires

### Handling Expired Tokens

**Error Response:**
```json
{
  "error": "Invalid authentication credentials.",
  "detail": "Token has expired."
}
```

**Refresh Token (JavaScript):**
```javascript
const { data, error } = await supabase.auth.refreshSession()
if (data?.session) {
  const newToken = data.session.access_token
  // Update your stored token
}
```

## User Roles & Permissions

### Role Types
- **Regular User**: Can upload files, view own data
- **Admin User**: Can access system logs and admin endpoints

### Permission Checking
```bash
# Check user permissions
curl -H "Authorization: Bearer your-token" \
  "https://riskradar.dev.securitymetricshub.com/api/v1/auth/profile"
```

**Response:**
```json
{
  "user": {
    "email": "user@example.com",
    "is_staff": false,
    "is_superuser": false
  },
  "permissions": {
    "is_admin": false,
    "can_upload": true,
    "can_view_logs": false
  }
}
```

## Troubleshooting

### Common Issues

#### 1. Invalid Token Format
**Error:**
```json
{
  "error": "Invalid authentication credentials.",
  "detail": "Invalid token"
}
```

**Solution:**
- Ensure token is properly formatted (three parts separated by dots)
- Check for extra whitespace or characters
- Verify token was copied completely

#### 2. Token Expired
**Error:**
```json
{
  "error": "Invalid authentication credentials.",
  "detail": "Token has expired"
}
```

**Solution:**
- Get a fresh token from the frontend
- Implement automatic token refresh
- Check system clock synchronization

#### 3. Missing Authorization Header
**Error:**
```json
{
  "error": "Authentication credentials were not provided."
}
```

**Solution:**
- Add Authorization header: `Authorization: Bearer your-token`
- Ensure header is properly formatted
- Check for typos in header name

#### 4. Insufficient Permissions
**Error:**
```json
{
  "error": "Insufficient permissions",
  "detail": "Admin access required for this endpoint"
}
```

**Solution:**
- Check user permissions with `/api/v1/auth/profile`
- Contact admin to upgrade user role
- Use different user with appropriate permissions

### Testing Authentication

#### Test Token Validity
```bash
curl -H "Authorization: Bearer your-token" \
  "https://riskradar.dev.securitymetricshub.com/api/v1/auth/status"
```

**Valid Token Response:**
```json
{
  "authenticated": true,
  "user": {
    "email": "user@example.com",
    "is_admin": false
  }
}
```

**Invalid Token Response:**
```json
{
  "authenticated": false,
  "user": null
}
```

## Security Best Practices

### Token Storage
- **Frontend**: Store in memory or secure storage (not localStorage)
- **Mobile**: Use secure keychain/keystore
- **Server**: Never log tokens in plaintext

### Token Transmission
- **Always use HTTPS** in production
- **Never include tokens in URLs** or query parameters
- **Use Authorization header** for API requests

### Token Lifecycle
- **Refresh before expiry** to avoid interruptions
- **Revoke tokens** when user logs out
- **Monitor for suspicious activity** with invalid tokens

## Integration Examples

### Python Client with Token Management
```python
import requests
import time
from datetime import datetime, timedelta

class RiskRadarClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def set_token(self, token):
        """Update the authentication token"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    def is_authenticated(self):
        """Check if current token is valid"""
        try:
            response = self.session.get(f'{self.base_url}/api/v1/auth/status')
            if response.status_code == 200:
                data = response.json()
                return data.get('authenticated', False)
        except:
            pass
        return False
    
    def get_user_profile(self):
        """Get user profile (requires authentication)"""
        response = self.session.get(f'{self.base_url}/api/v1/auth/profile')
        if response.status_code == 401:
            raise Exception("Authentication required or token expired")
        elif response.status_code == 403:
            raise Exception("Insufficient permissions")
        return response.json()

# Usage
client = RiskRadarClient(
    base_url='https://riskradar.dev.securitymetricshub.com',
    token='your-jwt-token'
)

if client.is_authenticated():
    profile = client.get_user_profile()
    print(f"Welcome, {profile['user']['email']}")
else:
    print("Authentication failed")
```

### JavaScript Frontend Integration
```javascript
class RiskRadarAuth {
  constructor(supabaseClient) {
    this.supabase = supabaseClient;
    this.token = null;
  }
  
  async signIn(email, password) {
    const { data, error } = await this.supabase.auth.signInWithPassword({
      email,
      password
    });
    
    if (error) throw error;
    
    this.token = data.session.access_token;
    return data.session;
  }
  
  async getApiHeaders() {
    if (!this.token) {
      throw new Error('No authentication token available');
    }
    
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }
  
  async apiCall(endpoint, options = {}) {
    const headers = await this.getApiHeaders();
    
    const response = await fetch(`https://riskradar.dev.securitymetricshub.com${endpoint}`, {
      ...options,
      headers: {
        ...headers,
        ...options.headers
      }
    });
    
    if (response.status === 401) {
      // Token expired, try to refresh
      const { data } = await this.supabase.auth.refreshSession();
      if (data?.session) {
        this.token = data.session.access_token;
        // Retry request with new token
        return this.apiCall(endpoint, options);
      }
      throw new Error('Authentication failed');
    }
    
    return response;
  }
}

// Usage
const auth = new RiskRadarAuth(supabaseClient);
await auth.signIn('user@example.com', 'password');

const response = await auth.apiCall('/api/v1/auth/profile');
const profile = await response.json();
```

## Additional Resources

- **Supabase Auth Documentation**: [https://supabase.com/docs/guides/auth](https://supabase.com/docs/guides/auth)
- **JWT.io**: [https://jwt.io/](https://jwt.io/) - Decode and inspect JWT tokens
- **API Testing**: Use our [Postman collection](./risk-radar-api.postman_collection.json) for testing
- **Interactive Documentation**: [https://riskradar.dev.securitymetricshub.com/api/docs/](https://riskradar.dev.securitymetricshub.com/api/docs/) 