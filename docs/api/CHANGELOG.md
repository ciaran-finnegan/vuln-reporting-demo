# Risk Radar API Changelog

## Version 2.2 - January 2025

### 📊 Log Analytics API Enhancement

#### Enhanced: Complete Log Analytics Implementation
**Issue**: Frontend log analytics charts were empty due to missing/incomplete backend endpoints. The log levels distribution chart was not functional because the backend didn't provide the required data structure.

**Resolution**: Complete implementation of log analytics endpoints with proper data formatting:

- ✅ **New Endpoint**: `/api/v1/logs/analytics/by-level/` - Provides log distribution by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ **Enhanced Endpoint**: `/api/v1/logs/analytics/error-rate/` - Now includes `level_counts` for frontend charts
- ✅ **Consistent Data Format**: All analytics endpoints return properly structured data matching frontend expectations
- ✅ **Time Range Support**: All endpoints support `timeRange` parameter (`1h`, `24h`, `7d`)
- ✅ **Admin Security**: All analytics endpoints require admin permissions via JWT token validation

**API Changes**:
```json
// NEW: /api/v1/logs/analytics/by-level/
{
  "data": [
    {"level": "INFO", "count": 8542},
    {"level": "ERROR", "count": 67}
  ],
  "time_range": "24h"
}

// ENHANCED: /api/v1/logs/analytics/error-rate/
{
  "data": [...],
  "level_counts": [{"level": "INFO", "count": 8542}], // NEW FIELD
  "time_range": "24h"
}
```

**Frontend Impact**: Log levels distribution chart now populates with real data, analytics dashboard is fully functional.

### 🔐 Authentication System Overhaul

#### Fixed: Admin Permissions Transfer from JWT Tokens
**Issue**: Users with valid JWT tokens containing `user_metadata.is_staff: true` were receiving 403 Forbidden errors on admin endpoints because admin permissions weren't being transferred to the Django User model.

**Resolution**: Enhanced authentication backend (`riskradar/core/authentication.py`) with proper admin permission transfer:

- ✅ **JWT Token Parsing**: Now reads `user_metadata.is_staff` and `user_metadata.is_superuser` from JWT tokens
- ✅ **User Creation**: Transfers admin flags to Django User model during initial user creation
- ✅ **User Updates**: Updates existing users when admin flags change in JWT tokens
- ✅ **Admin Endpoints**: All admin endpoints now work correctly with JWT authentication

#### Enhanced JWT Token Structure
JWT tokens now support comprehensive user metadata:

```json
{
  "aud": "authenticated",
  "exp": 1749130783,
  "sub": "user-id-123",
  "email": "admin@example.com",
  "role": "authenticated",
  "user_metadata": {
    "is_staff": true,
    "is_superuser": false,
    "first_name": "Admin",
    "last_name": "User"
  }
}
```

#### Working Admin Endpoints
All admin endpoints now properly authenticate with JWT tokens:

- ✅ `GET /api/v1/logs/` - System logs with filtering
- ✅ `GET /api/v1/logs/analytics/error-rate/` - Error rate trending
- ✅ `GET /api/v1/logs/analytics/by-source/` - Log volume by source
- ✅ `GET /api/v1/logs/analytics/top-errors/` - Most frequent errors
- ✅ `GET /api/v1/logs/docker/{container}/` - Container logs
- ✅ `GET /api/v1/logs/health/` - System health metrics

#### Authentication Flow Improvements

**Before**: JWT tokens contained admin metadata but Django User didn't receive flags
```python
# Old implementation - admin flags lost
user = User.objects.create_user(
    username=email,
    email=email,
    # Missing is_staff and is_superuser
)
```

**After**: Authentication backend now transfers admin flags from JWT
```python
# New implementation - admin flags preserved
user_metadata = user_data.get('user_metadata', {})
user = User.objects.create_user(
    username=email,
    email=email,
    is_staff=user_metadata.get('is_staff', False),
    is_superuser=user_metadata.get('is_superuser', False),
)
```

### 📚 Documentation Updates

#### Enhanced API Documentation
- Updated `/api/v1/auth/profile` response examples with admin vs regular user
- Added JWT token structure documentation with `user_metadata` fields
- Enhanced troubleshooting guide with admin permission fixes
- Updated Postman collection with correct admin endpoint authentication

#### Updated Authentication Guide
- Added JWT payload examples showing admin metadata structure
- Enhanced permission checking examples
- Updated troubleshooting section with latest fixes
- Added security best practices for admin token handling

### 🔧 Testing Improvements

#### Local Testing Results
Created comprehensive test script showing successful authentication:

**Before Fix**:
- Authentication Profile: `Is Admin: False`
- All admin endpoints: `Status: 403 FORBIDDEN`

**After Fix**:
- Authentication Profile: `Is Admin: True` ✅
- System Logs: `Status: 200` with real data (5,326 logs) ✅
- Health Metrics: `Status: 200` with system stats (1.03% error rate) ✅
- Analytics Endpoints: `Status: 200` with real analytics ✅

### 💾 Database & Infrastructure

#### Environment Variables Fixed
- Resolved GitHub Actions deployment with proper `DJANGO_SECRET_KEY`
- Fixed Docker container environment variable synchronisation
- Ensured `SUPABASE_JWT_SECRET` consistency across environments

### 🚀 Deployment Status

- ✅ **Local Development**: All endpoints working with proper authentication
- ✅ **Code Committed**: Authentication fixes committed to dev branch
- 🔄 **Remote Deployment**: GitHub Actions deploying authentication improvements
- ✅ **Documentation**: All API docs and Postman collections updated

---

## Version 2.1 - December 2024

### Fixed: JWT Authentication for API Endpoints
- Resolved issue where log management endpoints were redirecting to `/accounts/login/`
- All API endpoints now consistently use JWT authentication
- Enhanced middleware to properly handle API vs web requests

### Enhanced Upload System
- Improved file validation and error handling
- Added upload progress tracking
- Enhanced duplicate detection with SHA-256 hashing

---

## Version 2.0 - November 2024

### Initial Release
- Complete Django backend with Supabase integration
- Nessus file upload and parsing
- JWT authentication system
- Admin log management endpoints
- Interactive API documentation with Swagger/OpenAPI

---

## Migration Notes

### For Existing Users
If you're experiencing authentication issues after the v2.2 update:

1. **Check Token Metadata**: Ensure your JWT token includes `user_metadata.is_staff: true` for admin access
2. **Test Authentication**: Use `GET /api/v1/auth/profile` to verify your admin status
3. **Refresh Tokens**: Generate new tokens from Supabase if you're still experiencing issues
4. **Update Postman**: Re-import the latest Postman collection for correct admin endpoint setup

### For Developers
The authentication backend changes are backward compatible:
- Existing non-admin users continue to work without changes
- Admin functionality requires proper `user_metadata` in JWT tokens
- All endpoints maintain the same URL structure and response format 