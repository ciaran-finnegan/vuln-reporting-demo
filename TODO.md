# Risk Radar Development Roadmap & TODO

## Status: Ready for API Development & Cloud Deployment

This document tracks implementation tasks aligned with the MVP Feature Matrix in the Product Requirements Document. See [CHANGES.md](./CHANGES.md) for release notes.

---

## 🌿 Feature Branch Status

### ✅ Completed Branches
| Branch | Status | Completed | Description |
|--------|---------|-----------|-------------|
| `feature/core-mvp` | 🔄 **Ready to Merge** | 2025-01-02 | Complete Django backend, enhanced asset schema, Nessus parser, 7 migrations, admin interface |

### 🚀 Planned Branches
| Branch | Priority | Phase | Description |
|--------|----------|-------|-------------|
| `feature/django-upload-api` | **High** | 1A | Django upload endpoint (`POST /api/upload/nessus`) |
| `feature/lovable-ui-supabase` | **High** | 1B | lovable.dev UI + Supabase authentication & storage |
| `feature/django-reporting-api` | **Medium** | 1C | Django reporting endpoints (`GET /api/reports/mttr`, `/sla`) |
| `feature/ui-dashboard` | **Medium** | 2 | Core UI pages (Dashboard, Assets, Vulnerabilities, Findings) |
| `feature/ui-upload-page` | **Medium** | 2 | File upload interface with drag-and-drop |
| `feature/testing-deployment` | **Low** | 4 | Testing, documentation, production deployment |

### 📊 Branch Completion Summary
- **Completed**: 0 branches merged to main
- **Ready to Merge**: 1 branch (`feature/core-mvp`)
- **In Progress**: 0 branches  
- **Planned**: 6 branches

---

## ✅ COMPLETED: Enhanced Asset Type Schema Implementation (2025-01-02)

### Enhanced Asset Categorisation Successfully Implemented
The enhanced asset type schema with categories and subtypes has been completed and tested. The system now supports sophisticated asset classification with 86 standard subtypes.

#### Changes Completed:
1. **AssetCategory and AssetSubtype Models**: Created with 5 categories and 86 subtypes ✅
2. **Migration 0007**: Successfully created and applied enhanced asset type schema ✅
3. **Enhanced Nessus Mapping**: System-type to subtype transformation working ✅
4. **Management Commands**: setup_asset_categories and setup_enhanced_nessus_mappings created ✅
5. **Admin Interface**: Enhanced with category/subtype management ✅
6. **Database Migration**: Existing AssetType data migrated to new structure ✅
7. **Testing**: Successfully imported 7 assets with proper categorisation ✅

#### Asset Categories and Subtypes Implemented:
- **Host** (18 subtypes): Server, Workstation, Network Device, IoT Device, Firewall, Router, etc.
- **Code Project** (11 subtypes): Repository, GitHub Repository, Application Project, Library, etc.
- **Website** (6 subtypes): Web Application, API Endpoint, Subdomain, Base URL, etc.
- **Image** (8 subtypes): Container Image, Docker Image, Virtual Machine Image, etc.
- **Cloud Resource** (43 subtypes): AWS, Azure, GCP resources with provider-specific subtypes

#### Enhanced Nessus Integration:
- ✅ System-type detection: "general-purpose" → "Server" subtype mapping
- ✅ Enhanced field mappings: fqdn, netbios_name, cloud instance IDs
- ✅ Transformation rules: nessus_system_type_map, default_scanner_category
- ✅ Smart fallback to scanner integration default category
- ✅ Successfully tested with sample Nessus file import

---

## ✅ COMPLETED: Schema Migration for Multi-Scanner Support (2025-01-02)

### Multi-Scanner Schema Successfully Implemented
The critical schema changes have been completed to support multi-scanner environments. The system is now ready for MVP development.

#### Changes Completed:
1. **Scanner Integration**: Added `type` field to distinguish scanner types ✅
2. **Vulnerabilities**: Added `cve_id`, `external_source`, `severity_level`, `severity_label` ✅
3. **Assets**: Added `operating_system`, `mac_address` fields ✅
4. **Findings**: Added `integration_id` FK and `severity_level` ✅
5. **Field Renames**: `metadata` → `extra`, `name` → `title`, `solution` → `fix_info` ✅
6. **Unique Constraints**: Updated for proper multi-scanner deduplication ✅

---

## ✅ COMPLETED: Phase 1 - MVP Infrastructure (MOSTLY COMPLETE)

### Django Project - ✅ COMPLETE
- ✅ **Complete Django project structure** (28 Python files implemented)
- ✅ **Full schema implementation** (models.py - 356 lines with all tables)
- ✅ **Complete Django admin interface** (enhanced category/subtype management)
- ✅ **Database configuration** (settings.py configured for PostgreSQL)
- ✅ **Static file serving configured**

### Database Schema - ✅ COMPLETE
- ✅ **7 working migrations** (0001_initial through 0007_enhanced_asset_types)
- ✅ **All tables implemented**: Assets, Vulnerabilities, Findings, Categories, Subtypes, etc.
- ✅ **Enhanced relationships** with proper foreign keys and constraints
- ✅ **JSONB extensibility** for scanner-specific data

### Initial Data & Commands - ✅ COMPLETE
- ✅ **6 management commands implemented**:
  - `setup_asset_categories.py` (86 subtypes across 5 categories)
  - `setup_nessus_field_mappings.py` (basic Nessus mappings)
  - `setup_enhanced_nessus_mappings.py` (enhanced with asset type detection)
  - `populate_initial_data.py` (SLA policies, business groups)
  - `clear_demo_data.py` (data management)
  - `import_nessus.py` (file import)
- ✅ **Successfully tested** with real Nessus file import

### Missing from Phase 1:
- [ ] **Supabase cloud project setup** (only local PostgreSQL configured)
- [ ] **Supabase authentication configuration**
- [ ] **Supabase storage buckets**
- [ ] **Row Level Security (RLS) policies**

---

## ✅ COMPLETED: Phase 1.5 - Scanner Integration (FULLY COMPLETE)

### Nessus Parser - ✅ COMPLETE
- ✅ **Complete XML parser** (nessus_scanreport_import.py - 513 lines)
- ✅ **Field mapping engine** using database configuration
- ✅ **Enhanced asset deduplication** (hostname + IP + categories)
- ✅ **Vulnerability deduplication** by CVE/plugin ID and external source
- ✅ **Finding creation** with proper asset/vulnerability relationships
- ✅ **Comprehensive error handling** and data validation
- ✅ **Progress tracking** and statistics reporting
- ✅ **System-type to subtype mapping** (e.g., "general-purpose" → "Server")

### Field Mapping System - ✅ COMPLETE
- ✅ **Database-driven field mappings** (no code changes needed for new scanners)
- ✅ **Transformation rules** (severity mapping, data conversion)
- ✅ **Enhanced mappings** for cloud IDs, scan times, metadata
- ✅ **ReportItem@attribute format** parsing
- ✅ **Successfully tested** with 7 assets, 48 findings import

---

## 🚨 CURRENT STATUS: Phase 2 Ready

**We are NOT at Phase 1 - we have COMPLETED Phase 1 and 1.5!**

**Current State**: Complete Django backend with database, parser, admin interface, and working data import. Missing only API endpoints and cloud infrastructure.

---

## 🔥 IMMEDIATE TASKS: Prioritized Implementation Plan

### Phase 1A: Django Upload Endpoint (Highest Priority - Next Branch)
- [ ] **Create Django API views** (views.py is currently empty - only 4 lines)
- [ ] **POST /api/upload/nessus** - File upload and parsing endpoint
  - [ ] File upload handling with validation
  - [ ] Integration with existing nessus_scanreport_import.py parser
  - [ ] Progress tracking and error responses
  - [ ] JSON response with import statistics
- [ ] **URL routing configuration** for upload endpoint
- [ ] **Basic error responses** and logging
- [ ] **CORS configuration** for frontend access
- [ ] **File size limits** and validation
- [ ] **Test endpoint** with existing Nessus sample files

### Phase 1B: lovable.dev UI + Supabase Auth (Second Priority)
- [ ] **Create Supabase project**
- [ ] **Deploy existing schema** to Supabase PostgreSQL
- [ ] **Configure authentication providers**
- [ ] **Set up storage buckets** for file uploads
- [ ] **Enable Row Level Security (RLS)**
- [ ] **lovable.dev Setup**:
  - [ ] Connect to Supabase project
  - [ ] Configure authentication flow
  - [ ] Create basic upload page with drag-and-drop
  - [ ] Test file upload to Django endpoint

### Phase 1C: Django Reporting Endpoints (Third Priority)
- [ ] **GET /api/reports/mttr** - MTTR calculations
  - [ ] Calculate mean time to remediate by severity
  - [ ] Group by business group and asset type
  - [ ] Support date range filtering
- [ ] **GET /api/reports/sla** - SLA compliance data
  - [ ] Calculate SLA compliance percentages
  - [ ] Show overdue findings count
  - [ ] Group by severity and business group
- [ ] **Connect Django to Supabase** database (migrate from local PostgreSQL)
- [ ] **Test reporting endpoints** with cloud database

---

## 🎨 Phase 2: UI Development (Days 7-10)

### lovable.dev Setup
- [ ] Connect to Supabase project
- [ ] Configure authentication flow
- [ ] Set up routing structure
- [ ] Create component library

### Core Pages
- [ ] **Dashboard**
  - [ ] Summary statistics widget
  - [ ] MTTR metrics widget
  - [ ] SLA compliance widget
  - [ ] Top risks widget
- [ ] **Assets Page**
  - [ ] Table with sorting/filtering
  - [ ] Business group assignment
  - [ ] Tag management
  - [ ] Bulk operations
- [ ] **Vulnerabilities Page**
  - [ ] Severity filtering
  - [ ] Search functionality
  - [ ] Risk score display
  - [ ] Export to CSV
- [ ] **Findings Page**
  - [ ] Status updates (Open/Fixed/Risk Accepted)
  - [ ] Bulk status changes
  - [ ] Filter by business group
  - [ ] SLA deadline display
- [ ] **Upload Page**
  - [ ] Drag-and-drop file upload
  - [ ] Progress indicator
  - [ ] Error display
  - [ ] Success confirmation

### Shared Components
- [ ] Data table component
- [ ] Filter sidebar
- [ ] Status badge component
- [ ] Export button
- [ ] Loading states

---

## 📊 Phase 3: Analytics & Reporting (Days 11-12)

### Database Views
- [ ] Create vulnerability_summary view
- [ ] Create asset_risk_summary view
- [ ] Create sla_compliance view
- [ ] Create mttr_metrics view

### Report Implementation
- [ ] MTTR calculation logic
- [ ] SLA compliance percentages
- [ ] Business group comparisons
- [ ] Trend calculations (30/60/90 days)
- [ ] CSV export functionality

### Dashboard Polish
- [ ] Real-time metric updates
- [ ] Responsive design
- [ ] Print-friendly layouts
- [ ] Chart interactions

---

## ✅ Phase 4: MVP Testing & Deployment (Days 13-14)

### Testing
- [ ] End-to-end workflow tests
- [ ] Performance testing (10K+ findings)
- [ ] Multi-user access testing
- [ ] Error handling validation
- [ ] Cross-browser testing

### Documentation
- [ ] User quick start guide
- [ ] Admin configuration guide
- [ ] API documentation
- [ ] Deployment guide

### Deployment
- [ ] Deploy Django to Heroku/Railway
- [ ] Configure production settings
- [ ] Set up SSL certificates
- [ ] Configure backups
- [ ] Set up monitoring

---

## 🚦 REALISTIC Priority Order

### IMMEDIATE (This Week)
1. **Create minimal API endpoints** (upload, reports)
2. **Set up Supabase cloud project**
3. **Deploy schema to Supabase**
4. **Test cloud integration**

### HIGH (Next Week)
1. **lovable.dev UI development**
2. **Core pages and components**
3. **Dashboard and reporting**

### MEDIUM (Week 3)
1. **Testing and validation**
2. **Documentation**
3. **Production deployment**

---

## 📋 Feature Checklist (MVP Only)

### Must Have ✅
- ✅ Nessus file parsing (COMPLETE)
- [ ] Asset/vulnerability/finding display (need UI)
- ✅ Basic risk scoring (COMPLETE)
- [ ] Status tracking (need UI)
- [ ] MTTR reporting (need API endpoints)
- [ ] SLA compliance (need API endpoints)
- ✅ Business groups (COMPLETE in backend)
- [ ] CSV export (need API endpoints)

### Nice to Have (If Time Permits)
- [ ] Email notifications
- [ ] Advanced filtering
- [ ] Saved searches
- [ ] User preferences
- [ ] Activity logging

---

## 🎯 Success Metrics

### Technical
- ✅ Parse 100K findings in < 15 minutes (ACHIEVED with current parser)
- [ ] Sub-second page loads
- [ ] 99%+ uptime
- [ ] Zero data loss

### Business
- [ ] Complete MVP in 2 weeks
- [ ] Support 100+ concurrent users
- ✅ Handle 1M+ findings (database schema supports this)
- [ ] Enable basic vulnerability management workflow

---

*Last Updated: 2025-01-02* 