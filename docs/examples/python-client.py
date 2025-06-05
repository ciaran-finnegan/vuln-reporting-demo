#!/usr/bin/env python3
"""
Risk Radar API Python Client

A comprehensive Python SDK for the Risk Radar vulnerability management API.
Includes authentication, file upload, error handling, and retry logic.

Example usage:
    from risk_radar_client import RiskRadarClient
    
    client = RiskRadarClient(
        base_url='https://riskradar.dev.securitymetricshub.com',
        token='your-jwt-token'
    )
    
    # Upload a file
    result = client.upload_nessus_file('scan.nessus')
    print(f"Uploaded: {result['statistics']}")
"""

import os
import sys
import time
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskRadarError(Exception):
    """Base exception for Risk Radar API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(RiskRadarError):
    """Authentication related errors"""
    pass


class PermissionError(RiskRadarError):
    """Permission related errors"""
    pass


class DuplicateFileError(RiskRadarError):
    """Duplicate file upload error"""
    def __init__(self, message: str, duplicate_info: Dict, **kwargs):
        super().__init__(message, **kwargs)
        self.duplicate_info = duplicate_info


class RiskRadarClient:
    """
    Risk Radar API Client
    
    Provides a complete interface to the Risk Radar vulnerability management API
    with authentication, error handling, and retry logic.
    """
    
    def __init__(self, base_url: str, token: Optional[str] = None, 
                 timeout: int = 30, max_retries: int = 3):
        """
        Initialize the Risk Radar client
        
        Args:
            base_url: Base URL of the Risk Radar API
            token: JWT authentication token (optional)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Setup session
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def set_token(self, token: str) -> None:
        """Update the authentication token"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    def _make_request(self, method: str, endpoint: str, 
                     retry_on_auth_fail: bool = False, **kwargs) -> requests.Response:
        """
        Make an HTTP request with error handling and retries
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            retry_on_auth_fail: Whether to retry on authentication failures
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            RiskRadarError: On API errors
            AuthenticationError: On authentication failures
            PermissionError: On permission failures
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Handle different status codes
                if response.status_code == 200 or response.status_code == 201:
                    return response
                elif response.status_code == 401:
                    raise AuthenticationError(
                        "Authentication required or token expired",
                        status_code=401
                    )
                elif response.status_code == 403:
                    raise PermissionError(
                        "Insufficient permissions for this endpoint",
                        status_code=403
                    )
                elif response.status_code == 409:
                    # Handle duplicate file specially
                    try:
                        error_data = response.json()
                        if 'duplicate_info' in error_data:
                            raise DuplicateFileError(
                                error_data.get('error', 'Duplicate file detected'),
                                duplicate_info=error_data['duplicate_info'],
                                status_code=409,
                                details=error_data
                            )
                    except json.JSONDecodeError:
                        pass
                    raise RiskRadarError(
                        "Conflict - possibly duplicate resource",
                        status_code=409
                    )
                elif response.status_code >= 500:
                    # Server errors - retry
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Server error, retrying in {wait_time}s... (attempt {attempt + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RiskRadarError(
                            f"Server error: {response.status_code}",
                            status_code=response.status_code
                        )
                else:
                    # Client errors
                    try:
                        error_data = response.json()
                        error_message = error_data.get('error', f'HTTP {response.status_code}')
                    except json.JSONDecodeError:
                        error_message = f'HTTP {response.status_code}: {response.text}'
                    
                    raise RiskRadarError(
                        error_message,
                        status_code=response.status_code
                    )
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    logger.warning(f"Request timeout, retrying... (attempt {attempt + 1})")
                    continue
                else:
                    raise RiskRadarError("Request timeout after retries")
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Connection error, retrying in {wait_time}s... (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise RiskRadarError("Connection error after retries")
        
        raise RiskRadarError("Maximum retries exceeded")
    
    # Authentication Methods
    def is_authenticated(self) -> bool:
        """Check if the current token is valid"""
        try:
            response = self._make_request('GET', '/api/v1/auth/status')
            data = response.json()
            return data.get('authenticated', False)
        except RiskRadarError:
            return False
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication status"""
        response = self._make_request('GET', '/api/v1/auth/status')
        return response.json()
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get current user profile (requires authentication)"""
        response = self._make_request('GET', '/api/v1/auth/profile')
        return response.json()
    
    # File Upload Methods
    def upload_nessus_file(self, file_path: str, force_reimport: bool = False,
                          progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Upload a Nessus .nessus file
        
        Args:
            file_path: Path to the .nessus file
            force_reimport: Whether to bypass duplicate detection
            progress_callback: Optional callback for upload progress
            
        Returns:
            Upload result with statistics
            
        Raises:
            FileNotFoundError: If file doesn't exist
            DuplicateFileError: If file is a duplicate (unless force_reimport=True)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.suffix.lower() == '.nessus':
            logger.warning(f"File {file_path} doesn't have .nessus extension")
        
        # Calculate file hash for tracking
        file_hash = self._calculate_file_hash(file_path)
        logger.info(f"Uploading {file_path.name} (hash: {file_hash[:8]}...)")
        
        # Prepare the file upload
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/xml')}
            
            params = {}
            if force_reimport:
                params['force_reimport'] = 'true'
            
            try:
                response = self._make_request(
                    'POST', 
                    '/api/v1/upload/nessus',
                    files=files,
                    params=params
                )
                
                result = response.json()
                logger.info(f"Upload successful: {result.get('statistics', {})}")
                return result
                
            except DuplicateFileError as e:
                if not force_reimport:
                    logger.warning(f"Duplicate file detected: {e.duplicate_info}")
                    logger.info("Use force_reimport=True to bypass duplicate detection")
                raise
    
    def get_upload_history(self, limit: int = 50, offset: int = 0,
                          status: Optional[str] = None, 
                          integration: Optional[str] = None) -> Dict[str, Any]:
        """
        Get upload history with optional filtering
        
        Args:
            limit: Number of records to return (max 200)
            offset: Number of records to skip
            status: Filter by status (pending, processing, completed, failed)
            integration: Filter by integration name
            
        Returns:
            Upload history data
        """
        params = {
            'limit': min(limit, 200),
            'offset': offset
        }
        
        if status:
            params['status'] = status
        if integration:
            params['integration'] = integration
        
        response = self._make_request('GET', '/api/v1/upload/history', params=params)
        return response.json()
    
    def get_upload_info(self) -> Dict[str, Any]:
        """Get file upload requirements and limits"""
        response = self._make_request('GET', '/api/v1/upload/info')
        return response.json()
    
    # System Monitoring Methods (Admin only)
    def get_system_logs(self, level: Optional[str] = None, source: Optional[str] = None,
                       search: Optional[str] = None, start_time: Optional[str] = None,
                       end_time: Optional[str] = None, limit: int = 50, 
                       offset: int = 0) -> Dict[str, Any]:
        """
        Get system logs (requires admin privileges)
        
        Args:
            level: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL, ALL)
            source: Filter by source (django, docker, system, nginx, ALL)
            search: Search in log messages
            start_time: Start time filter (ISO format)
            end_time: End time filter (ISO format)
            limit: Number of logs to return
            offset: Number of logs to skip
            
        Returns:
            System logs data
        """
        params = {'limit': limit, 'offset': offset}
        
        if level:
            params['level'] = level
        if source:
            params['source'] = source
        if search:
            params['search'] = search
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        
        response = self._make_request('GET', '/api/v1/logs/', params=params)
        return response.json()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics (requires admin privileges)"""
        response = self._make_request('GET', '/api/v1/logs/health/')
        return response.json()
    
    def get_error_rate_analytics(self, time_range: str = '24h') -> Dict[str, Any]:
        """Get error rate analytics (requires admin privileges)"""
        params = {'timeRange': time_range}
        response = self._make_request('GET', '/api/v1/logs/analytics/error-rate/', params=params)
        return response.json()
    
    def get_logs_by_source(self, time_range: str = '24h') -> Dict[str, Any]:
        """Get log distribution by source (requires admin privileges)"""
        params = {'timeRange': time_range}
        response = self._make_request('GET', '/api/v1/logs/analytics/by-source/', params=params)
        return response.json()
    
    def get_top_errors(self, limit: int = 10, time_range: str = '24h') -> Dict[str, Any]:
        """Get most frequent errors (requires admin privileges)"""
        params = {'limit': limit, 'timeRange': time_range}
        response = self._make_request('GET', '/api/v1/logs/analytics/top-errors/', params=params)
        return response.json()
    
    # System Status Methods
    def get_api_status(self) -> Dict[str, Any]:
        """Get API health status"""
        response = self._make_request('GET', '/api/v1/status')
        return response.json()
    
    # Utility Methods
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def bulk_upload_directory(self, directory_path: str, 
                             file_pattern: str = "*.nessus",
                             force_reimport: bool = False) -> List[Dict[str, Any]]:
        """
        Upload all matching files in a directory
        
        Args:
            directory_path: Path to directory containing scan files
            file_pattern: File pattern to match (default: *.nessus)
            force_reimport: Whether to bypass duplicate detection
            
        Returns:
            List of upload results
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        files = list(directory.glob(file_pattern))
        if not files:
            logger.warning(f"No files matching '{file_pattern}' found in {directory}")
            return []
        
        results = []
        for file_path in files:
            try:
                logger.info(f"Uploading {file_path.name}...")
                result = self.upload_nessus_file(file_path, force_reimport=force_reimport)
                results.append({
                    'file': str(file_path),
                    'success': True,
                    'result': result
                })
            except Exception as e:
                logger.error(f"Failed to upload {file_path.name}: {e}")
                results.append({
                    'file': str(file_path),
                    'success': False,
                    'error': str(e)
                })
        
        return results


def main():
    """Example usage of the Risk Radar client"""
    
    # Configuration
    BASE_URL = 'https://riskradar.dev.securitymetricshub.com'
    # Get token from environment or set directly
    TOKEN = os.getenv('RISK_RADAR_TOKEN', 'your-jwt-token-here')
    
    if TOKEN == 'your-jwt-token-here':
        print("Please set your JWT token:")
        print("1. Set environment variable: export RISK_RADAR_TOKEN='your-token'")
        print("2. Or edit this script and set TOKEN directly")
        return
    
    # Initialize client
    client = RiskRadarClient(BASE_URL, TOKEN)
    
    try:
        # Test authentication
        print("Testing authentication...")
        if client.is_authenticated():
            profile = client.get_user_profile()
            print(f"✓ Authenticated as: {profile['user']['email']}")
        else:
            print("✗ Authentication failed")
            return
        
        # Get API status
        print("\nChecking API status...")
        status = client.get_api_status()
        print(f"✓ API Status: {status['status']}")
        
        # Get upload requirements
        print("\nGetting upload requirements...")
        upload_info = client.get_upload_info()
        print(f"✓ Max file size: {upload_info['file_upload_limits']['max_file_size_mb']} MB")
        
        # Get upload history
        print("\nGetting recent uploads...")
        history = client.get_upload_history(limit=5)
        print(f"✓ Found {history['total_count']} total uploads")
        for upload in history['uploads'][:3]:
            print(f"  - {upload['filename']} ({upload['status']})")
        
        # Example file upload (uncomment to test)
        # print("\nUploading example file...")
        # result = client.upload_nessus_file('path/to/your/scan.nessus')
        # print(f"✓ Upload successful: {result['statistics']}")
        
        # Admin-only features (uncomment if you have admin access)
        try:
            print("\nTesting admin features...")
            health = client.get_system_health()
            print(f"✓ System health: {health}")
        except PermissionError:
            print("✓ Admin features require admin privileges")
        
        print("\n✓ All tests completed successfully!")
        
    except AuthenticationError as e:
        print(f"✗ Authentication error: {e}")
    except PermissionError as e:
        print(f"✗ Permission error: {e}")
    except RiskRadarError as e:
        print(f"✗ API error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


if __name__ == "__main__":
    main() 