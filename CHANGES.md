# Changes

## 0.3.0 (2025-01-06) - Enhanced Metrics & KPI Framework

### Comprehensive Metrics System with Dimensional Analysis
- **Enhanced metrics database schema**:
  - Created separate Category, Audience, Framework, and ControlRef models for proper taxonomy
  - Enhanced Metric model with individual SLO fields instead of JSON configuration
  - Added dimension_config JSONB field for flexible filtering and grouping
  - Implemented many-to-many relationships for metrics to categories, audiences, and controls
- **Dimensional analysis framework**:
  - 12 available dimensions: business_group, asset_category, vulnerability_severity, finding_status, etc.
  - Flexible configuration: default, allowed, required, groupable, filterable dimension sets
  - API integration with dimension-aware endpoints and dynamic filtering
  - Frontend-ready with current values API for dropdown population
- **Comprehensive metric types support**:
  - KPI metrics: Numeric and ordinal snapshot measurements with SLO thresholds
  - Trend metrics: Percentage change calculations with configurable comparison periods
  - Chart metrics: Distribution and visualization data without SLO requirements
  - List metrics: Enumerated data sets for reporting and analysis
- **YAML configuration system**:
  - Complete YAML schema for easy metric definition and maintenance
  - Support for complex SLO configurations with target/limit thresholds
  - Compliance framework mapping with CIS Controls, ISO 27001, and custom frameworks
  - Enhanced metadata fields: calc_logic, viewer_guidance, impl_guidance, more_info_url
- **Production-ready framework**:
  - Future-proof schema supporting advanced analytics without migrations
  - API endpoints for metric management, calculation, and dimensional querying
  - Complete documentation with 5 comprehensive metric examples
  - Executive dashboard and operational monitoring capabilities

### Documentation Enhancements (2025-01-06)
- **Updated PRODUCT_REQUIREMENTS_DOCUMENT.md**:
  - Complete rewrite of metrics schema section with enhanced structure
  - Added dimensional configuration system documentation
  - Comprehensive YAML configuration examples covering all metric types
  - API integration documentation with dimension filtering examples
- **Enhanced implementation guidance**:
  - Detailed metric calculation examples for all value types
  - SQL examples for numeric, trend, and ordinal metric calculations
  - API endpoint specifications for dimensional analysis
  - Frontend integration patterns for metric visualization

## 0.2.1 (2025-01-03)

### Upload Permissions Automation (2025-01-03)
- **Permanent fix for file upload permissions**:
  - Added automated temp_uploads directory creation to GitHub Actions deployment workflow
  - Configured proper directory permissions (777) during deployment process
  - Eliminated manual SSH intervention required for upload functionality
  - Both production and development environments automatically configured
- **Infrastructure automation improvements**:
  - Deployment workflow creates temp_uploads directory before Docker container startup
  - Idempotent operations ensure safe repeated deployments
  - Clear deployment logging shows upload directory configuration status
  - Zero-touch deployment process for complete infrastructure provisioning
- **Documentation updates**:
  - Updated PRODUCT_REQUIREMENTS_DOCUMENT.md with infrastructure automation details
  - Added Phase 1F completion status to TODO.md
  - Enhanced deployment troubleshooting documentation
- **Production impact**:
  - ✅ Resolves "The server doesn't have permission to write to the upload directory" error
  - ✅ Ensures consistent upload functionality across all deployments
  - ✅ Reduces deployment complexity and human error
  - ✅ Provides automated recovery for infrastructure issues

## 0.2.0 (Unreleased)

### Duplicate File Detection Implementation (2025-01-03)
- **Complete duplicate detection system**:
  - Added SHA-256 file hash calculation for uploaded files
  - Created migration 0010_add_file_hash_duplicate_detection with file_hash field and unique constraint
  - Implemented hash-based duplicate detection in both API and CLI interfaces
  - Added comprehensive error handling with 409 Conflict responses for duplicates
- **Force re-import functionality**:
  - API: `force_reimport=true` query parameter bypasses duplicate detection
  - CLI: `--force-reimport` flag allows re-processing of duplicate files
  - Intelligent record updating: reuses existing upload records instead of creating duplicates
  - Maintains data integrity while allowing legitimate re-imports
- **Upload history management**:
  - New `GET /api/v1/upload/history` endpoint with pagination and filtering
  - Complete upload metadata tracking: file size, hash, status, timestamps
  - Processing statistics and error message storage
  - Status progression tracking (pending → processing → completed/failed)
- **Enhanced API endpoints**:
  - Updated upload responses include file hash and upload ID
  - Detailed duplicate information with original upload metadata
  - Clear resolution guidance in error messages
  - Updated API status endpoint to include all available endpoints
- **Utility functions and testing**:
  - Created `core/utils.py` with hash calculation and duplicate detection utilities
  - Comprehensive test suite: `commands/testing/test_duplicate_detection.py`
  - Tests cover: API uploads, duplicate detection, force re-import, upload history
  - Enhanced CLI commands with duplicate detection and comprehensive progress reporting
- **Documentation and integration**:
  - Updated README.md with duplicate detection features and API documentation
  - Enhanced management command help text and error handling
  - Consistent duplicate handling between API and CLI interfaces
  - Production-ready with complete error recovery and rollback support

### Database Schema Cleanup (2025-01-03)
- **Table naming consistency improvements**:
  - Renamed `vulnerability` table to `vulnerabilities` for proper plural naming
  - Renamed `scanner_integration` table to `integrations` for more concise naming 
  - Renamed `field_mapping` table to `integration_field_mappings` for better descriptive naming
  - Created migration 0009_table_naming_consistency to handle all table renames
  - Maintained Django model class names (`ScannerIntegration`, `FieldMapping`) for backwards compatibility
  - Updated all management commands, admin interface, and imports to use correct references
  - Verified migration compatibility and tested system functionality

Planned features and improvements for the next release:

### Django Upload API with Authentication (2025-01-02)
- **Complete API endpoint implementation**:
  - Created Django views.py with file upload handling and validation
  - Implemented POST /api/v1/upload/nessus endpoint with comprehensive error handling
  - Added API status and upload info endpoints for system verification
  - Configured URL routing with core/urls.py and main URL inclusion
- **Supabase JWT Authentication integration**:
  - Created authentication.py with SupabaseJWTAuthentication backend
  - Implemented JWT token validation with proper Supabase format support
  - Added OptionalSupabaseJWTAuthentication for MVP permissive access
  - User auto-creation with UserProfile model linking to business groups
- **Enhanced security and configuration**:
  - Added CORS support for frontend integration
  - Updated settings.py with Supabase configuration and authentication classes
  - Created UserProfile model with migration 0008 for user context tracking
  - Added PyJWT dependency for token handling
- **Comprehensive testing infrastructure**:
  - Created /commands directory structure for organised utility scripts
  - Implemented test_upload_api.py with full authentication test coverage
  - Added environment variable loading from riskradar/.env
  - Tests cover: unauthenticated uploads, authenticated uploads, invalid tokens, error scenarios
- **File upload features**:
  - Integration with existing nessus_scanreport_import.py parser
  - File validation (type, size limits up to 100MB)
  - Detailed response with statistics and user context
  - Authenticated uploads show user email and authentication status
  - Temporary file handling with proper cleanup
- **Documentation and organisation**:
  - Created comprehensive README files for commands directory structure
  - Updated BACKEND_DEVELOPMENT_GUIDELINES.md with script organisation rules
  - Enhanced PRODUCT_REQUIREMENTS_DOCUMENT.md with testing infrastructure details
  - Updated README.md with commands usage examples
  - Clear guidelines for LLM/AI agents on script placement
### Enhanced Asset Type Schema Implementation (2025-01-02)
- **Completed migration 0007_enhanced_asset_types**:
  - Created AssetCategory and AssetSubtype models with 5 categories and 86 subtypes
  - Added default_asset_category field to ScannerIntegration model
  - Migrated existing AssetType data to new category/subtype structure
  - Maintained backward compatibility with legacy asset_type field
- **Asset categorisation from ASSET_TYPES.md**:
  - Host: 18 subtypes (Server, Workstation, Network Device, IoT Device, etc.)
  - Code Project: 11 subtypes (Repository, GitHub Repository, Application Project, etc.)
  - Website: 6 subtypes (Web Application, API Endpoint, Subdomain, etc.)
  - Image: 8 subtypes (Container Image, Docker Image, Virtual Machine Image, etc.)
  - Cloud Resource: 43 subtypes across AWS, Azure, and GCP providers
- **Enhanced Nessus asset mapping**:
  - System-type detection: Maps Nessus "general-purpose" → "Server" subtype
  - Enhanced field mappings: fqdn, netbios_name, cloud instance IDs, scan times
  - Transformation rules: nessus_system_type_map, default_scanner_category
  - Smart categorisation with fallback to scanner integration defaults
- **New management commands**:
  - `setup_asset_categories` - Creates standard categories and subtypes
  - `setup_enhanced_nessus_mappings` - Configures enhanced field mappings with asset type detection
- **Admin interface enhancements**:
  - Added AssetCategory and AssetSubtype admin with inline editing
  - Enhanced filtering and search capabilities
  - Subtype count display and cloud provider filtering
- **Database improvements**:
  - Fixed risk_score calculation overflow with proper type conversion
  - Enhanced error handling for malformed data
  - Optimised asset lookup with category/subtype relationships
- **Successful testing**:
  - Imported 7 assets with proper Host category and Server subtype mapping
  - All assets correctly categorised based on system-type detection
  - Enhanced metadata preserved: fqdn, netbios_name, original system_type
  - Field mappings working correctly with ReportItem@attribute format

### Schema Migration for Multi-Scanner Support (2025-01-02)
- **Completed migration 0006_multi_scanner_support**:
  - Added `type` field to ScannerIntegration model
  - Added new fields to Vulnerability: `cve_id`, `external_source`, `severity_level`, `severity_label`
  - Added new fields to Asset: `operating_system`, `mac_address`
  - Added `integration_id` FK and `severity_level` to Finding
  - Renamed fields for consistency: `metadata` → `extra`, `name` → `title`, `solution` → `fix_info`
  - Updated unique constraints for proper multi-scanner deduplication
- **Updated all management commands** to use new field names:
  - `setup_nessus_field_mappings.py` - Updated field mappings for new schema
  - `populate_initial_data.py` - Created to seed AssetTypes, BusinessGroups, and SLA policies
  - `generate_weekly_nessus_files.py` - Updated for new field names
  - `clear_demo_data.py` - Already compatible
- **Fixed Nessus import issues**:
  - Removed problematic `_process_*` methods that added invalid fields
  - Fixed XML attribute parsing for `ReportItem@pluginID` format
  - Successfully imported sample data: 7 assets, 14 vulnerabilities, 20 findings
- **Production-ready multi-scanner schema** now in place

### Documentation Updates (2024-12-18)
- Validated schema design against industry standards and scanner requirements
- Confirmed production-readiness for multi-scanner support (Qualys, Tenable, CrowdStrike, Microsoft Defender)
- Consolidated duplicate PRD content and removed `docs/risk_radar_prd.md`
- Updated TODO.md to reflect schema validation completion
- Added Schema Validation section to main PRD
- **Refocused on hybrid MVP architecture**:
  - Clarified Supabase's role for direct CRUD operations
  - Updated Django's scope to complex logic only (parsing, risk calculation, reporting)
  - Moved comprehensive API development to post-MVP phase
  - Restored lovable.dev as primary UI with dual data source capability
- **Major PRD enhancements**:
  - Added comprehensive Features Overview section detailing all platform capabilities
  - Created detailed MVP Feature Matrix showing what's in/out of MVP scope
  - Simplified Feature Specifications for MVP implementation
  - Updated Implementation Guide with clear 14-day MVP timeline
  - Added development best practices and security considerations
- **TODO.md overhaul**:
  - Aligned with MVP Feature Matrix from PRD
  - Created clear day-by-day implementation schedule
  - Added success metrics and technical decisions
  - Simplified phases to match 2-week MVP timeline

### Features
- Enhanced reporting and export options (PDF, CSV)
- Remediation performance metrics dashboard
- Customisable risk scoring
- Additional scanner integrations (OpenVAS, etc.)
- Improved API documentation and OpenAPI spec

### Improvements
- UI/UX enhancements in Django admin
- More granular role-based access control
- Performance and security hardening

### Bug Fixes
- To be announced

---

## 0.1.0 (2024-06-07)

Initial MVP release of Risk Radar.

### Features
- Supabase + Django hybrid architecture
- Nessus file import and parsing (configurable field mapping)
- Asset and vulnerability management (all asset types)
- SLA tracking and compliance reporting
- Remediation campaign management
- Business groups and asset tagging
- REST API for complex logic and reporting
- Supabase for authentication, storage, and direct CRUD
- Django Admin for backend management

### Improvements
- Configurable field and severity mappings via Django admin
- Batch import and management commands
- Initial reporting (SLA compliance, campaign progress)

### Bug Fixes
- N/A (initial release) 