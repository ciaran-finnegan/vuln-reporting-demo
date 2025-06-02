# Risk Radar Development Roadmap & TODO

## Status: Ready for MVP Development

This document tracks implementation tasks aligned with the MVP Feature Matrix in the Product Requirements Document. See [CHANGES.md](./CHANGES.md) for release notes.

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

#### Implementation Completed:
1. ✅ Created migration 0006_multi_scanner_support.py
2. ✅ Updated models.py with new fields and renames
3. ✅ Updated setup_nessus_field_mappings.py command
4. ✅ Created populate_initial_data.py command
5. ✅ Updated generate_weekly_nessus_files.py for test data
6. ✅ Updated nessus_scanreport_import.py parser
7. ✅ Ran migration: `python manage.py migrate`
8. ✅ Cleared old data: `python manage.py clear_demo_data --keep-asset-types --keep-mappings`
9. ✅ Populated initial data: `python manage.py populate_initial_data`
10. ✅ Re-setup mappings: `python manage.py setup_nessus_field_mappings`
11. ✅ Re-imported sample: `python manage.py import_nessus` - Successfully imported 7 assets, 14 vulnerabilities, 20 findings

---

## ✅ Phase 0: Schema Validation Complete

### Schema Assessment Results
Based on analysis of Vulcan Cyber connector documentation, our current schema is **production-ready** for multi-scanner support.

### Key Validations
- [x] Flexible asset identification (hostname, IP, MAC, cloud IDs via JSONB)
- [x] Scanner-agnostic field mapping tables
- [x] Severity normalisation framework
- [x] JSONB extensibility for vendor-specific data
- [x] Proper foreign key relationships and constraints

---

## 🚀 Phase 1: MVP Infrastructure (Days 1-3)

### Supabase Setup
- [ ] Create Supabase project
- [ ] Deploy database schema
- [ ] Configure authentication providers
- [ ] Set up storage buckets for file uploads
- [ ] Enable Row Level Security (RLS)

### Django Project
- [ ] Create minimal Django project structure
- [ ] Mirror Supabase schema in models.py
- [ ] Set up Supabase database connection
- [ ] Create Django admin interface
- [ ] Configure static file serving

### Initial Data
- [ ] Create AssetType entries (Host, Website, Container, Code, Cloud)
- [ ] Populate Nessus field mappings
- [ ] Create default SLA policies (7 days Critical, 30 days High)
- [ ] Set up initial business groups (Production, Development)
- [ ] Load Nessus severity mappings

---

## 🔨 Phase 1.5: Scanner Integration (Days 4-6)

### Nessus Parser Implementation
- [ ] XML parsing with configurable field extraction
- [ ] Field mapping engine using database configuration
- [ ] Asset deduplication (basic hostname + IP)
- [ ] Vulnerability deduplication by CVE/plugin ID
- [ ] Finding creation with proper relationships
- [ ] Error handling and validation
- [ ] Progress tracking for large files

### Django API Endpoints
- [ ] `POST /api/upload/nessus` - File upload and parsing
- [ ] `GET /api/reports/mttr` - MTTR calculations
- [ ] `GET /api/reports/sla` - SLA compliance data
- [ ] Basic error responses and logging

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

## 🚦 Priority Order

### MVP (2 Weeks)
1. **Immediate**: Infrastructure setup and schema deployment
2. **High**: Nessus parser and basic UI
3. **High**: Dashboard and core reporting
4. **Medium**: Testing and documentation

### Post-MVP (Months 2-4)
1. **Month 2**: Additional scanners, advanced deduplication
2. **Month 3**: API development, campaign management
3. **Month 4**: Enterprise features (SSO, multi-tenancy)

---

## 📋 Feature Checklist (MVP Only)

### Must Have ✅
- [ ] Nessus file parsing
- [ ] Asset/vulnerability/finding display
- [ ] Basic risk scoring
- [ ] Status tracking
- [ ] MTTR reporting
- [ ] SLA compliance
- [ ] Business groups
- [ ] CSV export

### Nice to Have (If Time Permits)
- [ ] Email notifications
- [ ] Advanced filtering
- [ ] Saved searches
- [ ] User preferences
- [ ] Activity logging

### Not in MVP ❌
- Automated workflows
- Ticketing integration
- Exception requests
- Campaign management
- Custom report builder
- Additional scanners
- Full REST API

---

## 📝 Technical Decisions

### Architecture
- **Hybrid approach**: Django for parsing, Supabase for CRUD
- **Direct DB access**: lovable.dev connects directly to PostgreSQL
- **Minimal API surface**: Only complex operations via Django

### Technology Stack
- **Backend**: Django 4.2 + PostgreSQL (Supabase)
- **Frontend**: React (lovable.dev)
- **Authentication**: Supabase Auth
- **Storage**: Supabase Storage
- **Deployment**: Heroku/Railway + Supabase Cloud

### Development Principles
- **KISS**: Keep it simple for MVP
- **Progressive Enhancement**: Basic features first
- **User-Centric**: Focus on core workflows
- **Performance**: Optimise for common operations

---

## 🎯 Success Metrics

### Technical
- Parse 100K findings in < 15 minutes
- Sub-second page loads
- 99%+ uptime
- Zero data loss

### Business
- Complete MVP in 2 weeks
- Support 100+ concurrent users
- Handle 1M+ findings
- Enable basic vulnerability management workflow

---

## 🔄 Post-MVP Roadmap

See [PRODUCT_REQUIREMENTS_DOCUMENT.md](./PRODUCT_REQUIREMENTS_DOCUMENT.md) Section 7.5 for detailed post-MVP phases.

Key themes:
- **Phase 4**: Enhanced features (Month 2)
- **Phase 5**: Enterprise features (Month 3)
- **Phase 6**: Scale & security (Month 4)
- **Phase 7**: Full API development (Month 5+)

---

## Migration and Refactoring of Existing AssetType Table

**Migration Steps:**
1. **Backup Existing Data:**  
   - Export all current `AssetType` records for reference and rollback.

2. **Schema Migration:**  
   - Rename or deprecate the current `AssetType` table.
   - Create new `asset_categories` and `asset_subtypes` tables as per the enhanced schema.
   - Migrate existing `AssetType` values to the new `asset_categories` table (e.g., Host, Website, Container, Code, Cloud).
   - For each category, populate standard subtypes (from `ASSET_TYPES.md`).

3. **Data Migration:**  
   - Update all existing `Asset` records to reference the new `category_id` and (where possible) `subtype_id`.
   - If subtype cannot be determined, set to NULL or a default value.

4. **Code & Admin Refactor:**  
   - Update Django models and admin to use the new tables.
   - Remove or archive the old `AssetType` model after migration is verified.

5. **Validation:**  
   - Ensure all assets have a valid category.
   - Spot-check that subtypes are correctly assigned where possible.

**Rollback Plan:**
- If issues arise, restore the original `AssetType` table and revert asset references.

*Last Updated: 2025-01-02* 