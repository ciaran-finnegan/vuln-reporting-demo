# Risk Radar API Developer Guide

## Quick Start

1. **Get API Access**: Sign up at [https://riskradar.dev.securitymetricshub.com](https://riskradar.dev.securitymetricshub.com) and get a JWT token
2. **Test the API**: Import our [Postman collection](./risk-radar-api.postman_collection.json)
3. **View Interactive Docs**: Visit [https://riskradar.dev.securitymetricshub.com/api/docs/](https://riskradar.dev.securitymetricshub.com/api/docs/)

## Base URL
```
Production: https://riskradar.dev.securitymetricshub.com
Development: http://localhost:8000
```

## Authentication
All authenticated endpoints require a Bearer token in the Authorization header:
```bash
Authorization: Bearer your-jwt-token-here
```

## Rate Limits
- Upload endpoints: 10 requests/minute
- Other endpoints: 100 requests/minute

## Response Format
All responses are JSON with consistent error handling:

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "details": { ... }
}
```

## Endpoints Overview

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/v1/status` | GET | No | API health check |
| `/api/v1/upload/nessus` | POST | Optional | Upload Nessus files |
| `/api/v1/upload/history` | GET | No | View upload history |
| `/api/v1/upload/info` | GET | No | Upload requirements |
| `/api/v1/auth/status` | GET | No | Check authentication status |
| `/api/v1/auth/profile` | GET | Yes | Get user profile |
| `/api/v1/logs/` | GET | Admin | System logs |
| `/api/v1/logs/health/` | GET | Admin | System health |

## File Upload & Management

### Upload Nessus Files
Upload and process Nessus .nessus scan files with automatic parsing and duplicate detection.

**Endpoint:** `POST /api/v1/upload/nessus`

**Headers:**
```bash
Content-Type: multipart/form-data
Authorization: Bearer your-jwt-token  # Optional
```

**Parameters:**
- `file` (required): Nessus .nessus file
- `force_reimport` (optional): Set to `true` to bypass duplicate detection

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer your-jwt-token" \
  -F "file=@scan_results.nessus" \
  "https://riskradar.dev.securitymetricshub.com/api/v1/upload/nessus"
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "File uploaded and processed successfully",
  "filename": "scan_results.nessus",
  "file_size": 1048576,
  "file_hash": "a1b2c3d4...",
  "upload_id": 123,
  "force_reimport_used": false,
  "authenticated": true,
  "uploaded_by": "user@example.com",
  "statistics": {
    "assets_processed": 15,
    "vulnerabilities_processed": 42,
    "findings_processed": 158,
    "errors": []
  },
  "parser_details": {
    "assets_created": 12,
    "vulnerabilities_created": 38,
    "findings_created": 145,
    "findings_updated": 13
  }
}
```

**Duplicate File Response (409 Conflict):**
```json
{
  "error": "Duplicate file detected",
  "message": "This file has already been uploaded and processed.",
  "duplicate_info": {
    "original_filename": "previous_scan.nessus",
    "original_upload_date": "2025-01-02T10:30:00Z",
    "upload_id": 120
  },
  "solution": "Use force_reimport=true query parameter to bypass duplicate detection.",
  "filename": "scan_results.nessus",
  "file_hash": "a1b2c3d4...",
  "is_duplicate": true
}
```

### Get Upload History
Retrieve upload history with optional filtering and pagination.

**Endpoint:** `GET /api/v1/upload/history`

**Parameters:**
- `limit` (optional): Number of records to return (default: 50, max: 200)
- `offset` (optional): Number of records to skip (default: 0)
- `status` (optional): Filter by status (`pending`, `processing`, `completed`, `failed`)
- `integration` (optional): Filter by integration name

**Example:**
```bash
curl "https://riskradar.dev.securitymetricshub.com/api/v1/upload/history?limit=10&status=completed"
```

**Response:**
```json
{
  "success": true,
  "total_count": 150,
  "limit": 10,
  "offset": 0,
  "uploads": [
    {
      "upload_id": 123,
      "filename": "scan_results.nessus",
      "file_size": 1048576,
      "file_hash": "a1b2c3d4...",
      "integration": "Nessus",
      "status": "completed",
      "uploaded_at": "2025-01-02T10:30:00Z",
      "processed_at": "2025-01-02T10:32:15Z",
      "error_message": null,
      "stats": {
        "assets": 15,
        "vulnerabilities": 42,
        "findings": 158,
        "errors": []
      }
    }
  ]
}
```

### Get Upload Requirements
Get file upload limits and requirements.

**Endpoint:** `GET /api/v1/upload/info`

**Example:**
```bash
curl "https://riskradar.dev.securitymetricshub.com/api/v1/upload/info"
```

**Response:**
```json
{
  "file_upload_limits": {
    "max_file_size_mb": 100,
    "allowed_extensions": [".nessus"],
    "max_memory_size_mb": 100
  },
  "supported_scanners": ["Nessus"],
  "upload_endpoint": "/api/v1/upload/nessus"
}
```

## Authentication & User Management

### Check Authentication Status
Check if the current request is authenticated.

**Endpoint:** `GET /api/v1/auth/status`

**Example:**
```bash
curl -H "Authorization: Bearer your-jwt-token" \
  "https://riskradar.dev.securitymetricshub.com/api/v1/auth/status"
```

**Authenticated Response:**
```json
{
  "authenticated": true,
  "user": {
    "email": "user@example.com",
    "is_admin": false
  }
}
```

**Unauthenticated Response:**
```json
{
  "authenticated": false,
  "user": null
}
```

### Get User Profile
Get detailed user profile and permissions.

**Endpoint:** `GET /api/v1/auth/profile`
**Authentication:** Required

**Example:**
```bash
curl -H "Authorization: Bearer your-jwt-token" \
  "https://riskradar.dev.securitymetricshub.com/api/v1/auth/profile"
```

**Response:**
```json
{
  "user": {
    "id": 123,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_staff": false,
    "is_superuser": false,
    "date_joined": "2025-01-01T00:00:00Z"
  },
  "profile": {
    "business_group": "Production",
    "supabase_user_id": "uuid-string"
  },
  "permissions": {
    "is_admin": false,
    "can_upload": true,
    "can_view_logs": false
  }
}
```

## System Monitoring (Admin Only)

### Get System Logs
Retrieve filtered system logs with pagination.

**Endpoint:** `GET /api/v1/logs/`
**Authentication:** Required (Admin only)

**Parameters:**
- `level` (optional): Filter by log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, `ALL`)
- `source` (optional): Filter by source (`django`, `docker`, `system`, `nginx`, `ALL`)
- `search` (optional): Search in log messages
- `start_time` (optional): Start time filter (ISO format)
- `end_time` (optional): End time filter (ISO format)
- `limit` (optional): Number of logs to return (default: 50)
- `offset` (optional): Number of logs to skip (default: 0)

**Example:**
```bash
curl -H "Authorization: Bearer admin-jwt-token" \
  "https://riskradar.dev.securitymetricshub.com/api/v1/logs/?level=ERROR&limit=10"
```

**Response:**
```json
{
  "logs": [
    {
      "id": "log-123",
      "timestamp": "2025-01-02T10:30:00Z",
      "level": "ERROR",
      "source": "django",
      "module": "core.views",
      "message": "File upload failed: Invalid format",
      "metadata": {
        "file": "views.py",
        "line": 123,
        "function": "upload_nessus_file",
        "request_id": "req-456"
      },
      "user": {
        "id": "user-789",
        "email": "user@example.com"
      }
    }
  ],
  "total_count": 150,
  "has_more": true,
  "next_offset": 10
}
```

### Get System Health
Get system health metrics and status.

**Endpoint:** `GET /api/v1/logs/health/`
**Authentication:** Required (Admin only)

**Example:**
```bash
curl -H "Authorization: Bearer admin-jwt-token" \
  "https://riskradar.dev.securitymetricshub.com/api/v1/logs/health/"
```

**Response:**
```json
{
  "total_logs_24h": 12486,
  "error_rate": 0.8,
  "active_users": 23,
  "avg_response_time": null,
  "timestamp": "2025-01-02T10:30:00Z"
}
```

## System Status

### API Health Check
Check API health and available endpoints.

**Endpoint:** `GET /api/v1/status`

**Example:**
```bash
curl "https://riskradar.dev.securitymetricshub.com/api/v1/status"
```

**Response:**
```json
{
  "status": "ok",
  "message": "Risk Radar API is operational",
  "endpoints": {
    "upload_nessus": "/api/v1/upload/nessus",
    "upload_history": "/api/v1/upload/history",
    "status": "/api/v1/status",
    "upload_info": "/api/v1/upload/info"
  }
}
```

## Error Handling

### HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate resource (e.g., file already uploaded)
- `413 Payload Too Large` - File too large
- `422 Unprocessable Entity` - Invalid file format
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Common Error Responses

**Authentication Error (401):**
```json
{
  "error": "Authentication required",
  "message": "Invalid or missing JWT token"
}
```

**Permission Error (403):**
```json
{
  "error": "Insufficient permissions",
  "message": "Admin access required for this endpoint"
}
```

**File Too Large (413):**
```json
{
  "error": "File too large",
  "message": "Maximum file size is 100MB"
}
```

**Rate Limit Exceeded (429):**
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again in 60 seconds."
}
```

## Best Practices

### Authentication
- Store JWT tokens securely
- Refresh tokens before expiry
- Use HTTPS in production
- Never log or expose tokens

### File Uploads
- Validate file types before upload
- Check file sizes against limits
- Handle duplicate detection gracefully
- Monitor upload progress for large files

### Error Handling
- Always check HTTP status codes
- Parse error messages for user feedback
- Implement retry logic for transient errors
- Log errors for debugging

### Performance
- Use pagination for large datasets
- Cache responses when appropriate
- Implement request timeouts
- Monitor API response times

## Integration Examples

See the [examples directory](../examples/) for complete integration examples:
- [Python Client](../examples/python-client.py)
- [JavaScript Integration](../examples/javascript-client.js)
- [cURL Examples](../examples/curl-examples.sh)

## Support

- **Documentation**: [https://riskradar.dev.securitymetricshub.com/api/docs/](https://riskradar.dev.securitymetricshub.com/api/docs/)
- **Postman Collection**: [risk-radar-api.postman_collection.json](./risk-radar-api.postman_collection.json)
- **Authentication Guide**: [authentication.md](./authentication.md)
- **GitHub Repository**: [vuln-reporting-demo](https://github.com/ciaran-finnegan/vuln-reporting-demo) 