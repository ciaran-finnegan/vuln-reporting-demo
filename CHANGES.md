# Changes

## 0.2.0 (Unreleased)

Planned features and improvements for the next release:

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