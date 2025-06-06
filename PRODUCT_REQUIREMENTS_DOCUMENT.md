# Risk Radar Product Requirements Document (MVP)

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Features Overview](#features-overview)
3. [System Architecture](#system-architecture)
4. [Core Data Model](#core-data-model)
5. [Feature Specifications](#feature-specifications)
6. [Ingestion Architecture](#ingestion-architecture)
7. [Implementation Guide](#implementation-guide)
8. [Non-Functional Requirements](#non-functional-requirements)
9. [Appendices](#appendices)

---

## Executive Summary

Risk Radar is a vulnerability management platform that consolidates security data from multiple sources, prioritises risks based on business context, and tracks remediation efforts. The platform uses a flexible, configuration-driven architecture that enables integration with any vulnerability scanner without code changes.

### Core Value Propositions
- **Multi-Scanner Support**: Integrate any vulnerability scanner through configuration, not code
- **Deduplication**: Asset and vulnerability correlation across sources
- **Business Context**: Risk scoring based on asset criticality and organisational structure
- **Remediation Tracking**: Campaign management with SLA enforcement and performance metrics
- **Extensibility**: Schema designed for evolution without migrations

---

## Features Overview

Risk Radar provides a vulnerability management platform with features designed to streamline security operations from discovery through remediation. Built on industry best practices and proven vulnerability management principles, the platform delivers the following capabilities:

### 🔍 Discovery & Ingestion
- **Multi-Scanner Support**: Integrate any vulnerability scanner through configuration-driven field mappings
- **Automated Asset Discovery**: Continuous asset inventory updates from multiple sources
- **Deduplication**: Correlation logic prevents duplicate assets and vulnerabilities
- **Production File Upload System**: ✅ **FULLY IMPLEMENTED** - Direct upload of Nessus scanner reports with duplicate detection
- **Nessus Parser**: ✅ **FULLY IMPLEMENTED** - XML processing with dynamic field mapping and asset categorisation
- **Real-time Sync**: Automated connector scheduling with activity logging

### 🔧 Integration Management System ✨ **NEW FEATURE**
- **Visual Integration Gallery**: Modern card-based interface showcasing 15+ available and planned integrations
- **Multi-Type Support**: File upload, API connections, cloud storage, webhooks, and custom integrations
- **Configuration Wizard**: Guided 8-step setup with connection testing and data preview
- **Integration Templates**: Pre-configured setups for major vendors (Nessus, Qualys, CrowdStrike, etc.)
- **Advanced Scheduling**: Cron-based sync scheduling with timezone support and conflict detection
- **Health Monitoring**: Real-time status tracking, error alerts, and performance metrics
- **Connection Testing**: Validate credentials, endpoints, and data access before activation
- **Data Preview**: Sample data display during setup to verify field mappings
- **Field Mapping Studio**: Visual drag-and-drop interface for complex data transformations
- **Rate Limiting**: Configurable API throttling and retry logic per integration
- **Sync Management**: Manual sync triggers, progress tracking, and history retention
- **Error Recovery**: Automatic retry with exponential backoff and dead letter handling
- **Notification System**: Email/Slack alerts for sync failures, thresholds, and health issues
- **Activity Logging**: Comprehensive audit trail for compliance and troubleshooting
- **Multi-Environment**: Support for dev/staging/production configurations per integration

### 📊 Risk Management
- **Business Context Integration**: Business Groups and Asset Tags for organisational alignment
- **Dynamic Risk Scoring**: Multi-factor risk calculation combining severity, threats, and business impact
- **Threat Intelligence**: Integration with exploit databases and threat feeds
- **Vulnerability Prioritisation**: VPR-style scoring beyond basic CVSS
- **Custom Risk Weights**: Configurable importance factors for your environment

### 🎯 Asset Management
- **Unified Asset Inventory**: Single source of truth across all scanners
- **Multi-Type Support**: Hosts, websites, code repositories, containers, cloud resources
- **Advanced Deduplication**: Priority-based matching (cloud ID → agent UUID → MAC → hostname → IP)
- **Proactive Detach**: Automatic splitting of incorrectly merged assets
- **Dynamic Properties**: Custom metadata and ownership assignment

### 📈 Analytics & Reporting
- **Executive Dashboard**: Real-time KPIs and risk trends
- **MTTR Analytics**: Mean Time to Remediate by severity, group, and asset type
- **SLA Compliance**: Track performance against defined service levels
- **Remediation Velocity**: Daily/weekly/monthly fix rates and capacity analysis
- **Custom Reports**: Self-service report builder with export capabilities
- **Trend Analysis**: Historical comparisons with improvement tracking

### 🔧 Remediation Management
- **Campaign Tracking**: Group remediation efforts with progress monitoring
- **Ticketing Integration**: JIRA, ServiceNow, Azure Boards connectors
- **Remediation Work Form**: External user interface for collaboration
- **Bulk Operations**: Mass status updates and assignments
- **Due Date Management**: SLA-driven or manual deadline setting
- **Fix Verification**: Automatic closure when vulnerabilities remediated

### 🤖 Automation & Workflows
- **Playbook Engine**: Condition-based automation for routine tasks
- **Auto-Ticketing**: Create tickets based on vulnerability criteria
- **Smart Updates**: Append new findings to existing tickets
- **Notification System**: Email/Slack alerts for critical events
- **Scheduled Actions**: Time-based automation triggers

### 🛡️ Compliance & Governance
- **Exception Requests**: Risk acceptance workflow with approvals
- **Audit Trail**: Complete activity logging for compliance
- **Role-Based Access**: Granular permissions by business group
- **SLA Policies**: Configurable by severity and business group
- **Compliance Reports**: Pre-built templates for common frameworks

### 🔐 Security & Administration
- **SSO Integration**: SAML/OIDC support for enterprise authentication
- **Row-Level Security**: Database-enforced access controls
- **API Access**: RESTful APIs for integration and automation
- **Multi-Tenancy**: Logical separation of business units
- **Backup & Recovery**: Automated backup with point-in-time recovery

### 📖 Developer Experience & API Documentation
- **Interactive Documentation**: Swagger/OpenAPI specification with live testing
- **Postman Collections**: Ready-to-import API testing collections
- **Developer Portal**: Comprehensive API guides and examples
- **Code Examples**: Python, JavaScript, and cURL integration examples
- **Authentication Guides**: JWT token setup and usage documentation
- **Error Handling**: Standardised error responses and troubleshooting guides

### 📊 System Monitoring & Logs
- **Centralised Log Management**: System, application, and container logs in unified interface
- **Real-time Log Streaming**: Live log monitoring with WebSocket updates
- **Advanced Log Filtering**: Filter by level, source, user, date range, and custom search
- **Log Analytics**: Error trending, performance monitoring, and system health metrics
- **Admin Log Access**: Secure admin-only access to sensitive system logs
- **Request Correlation**: Track requests across services with correlation IDs
- **Log Retention**: Automated cleanup with configurable retention policies

---

## MVP Feature Matrix

The following table outlines which features will be implemented in the MVP phase versus future releases:

| Feature Category | Feature | MVP | Future | Notes |
|-----------------|---------|-----|---------|-------|
| **Discovery & Ingestion** | | | | |
| | Nessus file upload & parsing | ✅ | | Core MVP requirement |
| | Qualys integration | ❌ | ✅ | Phase 3 |
| | CrowdStrike integration | ❌ | ✅ | Phase 3 |
| | Real-time connector sync | ❌ | ✅ | Manual upload only in MVP |
| | Connector activity logging | ✅ | | Basic logging via Django |
| **Integration Management** | | | | |
| | Visual integration gallery | ✅ | | Modern card-based UI with roadmap |
| | Nessus file upload (active) | ✅ | | Production-ready integration |
| | Integration templates | ✅ | | Pre-configured vendor setups |
| | Configuration wizard | ✅ | | 8-step guided setup process |
| | Connection testing | ✅ | | Validate settings before activation |
| | Data preview | ✅ | | Sample data during setup |
| | Basic field mapping | ✅ | | Manual configuration interface |
| | Health monitoring | ✅ | | Status indicators and error tracking |
| | API integrations | ❌ | ✅ | Qualys, Tenable.io, CrowdStrike APIs |
| | Cloud storage integrations | ❌ | ✅ | S3, Azure Blob, GCP Storage |
| | Webhook integrations | ❌ | ✅ | Real-time data push notifications |
| | Advanced scheduling | ❌ | ✅ | Cron-based automation with timezones |
| | Field mapping studio | ❌ | ✅ | Visual drag-and-drop interface |
| | Rate limiting | ❌ | ✅ | API throttling and retry logic |
| | Notification system | ❌ | ✅ | Email/Slack alerts for issues |
| | Multi-environment support | ❌ | ✅ | Dev/staging/production configs |
| **Risk Management** | | | | |
| | Basic risk scoring (severity-based) | ✅ | | Simplified formula |
| | Threat intelligence integration | ❌ | ✅ | Phase 4 |
| | Custom risk weights | ✅ | | Via Django admin |
| | VPR-style scoring | ❌ | ✅ | CVSS only in MVP |
| **Asset Management** | | | | |
| | Asset CRUD operations | ✅ | | Via Supabase direct access |
| | Basic deduplication | ✅ | | Hostname + IP matching |
| | Advanced deduplication | ❌ | ✅ | Full algorithm in Phase 2 |
| | Proactive detach | ❌ | ✅ | Phase 3 |
| | Business Groups | ✅ | | Essential for MVP |
| | Asset Tags | ✅ | | Manual tagging only |
| | Dynamic properties | ❌ | ✅ | Phase 4 |
| **Analytics & Reporting** | | | | |
| | Basic dashboard | ✅ | | Key metrics only |
| | MTTR reporting | ✅ | | Core KPI |
| | SLA compliance tracking | ✅ | | Basic implementation |
| | Remediation velocity | ❌ | ✅ | Phase 3 |
| | Custom report builder | ❌ | ✅ | Phase 5 |
| | Export to CSV | ✅ | | Basic export |
| **Remediation Management** | | | | |
| | Manual status updates | ✅ | | Via Supabase UI |
| | Campaign management | ❌ | ✅ | Phase 4 |
| | Ticketing integration | ❌ | ✅ | Phase 4 |
| | Bulk operations | ✅ | | Basic bulk update |
| | Fix verification | ✅ | | Status tracking only |
| **Automation** | | | | |
| | Playbook engine | ❌ | ✅ | Phase 5 |
| | Auto-ticketing | ❌ | ✅ | Phase 5 |
| | Email notifications | ❌ | ✅ | Phase 4 |
| | Scheduled imports | ❌ | ✅ | Phase 3 |
| **Compliance** | | | | |
| | Exception requests | ❌ | ✅ | Phase 4 |
| | Basic audit logging | ✅ | | Django logging |
| | Advanced audit trail | ❌ | ✅ | Phase 5 |
| | Compliance reports | ❌ | ✅ | Phase 5 |
| **Security & Admin** | | | | |
| | JWT authentication | ✅ | | Via Supabase |
| | Row-level security | ✅ | | Supabase RLS |
| | Basic role management | ✅ | | Admin/User roles |
| | Advanced RBAC | ❌ | ✅ | Phase 5 |
| | SSO integration | ❌ | ✅ | Phase 6 |
| | REST API (minimal) | ✅ | | Upload & reports only |
| | Full REST API | ❌ | ✅ | Phase 7 |
| **System Monitoring** | | | | |
| | Basic system logs | ✅ | | Django logging only |
| | Centralised log management | ❌ | ✅ | Phase 3 |
| | Real-time log streaming | ❌ | ✅ | Phase 3 |
| | Log analytics & trending | ❌ | ✅ | Phase 4 |
| | Advanced log filtering | ❌ | ✅ | Phase 3 |
| | Request correlation | ❌ | ✅ | Phase 4 |
| **UI/UX** | | | | |
| | lovable.dev UI | ✅ | | Rapid development |
| | Mobile responsive | ✅ | | Built-in with lovable |
| | Dark mode | ❌ | ✅ | Future enhancement |
| | Custom branding | ❌ | ✅ | Enterprise feature |
| **Developer Experience** | | | | |
| | Interactive API documentation | ✅ | | Swagger/OpenAPI spec |
| | Postman collections | ✅ | | Ready-to-import testing |
| | Code examples | ✅ | | Python, JS, cURL samples |
| | Authentication guides | ✅ | | JWT token setup |
| | Developer portal | ❌ | ✅ | Advanced documentation |

### MVP Success Criteria
The MVP will be considered successful when it can:
1. ✅ Import and parse Nessus scan files
2. ✅ Display vulnerabilities and affected assets with filtering
3. ✅ Calculate basic risk scores
4. ✅ Track remediation progress with status updates
5. ✅ Show MTTR and SLA compliance metrics
6. ✅ Support business groups for organisational context
7. ✅ Provide basic user access control
8. ✅ Export data for external reporting
9. ✅ Provide comprehensive API documentation for developers

---

## File Upload & Parsing System (Production Ready)

Risk Radar includes a file upload and parsing system that is **fully implemented and production-ready**. This system provides vulnerability data ingestion with duplicate detection and processing capabilities.

### File Upload API System

**File Upload Handling**
- **RESTful API Endpoint**: `POST /api/v1/upload/nessus` accepts multipart file uploads
- **File Validation**: Validation of file type (.nessus), size limits (100MB), and format integrity
- **Authentication Support**: Optional JWT token authentication with user tracking
- **Progress Tracking**: Upload progress and processing status
- **Error Handling**: Error responses with diagnostic information

**Duplicate Detection**
- **SHA-256 File Hashing**: Every uploaded file is fingerprinted using cryptographic hashing
- **Deduplication**: Prevents re-processing of identical scan files
- **Force Re-import Option**: `?force_reimport=true` parameter bypasses duplicate detection when needed
- **Upload History Tracking**: Audit trail of all uploads with timestamps and user attribution
- **Conflict Resolution**: Messaging when duplicates are detected with resolution options

**Upload Response Data**
The upload API provides feedback including:
- File processing statistics (assets created/updated, vulnerabilities processed, findings generated)
- Upload metadata (file hash, size, processing time)
- Parser performance metrics (creation vs update counts)
- Error reporting with line-by-line diagnostics
- User attribution and authentication status

### Nessus Parser Engine

**XML Processing**
- **Standards-Compliant Parser**: Support for Nessus .nessus XML format specification
- **Field Extraction**: Database-driven field mapping system - no code changes needed for new fields
- **Nested Data Handling**: Extraction of nested XML elements and attributes
- **Large File Support**: Processing of multi-gigabyte scan files
- **Memory Management**: Streaming XML processing prevents memory exhaustion

**Asset Processing**
- **Multi-Identifier Recognition**: Extracts hostnames, IP addresses, MAC addresses, FQDN, NetBIOS names
- **Operating System Detection**: Normalises OS information from scanner output
- **Asset Categorisation**: Classification using 86-subtype system
- **Deduplication**: Priority-based asset matching (cloud ID → agent UUID → MAC → hostname → IP)
- **Metadata Preservation**: Storage of scan timing, scanner version, and custom attributes

**Vulnerability Data Extraction**
- **CVE Correlation**: Extraction and correlation of CVE identifiers
- **Multi-Reference Support**: Captures BID, OSVDB, vendor advisories, and custom references
- **CVSS Processing**: CVSS v2 and v3 score extraction with vector notation
- **Exploit Intelligence**: Detection of exploit availability, framework compatibility
- **Severity Normalisation**: Database-driven mapping of scanner-specific severity scales to internal standards
- **Temporal Tracking**: Publication dates, modification dates, and patch availability timelines

**Finding Generation & Correlation**
- **Finding Identification**: Deduplication using asset + vulnerability + port + protocol + service
- **Network Context**: Capture of port numbers, protocols, and service names
- **Evidence Preservation**: Plugin output, detection methods, and scanner-specific metadata
- **Risk Calculation**: Risk scoring based on severity, asset criticality, and threat intelligence
- **Temporal Tracking**: First seen, last seen, and remediation timestamps for MTTR calculations

### Database-Driven Configuration

**Field Mapping System**
- **No-Code Integration**: Add support for new scanners without code changes
- **Transformation Rules**: Data transformation capabilities (lowercase, split, regex, custom functions)
- **Extensible Design**: JSONB storage for scanner-specific data that doesn't fit standard schema
- **Validation & Defaults**: Field-level validation with fallback default values
- **Priority Ordering**: Processing order for dependent field mappings

**Severity Mapping Engine**
- **Scanner-Agnostic**: Each scanner integration has its own severity mapping configuration
- **Flexible Scales**: Support for numeric (0-5), descriptive (Critical/High/Medium/Low), or custom scales
- **Internal Normalisation**: All severities mapped to consistent 0-10 internal scale
- **Label Generation**: Generation of human-readable severity labels
- **Compliance Ready**: Mapping supports regulatory frameworks (PCI, SOX, etc.)

### Production Deployment Features

**Upload Management**
- **Concurrent Processing**: Multiple files can be uploaded and processed simultaneously
- **Queue Management**: Background processing with status tracking
- **Retry Logic**: Retry of failed uploads with exponential backoff
- **File Cleanup**: Cleanup of temporary files with configurable retention
- **Audit Logging**: Logging of all upload activities for compliance
- **Automated Infrastructure**: GitHub Actions automatically configures upload directory permissions during deployment

**Performance Optimisation**
- **Bulk Operations**: Database operations using Django bulk_create/bulk_update
- **Transaction Management**: Atomic processing ensures data consistency
- **Connection Pooling**: Database connections for high-throughput processing
- **Memory Efficiency**: Streaming processing prevents memory issues with large files
- **Index Optimisation**: Database indexes optimised for common query patterns

**Infrastructure Automation**
- **Deployment Integration**: Upload directory creation and permission setup automated via GitHub Actions
- **Permission Management**: Proper file system permissions configured automatically during deployment
- **Environment Configuration**: Automated environment variable and directory setup
- **Zero-Touch Deployment**: Complete infrastructure provisioning without manual server access

### Frontend Integration Ready

**API Endpoints Available**
- `POST /api/v1/upload/nessus` - File upload with response data
- `GET /api/v1/upload/history` - Upload history with filtering
- `GET /api/v1/upload/info` - Upload requirements and system limits
- `GET /api/v1/status` - System health and processing status

**Frontend Integration Points**
The upload system is designed for frontend integration:
- **RESTful Design**: Standard HTTP responses with JSON payloads
- **Progress Callbacks**: Upload progress and processing status
- **Error Handling**: Structured error responses for user-friendly messaging
- **File Validation**: Client-side validation rules available via API
- **Authentication Integration**: JWT token integration for user attribution

**lovable.dev Integration Ready**
The file upload system is positioned for rapid frontend development:
- **Drag-and-Drop Support**: API designed for modern file upload components
- **Real-time Feedback**: Response data for progress indicators
- **Error Display**: Structured error messages for user feedback
- **Upload History**: Audit trail for dashboard display
- **Statistics Dashboard**: Processing statistics for analytics widgets

This production-ready upload and parsing system eliminates the need for complex backend development, allowing frontend teams to focus on creating user experiences while leveraging data processing capabilities.

---

## Developer Experience & API Documentation (Production Ready)

Risk Radar provides a comprehensive developer experience with multiple documentation formats and integration tools to make API consumption simple and efficient.

### API Documentation System

**Interactive Documentation**
- **Swagger/OpenAPI Specification**: Auto-generated from Django code with live testing capability
- **Interactive API Explorer**: Test endpoints directly from documentation browser
- **Request/Response Examples**: Complete examples for all endpoints
- **Authentication Testing**: Built-in JWT token testing interface
- **Schema Validation**: Real-time request/response validation

**Multi-Format Documentation**
- **Written Guides**: Comprehensive developer documentation in `/docs/api/`
- **Postman Collections**: Ready-to-import collections with pre-configured requests
- **Code Examples**: Integration examples in Python, JavaScript, and cURL
- **Authentication Guides**: Step-by-step JWT token setup and usage

### Developer Tools & Resources

**Postman Integration**
- **Complete API Collection**: All endpoints with examples and tests
- **Environment Variables**: Pre-configured for production and development
- **Automated Testing**: Built-in tests for response validation
- **Authentication Setup**: JWT token configuration examples
- **Error Scenarios**: Test cases for error handling validation

**Code Examples Library**
- **Python Client**: Complete SDK with error handling and retry logic
- **JavaScript Integration**: Frontend integration examples
- **cURL Scripts**: Command-line testing and automation examples
- **Authentication Flows**: Token acquisition and refresh examples

**Documentation Portal Structure**
```
/docs/api/
├── api-guide.md              # Complete developer guide
├── authentication.md         # JWT token setup and usage
├── risk-radar-api.postman_collection.json  # Postman collection
├── risk-radar-api.openapi.yml             # OpenAPI specification
└── examples/
    ├── python-client.py      # Python SDK example
    ├── javascript-client.js  # JavaScript integration
    └── curl-examples.sh      # Command-line examples
```

### API Endpoints Documentation

**Live Interactive Documentation**
- **Production**: `https://riskradar.dev.securitymetricshub.com/api/docs/`
- **Alternative Format**: `https://riskradar.dev.securitymetricshub.com/api/redoc/`
- **OpenAPI Schema**: `https://riskradar.dev.securitymetricshub.com/api/schema/`

**Core API Endpoints**
```bash
# File Upload & Management
POST   /api/v1/upload/nessus        # Upload Nessus files
GET    /api/v1/upload/history       # Upload audit trail
GET    /api/v1/upload/info          # Upload requirements

# Authentication & User Management
GET    /api/v1/auth/status          # Check authentication
GET    /api/v1/auth/profile         # User profile & permissions

# System Monitoring (Admin Only)
GET    /api/v1/logs/                # System logs with filtering
GET    /api/v1/logs/analytics/      # Log analytics & trends
GET    /api/v1/logs/health/         # System health metrics

# System Status
GET    /api/v1/status               # API health check
```

### Developer Support Features

**Error Handling & Debugging**
- **Standardised Error Responses**: Consistent JSON error format across all endpoints
- **HTTP Status Codes**: Proper status codes for all scenarios
- **Error Documentation**: Common errors with solutions
- **Debugging Headers**: Request correlation IDs for troubleshooting

**Rate Limiting & Performance**
- **Documented Limits**: Clear rate limits for each endpoint type
- **Performance Guidelines**: Best practices for high-volume usage
- **Pagination Support**: Efficient data retrieval for large datasets
- **Caching Headers**: Proper cache control for optimal performance

**Authentication & Security**
- **JWT Token Documentation**: Complete token lifecycle management
- **Security Best Practices**: Token storage and refresh guidelines
- **CORS Configuration**: Cross-origin request setup
- **API Versioning**: Forward compatibility guidelines

### Integration Examples

**Quick Start Integration**
```python
# Python client example
from risk_radar_client import RiskRadarClient

client = RiskRadarClient(
    base_url='https://riskradar.dev.securitymetricshub.com',
    token='your-jwt-token'
)

# Upload a file
result = client.upload_nessus_file('scan.nessus')
print(f"Processed: {result['statistics']}")

# Get upload history
history = client.get_upload_history()
```

**Frontend Integration**
```javascript
// JavaScript/React integration
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/v1/upload/nessus', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  return response.json();
};
```

This comprehensive developer experience ensures easy API adoption and reduces integration time for development teams.

---

## System Architecture

### Technical Stack (Hybrid Architecture)
- **Database**: PostgreSQL (managed by Supabase) with JSONB for extensibility
- **Authentication**: Supabase Auth with JWT tokens
- **Storage**: Supabase Storage for scanner files
- **Direct CRUD**: Supabase auto-generated APIs for basic operations
- **Complex Logic**: Django for parsing, risk calculation, reporting
- **Frontend**: lovable.dev for rapid UI development
- **Background Jobs**: Django-Q with Redis for async processing

### MVP Architecture Philosophy
The MVP leverages Supabase's capabilities to minimise backend development:
- **Direct Database Access**: lovable.dev connects directly to Supabase for most CRUD operations
- **Row Level Security**: Supabase RLS policies handle data access control
- **Minimal API Surface**: Django provides endpoints only for complex operations that can't be handled by direct DB access
- **Rapid Development**: lovable.dev's visual builder accelerates UI creation

### Data Flow Architecture
```
┌─────────────────┐     ┌────────────────┐     ┌──────────────────┐
│ Scanner Sources │────▶│ Django         │────▶│ PostgreSQL       │
│ (Nessus files) │     │ (Parser)       │     │ (Supabase)       │
└─────────────────┘     └────────────────┘     └──────────────────┘
                                                       │
                                                       ▼
                        ┌────────────────┐      ┌──────────────────┐
                        │ Supabase Auth  │      │ lovable.dev UI   │
                        │ & Storage      │◀────▶│ - Direct DB CRUD │
                        └────────────────┘      │ - Django APIs    │
                                                └──────────────────┘
```

### Django API Endpoints (Currently Implemented)
```
# File Operations - ✅ PRODUCTION READY
POST   /api/v1/upload/nessus        # ✅ Upload & parse Nessus file (COMPLETE)
GET    /api/v1/upload/history       # ✅ Upload history with filtering (COMPLETE)
GET    /api/v1/upload/info          # ✅ Upload requirements and limits (COMPLETE)
GET    /api/v1/status               # ✅ System health and status (COMPLETE)

# Planned Log Management Operations
GET    /api/v1/logs                 # Get filtered logs with pagination
WS     /ws/logs/                    # Real-time log streaming
GET    /api/v1/logs/analytics/error-rate  # Error rate trending
GET    /api/v1/logs/analytics/by-source   # Logs by source breakdown
GET    /api/v1/logs/analytics/top-errors  # Most frequent errors
GET    /api/v1/logs/docker/{container}    # Container logs
GET    /api/v1/logs/health          # System health metrics

# Planned Complex Operations  
POST   /api/v1/risk/calculate       # Recalculate risk scores
GET    /api/v1/reports/sla          # SLA compliance report
GET    /api/v1/reports/mttr         # MTTR metrics
POST   /api/v1/campaigns/create     # Create remediation campaign

# All other CRUD operations handled directly via Supabase
```

---

## Core Data Model

### Schema Overview
The schema centres on separate tables for assets, vulnerabilities, and findings to normalise data and avoid duplication. An integrations table lists all configured integrations, while integration_field_mappings and severity_mapping tables provide flexible mapping from vendor-specific fields and severity ratings to the internal schema.

### 3.1 Scanner Integration Table

> **Note**: Enhanced as of 2025-01-02 to include default asset category assignment for improved scanner-specific asset classification.

#### Enhanced Implementation (Current)
```sql
CREATE TABLE integrations (
    integration_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL DEFAULT 'vuln_scanner',  -- e.g., 'vuln_scanner', 'asset_inventory'
    default_asset_category_id INTEGER REFERENCES asset_category(category_id) ON DELETE SET NULL,
    version VARCHAR(50),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Legacy Design (Reference)
```sql
CREATE TABLE integrations (
    integration_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,               -- e.g., 'vuln_scanner', 'asset_inventory'
    description TEXT,
    active BOOLEAN DEFAULT TRUE
);
```

**Purpose**: Lists each external scanner integration configured in the system. Enhanced to provide default asset categorisation based on scanner type.

**Enhanced Field Descriptions**:
- `integration_id`: Synthetic primary key used throughout the system
- `name`: Human-readable name (e.g., "Nessus", "Qualys VM", "CrowdStrike Falcon")
- `type`: Category of integration for future extensibility
- `default_asset_category_id`: Default category for assets from this scanner (e.g., Nessus defaults to "Host")
- `version`: Scanner version for compatibility tracking
- `description`: Optional text describing the integration or version
- `is_active`: Enables/disables data sync without removing configuration
- `created_at`: Timestamp for audit and tracking purposes

### 3.2 Asset Types Table

> **Note**: This section describes the original asset types design. As of 2025-01-02, this has been enhanced with the implementation of AssetCategory and AssetSubtype models providing 86 standard subtypes across 5 main categories. See CHANGES.md for full details.

#### Enhanced Implementation (Current)
```sql
CREATE TABLE asset_category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE asset_subtype (
    subtype_id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES asset_category(category_id),
    name VARCHAR(100) NOT NULL,
    cloud_provider VARCHAR(20),  -- AWS, Azure, GCP for Cloud Resource category
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(category_id, name, cloud_provider)
);
```

**Current Categories**:
- `Host` (18 subtypes) - Physical servers, VMs, workstations, network devices, IoT
- `Code Project` (11 subtypes) - Repositories, application projects, libraries
- `Website` (6 subtypes) - Web applications, APIs, domains
- `Image` (8 subtypes) - Container images, VM images
- `Cloud Resource` (43 subtypes) - AWS/Azure/GCP resources with provider-specific classification

#### Legacy Design (Reference)
```sql
CREATE TABLE asset_types (
    asset_type_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
```

**Purpose**: Originally defined basic asset types. Enhanced implementation provides sophisticated categorisation with provider-aware cloud resource classification and standardised subtypes from ASSET_TYPES.md specification.

### 3.3 Assets Table

> **Note**: This schema has been enhanced as of 2025-01-02 to include category and subtype foreign key references for sophisticated asset classification.

#### Enhanced Implementation (Current)
```sql
CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    hostname VARCHAR(255),
    ip_address INET,
    -- Enhanced categorisation
    category_id INTEGER NOT NULL REFERENCES asset_category(category_id) ON DELETE PROTECT,
    subtype_id INTEGER REFERENCES asset_subtype(subtype_id) ON DELETE SET NULL,
    -- Legacy compatibility
    asset_type_id INTEGER REFERENCES asset_types(asset_type_id) ON DELETE PROTECT,
    -- Enhanced fields
    operating_system VARCHAR(100),
    mac_address VARCHAR(50),
    extra JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(hostname, ip_address)
);
```

#### Legacy Design (Reference)
```sql
CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    hostname VARCHAR(255),
    ip_address INET,
    asset_type_id INTEGER NOT NULL REFERENCES asset_types(asset_type_id),
    operating_system VARCHAR(100),
    mac_address VARCHAR(50),
    extra JSONB,                    -- unstructured metadata (e.g., cloud IDs, tags)
    UNIQUE(hostname, ip_address)
);
```

**Purpose**: Stores unique IT assets discovered by scanners. Enhanced to support sophisticated categorisation while maintaining backward compatibility.

**Enhanced Field Descriptions**:
- `category_id`: Reference to AssetCategory (Host, Code Project, Website, Image, Cloud Resource)
- `subtype_id`: Reference to AssetSubtype (Server, Router, GitHub Repository, Docker Image, EC2 Instance, etc.)
- `asset_type_id`: Legacy field maintained for backward compatibility during migration
- `name`: Asset display name (auto-generated from hostname/IP if not provided)
- `hostname` / `ip_address`: Core identifiers with unique constraint for deduplication
- `operating_system`: Normalised OS name/version
- `mac_address`: Network interface identifier for correlation
- `extra`: Enhanced JSONB field storing:
  - `fqdn`: Fully qualified domain name
  - `netbios_name`: Windows NetBIOS name
  - `system_type`: Original scanner system type value
  - `scan_start_time` / `scan_end_time`: Scan timing metadata
  - Cloud identifiers (AWS instance ID, Azure VM ID, GCP instance ID)
  - Agent UUIDs
  - Scanner-specific attributes

**Deduplication Strategy**:
1. Cloud instance IDs (highest priority)
2. Agent UUIDs
3. MAC address + hostname
4. Hostname + primary IP
5. IP address only (lowest priority)

### 3.4 Vulnerabilities Table
```sql
CREATE TABLE vulnerabilities (
    vulnerability_id SERIAL PRIMARY KEY,
    cve_id VARCHAR(50),                     -- e.g., 'CVE-2023-12345'
    external_id VARCHAR(100),               -- scanner-specific vuln ID
    external_source VARCHAR(50),            -- source of external_id
    title TEXT NOT NULL,
    description TEXT,
    cvss_score NUMERIC(4,1),                -- CVSS base score 0.0-10.0
    severity_level SMALLINT,                -- normalised 0-10 scale
    severity_label VARCHAR(20),             -- normalised label
    fix_info TEXT,                          -- remediation advice
    published_at TIMESTAMPTZ,               -- vulnerability publication date
    modified_at TIMESTAMPTZ,                -- last update date
    extra JSONB,                            -- extensible metadata
    UNIQUE(cve_id),
    UNIQUE(external_source, external_id)
);
```

**Purpose**: Centralised vulnerability catalogue with normalised severity and deduplication support.

**Field Descriptions**:
- `cve_id`: Standard CVE identifier for cross-scanner deduplication
- `external_id` & `external_source`: Scanner-specific identifiers (e.g., Nessus pluginID, Qualys QID)
- `title`: Short, descriptive name
- `description`: Full vulnerability details
- `cvss_score`: Industry-standard severity metric
- `severity_level` & `severity_label`: Normalised internal severity (via severity_mapping)
- `fix_info`: Remediation instructions
- `published_at` / `modified_at`: Temporal tracking
- `extra`: JSONB for extensible data:
  - Exploit availability flags
  - Reference URLs (BID, OSVDB, vendor advisories)
  - CWE IDs
  - Scanner-specific metadata

### 3.5 Findings Table
```sql
CREATE TABLE findings (
    finding_id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(asset_id) ON DELETE CASCADE,
    vulnerability_id INTEGER NOT NULL REFERENCES vulnerabilities(vulnerability_id) ON DELETE CASCADE,
    integration_id INTEGER NOT NULL REFERENCES integrations(integration_id) ON DELETE CASCADE,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    fixed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'open',      -- 'open', 'fixed', 'risk_accepted'
    severity_level SMALLINT,                -- normalised severity at finding level
    port VARCHAR(10),                       -- network port if applicable
    protocol VARCHAR(10),                   -- protocol if applicable
    service VARCHAR(100),                   -- service name
    risk_score NUMERIC(5,2),                -- calculated risk score
    details JSONB,                          -- scanner evidence & metadata
    UNIQUE(asset_id, vulnerability_id, integration_id, port, protocol, service)
);
```

**Purpose**: Links vulnerabilities to assets with full context. Supports multiple scanners reporting the same issue.

**Field Descriptions**:
- `asset_id` / `vulnerability_id` / `integration_id`: Core relationships
- `first_seen` / `last_seen` / `fixed_at`: Temporal tracking for MTTR
- `status`: Lifecycle management (open → fixed/risk_accepted)
- `severity_level`: Can differ from vulnerability severity based on context
- `port` / `protocol` / `service`: Network context for service-specific vulnerabilities
- `risk_score`: Calculated based on severity, asset criticality, and threat intelligence
- `details`: JSONB for scanner-specific evidence:
  - Plugin output (Nessus)
  - Vulnerability test results (Qualys)
  - File paths (CrowdStrike)
  - Registry keys (Defender)

### 3.6 Field Mapping Table
```sql
CREATE TABLE integration_field_mappings (
    mapping_id SERIAL PRIMARY KEY,
    integration_id INTEGER NOT NULL REFERENCES integrations(integration_id) ON DELETE CASCADE,
    source_field VARCHAR(200) NOT NULL,     -- Scanner field name/path
    target_model VARCHAR(50) NOT NULL,      -- 'assets', 'vulnerabilities', 'findings'
    target_field VARCHAR(100) NOT NULL,     -- Model field or JSON path
    field_type VARCHAR(20) DEFAULT 'string',
    transformation VARCHAR(500),            -- Python expression or function
    default_value TEXT,
    is_required BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    UNIQUE (integration_id, source_field, target_model, target_field)
);
```

**Purpose**: Configuration-driven field extraction and transformation. Enables no-code scanner integration.

**Field Descriptions**:
- `source_field`: Exact field name from scanner (XML tag, JSON key, CSV column)
- `target_model` / `target_field`: Destination in internal schema
- `field_type`: Data type for conversion (string, integer, decimal, boolean, json, datetime)
- `transformation`: Python expression for complex mappings:
  - `value.lower()` - Convert to lowercase
  - `value.split(',')[0]` - Extract first element
  - `severity_map` - Use severity mapping table
- `default_value`: Fallback for missing data
- `sort_order`: Process fields in specific order for dependencies

### 3.7 Severity Mapping Table
```sql
CREATE TABLE severity_mapping (
    severity_mapping_id SERIAL PRIMARY KEY,
    integration_id INTEGER NOT NULL REFERENCES integrations(integration_id) ON DELETE CASCADE,
    external_severity VARCHAR(50) NOT NULL,
    internal_severity_level SMALLINT NOT NULL,
    internal_severity_label VARCHAR(20) NOT NULL,
    UNIQUE(integration_id, external_severity)
);
```

**Purpose**: Normalises different scanner severity scales to consistent internal ratings.

### Schema Validation

#### Multi-Scanner Support Validation
The schema design has been validated against major vulnerability scanner requirements and industry standards:
- ✅ **Qualys VM** - All required fields mappable
- ✅ **Tenable.io/Nessus** - Complete field coverage confirmed
- ✅ **CrowdStrike Falcon** - Agent-based findings supported
- ✅ **Microsoft Defender VM** - Host vulnerability data compatible

#### Key Validation Findings
1. **Identification Strategy**: Our multi-identifier approach (cloud ID → agent UUID → MAC → hostname → IP) matches industry best practices
2. **JSONB Flexibility**: Provides flexible handling of vendor-specific fields without schema changes
3. **Normalisation Framework**: integration_field_mappings and severity_mapping tables enable configuration-driven integration
4. **Nessus MVP**: All fields from the [Nessus file format](https://docs.tenable.com/quick-reference/nessus-file-format/Nessus-File-Format.pdf) are fully supported

The schema is **production-ready** for the MVP and future scanner integrations.

---

## Feature Specifications

This section details the core features that will be implemented in the MVP, focusing on the essential capabilities needed for a functional vulnerability management platform.

### 4.1 Asset Management & Deduplication

#### Core Functionality (MVP)
- **Asset Types**: Support for hosts (physical/virtual servers, workstations)
- **Basic Deduplication**: Match assets by hostname + IP combination
- **Manual Tagging**: Add tags via UI for categorisation
- **Business Groups**: Assign assets to organisational units
- **CRUD Operations**: Direct database operations via Supabase

#### Deduplication Algorithm (Simplified for MVP)
```python
# MVP implementation - basic matching only
def deduplicate_asset_mvp(incoming_asset):
    # Simple hostname + IP matching
    if incoming_asset.hostname and incoming_asset.ip_address:
        existing = find_by_hostname_ip(incoming_asset.hostname, 
                                     incoming_asset.ip_address)
        if existing:
            return merge_assets(existing, incoming_asset)
    
    # Create new asset if no match
    return create_asset(incoming_asset)
```

#### Future Enhancements
The full deduplication algorithm with cloud IDs, agent UUIDs, and MAC addresses will be implemented post-MVP as shown in the original specification.

### 4.2 Vulnerability Management

#### MVP Implementation
- **CVE Tracking**: Store and deduplicate by CVE identifier
- **Basic Severity**: Use CVSS scores from scanners
- **Scanner Mapping**: Nessus plugin IDs via integration_field_mappings table
- **Status Tracking**: Open, Fixed, Risk Accepted states

#### Severity Normalisation (MVP)
Simple mapping to 4 levels:
- Critical: CVSS 9.0-10.0
- High: CVSS 7.0-8.9
- Medium: CVSS 4.0-6.9
- Low: CVSS 0.0-3.9

### 4.3 Risk Scoring (Simplified for MVP)

#### MVP Formula
```
Risk Score = CVSS Score × Business Group Criticality

Where:
- CVSS Score = 0-10 from scanner
- Business Group Criticality = 1.0 (normal) or 1.5 (critical)
```

#### Future Enhancement
Post-MVP will implement the full formula with threat intelligence and multi-factor scoring as originally specified.

### 4.4 Business Groups & Asset Tagging

#### MVP Features
- **Create Business Groups**: Via Django admin or Supabase UI
- **Assign Criticality**: Normal or Critical designation
- **Asset Assignment**: Manual assignment through UI
- **Tag Creation**: Free-form tags for filtering
- **Basic Filtering**: Filter all views by business group

#### Supported Asset Types (MVP)
- **Hosts Only**: Physical servers, VMs, workstations
- Future phases will add: Code projects, websites, containers, cloud resources

### 4.5 Enhanced SLA Management System

Risk Radar implements an SLA management system. The system supports multiple SLA policies with priority-based resolution for complex organisational structures.

#### Core SLA Concepts

**SLA Policy**: A named configuration that defines remediation timeframes for each severity level (Critical, High, Medium, Low, Informational). Each policy can be assigned to one or more business groups.

**Global SLA Policy**: A default fallback policy that applies to all assets not explicitly assigned to other SLA policies. This policy cannot be deleted but can be modified.

**Priority-Based Resolution**: When an asset belongs to multiple business groups with different SLA policies, the system uses priority ordering to determine which SLA applies.

#### SLA Policy Structure

Each SLA policy contains:
- **Name**: Human-readable identifier (e.g., "Production Environment", "PCI Compliance", "Development")
- **Priority Order**: Numeric value determining precedence (higher numbers = higher priority)
- **Severity-Specific Days**: Different remediation timeframes for each severity level
- **Zero Days Handling**: Setting 0 days for any severity level disables SLA tracking for that severity

#### Example SLA Policies

```json
{
  "sla_policies": [
    {
      "name": "PCI Compliance",
      "priority_order": 200,
      "critical_days": 3,
      "high_days": 14,
      "medium_days": 30,
      "low_days": 90,
      "informational_days": 0
    },
    {
      "name": "Production Environment", 
      "priority_order": 100,
      "critical_days": 7,
      "high_days": 30,
      "medium_days": 90,
      "low_days": 180,
      "informational_days": 0
    },
    {
      "name": "Global SLA Policy",
      "priority_order": 0,
      "is_global_default": true,
      "critical_days": 14,
      "high_days": 60,
      "medium_days": 180,
      "low_days": 365,
      "informational_days": 0
    }
  ]
}
```

#### Priority-Based SLA Resolution

**The Challenge**: When an asset belongs to multiple business groups, each with different SLA policies, which SLA should apply?

**The Solution**: Risk Radar uses a priority-based resolution system:

1. **Identify Business Groups**: Find all business groups the asset belongs to
2. **Collect SLA Policies**: Get SLA policies assigned to those business groups
3. **Apply Priority Ordering**: Select the SLA policy with the highest priority number
4. **Fallback to Global**: If no business group assignments exist, use the Global SLA Policy

**Example Scenario**:
- Asset: `database-server-01.company.com`
- Business Groups: `Finance` (assigned to "PCI Compliance" SLA) + `Production` (assigned to "Production Environment" SLA)
- Priority Resolution: "PCI Compliance" (priority 200) wins over "Production Environment" (priority 100)
- Result: Critical vulnerabilities must be remediated within 3 days

#### SLA Compliance Tracking

**SLA Status Calculation**:
- **Within SLA**: Vulnerability age ≤ SLA policy days for its severity
- **Overdue/Exceeding**: Vulnerability age > SLA policy days for its severity
- **No SLA**: Severity has 0 days configured (no tracking)

**Compliance Metrics**:
- **Compliance Percentage**: (Total findings - Overdue findings) / Total findings × 100
- **Overdue Count**: Number of findings exceeding their SLA timeframe
- **Average Days Overdue**: For findings that have exceeded their SLA

#### Frontend API Integration

The frontend will consume several API endpoints to display SLA information:

##### 1. SLA Policies Management (`/api/v1/sla/policies`)

**GET Request**: Retrieve all SLA policies with assignment information
```json
{
  "sla_policies": [
    {
      "id": 1,
      "name": "PCI Compliance",
      "priority_order": 200,
      "is_global_default": false,
      "severity_days": {
        "critical": 3,
        "high": 14,
        "medium": 30,
        "low": 90,
        "informational": 0
      },
      "assigned_business_groups": ["Finance", "Payment Processing"],
      "affected_assets_count": 45,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

**Frontend Usage**: 
- Display SLA policies in a management interface
- Show priority ordering with drag-and-drop reordering
- Enable creation/editing of policies
- Display business group assignments

##### 2. Asset SLA Resolution (`/api/v1/assets/{id}/sla`)

**GET Request**: Get effective SLA policy for a specific asset
```json
{
  "asset_id": 123,
  "hostname": "database-server-01.company.com",
  "business_groups": ["Finance", "Production"],
  "effective_sla_policy": {
    "name": "PCI Compliance",
    "priority_order": 200,
    "reason": "Highest priority among assigned business groups"
  },
  "sla_resolution_details": [
    {
      "business_group": "Finance",
      "sla_policy": "PCI Compliance",
      "priority": 200,
      "selected": true
    },
    {
      "business_group": "Production", 
      "sla_policy": "Production Environment",
      "priority": 100,
      "selected": false
    }
  ]
}
```

**Frontend Usage**:
- Show asset details with effective SLA policy
- Display SLA resolution logic for transparency
- Highlight when assets have SLA conflicts
- Provide audit trail for SLA assignments

##### 3. SLA Compliance Dashboard (`/api/v1/reports/sla-compliance`)

**GET Request**: SLA compliance reporting
```json
{
  "global_summary": {
    "total_findings": 1250,
    "within_sla": 1050,
    "overdue": 200,
    "compliance_percentage": 84.0,
    "no_sla_tracking": 0
  },
  "by_sla_policy": [
    {
      "policy_name": "PCI Compliance",
      "total_findings": 156,
      "compliance_by_severity": {
        "critical": {
          "sla_days": 3,
          "total": 12,
          "overdue": 2,
          "compliance_percentage": 83.3,
          "avg_days_overdue": 1.5
        },
        "high": {
          "sla_days": 14,
          "total": 45,
          "overdue": 5,
          "compliance_percentage": 88.9,
          "avg_days_overdue": 3.2
        }
      }
    }
  ],
  "by_business_group": [
    {
      "business_group": "Finance",
      "effective_sla_policy": "PCI Compliance",
      "compliance_percentage": 82.5,
      "total_findings": 89,
      "overdue_findings": 16
    }
  ]
}
```

**Frontend Usage**:
- Display executive dashboard with SLA compliance KPIs
- Show compliance trends over time
- Enable filtering by business group, SLA policy, or severity
- Generate compliance reports for management

##### 4. Finding SLA Status (`/api/v1/findings?include_sla=true`)

**GET Request**: Findings list with SLA status information
```json
{
  "findings": [
    {
      "finding_id": 789,
      "vulnerability_title": "Critical SQL Injection in Login Form",
      "asset_hostname": "web-server-01.finance.com",
      "severity_level": 10,
      "severity_label": "Critical",
      "first_seen": "2025-01-01T10:00:00Z",
      "status": "open",
      "sla_info": {
        "policy_name": "PCI Compliance",
        "sla_days": 3,
        "days_since_discovery": 5,
        "sla_status": "overdue",
        "days_overdue": 2,
        "due_date": "2025-01-04T10:00:00Z"
      }
    }
  ]
}
```

**Frontend Usage**:
- Display findings with clear SLA status indicators
- Show overdue findings with red highlighting
- Enable sorting/filtering by SLA status
- Display countdown timers for upcoming SLA deadlines

#### Frontend User Experience

**SLA Policy Management Page**:
- Drag-and-drop interface for priority reordering
- Visual indicators showing which policy wins in conflicts
- Business group assignment interface
- Preview of how changes affect asset SLA assignments

**Asset Detail Pages**:
- Clear display of effective SLA policy
- Explanation of why a particular SLA was chosen
- Warning indicators for SLA conflicts
- Historical SLA compliance for this asset

**Dashboard Widgets**:
- SLA compliance gauge charts
- Overdue findings count with drill-down capability
- Trending compliance over time
- Top business groups with SLA issues

**Findings Management**:
- SLA status column in findings table
- Color-coded SLA indicators (green = within SLA, red = overdue)
- Bulk operations to update findings nearing SLA deadlines
- SLA deadline notifications

#### Administrative Features

**SLA Policy Administration**:
- Creation of new SLA policies with priority assignment
- Modification of existing policies (except Global SLA Policy name/deletion)
- Business group assignment management
- Impact analysis before policy changes

**Audit and Compliance**:
- SLA policy change history
- Compliance reporting over time
- Export capabilities for compliance audits
- Integration with external reporting systems

This enhanced SLA system provides capability while maintaining simplicity for smaller organisations through the Global SLA Policy fallback.

### 4.6 System Monitoring & Log Management

Risk Radar provides comprehensive system monitoring and log management capabilities for administrators to monitor system health, troubleshoot issues, and maintain operational visibility.

#### Core Log Management Features

**Centralised Log Collection**
- **Multi-Source Integration**: Django application logs, Docker container logs, system logs, and nginx access logs
- **Structured Logging**: JSON-formatted logs with consistent fields (timestamp, level, source, message, metadata)
- **Real-time Processing**: Live log streaming with WebSocket connections for immediate visibility
- **Persistent Storage**: Logs stored in Supabase with proper indexing for fast retrieval

**Advanced Filtering & Search**
- **Log Level Filtering**: Filter by DEBUG, INFO, WARNING, ERROR, CRITICAL levels
- **Source Filtering**: Filter by django, docker, system, nginx sources
- **Time Range Selection**: Custom date/time range picker with preset options (Last hour, Today, Last 7 days)
- **Text Search**: Full-text search across log messages with highlighting
- **User Filtering**: Filter logs by specific user activities (admin only)
- **Request Correlation**: Group related logs by request ID for end-to-end tracing

**Log Analytics Dashboard**
- **Error Rate Trending**: Charts showing error rates over time
- **Log Volume Metrics**: Logs per minute/hour by source and level
- **Top Errors**: Most frequent error messages with counts
- **Performance Monitoring**: Response time tracking from request logs
- **System Health**: Container status and resource usage indicators

#### Frontend UI Components (lovable.dev Implementation)

**Log Viewer Page (`/admin/logs`)**
```typescript
interface LogViewerPage {
  layout: "admin-dashboard";
  components: [
    {
      type: "FilterBar";
      position: "top";
      elements: [
        {
          type: "dropdown";
          label: "Log Level";
          options: ["ALL", "ERROR", "WARNING", "INFO", "DEBUG"];
          defaultValue: "ALL";
        },
        {
          type: "dropdown"; 
          label: "Source";
          options: ["ALL", "django", "docker", "system", "nginx"];
          defaultValue: "ALL";
        },
        {
          type: "dateRangePicker";
          label: "Time Range";
          presets: ["Last hour", "Today", "Last 7 days", "Custom"];
          defaultValue: "Last hour";
        },
        {
          type: "searchInput";
          placeholder: "Search log messages...";
          icon: "search";
        },
        {
          type: "toggle";
          label: "Real-time";
          description: "Auto-update with new logs";
        }
      ];
    },
    {
      type: "LogTable";
      position: "main";
      features: [
        "virtualScrolling",
        "autoRefresh", 
        "rowHighlighting",
        "expandableRows"
      ];
      columns: [
        {
          field: "timestamp";
          label: "Time";
          width: "180px";
          format: "datetime";
          sortable: true;
        },
        {
          field: "level";
          label: "Level";
          width: "80px";
          render: "LogLevelBadge";
          sortable: true;
        },
        {
          field: "source";
          label: "Source";
          width: "100px";
          render: "SourceIcon";
          sortable: true;
        },
        {
          field: "module";
          label: "Module";
          width: "150px";
          sortable: true;
        },
        {
          field: "message";
          label: "Message";
          width: "flexible";
          render: "ExpandableText";
          searchHighlight: true;
        },
        {
          field: "user";
          label: "User";
          width: "120px";
          render: "UserLink";
        }
      ];
    },
    {
      type: "LogDetailsSidebar";
      position: "right";
      trigger: "rowClick";
      sections: [
        {
          title: "Log Details";
          fields: ["timestamp", "level", "source", "module", "message"];
        },
        {
          title: "Context";
          fields: ["user_id", "request_id", "file", "line_number"];
        },
        {
          title: "Metadata";
          render: "JsonViewer";
          field: "metadata";
        }
      ];
    }
  ];
  permissions: ["admin"];
}
```

**Log Level Badge Component**
```typescript
interface LogLevelBadge {
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  styling: {
    DEBUG: { bg: "gray-100", text: "gray-600", border: "gray-300" };
    INFO: { bg: "blue-100", text: "blue-600", border: "blue-300" };
    WARNING: { bg: "yellow-100", text: "yellow-600", border: "yellow-300" };
    ERROR: { bg: "red-100", text: "red-600", border: "red-300" };
    CRITICAL: { bg: "red-600", text: "white", border: "red-700" };
  };
  size: "sm" | "md";
  showIcon: boolean;
}
```

**Real-time Log Stream Component**
```typescript
interface RealTimeLogStream {
  websocketUrl: "/ws/logs/";
  maxBuffer: 1000; // Maximum logs to keep in memory
  autoScroll: boolean;
  pauseOnUserScroll: boolean;
  reconnectOnFailure: true;
  showConnectionStatus: true;
  rateLimit: "10/second"; // Prevent overwhelming the UI
}
```

**Log Analytics Dashboard (`/admin/logs/analytics`)**
```typescript
interface LogAnalyticsDashboard {
  layout: "grid-2x2";
  components: [
    {
      type: "LineChart";
      title: "Error Rate Trend";
      dataSource: "/api/v1/logs/analytics/error-rate";
      xAxis: "time";
      yAxis: "error_count";
      timeRange: "24h";
      refreshInterval: "5m";
    },
    {
      type: "PieChart";
      title: "Logs by Source";
      dataSource: "/api/v1/logs/analytics/by-source";
      refreshInterval: "5m";
    },
    {
      type: "TopErrorsList";
      title: "Most Frequent Errors";
      dataSource: "/api/v1/logs/analytics/top-errors";
      showCount: 10;
      linkToLogs: true;
    },
    {
      type: "MetricsGrid";
      title: "System Health";
      metrics: [
        { label: "Total Logs (24h)", value: "12,486", trend: "+5%" },
        { label: "Error Rate", value: "0.8%", trend: "-12%" },
        { label: "Avg Response Time", value: "245ms", trend: "+8%" },
        { label: "Active Users", value: "23", trend: "stable" }
      ];
    }
  ];
  permissions: ["admin"];
}
```

#### Backend API Endpoints

**Log Retrieval APIs**
```typescript
// Get filtered logs with pagination
GET /api/v1/logs?level={level}&source={source}&search={query}&limit={limit}&offset={offset}&start_time={iso_time}&end_time={iso_time}

// Get real-time log stream
WebSocket /ws/logs/?level={level}&source={source}

// Get log analytics data
GET /api/v1/logs/analytics/error-rate?timeRange={range}
GET /api/v1/logs/analytics/by-source?timeRange={range}
GET /api/v1/logs/analytics/top-errors?limit={count}&timeRange={range}

// Get container logs (Docker)
GET /api/v1/logs/docker/{container}?lines={count}

// Get system health metrics
GET /api/v1/logs/health
```

**Response Format**
```typescript
interface LogEntry {
  id: string;
  timestamp: string; // ISO 8601
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  source: "django" | "docker" | "system" | "nginx";
  module?: string; // Django module name
  message: string;
  metadata?: {
    file?: string;
    line?: number;
    function?: string;
    request_id?: string;
    user_id?: string;
    [key: string]: any;
  };
  user?: {
    id: string;
    email: string;
  };
}

interface LogsResponse {
  logs: LogEntry[];
  total_count: number;
  has_more: boolean;
  next_offset?: number;
}
```

#### Security & Access Control

**Admin-Only Access**
- Log viewing restricted to users with admin role
- Supabase RLS policies enforce access control
- Sensitive data (passwords, tokens) automatically redacted
- Audit trail for log access activities

**Data Privacy**
- Personal data masking in logs
- Configurable log retention periods
- Secure log transmission (WSS/HTTPS only)
- Optional log encryption at rest

### 4.7 Remediation Tracking (MVP)

#### Basic Features
- **Status Updates**: Mark findings as fixed/risk accepted
- **Bulk Operations**: Update multiple findings at once
- **Progress Tracking**: Simple percentage complete
- **Export**: CSV export of current status

#### Not in MVP
- Campaign management
- Ticketing integration
- Automated workflows
- Remediation work forms

### 4.7 Reporting & Analytics

#### MVP Reports

##### Dashboard Widgets
1. **Summary Stats**
   - Total vulnerabilities by severity
   - Total assets
   - Findings past SLA
   - Overall risk score

2. **MTTR Report**
   - Average days to remediate
   - By severity level
   - By business group
   - Last 30/60/90 days

3. **SLA Compliance**
   - Percentage meeting SLA
   - Count overdue by severity
   - Trend chart (simple)

4. **Top Risks**
   - Most critical vulnerabilities
   - Most affected assets
   - Highest risk business groups

##### Data Access
- **Direct SQL**: Supabase allows direct SQL queries
- **CSV Export**: All data exportable
- **Real-time**: Live data, no batch processing

#### Future Analytics
Post-MVP phases will add:
- Remediation velocity metrics
- Capacity planning
- Custom report builder
- Executive PowerBI-style dashboards
- Automated report distribution

---

## Ingestion Architecture

### 5.1 Processing Pipeline

```mermaid
graph LR
    A[Scanner File] --> B[Format Detection]
    B --> C[Field Extraction]
    C --> D[Transformation]
    D --> E[Deduplication]
    E --> F[Risk Scoring]
    F --> G[Persistence]
    G --> H[Statistics]
```

### 5.2 Field Mapping Examples

#### Nessus to Risk Radar
```sql
-- Asset mappings
INSERT INTO integration_field_mappings (integration_id, source_field, target_model, target_field) VALUES
(1, 'HostName', 'assets', 'hostname'),
(1, 'host-ip', 'assets', 'ip_address'),
(1, 'operating-system', 'assets', 'operating_system'),
(1, 'mac-address', 'assets', 'mac_address'),
(1, 'netbios-name', 'assets', 'extra.netbios_name'),
(1, 'host-fqdn', 'assets', 'extra.fqdn');

-- Vulnerability mappings
INSERT INTO integration_field_mappings (integration_id, source_field, target_model, target_field, transformation) VALUES
(1, '@pluginID', 'vulnerabilities', 'external_id', NULL),
(1, '@pluginName', 'vulnerabilities', 'title', NULL),
(1, 'synopsis', 'vulnerabilities', 'extra.synopsis', NULL),
(1, 'description', 'vulnerabilities', 'description', NULL),
(1, 'solution', 'vulnerabilities', 'fix_info', NULL),
(1, '@severity', 'vulnerabilities', 'severity_level', 'severity_map'),
(1, 'risk_factor', 'vulnerabilities', 'extra.risk_factor', NULL),
(1, 'pluginFamily', 'vulnerabilities', 'extra.plugin_family', NULL);

-- CVE and Reference mappings
INSERT INTO integration_field_mappings (integration_id, source_field, target_model, target_field, transformation) VALUES
(1, 'cve', 'vulnerabilities', 'cve_id', 'first'),  -- Take first CVE if multiple
(1, 'cve', 'vulnerabilities', 'extra.references.cve', 'list'),
(1, 'bid', 'vulnerabilities', 'extra.references.bid', 'list'),
(1, 'xref', 'vulnerabilities', 'extra.references.xref', 'list'),
(1, 'see_also', 'vulnerabilities', 'extra.references.see_also', 'list');

-- CVSS mappings
INSERT INTO integration_field_mappings (integration_id, source_field, target_model, target_field) VALUES
(1, 'cvss_base_score', 'vulnerabilities', 'cvss_score', NULL),
(1, 'cvss_vector', 'vulnerabilities', 'extra.cvss.vector', NULL),
(1, 'cvss_temporal_score', 'vulnerabilities', 'extra.cvss.temporal_score', NULL),
(1, 'cvss_temporal_vector', 'vulnerabilities', 'extra.cvss.temporal_vector', NULL),
(1, 'cvss3_base_score', 'vulnerabilities', 'extra.cvss.cvss3_base_score', NULL),
(1, 'cvss3_vector', 'vulnerabilities', 'extra.cvss.cvss3_vector', NULL);

-- Exploit mappings
INSERT INTO integration_field_mappings (integration_id, source_field, target_model, target_field) VALUES
(1, 'exploitability_ease', 'vulnerabilities', 'extra.exploit.exploitability_ease', NULL),
(1, 'exploit_available', 'vulnerabilities', 'extra.exploit.exploit_available', 'boolean'),
(1, 'exploit_framework_canvas', 'vulnerabilities', 'extra.exploit.canvas', 'boolean'),
(1, 'exploit_framework_metasploit', 'vulnerabilities', 'extra.exploit.metasploit', 'boolean'),
(1, 'exploit_framework_core', 'vulnerabilities', 'extra.exploit.core', 'boolean'),
(1, 'exploited_by_malware', 'vulnerabilities', 'extra.exploit.exploited_by_malware', 'boolean'),
(1, 'metasploit_name', 'vulnerabilities', 'extra.exploit.metasploit_name', NULL),
(1, 'canvas_package', 'vulnerabilities', 'extra.exploit.canvas_package', NULL);

-- Date mappings
INSERT INTO integration_field_mappings (integration_id, source_field, target_model, target_field, transformation) VALUES
(1, 'vuln_publication_date', 'vulnerabilities', 'published_at', 'parse_date'),
(1, 'plugin_modification_date', 'vulnerabilities', 'modified_at', 'parse_date'),
(1, 'plugin_publication_date', 'vulnerabilities', 'extra.plugin_publication_date', 'parse_date'),
(1, 'patch_publication_date', 'vulnerabilities', 'extra.patch_publication_date', 'parse_date');

-- Finding mappings
INSERT INTO integration_field_mappings (integration_id, source_field, target_model, target_field, transformation) VALUES
(1, '@port', 'findings', 'port', NULL),
(1, '@protocol', 'findings', 'protocol', NULL),
(1, '@svc_name', 'findings', 'service', NULL),
(1, 'plugin_output', 'findings', 'details.plugin_output', NULL),
(1, 'plugin_type', 'findings', 'details.plugin_type', NULL),
(1, 'script_version', 'findings', 'details.script_version', NULL);
```

#### Qualys to Risk Radar
```sql
-- Similar structure with Qualys-specific fields
INSERT INTO integration_field_mappings (integration_id, source_field, target_model, target_field) VALUES
(2, 'QID', 'vulnerabilities', 'external_id'),
(2, 'IP', 'assets', 'ip_address'),
(2, 'DNS', 'assets', 'hostname'),
(2, 'OS', 'assets', 'operating_system');
```

### 5.3 Severity Mapping Examples

#### Nessus Severity Mapping
```sql
INSERT INTO severity_mapping (integration_id, external_severity, internal_severity_level, internal_severity_label) VALUES
(1, '4', 10, 'Critical'),
(1, '3', 8, 'High'),
(1, '2', 5, 'Medium'),
(1, '1', 3, 'Low'),
(1, '0', 0, 'Informational');
```

#### Qualys Severity Mapping
```sql
INSERT INTO severity_mapping (integration_id, external_severity, internal_severity_level, internal_severity_label) VALUES
(2, '5', 10, 'Critical'),
(2, '4', 8, 'High'),
(2, '3', 5, 'Medium'),
(2, '2', 3, 'Low'),
(2, '1', 1, 'Informational');
```

---

## Implementation Guide

### 7.1 Current Implementation Status (2025-01-02)

#### ✅ **COMPLETED** (feature/core-mvp - Ready to Merge)

**Database & Schema:**
- ✅ Complete PostgreSQL schema with 7 migrations
- ✅ Enhanced asset type system (5 categories, 86 subtypes)
- ✅ Multi-scanner support schema (migrations 0006 & 0007)
- ✅ Field mapping and severity mapping tables
- ✅ All core tables: Assets, Vulnerabilities, Findings, Categories, Subtypes

**Django Backend:**
- ✅ Complete Django project structure (28 Python files)
- ✅ Full models.py implementation (356 lines)
- ✅ Enhanced admin interface with category/subtype management
- ✅ Complete Nessus parser (513 lines) with enhanced asset type detection
- ✅ 6 management commands for setup and data operations
- ✅ Successfully tested imports (7 assets, 48 findings)

**Data Processing:**
- ✅ Database-driven field mapping engine
- ✅ System-type to subtype transformation (e.g., "general-purpose" → "Server")
- ✅ Enhanced field mappings (fqdn, netbios_name, cloud IDs, scan times)
- ✅ Asset deduplication with category support
- ✅ Vulnerability deduplication by CVE/plugin ID

#### ❌ **PENDING** (Upcoming Branches)

**Phase 1A: Django Upload API** (`feature/django-upload-api`)
- ❌ Django API endpoints (views.py currently only 4 lines)
- ❌ POST /api/upload/nessus endpoint
- ❌ File upload handling and validation
- ❌ URL routing configuration
- ❌ CORS configuration

**Phase 1B: Cloud Infrastructure** (`feature/lovable-ui-supabase`)
- ❌ Supabase project setup
- ❌ Schema deployment to Supabase
- ❌ Authentication configuration
- ❌ Storage bucket setup
- ❌ Row Level Security (RLS) policies
- ❌ lovable.dev UI connection to Supabase

**Phase 1C: Reporting APIs** (`feature/django-reporting-api`)
- ❌ GET /api/reports/mttr endpoint
- ❌ GET /api/reports/sla endpoint
- ❌ Migration from local PostgreSQL to Supabase

### 7.2 Implementation Roadmap

#### **Immediate Next Steps** (This Week)
```
Branch: feature/django-upload-api
Priority: High
Tasks:
- Create Django API views (replace 4-line views.py)
- Implement POST /api/upload/nessus endpoint
- Integrate with existing nessus_scanreport_import.py parser
- Add file validation and progress tracking
- Configure URL routing and CORS
```

#### **Phase 1B: Cloud Setup** (Next Week)
```
Branch: feature/lovable-ui-supabase
Priority: High
Tasks:
- Set up Supabase cloud project
- Deploy existing 7-migration schema to Supabase
- Configure authentication and storage
- Build basic upload UI in lovable.dev
- Test integration with Django upload endpoint
```

#### **Phase 1C: Reporting** (Week 3)
```
Branch: feature/django-reporting-api
Priority: Medium
Tasks:
- Implement MTTR calculation endpoints
- Implement SLA compliance endpoints
- Connect Django to Supabase database
- Test reporting with cloud data
```

### 7.2.1 Testing & Development Tools

The platform includes comprehensive testing and development tools organised in the `/commands` directory:

#### Testing Infrastructure (`/commands/testing/`)
- **API Authentication Testing**: `test_upload_api.py` validates JWT token handling
- **Upload Validation**: Tests both authenticated and unauthenticated file uploads
- **Error Scenario Testing**: Validates handling of invalid files and tokens
- **Environment Integration**: Automatically loads Supabase credentials from `.env`

#### Data Generation (`/commands/data_generation/`)
- **Synthetic Nessus Generation**: `generate_weekly_nessus_files.py` creates realistic test data
- **Progressive Data Simulation**: Multiple weeks with varying host/vulnerability counts
- **Scan Profile Simulation**: Production, DMZ, and development environments
- **Realistic Vulnerability Data**: Proper CVEs, plugin IDs, and CVSS scores

#### Usage Examples
```bash
# Test authentication implementation
cd commands/testing && python test_upload_api.py

# Generate test data for development
cd commands/data_generation && python generate_weekly_nessus_files.py
```

These tools are essential for:
- **Development Testing**: Validating authentication and upload functionality
- **Integration Testing**: End-to-end API testing with real data flows
- **Performance Testing**: Large datasets for load testing
- **Demo Preparation**: Consistent, realistic data for demonstrations
### 7.3 Original Phase Structure (Reference)

> **Note**: The original phase structure below is for reference. Actual implementation has progressed beyond the original timeline due to comprehensive backend development in feature/core-mvp.

#### ~~Phase 1: Infrastructure Setup (Days 1-3)~~ **COMPLETED**

---

## Non-Functional Requirements

### Performance
- **Data ingestion**: Process 100,000 findings in under 15 minutes
- **Query response**: Sub-second response for filtered finding lists
- **Concurrent users**: Support 100+ simultaneous users
- **Real-time updates**: Instant reflection of status changes

### Scalability
- **Horizontal scaling**: Stateless API servers
- **Database optimisation**: Proper indexing on foreign keys and commonly queried fields
- **Batch processing**: Chunked processing for large files
- **Archive strategy**: Move closed findings to archive tables after 90 days

### Security
- **Encryption at rest**: All sensitive fields encrypted
- **Encryption in transit**: TLS 1.2+ mandatory
- **Authentication**: JWT tokens with 1-hour expiry
- **Audit logging**: Every create/update/delete logged with user context

### Reliability
- **Availability**: 99.5% monthly uptime
- **Backup**: Daily automated backups with 30-day retention
- **Recovery**: RPO < 24 hours, RTO < 4 hours
- **Monitoring**: Application and infrastructure metrics

---

## Appendices

### A. Example Nessus XML Structure
```xml
<NessusClientData_v2>
  <Report>
    <ReportHost name="192.168.1.100">
      <HostProperties>
        <tag name="host-ip">192.168.1.100</tag>
        <tag name="host-fqdn">server.example.com</tag>
        <tag name="operating-system">Microsoft Windows Server 2019</tag>
        <tag name="mac-address">00:50:56:94:5a:34</tag>
      </HostProperties>
      <ReportItem port="445" svc_name="cifs" protocol="tcp" severity="3" pluginID="57582">
        <pluginName>SMB Signing not required</pluginName>
        <cve>CVE-2023-12345</cve>
        <cvss_base_score>7.5</cvss_base_score>
        <description>The remote SMB server does not require signing...</description>
        <solution>Enforce message signing in the host's configuration...</solution>
        <plugin_output>The remote host is missing a security update...</plugin_output>
      </ReportItem>
    </ReportHost>
  </Report>
</NessusClientData_v2>
```

### B. JSONB Usage Examples

#### Asset Extra Field
```json
{
  "cloud_instance_id": "i-1234567890abcdef0",
  "agent_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "tags": ["production", "web-server", "pci-scope"],
  "last_scan_date": "2024-01-15T10:30:00Z",
  "scanner_metadata": {
    "nessus_host_id": "12345",
    "qualys_asset_id": "67890"
  }
}
```

#### Finding Details Field
```json
{
  "plugin_output": "The remote host is missing security update KB5021089...",
  "evidence": {
    "vulnerable_software": "Apache 2.4.41",
    "installed_path": "/usr/local/apache2",
    "configuration_issue": "SSLProtocol allows TLSv1.0"
  },
  "scanner_specific": {
    "nessus_plugin_family": "Web Servers",
    "exploit_framework_metasploit": true,
    "cvss_temporal_score": 6.5
  }
}
```

### C. Performance Optimisation

#### Recommended Indexes
```sql
-- Assets
CREATE INDEX idx_assets_hostname ON assets(hostname);
CREATE INDEX idx_assets_ip ON assets(ip_address);
CREATE INDEX idx_assets_extra_cloud ON assets((extra->>'cloud_instance_id'));

-- Findings
CREATE INDEX idx_findings_status ON findings(status) WHERE status = 'open';
CREATE INDEX idx_findings_asset_vuln ON findings(asset_id, vulnerability_id);
CREATE INDEX idx_findings_integration ON findings(integration_id);
CREATE INDEX idx_findings_severity ON findings(severity_level);
CREATE INDEX idx_findings_first_seen ON findings(first_seen);

-- Vulnerabilities
CREATE INDEX idx_vulnerabilities_cve ON vulnerabilities(cve_id);
CREATE INDEX idx_vulnerabilities_external ON vulnerabilities(external_source, external_id);
```

### D. API Endpoints

```
# Assets
GET    /api/v1/assets/              # List assets with filtering
POST   /api/v1/assets/              # Create asset
GET    /api/v1/assets/{id}/         # Get asset details
PUT    /api/v1/assets/{id}/         # Update asset
DELETE /api/v1/assets/{id}/         # Delete asset
POST   /api/v1/assets/merge/        # Merge duplicate assets

# Vulnerabilities
GET    /api/v1/vulnerabilities/     # List vulnerabilities
GET    /api/v1/vulnerabilities/{id}/# Get vulnerability details

# Findings
GET    /api/v1/findings/            # List findings with filtering
PUT    /api/v1/findings/{id}/       # Update finding status
POST   /api/v1/findings/bulk/       # Bulk status update

# Campaigns
POST   /api/v1/campaigns/           # Create campaign
GET    /api/v1/campaigns/{id}/      # Get campaign progress
POST   /api/v1/campaigns/{id}/close # Close campaign

# Metrics
GET    /api/v1/metrics/mttr/        # MTTR by group/severity
GET    /api/v1/metrics/velocity/    # Remediation velocity
GET    /api/v1/metrics/capacity/    # Remediation capacity
GET    /api/v1/metrics/sla/         # SLA compliance

# Ingestion
POST   /api/v1/ingest/upload/       # Upload scanner file
GET    /api/v1/ingest/status/{id}/  # Check import status
```

---

*End of Product Requirements Document*

> **Note**: For detailed database schemas, field mappings, and comprehensive scanner integration documentation, see [Risk Radar Vulnerability Ingestion Schema](./docs/risk_radar_vulnerability_ingestion_schema.md)