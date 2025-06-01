# Risk Radar Development Roadmap & TODO

## Status: MVP Backend Partially Complete, Schema Validated for Multi-Scanner Support

This document tracks implementation tasks based on the comprehensive Product Requirements Document. See [CHANGES.md](./CHANGES.md) for release notes.

---

## ✅ Phase 0: Schema Validation Complete

### Schema Assessment Results
Based on analysis of Vulcan Cyber connector documentation for Qualys, Tenable, CrowdStrike, and Microsoft Defender, our current schema is **production-ready** for multi-scanner support:

#### Validated Schema Strengths
- [x] **Flexible Identification**: Assets table supports multiple identifiers (hostname, IP, MAC) with JSONB for cloud IDs
- [x] **Dual Vulnerability Keys**: CVE for cross-scanner deduplication, external_id for scanner-specific
- [x] **Integration Attribution**: Finding-level integration_id prevents cross-scanner conflicts
- [x] **JSONB Extensibility**: Matches Vulcan's approach for vendor-specific fields
- [x] **Configuration-Driven**: field_mapping and severity_mapping enable no-code integration

#### Minor Schema Enhancements (Optional)
- [ ] Consider adding `last_scan_date` to assets table (currently storable in extra)
- [ ] Consider adding `service VARCHAR(100)` to findings table for service context
- [ ] Ensure finding unique constraint includes port/protocol/service for granularity

### Django Model Alignment
- [ ] Verify all Django models match current schema
- [ ] Add model methods for deduplication logic
- [ ] Add calculated properties for risk scoring
- [ ] Update admin interfaces for all fields

---

## 🔧 Phase 1: Core Feature Implementation

### Asset Deduplication Engine
- [ ] Implement priority-based deduplication algorithm:
  - [ ] Cloud instance ID matching (highest priority)
  - [ ] Agent UUID matching
  - [ ] MAC + hostname matching
  - [ ] Hostname + IP matching
  - [ ] IP-only matching (lowest priority)
- [ ] Create `merge_assets()` function
- [ ] Implement proactive detach monitoring
- [ ] Add deduplication statistics tracking

### Vulnerability Normalisation
- [ ] Implement CVE-based deduplication
- [ ] Add scanner-specific ID handling
- [ ] Create cross-scanner correlation logic
- [ ] Add reference URL parsing and storage

### Field Mapping Engine
- [ ] Create transformation rule interpreter
  - [ ] Support Python expressions
  - [ ] Add built-in functions (lower, upper, split, etc.)
  - [ ] Implement severity_map transformation
- [ ] Add support for nested field paths (e.g., `extra.cloud_id`)
- [ ] Create field type converters
- [ ] Add validation for required fields
- [ ] Implement sort order processing

### Severity Mapping Implementation
- [ ] Create severity normalisation service
- [ ] Add per-scanner severity configurations
- [ ] Implement 0-10 scale conversions
- [ ] Add severity label standardisation

### Risk Scoring Engine
- [ ] Implement weighted risk formula:
  - [ ] Severity component (45%)
  - [ ] Threat component (35%)
  - [ ] Impact component (20%)
- [ ] Add asset criticality factors
- [ ] Include exploit availability scoring
- [ ] Create risk score recalculation jobs

---

## 📥 Phase 1.5: Scanner Import & Ingestion Pipeline

### Nessus XML Parser Enhancement
- [ ] Update XML parser to handle all Nessus fields:
  - [ ] Host properties extraction (OS, MAC, hostnames)
  - [ ] Plugin metadata extraction
  - [ ] CVE and reference parsing
  - [ ] CVSS score extraction
  - [ ] Exploit availability flags
  - [ ] Plugin output and evidence
- [ ] Add XML validation and error handling
- [ ] Implement streaming parser for large files

### Field Mapping Implementation
- [ ] Create `FieldMapper` class that:
  - [ ] Loads active field mappings for integration
  - [ ] Applies mappings in sort_order sequence
  - [ ] Handles source field extraction (XML paths, attributes)
  - [ ] Executes transformation rules
  - [ ] Applies default values for missing fields
  - [ ] Validates required fields
- [ ] Implement transformation functions:
  - [ ] `value.lower()`, `value.upper()`
  - [ ] `value.split(delimiter)[index]`
  - [ ] `severity_map` lookup
  - [ ] Date parsing transformations
  - [ ] Numeric conversions
- [ ] Add support for nested target fields (`extra.cloud_id`)

### Severity Normalisation Pipeline
- [ ] Create `SeverityNormaliser` that:
  - [ ] Loads severity mappings for integration
  - [ ] Translates scanner severity to internal scale
  - [ ] Sets both severity_level (0-10) and severity_label
  - [ ] Handles unmapped severities with defaults
- [ ] Add severity validation and logging

### Asset Import & Deduplication
- [ ] Implement asset extraction from Nessus:
  - [ ] Extract all identifiers (hostname, IP, MAC)
  - [ ] Build extra JSONB with scanner metadata
  - [ ] Apply field mappings to populate fields
- [ ] Execute deduplication algorithm:
  - [ ] Search for existing assets by priority
  - [ ] Merge with existing or create new
  - [ ] Update last_seen timestamps
  - [ ] Aggregate metadata in extra field
- [ ] Add asset import statistics

### Vulnerability Import & Deduplication
- [ ] Implement vulnerability extraction:
  - [ ] Extract plugin ID as external_id
  - [ ] Set external_source = 'Nessus'
  - [ ] Extract CVE if available
  - [ ] Apply field mappings for all fields
  - [ ] Build extra JSONB with references
- [ ] Execute vulnerability deduplication:
  - [ ] Check for existing CVE match
  - [ ] Check for existing (external_source, external_id)
  - [ ] Merge or create vulnerability record
- [ ] Apply severity normalisation

### Finding Import & Lifecycle
- [ ] Create findings linking assets and vulnerabilities:
  - [ ] Set integration_id from scanner
  - [ ] Extract port, protocol, service
  - [ ] Store plugin_output in details JSONB
  - [ ] Set initial status = 'open'
  - [ ] Calculate risk_score
- [ ] Handle finding updates:
  - [ ] Update last_seen for existing findings
  - [ ] Detect fixed findings (not in latest scan)
  - [ ] Update fixed_at timestamp
  - [ ] Preserve finding history

### Import Transaction Management
- [ ] Wrap import in database transaction
- [ ] Add rollback on errors
- [ ] Create import statistics:
  - [ ] Assets: created, updated, errors
  - [ ] Vulnerabilities: created, updated, errors  
  - [ ] Findings: created, updated, fixed, errors
- [ ] Store statistics in scanner_upload record
- [ ] Add progress tracking for large files

### Error Handling & Logging
- [ ] Add comprehensive error handling:
  - [ ] Invalid XML structure
  - [ ] Missing required fields
  - [ ] Failed transformations
  - [ ] Database constraint violations
- [ ] Create detailed import logs
- [ ] Add field mapping debugging mode
- [ ] Implement dry-run mode for testing

---

## 🚀 Phase 2: API Development

### REST API Implementation
- [ ] **Asset Endpoints**
  - [ ] GET /api/v1/assets/ (list with filtering)
  - [ ] POST /api/v1/assets/ (create)
  - [ ] GET /api/v1/assets/{id}/ (detail)
  - [ ] PUT /api/v1/assets/{id}/ (update)
  - [ ] DELETE /api/v1/assets/{id}/ (delete)
  - [ ] POST /api/v1/assets/merge/ (merge duplicates)

- [ ] **Vulnerability Endpoints**
  - [ ] GET /api/v1/vulnerabilities/ (list)
  - [ ] GET /api/v1/vulnerabilities/{id}/ (detail)

- [ ] **Finding Endpoints**
  - [ ] GET /api/v1/findings/ (list with filters)
  - [ ] PUT /api/v1/findings/{id}/ (status update)
  - [ ] POST /api/v1/findings/bulk/ (bulk operations)

- [ ] **Campaign Endpoints**
  - [ ] POST /api/v1/campaigns/ (create)
  - [ ] GET /api/v1/campaigns/{id}/ (progress)
  - [ ] POST /api/v1/campaigns/{id}/close (close)

- [ ] **Metrics Endpoints**
  - [ ] GET /api/v1/metrics/mttr/
  - [ ] GET /api/v1/metrics/velocity/
  - [ ] GET /api/v1/metrics/capacity/
  - [ ] GET /api/v1/metrics/sla/

- [ ] **Ingestion Endpoints**
  - [ ] POST /api/v1/ingest/upload/
  - [ ] GET /api/v1/ingest/status/{id}/

### API Features
- [ ] Implement pagination
- [ ] Add filtering and search
- [ ] Create serializers for all models
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Implement rate limiting
- [ ] Add JWT authentication

---

## 📊 Phase 3: Analytics & Reporting

### Database Views for Remediation Performance

#### MTTR Views
- [ ] Create `mttr_overall` view:
  - [ ] Calculate organisation-wide MTTR
  - [ ] Include current period and previous period
  - [ ] Add trend calculation
- [ ] Create `mttr_by_business_group` view:
  - [ ] Group MTTR by business group
  - [ ] Include finding counts
  - [ ] Add period comparisons
- [ ] Create `mttr_by_risk_level` view:
  - [ ] Group MTTR by severity levels
  - [ ] Support filtering by date range
  - [ ] Include trend percentages
- [ ] Create `mttr_by_asset_type` view:
  - [ ] Group MTTR by asset classification
  - [ ] Include min/max/avg calculations
- [ ] Create `mttr_over_time` view:
  - [ ] Daily MTTR calculations
  - [ ] Support for rolling averages
  - [ ] Enable time series analysis

#### Remediation Performance Views
- [ ] Create `daily_remediation_stats` view:
  - [ ] Count of findings fixed per day
  - [ ] Average daily remediation rate
  - [ ] Period-over-period comparisons
- [ ] Create `remediation_by_business_group` view:
  - [ ] Daily remediation counts by group
  - [ ] Ranking calculations
  - [ ] Trend analysis
- [ ] Create `remediation_capacity` view:
  - [ ] Daily introduced findings count
  - [ ] Daily remediated findings count
  - [ ] Capacity percentage calculation
  - [ ] By risk level breakdown
  - [ ] By asset type breakdown

#### SLA Compliance Views
- [ ] Create `sla_compliance_summary` view:
  - [ ] Assets meeting SLA (count and %)
  - [ ] Findings within SLA window
  - [ ] By business group breakdown
- [ ] Create `sla_breach_details` view:
  - [ ] Findings exceeding SLA
  - [ ] Days overdue buckets (1-7, 8-30, 31-90, >90)
  - [ ] Percentage and count views
- [ ] Create `sla_trend_analysis` view:
  - [ ] Historical SLA compliance rates
  - [ ] Trend calculations
  - [ ] By risk level analysis

### Time Period Functions
- [ ] Create `get_period_range()` function:
  - [ ] Support 7d, 30d, 90d, 1y, all time
  - [ ] Return start and end dates
  - [ ] Calculate previous period ranges
- [ ] Create `calculate_trend()` function:
  - [ ] Compare current vs previous period
  - [ ] Return percentage change
  - [ ] Indicate direction (improving/worsening)

### Filtering Framework
- [ ] Implement multi-dimensional filtering:
  - [ ] Business group filter (single/multiple)
  - [ ] Risk level filter (single/multiple)
  - [ ] Asset type filter (single/multiple)
  - [ ] Date range filter (preset and custom)
  - [ ] Status filter (where applicable)
- [ ] Create filter combination logic:
  - [ ] AND/OR conditions
  - [ ] Filter persistence
  - [ ] Performance optimisation

### Report Generation

#### Executive Dashboard Implementation
- [ ] Create KPI summary component:
  - [ ] MTTR with trend arrow
  - [ ] Daily remediation with trend
  - [ ] Capacity percentage with trend
  - [ ] SLA compliance with trend
- [ ] Implement chart components:
  - [ ] MTTR by business group (bar chart)
  - [ ] Remediation capacity by risk (stacked bar)
  - [ ] MTTR trend line chart
  - [ ] SLA compliance gauge charts

#### Operational Reports
- [ ] **MTTR Deep Dive Report**:
  - [ ] Tabular breakdown by all dimensions
  - [ ] Sorting and filtering
  - [ ] Export to CSV/PDF
  - [ ] Drill-down capabilities
- [ ] **Remediation Velocity Report**:
  - [ ] Daily fix rate trends
  - [ ] Capacity analysis graphs
  - [ ] Business group rankings
  - [ ] Peak/low performance identification
- [ ] **SLA Breach Report**:
  - [ ] Actionable finding list
  - [ ] Overdue day calculations
  - [ ] Priority sorting
  - [ ] Bulk action capabilities
- [ ] **Business Group Scorecard**:
  - [ ] Comparative metrics table
  - [ ] Performance rankings
  - [ ] Trend indicators
  - [ ] Executive summary

### Performance Optimisation for Reporting
- [ ] Create materialised views for:
  - [ ] Daily MTTR calculations
  - [ ] Remediation counts
  - [ ] SLA compliance rates
- [ ] Add report-specific indexes:
  - [ ] `idx_findings_fixed_at`
  - [ ] `idx_findings_first_seen_status`
  - [ ] `idx_findings_business_group_severity`
- [ ] Implement report caching:
  - [ ] Cache calculated metrics
  - [ ] Refresh on data changes
  - [ ] TTL for different report types

### Report API Endpoints
- [ ] **MTTR Endpoints**:
  - [ ] GET /api/v1/reports/mttr/overall
  - [ ] GET /api/v1/reports/mttr/by-business-group
  - [ ] GET /api/v1/reports/mttr/by-risk-level
  - [ ] GET /api/v1/reports/mttr/by-asset-type
  - [ ] GET /api/v1/reports/mttr/trends
- [ ] **Remediation Performance Endpoints**:
  - [ ] GET /api/v1/reports/remediation/daily-stats
  - [ ] GET /api/v1/reports/remediation/capacity
  - [ ] GET /api/v1/reports/remediation/velocity
  - [ ] GET /api/v1/reports/remediation/rankings
- [ ] **SLA Compliance Endpoints**:
  - [ ] GET /api/v1/reports/sla/compliance
  - [ ] GET /api/v1/reports/sla/breaches
  - [ ] GET /api/v1/reports/sla/trends
  - [ ] GET /api/v1/reports/sla/by-group

### Report Export Functionality
- [ ] CSV export for all reports
- [ ] PDF generation with charts
- [ ] Excel export with multiple sheets
- [ ] Scheduled report delivery
- [ ] Report templates

### Historical Data Management
- [ ] Create snapshot tables:
  - [ ] `mttr_daily_snapshot`
  - [ ] `remediation_daily_snapshot`
  - [ ] `sla_compliance_snapshot`
- [ ] Implement snapshot jobs:
  - [ ] Daily metric calculation
  - [ ] Data retention policies
  - [ ] Compression for old data
- [ ] Enable historical comparisons:
  - [ ] Year-over-year analysis
  - [ ] Seasonal trend detection
  - [ ] Long-term performance tracking

---

## ⚡ Phase 4: Performance & Scale

### Database Optimisation
- [ ] Add indexes per PRD Appendix C:
  - [ ] Asset indexes (hostname, ip, cloud_id)
  - [ ] Finding indexes (status, asset/vuln, severity)
  - [ ] Vulnerability indexes (cve, external_id)
- [ ] Implement query optimisation
- [ ] Add connection pooling
- [ ] Create archive strategy for old findings

### Processing Optimisation
- [ ] Implement batch processing for large files
- [ ] Add async task processing (Celery)
- [ ] Create progress tracking for imports
- [ ] Implement chunked database operations

### Caching
- [ ] Add Redis for query caching
- [ ] Implement finding count caches
- [ ] Add severity distribution caches
- [ ] Create metric calculation caches

---

## 🔐 Phase 5: Security & Compliance

### Security Hardening
- [ ] Implement field-level encryption
- [ ] Add comprehensive audit logging
- [ ] Create security headers middleware
- [ ] Implement input validation
- [ ] Add SQL injection protection

### Authentication & Authorisation
- [ ] Implement JWT token management
- [ ] Add role-based permissions
- [ ] Create business group scoping
- [ ] Implement field-level permissions
- [ ] Add SSO preparation

---

## 📦 Phase 6: Additional Scanner Support

### Scanner Integrations
- [ ] **Qualys Integration**
  - [ ] Add field mappings
  - [ ] Create severity mappings
  - [ ] Implement QID handling
  - [ ] Add API connector

- [ ] **CrowdStrike Integration**
  - [ ] Add field mappings
  - [ ] Create severity mappings
  - [ ] Implement finding correlation
  - [ ] Add API connector

- [ ] **Microsoft Defender Integration**
  - [ ] Add field mappings
  - [ ] Create severity mappings
  - [ ] Implement KB handling
  - [ ] Add API connector

---

## ✅ Completed Items
- Basic Django project structure
- Initial models (partial implementation)
- Scanner integration framework
- Basic field mapping structure
- Nessus file parsing (basic)
- Django admin setup

---

## 📋 Development Guidelines

### Testing Requirements
- [ ] Unit tests for deduplication logic
- [ ] Integration tests for field mappings
- [ ] API endpoint tests
- [ ] Performance benchmarks
- [ ] Security scan validation

### Documentation Needs
- [ ] API documentation
- [ ] Field mapping examples
- [ ] Deployment guide
- [ ] User manual
- [ ] Developer setup guide

### Performance Targets
- Process 100,000 findings in < 15 minutes
- Sub-second API response times
- Support 100+ concurrent users
- 99.5% uptime SLA

---

## 🚦 Priority Order

1. **Complete**: Schema validation - confirmed production-ready
2. **Immediate**: Scanner import pipeline (Phase 1.5) - Nessus parser with field mappings
3. **High**: Asset deduplication and finding lifecycle
4. **High**: API implementation for core resources
5. **Medium**: Additional scanner support
6. **Medium**: Performance optimisation
7. **Low**: Advanced reporting features

---

## Notes
- All schema changes must be backwards compatible
- Use Django migrations for all database changes
- Maintain API versioning from the start
- Document all transformation rules
- Keep JSONB fields for extensibility 