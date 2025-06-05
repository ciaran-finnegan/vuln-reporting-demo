# Backend Development Guidelines for Risk Radar

## Current File Layout (As of 2025-01-03)

```
/riskradar/                # Django project root ✅ IMPLEMENTED
    __init__.py           ✅
    settings.py           ✅ Complete PostgreSQL configuration + Supabase auth
    urls.py               ✅ Basic admin + API routing
    wsgi.py               ✅
    asgi.py               ✅

/core/                    # Main Django app ✅ FULLY IMPLEMENTED
    __init__.py           ✅
    admin.py              ✅ Enhanced with AssetCategory/AssetSubtype management
    apps.py               ✅
    models.py             ✅ Complete schema (360+ lines, UserProfile + enhanced asset types)
    views.py              ✅ API endpoints with authentication + duplicate detection
    authentication.py     ✅ Supabase JWT authentication backend
    forms.py              ✅ FieldMapping forms
    nessus_scanreport_import.py  ✅ Complete parser (513 lines)
    urls.py               ✅ API URL routing
    utils.py              ✅ Hash calculation and duplicate detection utilities
    
    management/           ✅ FULLY IMPLEMENTED
        commands/         ✅ 6 commands implemented
            __init__.py   ✅
            import_nessus.py              ✅ File import command
            setup_asset_categories.py     ✅ 86 asset subtypes setup
            setup_nessus_field_mappings.py ✅ Basic field mappings
            setup_enhanced_nessus_mappings.py ✅ Enhanced with asset type detection
            populate_initial_data.py      ✅ SLA policies, business groups
            clear_demo_data.py            ✅ Data management
            
    migrations/           ✅ FULLY IMPLEMENTED
        __init__.py       ✅
        0001_initial.py   ✅ Base schema
        0002-0007_*.py    ✅ Incremental updates including UserProfile
        0008_*.py         ✅ Authentication migration
        0009_*.py         ✅ Table naming consistency
        0010_*.py         ✅ Duplicate file detection (file_hash field)
        
    tests/                ❌ PENDING (placeholder files only)
        __init__.py       ✅
        test_models.py    ❌ TODO
        test_views.py     ❌ TODO
        test_api.py       ❌ TODO

/commands/                ✅ NEW - Organised script directory
    README.md             ✅ Complete documentation
    testing/              ✅ Test and validation scripts
        README.md         ✅ Testing documentation
        test_upload_api.py ✅ Authentication testing script
        test_duplicate_detection.py ✅ Duplicate detection testing script
    data_generation/      ✅ Synthetic data generation
        README.md         ✅ Data generation documentation
        generate_weekly_nessus_files.py ✅ Nessus file generator

/manage.py                ✅ IMPLEMENTED
/requirements.txt         ✅ IMPLEMENTED (Django, PyJWT, etc.)
/.env                     ❌ TODO (environment variables)
/Dockerfile               ❌ TODO (containerisation)

# PLANNED ADDITIONS:
/core/serializers.py     ❌ TODO (DRF serializers for API endpoints)
/core/reports.py         ❌ TODO (CSV/PDF reporting logic)
/commands/maintenance/   ❌ TODO (database operations)
/commands/deployment/    ❌ TODO (setup scripts)
```

## Implementation Status Summary

### ✅ **COMPLETED** (feature/duplicate-file-detection branch)
- **Complete Django project structure** (30+ Python files)
- **Full database schema** with 10 migrations including duplicate detection
- **Enhanced asset type system** (5 categories, 86 subtypes)
- **Complete Nessus parser** with field mapping engine
- **Duplicate file detection** with SHA-256 hashing and force re-import
- **Enhanced Django admin interface**
- **6 management commands** for setup and data operations
- **Upload history management** and comprehensive API endpoints
- **Successfully tested** with real Nessus imports and duplicate detection

### ❌ **PENDING** (upcoming branches)
- **API endpoints** (views.py, serializers.py)
- **Comprehensive testing** (test files are placeholders)
- **Reporting logic** (reports.py)
- **Environment configuration** (.env)
- **Containerisation** (Dockerfile)

---

## Development Guidelines

### 1. File/Module Boundaries
- **models.py**: All Django ORM models.
- **admin.py**: Django admin customisations.
- **serializers.py**: DRF serializers only.
- **views.py**: API and web views (keep logic thin, call services/helpers).
- **scanner_import.py**: All scanner import logic (Nessus, future connectors). See also [nessus_extractor.py extraction script](https://github.com/ciaran-finnegan/nessus-reporting-metrics-demo/blob/main/etl/extractors/nessus_extractor.py) for practical field extraction examples.
- **reports.py**: All reporting/export logic (CSV, PDF).
- **management/commands/**: Only Django management commands.
- **tests/**: All tests, grouped by type (models, views, API).

### 2. No Unnecessary Refactoring
- Do not rename, move, or split files unless there is a clear, documented reason.
- Do not introduce new apps unless the domain model grows significantly.
- Keep all scanner import logic in `scanner_import.py` unless a new scanner type requires a major refactor.

### 3. Extending Functionality
- New scanner integrations: Add config via Django admin, not code changes.
- New API endpoints: Add to `views.py` and `urls.py` only if not achievable via Supabase direct.
- New models: Add to `models.py` and run migrations; update admin/serializers as needed.

### 4. Testing
- All new business logic must have a corresponding test in `tests/`.
- Use Django's test runner; do not introduce new test frameworks without discussion.

### 5. Configuration
- All environment-specific settings go in `.env` and are loaded in `settings.py`.
- Do not hardcode secrets or credentials.

### 6. Documentation
- Update architecture and todo docs if you make any structural changes.
- Document any new endpoints or models in the appropriate section of the architecture doc.
- Use concise professional language with british english spelling
- Do not use unnecessary words, particularly adjectives, for example words like the following should rarely be required 'advanced, enhanced, robust, enterprise-grade', these are just examples
- Do not use em dashes, use correct British English grammar and punctuation

### 7. Script and Utility File Organisation
- **ALL scripts, utilities, and test files MUST be placed in the `/commands` directory**
- **NEVER create scripts in the project root directory**
- Use appropriate subdirectories:
  - `/commands/testing/` - Test and validation scripts
  - `/commands/data_generation/` - Synthetic data creation scripts
  - `/commands/maintenance/` - Database and system maintenance scripts
  - `/commands/deployment/` - Deployment and setup scripts
- Each subdirectory must have a README.md explaining its scripts
- Scripts must handle relative paths correctly for their subdirectory location

### 8. LLM/AI Usage
- When using an LLM to generate code, always specify the file and function/class to edit.
- Do not allow the LLM to move, rename, or split files unless explicitly instructed.
- LLM should always check for existing conventions before introducing new patterns.
- **CRITICAL: LLM must ALWAYS place new scripts in `/commands` subdirectories, NEVER in project root**
- LLM must update relevant README files when adding new scripts

---

## Reference Documents

- Always refer to `BACKEND_DEVELOPMENT_GUIDELINES.md` and `PRODUCT_REQUIREMENTS_DOCUMENT.md` before suggesting or making backend changes.
- These documents define the canonical structure and conventions for the backend. 