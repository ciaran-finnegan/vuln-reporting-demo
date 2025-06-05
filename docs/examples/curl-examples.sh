#!/bin/bash
# Risk Radar API cURL Examples
#
# This script demonstrates how to use the Risk Radar API with cURL commands.
# It includes examples for all endpoints with proper authentication and error handling.
#
# Prerequisites:
# 1. Set your JWT token: export RISK_RADAR_TOKEN="your-jwt-token"
# 2. Install jq for JSON parsing: brew install jq (or apt-get install jq)
#
# Usage:
#   chmod +x curl-examples.sh
#   ./curl-examples.sh

set -e  # Exit on any error

# Configuration
BASE_URL="https://riskradar.dev.securitymetricshub.com"
TOKEN="${RISK_RADAR_TOKEN:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if jq is installed
check_dependencies() {
    if ! command -v jq &> /dev/null; then
        log_error "jq is required for JSON parsing. Install with: brew install jq (macOS) or apt-get install jq (Ubuntu)"
        exit 1
    fi
}

# Check if token is set
check_token() {
    if [ -z "$TOKEN" ]; then
        log_warning "JWT token not set. Some endpoints will fail."
        log_info "Set token with: export RISK_RADAR_TOKEN='your-jwt-token'"
        echo
    else
        log_success "JWT token is set"
    fi
}

# Make authenticated request
auth_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    
    local curl_args=("-s" "-w" "\n%{http_code}" "$method" "${BASE_URL}${endpoint}")
    
    if [ -n "$TOKEN" ]; then
        curl_args+=("-H" "Authorization: Bearer $TOKEN")
    fi
    
    if [ -n "$data" ]; then
        curl_args+=("-H" "Content-Type: application/json" "-d" "$data")
    fi
    
    curl "${curl_args[@]}"
}

# Make file upload request
upload_request() {
    local endpoint="$1"
    local file_path="$2"
    local force_reimport="$3"
    
    local curl_args=("-s" "-w" "\n%{http_code}" "-X" "POST" "${BASE_URL}${endpoint}")
    
    if [ -n "$TOKEN" ]; then
        curl_args+=("-H" "Authorization: Bearer $TOKEN")
    fi
    
    curl_args+=("-F" "file=@$file_path")
    
    if [ "$force_reimport" = "true" ]; then
        curl_args[2]="${curl_args[2]}?force_reimport=true"
    fi
    
    curl "${curl_args[@]}"
}

# Parse response and extract status code
parse_response() {
    local response="$1"
    local last_line
    last_line=$(echo "$response" | tail -n1)
    local status_code="$last_line"
    local body
    body=$(echo "$response" | head -n -1)
    
    echo "$status_code|$body"
}

# Pretty print JSON
pretty_json() {
    echo "$1" | jq '.' 2>/dev/null || echo "$1"
}

# Test an endpoint
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    
    log_info "Testing: $name"
    echo "  Command: curl $method ${BASE_URL}${endpoint}"
    
    local response
    response=$(auth_request "$method" "$endpoint" "$data")
    local parsed
    parsed=$(parse_response "$response")
    local status_code
    status_code=$(echo "$parsed" | cut -d'|' -f1)
    local body
    body=$(echo "$parsed" | cut -d'|' -f2-)
    
    if [ "$status_code" = "$expected_status" ]; then
        log_success "Response ($status_code): $(echo "$body" | jq -r '.status // .message // .authenticated // "Success"' 2>/dev/null || echo "OK")"
    else
        log_error "Expected $expected_status, got $status_code"
        echo "  Response: $(pretty_json "$body")"
    fi
    echo
}

# Print section header
section() {
    echo
    echo "================================================="
    echo "$1"
    echo "================================================="
    echo
}

# Main test suite
main() {
    check_dependencies
    
    echo "Risk Radar API cURL Examples"
    echo "Base URL: $BASE_URL"
    echo
    
    check_token
    
    # System Status Endpoints (No authentication required)
    section "1. System Status"
    
    log_info "API Status Check"
    echo "curl -s '$BASE_URL/api/v1/status' | jq"
    response=$(curl -s "$BASE_URL/api/v1/status")
    echo "Response:"
    pretty_json "$response"
    echo
    
    # Authentication Endpoints
    section "2. Authentication"
    
    log_info "Check Authentication Status (without token)"
    echo "curl -s '$BASE_URL/api/v1/auth/status' | jq"
    response=$(curl -s "$BASE_URL/api/v1/auth/status")
    echo "Response:"
    pretty_json "$response"
    echo
    
    if [ -n "$TOKEN" ]; then
        log_info "Check Authentication Status (with token)"
        echo "curl -s -H 'Authorization: Bearer \$TOKEN' '$BASE_URL/api/v1/auth/status' | jq"
        response=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/auth/status")
        echo "Response:"
        pretty_json "$response"
        echo
        
        log_info "Get User Profile"
        echo "curl -s -H 'Authorization: Bearer \$TOKEN' '$BASE_URL/api/v1/auth/profile' | jq"
        response=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/auth/profile")
        status_code=$(curl -s -w "%{http_code}" -o /dev/null -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/auth/profile")
        
        if [ "$status_code" = "200" ]; then
            echo "Response:"
            pretty_json "$response"
        else
            log_error "Authentication failed (status: $status_code)"
            echo "Response: $response"
        fi
        echo
    fi
    
    # File Upload Endpoints
    section "3. File Upload & Management"
    
    log_info "Get Upload Requirements"
    echo "curl -s '$BASE_URL/api/v1/upload/info' | jq"
    response=$(curl -s "$BASE_URL/api/v1/upload/info")
    echo "Response:"
    pretty_json "$response"
    echo
    
    log_info "Get Upload History"
    echo "curl -s '$BASE_URL/api/v1/upload/history?limit=5' | jq"
    response=$(curl -s "$BASE_URL/api/v1/upload/history?limit=5")
    echo "Response:"
    pretty_json "$response"
    echo
    
    # File Upload Example (commented out - requires actual file)
    cat << 'EOF'
File Upload Example (requires actual .nessus file):

# Upload without authentication
curl -s -X POST \
  -F "file=@/path/to/scan.nessus" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/upload/nessus' | jq

# Upload with authentication
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/scan.nessus" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/upload/nessus' | jq

# Force re-import (bypass duplicate detection)
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/scan.nessus" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/upload/nessus?force_reimport=true' | jq

EOF
    
    # System Monitoring (Admin only)
    if [ -n "$TOKEN" ]; then
        section "4. System Monitoring (Admin Only)"
        
        log_info "Get System Logs"
        echo "curl -s -H 'Authorization: Bearer \$TOKEN' '$BASE_URL/api/v1/logs/?level=ERROR&limit=10' | jq"
        response=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/logs/?level=ERROR&limit=10")
        status_code=$(curl -s -w "%{http_code}" -o /dev/null -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/logs/?level=ERROR&limit=10")
        
        if [ "$status_code" = "200" ]; then
            log_success "System logs retrieved successfully"
            echo "Sample response structure:"
            echo "$response" | jq '{total_count: .total_count, sample_log: .logs[0]}' 2>/dev/null || echo "$response"
        elif [ "$status_code" = "403" ]; then
            log_warning "Admin privileges required for system logs"
        else
            log_error "Failed to retrieve logs (status: $status_code)"
        fi
        echo
        
        log_info "Get System Health"
        echo "curl -s -H 'Authorization: Bearer \$TOKEN' '$BASE_URL/api/v1/logs/health/' | jq"
        response=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/logs/health/")
        status_code=$(curl -s -w "%{http_code}" -o /dev/null -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/logs/health/")
        
        if [ "$status_code" = "200" ]; then
            log_success "System health retrieved successfully"
            echo "Response:"
            pretty_json "$response"
        elif [ "$status_code" = "403" ]; then
            log_warning "Admin privileges required for system health"
        else
            log_error "Failed to retrieve health (status: $status_code)"
        fi
        echo
        
        # Log Analytics Examples
        log_info "Log Analytics Examples"
        
        cat << 'EOF'
# Error rate analytics
curl -s -H "Authorization: Bearer $TOKEN" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/logs/analytics/error-rate/?timeRange=24h' | jq

# Logs by source
curl -s -H "Authorization: Bearer $TOKEN" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/logs/analytics/by-source/?timeRange=24h' | jq

# Top errors
curl -s -H "Authorization: Bearer $TOKEN" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/logs/analytics/top-errors/?limit=10&timeRange=24h' | jq

# Docker container logs
curl -s -H "Authorization: Bearer $TOKEN" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/logs/docker/riskradar-web/?lines=100' | jq

EOF
    fi
    
    # Advanced Examples
    section "5. Advanced Examples"
    
    cat << 'EOF'
# Upload with progress tracking (using verbose mode)
curl -v -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@scan.nessus" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/upload/nessus'

# Filter upload history by status
curl -s 'https://riskradar.dev.securitymetricshub.com/api/v1/upload/history?status=completed&limit=10' | jq

# Filter logs by time range
curl -s -H "Authorization: Bearer $TOKEN" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/logs/?start_time=2025-01-01T00:00:00Z&end_time=2025-01-02T00:00:00Z' | jq

# Search logs for specific text
curl -s -H "Authorization: Bearer $TOKEN" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/logs/?search=error&level=ERROR' | jq

# Get multiple pages of results
curl -s 'https://riskradar.dev.securitymetricshub.com/api/v1/upload/history?limit=50&offset=0' | jq
curl -s 'https://riskradar.dev.securitymetricshub.com/api/v1/upload/history?limit=50&offset=50' | jq

EOF
    
    # Error Handling Examples
    section "6. Error Handling Examples"
    
    cat << 'EOF'
# Test invalid token
curl -s -H "Authorization: Bearer invalid-token" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/auth/profile' | jq

# Test file too large (example - adjust file size)
curl -s -X POST \
  -F "file=@large-file.nessus" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/upload/nessus' | jq

# Test rate limiting (make many requests quickly)
for i in {1..20}; do
  curl -s 'https://riskradar.dev.securitymetricshub.com/api/v1/status' > /dev/null
done

# Test with error handling
response=$(curl -s -w "%{http_code}" -H "Authorization: Bearer $TOKEN" \
  'https://riskradar.dev.securitymetricshub.com/api/v1/auth/profile')

status_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [ "$status_code" = "200" ]; then
  echo "Success: $body" | jq
elif [ "$status_code" = "401" ]; then
  echo "Authentication error: $body" | jq
elif [ "$status_code" = "403" ]; then
  echo "Permission error: $body" | jq
else
  echo "Error $status_code: $body" | jq
fi

EOF
    
    # Automation Examples
    section "7. Automation & Scripting Examples"
    
    cat << 'EOF'
# Batch upload multiple files
for file in *.nessus; do
  if [ -f "$file" ]; then
    echo "Uploading: $file"
    response=$(curl -s -X POST \
      -H "Authorization: Bearer $TOKEN" \
      -F "file=@$file" \
      'https://riskradar.dev.securitymetricshub.com/api/v1/upload/nessus')
    
    if echo "$response" | jq -e '.success' > /dev/null; then
      echo "✓ Success: $file"
      echo "$response" | jq -r '.statistics | "Assets: \(.assets_processed), Findings: \(.findings_processed)"'
    else
      echo "✗ Failed: $file"
      echo "$response" | jq -r '.error // "Unknown error"'
    fi
    echo
  fi
done

# Monitor system health
check_health() {
  response=$(curl -s -H "Authorization: Bearer $TOKEN" \
    'https://riskradar.dev.securitymetricshub.com/api/v1/logs/health/')
  
  error_rate=$(echo "$response" | jq -r '.error_rate // 0')
  
  if (( $(echo "$error_rate > 5.0" | bc -l) )); then
    echo "⚠ High error rate: $error_rate%"
    # Send alert
  else
    echo "✓ Error rate normal: $error_rate%"
  fi
}

# Get recent errors for debugging
get_recent_errors() {
  curl -s -H "Authorization: Bearer $TOKEN" \
    'https://riskradar.dev.securitymetricshub.com/api/v1/logs/?level=ERROR&limit=20' | \
    jq -r '.logs[] | "\(.timestamp) [\(.level)] \(.message)"'
}

# Export upload history to CSV
export_uploads() {
  curl -s 'https://riskradar.dev.securitymetricshub.com/api/v1/upload/history?limit=1000' | \
    jq -r '.uploads[] | [.upload_id, .filename, .status, .uploaded_at, .stats.assets, .stats.findings] | @csv' > uploads.csv
  echo "Upload history exported to uploads.csv"
}

EOF
    
    log_success "All examples completed!"
    echo
    echo "For more information:"
    echo "- API Documentation: $BASE_URL/api/docs/"
    echo "- Developer Guide: https://github.com/ciaran-finnegan/vuln-reporting-demo/blob/main/docs/api/api-guide.md"
    echo "- Authentication Guide: https://github.com/ciaran-finnegan/vuln-reporting-demo/blob/main/docs/api/authentication.md"
}

# Run examples if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 