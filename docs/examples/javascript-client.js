/**
 * Risk Radar API JavaScript Client
 * 
 * A comprehensive JavaScript SDK for the Risk Radar vulnerability management API.
 * Supports both browser and Node.js environments with authentication, file upload,
 * error handling, and retry logic.
 * 
 * @example Browser Usage
 * import { RiskRadarClient } from './risk-radar-client.js';
 * 
 * const client = new RiskRadarClient({
 *   baseUrl: 'https://riskradar.dev.securitymetricshub.com',
 *   token: 'your-jwt-token'
 * });
 * 
 * // Upload a file
 * const result = await client.uploadNessusFile(fileInput.files[0]);
 * console.log('Upload result:', result.statistics);
 * 
 * @example Node.js Usage
 * const { RiskRadarClient } = require('./risk-radar-client.js');
 * const fs = require('fs');
 * 
 * const client = new RiskRadarClient({
 *   baseUrl: 'https://riskradar.dev.securitymetricshub.com',
 *   token: process.env.RISK_RADAR_TOKEN
 * });
 * 
 * // Upload a file from filesystem
 * const fileBuffer = fs.readFileSync('scan.nessus');
 * const result = await client.uploadNessusFile(fileBuffer, 'scan.nessus');
 */

// Error classes for different types of API errors
class RiskRadarError extends Error {
  constructor(message, statusCode = null, details = {}) {
    super(message);
    this.name = 'RiskRadarError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

class AuthenticationError extends RiskRadarError {
  constructor(message, statusCode = 401, details = {}) {
    super(message, statusCode, details);
    this.name = 'AuthenticationError';
  }
}

class PermissionError extends RiskRadarError {
  constructor(message, statusCode = 403, details = {}) {
    super(message, statusCode, details);
    this.name = 'PermissionError';
  }
}

class DuplicateFileError extends RiskRadarError {
  constructor(message, duplicateInfo, statusCode = 409, details = {}) {
    super(message, statusCode, details);
    this.name = 'DuplicateFileError';
    this.duplicateInfo = duplicateInfo;
  }
}

/**
 * Risk Radar API Client
 * 
 * Provides a complete interface to the Risk Radar vulnerability management API
 * with authentication, error handling, and retry logic.
 */
class RiskRadarClient {
  /**
   * Initialize the Risk Radar client
   * 
   * @param {Object} options - Configuration options
   * @param {string} options.baseUrl - Base URL of the Risk Radar API
   * @param {string} [options.token] - JWT authentication token
   * @param {number} [options.timeout=30000] - Request timeout in milliseconds
   * @param {number} [options.maxRetries=3] - Maximum number of retry attempts
   */
  constructor(options = {}) {
    this.baseUrl = options.baseUrl?.replace(/\/$/, '') || 'https://riskradar.dev.securitymetricshub.com';
    this.token = options.token;
    this.timeout = options.timeout || 30000;
    this.maxRetries = options.maxRetries || 3;
    
    // Track authentication state
    this._isAuthenticated = null;
    this._userProfile = null;
  }

  /**
   * Update the authentication token
   * @param {string} token - JWT token
   */
  setToken(token) {
    this.token = token;
    this._isAuthenticated = null; // Reset authentication cache
    this._userProfile = null;
  }

  /**
   * Get headers for API requests
   * @param {boolean} includeAuth - Whether to include authentication header
   * @returns {Object} Headers object
   */
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json'
    };

    if (includeAuth && this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  /**
   * Make an HTTP request with error handling and retries
   * @private
   */
  async _makeRequest(method, endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        const response = await fetch(url, {
          method,
          signal: controller.signal,
          ...options
        });
        
        clearTimeout(timeoutId);
        
        // Handle different status codes
        if (response.ok) {
          return response;
        }
        
        const errorData = await this._parseErrorResponse(response);
        
        switch (response.status) {
          case 401:
            throw new AuthenticationError(
              errorData.error || 'Authentication required or token expired',
              401,
              errorData
            );
          case 403:
            throw new PermissionError(
              errorData.error || 'Insufficient permissions for this endpoint',
              403,
              errorData
            );
          case 409:
            if (errorData.duplicate_info) {
              throw new DuplicateFileError(
                errorData.error || 'Duplicate file detected',
                errorData.duplicate_info,
                409,
                errorData
              );
            }
            throw new RiskRadarError(
              errorData.error || 'Conflict - possibly duplicate resource',
              409,
              errorData
            );
          case 429:
            // Rate limited - wait and retry
            if (attempt < this.maxRetries) {
              const retryAfter = response.headers.get('Retry-After') || (2 ** attempt);
              console.warn(`Rate limited, retrying in ${retryAfter}s... (attempt ${attempt + 1})`);
              await this._sleep(retryAfter * 1000);
              continue;
            }
            throw new RiskRadarError(
              errorData.error || 'Rate limit exceeded',
              429,
              errorData
            );
          default:
            if (response.status >= 500 && attempt < this.maxRetries) {
              // Server error - retry with exponential backoff
              const waitTime = 2 ** attempt;
              console.warn(`Server error, retrying in ${waitTime}s... (attempt ${attempt + 1})`);
              await this._sleep(waitTime * 1000);
              continue;
            }
            throw new RiskRadarError(
              errorData.error || `HTTP ${response.status}`,
              response.status,
              errorData
            );
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          if (attempt < this.maxRetries) {
            console.warn(`Request timeout, retrying... (attempt ${attempt + 1})`);
            continue;
          }
          throw new RiskRadarError('Request timeout after retries');
        }
        
        if (error instanceof RiskRadarError) {
          throw error;
        }
        
        // Network error - retry
        if (attempt < this.maxRetries) {
          const waitTime = 2 ** attempt;
          console.warn(`Network error, retrying in ${waitTime}s... (attempt ${attempt + 1})`);
          await this._sleep(waitTime * 1000);
          continue;
        }
        
        throw new RiskRadarError(`Network error: ${error.message}`);
      }
    }
    
    throw new RiskRadarError('Maximum retries exceeded');
  }

  /**
   * Parse error response from API
   * @private
   */
  async _parseErrorResponse(response) {
    try {
      return await response.json();
    } catch {
      return { error: response.statusText || `HTTP ${response.status}` };
    }
  }

  /**
   * Sleep for specified milliseconds
   * @private
   */
  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Authentication Methods

  /**
   * Check if the current token is valid
   * @returns {Promise<boolean>} True if authenticated
   */
  async isAuthenticated() {
    try {
      const response = await this._makeRequest('GET', '/api/v1/auth/status', {
        headers: this.getHeaders()
      });
      const data = await response.json();
      this._isAuthenticated = data.authenticated || false;
      return this._isAuthenticated;
    } catch (error) {
      this._isAuthenticated = false;
      return false;
    }
  }

  /**
   * Get authentication status
   * @returns {Promise<Object>} Authentication status
   */
  async getAuthStatus() {
    const response = await this._makeRequest('GET', '/api/v1/auth/status', {
      headers: this.getHeaders()
    });
    return response.json();
  }

  /**
   * Get current user profile (requires authentication)
   * @returns {Promise<Object>} User profile data
   */
  async getUserProfile() {
    const response = await this._makeRequest('GET', '/api/v1/auth/profile', {
      headers: this.getHeaders()
    });
    this._userProfile = await response.json();
    return this._userProfile;
  }

  // File Upload Methods

  /**
   * Upload a Nessus .nessus file
   * @param {File|Buffer|Blob} file - File to upload (File object in browser, Buffer in Node.js)
   * @param {string} [filename] - Filename (required when using Buffer)
   * @param {boolean} [forceReimport=false] - Whether to bypass duplicate detection
   * @param {Function} [progressCallback] - Optional progress callback
   * @returns {Promise<Object>} Upload result with statistics
   */
  async uploadNessusFile(file, filename = null, forceReimport = false, progressCallback = null) {
    // Handle different file input types
    let fileData, fileName;
    
    if (typeof File !== 'undefined' && file instanceof File) {
      // Browser File object
      fileData = file;
      fileName = file.name;
    } else if (typeof Buffer !== 'undefined' && Buffer.isBuffer(file)) {
      // Node.js Buffer
      if (!filename) {
        throw new Error('Filename is required when uploading Buffer');
      }
      fileData = new Blob([file]);
      fileName = filename;
    } else if (file instanceof Blob) {
      // Blob object
      fileData = file;
      fileName = filename || 'scan.nessus';
    } else {
      throw new Error('Unsupported file type. Use File, Buffer, or Blob.');
    }

    // Validate file extension
    if (!fileName.toLowerCase().endsWith('.nessus')) {
      console.warn(`File ${fileName} doesn't have .nessus extension`);
    }

    console.log(`Uploading ${fileName}...`);

    // Prepare form data
    const formData = new FormData();
    formData.append('file', fileData, fileName);

    // Prepare URL with query parameters
    const params = new URLSearchParams();
    if (forceReimport) {
      params.append('force_reimport', 'true');
    }
    const url = '/api/v1/upload/nessus' + (params.toString() ? `?${params}` : '');

    // Prepare headers (don't set Content-Type for FormData)
    const headers = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await this._makeRequest('POST', url, {
        headers,
        body: formData
      });

      const result = await response.json();
      console.log('Upload successful:', result.statistics);
      return result;
    } catch (error) {
      if (error instanceof DuplicateFileError && !forceReimport) {
        console.warn('Duplicate file detected:', error.duplicateInfo);
        console.info('Use forceReimport=true to bypass duplicate detection');
      }
      throw error;
    }
  }

  /**
   * Get upload history with optional filtering
   * @param {Object} options - Filter options
   * @param {number} [options.limit=50] - Number of records to return (max 200)
   * @param {number} [options.offset=0] - Number of records to skip
   * @param {string} [options.status] - Filter by status (pending, processing, completed, failed)
   * @param {string} [options.integration] - Filter by integration name
   * @returns {Promise<Object>} Upload history data
   */
  async getUploadHistory(options = {}) {
    const params = new URLSearchParams({
      limit: Math.min(options.limit || 50, 200).toString(),
      offset: (options.offset || 0).toString()
    });

    if (options.status) params.append('status', options.status);
    if (options.integration) params.append('integration', options.integration);

    const response = await this._makeRequest('GET', `/api/v1/upload/history?${params}`, {
      headers: this.getHeaders(false) // No auth required
    });
    return response.json();
  }

  /**
   * Get file upload requirements and limits
   * @returns {Promise<Object>} Upload requirements
   */
  async getUploadInfo() {
    const response = await this._makeRequest('GET', '/api/v1/upload/info', {
      headers: this.getHeaders(false) // No auth required
    });
    return response.json();
  }

  // System Monitoring Methods (Admin only)

  /**
   * Get system logs (requires admin privileges)
   * @param {Object} options - Filter options
   * @returns {Promise<Object>} System logs data
   */
  async getSystemLogs(options = {}) {
    const params = new URLSearchParams({
      limit: (options.limit || 50).toString(),
      offset: (options.offset || 0).toString()
    });

    if (options.level) params.append('level', options.level);
    if (options.source) params.append('source', options.source);
    if (options.search) params.append('search', options.search);
    if (options.startTime) params.append('start_time', options.startTime);
    if (options.endTime) params.append('end_time', options.endTime);

    const response = await this._makeRequest('GET', `/api/v1/logs/?${params}`, {
      headers: this.getHeaders()
    });
    return response.json();
  }

  /**
   * Get system health metrics (requires admin privileges)
   * @returns {Promise<Object>} System health data
   */
  async getSystemHealth() {
    const response = await this._makeRequest('GET', '/api/v1/logs/health/', {
      headers: this.getHeaders()
    });
    return response.json();
  }

  /**
   * Get error rate analytics (requires admin privileges)
   * @param {string} [timeRange='24h'] - Time range (1h, 24h, 7d)
   * @returns {Promise<Object>} Error rate data
   */
  async getErrorRateAnalytics(timeRange = '24h') {
    const params = new URLSearchParams({ timeRange });
    const response = await this._makeRequest('GET', `/api/v1/logs/analytics/error-rate/?${params}`, {
      headers: this.getHeaders()
    });
    return response.json();
  }

  /**
   * Get log distribution by source (requires admin privileges)
   * @param {string} [timeRange='24h'] - Time range (1h, 24h, 7d)
   * @returns {Promise<Object>} Logs by source data
   */
  async getLogsBySource(timeRange = '24h') {
    const params = new URLSearchParams({ timeRange });
    const response = await this._makeRequest('GET', `/api/v1/logs/analytics/by-source/?${params}`, {
      headers: this.getHeaders()
    });
    return response.json();
  }

  /**
   * Get most frequent errors (requires admin privileges)
   * @param {number} [limit=10] - Number of top errors to return
   * @param {string} [timeRange='24h'] - Time range (1h, 24h, 7d)
   * @returns {Promise<Object>} Top errors data
   */
  async getTopErrors(limit = 10, timeRange = '24h') {
    const params = new URLSearchParams({ limit: limit.toString(), timeRange });
    const response = await this._makeRequest('GET', `/api/v1/logs/analytics/top-errors/?${params}`, {
      headers: this.getHeaders()
    });
    return response.json();
  }

  // System Status Methods

  /**
   * Get API health status
   * @returns {Promise<Object>} API status
   */
  async getApiStatus() {
    const response = await this._makeRequest('GET', '/api/v1/status', {
      headers: this.getHeaders(false) // No auth required
    });
    return response.json();
  }

  // Utility Methods

  /**
   * Upload multiple files from a FileList or array
   * @param {FileList|Array} files - Files to upload
   * @param {boolean} [forceReimport=false] - Whether to bypass duplicate detection
   * @param {Function} [progressCallback] - Optional progress callback
   * @returns {Promise<Array>} Array of upload results
   */
  async uploadMultipleFiles(files, forceReimport = false, progressCallback = null) {
    const results = [];
    const fileArray = Array.from(files);

    for (let i = 0; i < fileArray.length; i++) {
      const file = fileArray[i];
      
      try {
        console.log(`Uploading file ${i + 1}/${fileArray.length}: ${file.name}`);
        
        if (progressCallback) {
          progressCallback({
            fileIndex: i,
            totalFiles: fileArray.length,
            fileName: file.name,
            status: 'uploading'
          });
        }

        const result = await this.uploadNessusFile(file, null, forceReimport);
        
        results.push({
          file: file.name,
          success: true,
          result
        });

        if (progressCallback) {
          progressCallback({
            fileIndex: i,
            totalFiles: fileArray.length,
            fileName: file.name,
            status: 'completed',
            result
          });
        }
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error.message);
        
        results.push({
          file: file.name,
          success: false,
          error: error.message,
          errorType: error.constructor.name
        });

        if (progressCallback) {
          progressCallback({
            fileIndex: i,
            totalFiles: fileArray.length,
            fileName: file.name,
            status: 'failed',
            error: error.message
          });
        }
      }
    }

    return results;
  }
}

// Browser-specific file upload helpers
if (typeof window !== 'undefined') {
  /**
   * Create a file upload component with drag-and-drop support
   * @param {HTMLElement} container - Container element
   * @param {RiskRadarClient} client - Risk Radar client instance
   * @param {Object} [options] - Configuration options
   * @returns {Object} Upload component with methods
   */
  function createFileUploader(container, client, options = {}) {
    const config = {
      multiple: true,
      acceptedTypes: ['.nessus'],
      maxFileSize: 100 * 1024 * 1024, // 100MB
      ...options
    };

    // Create upload interface
    container.innerHTML = `
      <div class="file-upload-area" style="
        border: 2px dashed #ccc;
        border-radius: 8px;
        padding: 40px;
        text-align: center;
        cursor: pointer;
        transition: border-color 0.3s;
      ">
        <div class="upload-icon" style="font-size: 48px; margin-bottom: 16px;">📁</div>
        <div class="upload-text">
          <p style="margin: 0; font-size: 18px; font-weight: bold;">
            Drop .nessus files here or click to browse
          </p>
          <p style="margin: 8px 0 0 0; color: #666;">
            Maximum file size: ${config.maxFileSize / (1024 * 1024)}MB
          </p>
        </div>
        <input type="file" id="file-input" style="display: none;" 
               accept="${config.acceptedTypes.join(',')}" 
               ${config.multiple ? 'multiple' : ''}>
      </div>
      <div class="upload-progress" style="margin-top: 16px; display: none;">
        <div class="progress-bar" style="
          width: 100%;
          height: 20px;
          background: #f0f0f0;
          border-radius: 10px;
          overflow: hidden;
        ">
          <div class="progress-fill" style="
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049);
            width: 0%;
            transition: width 0.3s;
          "></div>
        </div>
        <div class="progress-text" style="margin-top: 8px; font-size: 14px;"></div>
      </div>
      <div class="upload-results" style="margin-top: 16px;"></div>
    `;

    const uploadArea = container.querySelector('.file-upload-area');
    const fileInput = container.querySelector('#file-input');
    const progressContainer = container.querySelector('.upload-progress');
    const progressFill = container.querySelector('.progress-fill');
    const progressText = container.querySelector('.progress-text');
    const resultsContainer = container.querySelector('.upload-results');

    // Event handlers
    uploadArea.addEventListener('click', () => fileInput.click());

    uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadArea.style.borderColor = '#4CAF50';
      uploadArea.style.backgroundColor = '#f9f9f9';
    });

    uploadArea.addEventListener('dragleave', () => {
      uploadArea.style.borderColor = '#ccc';
      uploadArea.style.backgroundColor = 'transparent';
    });

    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadArea.style.borderColor = '#ccc';
      uploadArea.style.backgroundColor = 'transparent';
      handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
      handleFiles(e.target.files);
    });

    async function handleFiles(files) {
      if (files.length === 0) return;

      // Validate files
      const validFiles = Array.from(files).filter(file => {
        if (file.size > config.maxFileSize) {
          showResult(file.name, false, `File too large (${Math.round(file.size / 1024 / 1024)}MB > ${config.maxFileSize / 1024 / 1024}MB)`);
          return false;
        }
        if (!config.acceptedTypes.some(type => file.name.toLowerCase().endsWith(type.substring(1)))) {
          showResult(file.name, false, 'Invalid file type');
          return false;
        }
        return true;
      });

      if (validFiles.length === 0) return;

      // Show progress
      progressContainer.style.display = 'block';
      resultsContainer.innerHTML = '';

      try {
        const results = await client.uploadMultipleFiles(validFiles, false, (progress) => {
          const percentage = ((progress.fileIndex + (progress.status === 'completed' ? 1 : 0)) / progress.totalFiles) * 100;
          progressFill.style.width = `${percentage}%`;
          progressText.textContent = `${progress.status} ${progress.fileName} (${progress.fileIndex + 1}/${progress.totalFiles})`;

          if (progress.status === 'completed' && progress.result) {
            showResult(progress.fileName, true, `Processed: ${progress.result.statistics?.assets_processed || 0} assets, ${progress.result.statistics?.findings_processed || 0} findings`);
          } else if (progress.status === 'failed') {
            showResult(progress.fileName, false, progress.error);
          }
        });

        progressText.textContent = `Upload completed! ${results.filter(r => r.success).length}/${results.length} files successful`;
      } catch (error) {
        progressText.textContent = `Upload failed: ${error.message}`;
      }
    }

    function showResult(filename, success, message) {
      const resultDiv = document.createElement('div');
      resultDiv.style.cssText = `
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 4px;
        background: ${success ? '#d4edda' : '#f8d7da'};
        border: 1px solid ${success ? '#c3e6cb' : '#f5c6cb'};
        color: ${success ? '#155724' : '#721c24'};
        font-size: 14px;
      `;
      resultDiv.innerHTML = `
        <strong>${filename}</strong>: ${message}
      `;
      resultsContainer.appendChild(resultDiv);
    }

    return {
      setConfig: (newConfig) => Object.assign(config, newConfig),
      reset: () => {
        progressContainer.style.display = 'none';
        resultsContainer.innerHTML = '';
        fileInput.value = '';
      }
    };
  }

  // Make createFileUploader available globally
  window.createFileUploader = createFileUploader;
}

// Export for different environments
if (typeof module !== 'undefined' && module.exports) {
  // Node.js
  module.exports = {
    RiskRadarClient,
    RiskRadarError,
    AuthenticationError,
    PermissionError,
    DuplicateFileError
  };
} else if (typeof window !== 'undefined') {
  // Browser
  window.RiskRadarClient = RiskRadarClient;
  window.RiskRadarError = RiskRadarError;
  window.AuthenticationError = AuthenticationError;
  window.PermissionError = PermissionError;
  window.DuplicateFileError = DuplicateFileError;
}

// Example usage
async function exampleUsage() {
  const client = new RiskRadarClient({
    baseUrl: 'https://riskradar.dev.securitymetricshub.com',
    token: 'your-jwt-token'
  });

  try {
    // Test authentication
    console.log('Testing authentication...');
    if (await client.isAuthenticated()) {
      const profile = await client.getUserProfile();
      console.log('✓ Authenticated as:', profile.user.email);
    } else {
      console.log('✗ Authentication failed');
      return;
    }

    // Get API status
    console.log('\nChecking API status...');
    const status = await client.getApiStatus();
    console.log('✓ API Status:', status.status);

    // Get upload requirements
    console.log('\nGetting upload requirements...');
    const uploadInfo = await client.getUploadInfo();
    console.log('✓ Max file size:', uploadInfo.file_upload_limits.max_file_size_mb, 'MB');

    // Get upload history
    console.log('\nGetting recent uploads...');
    const history = await client.getUploadHistory({ limit: 5 });
    console.log('✓ Found', history.total_count, 'total uploads');

    console.log('\n✓ All tests completed successfully!');
  } catch (error) {
    console.error('✗ Error:', error.message);
  }
}

// Uncomment to run example
// exampleUsage(); 