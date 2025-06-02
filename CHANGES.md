# Changes

## 0.2.0 (Unreleased)

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
- Validated schema design against Vulcan Cyber connector requirements
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