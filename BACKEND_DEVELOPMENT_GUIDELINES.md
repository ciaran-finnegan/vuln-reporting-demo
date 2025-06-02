# Backend Development Guidelines for Risk Radar

## Current File Layout (As of 2025-01-02)

```
/riskradar/                # Django project root ✅ IMPLEMENTED
    __init__.py           ✅
    settings.py           ✅ Complete PostgreSQL configuration
    urls.py               ✅ Basic admin routing (API routes pending)
    wsgi.py               ✅
    asgi.py               ✅

/core/                    # Main Django app ✅ FULLY IMPLEMENTED
    __init__.py           ✅
    admin.py              ✅ Enhanced with AssetCategory/AssetSubtype management
    apps.py               ✅
    models.py             ✅ Complete schema (356 lines, 7 tables + enhanced asset types)
    views.py              ❌ PENDING (only 4 lines - needs API endpoints)
    forms.py              ✅ FieldMapping forms
    nessus_scanreport_import.py  ✅ Complete parser (513 lines)
    
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
        0002-0005_*.py    ✅ Incremental updates
        0006_multi_scanner_support.py ✅ Multi-scanner schema
        0007_enhanced_asset_types.py ✅ Categories & subtypes
        
    tests/                ❌ PENDING (placeholder files only)
        __init__.py       ✅
        test_models.py    ❌ TODO
        test_views.py     ❌ TODO
        test_api.py       ❌ TODO

/manage.py                ✅ IMPLEMENTED
/requirements.txt         ✅ IMPLEMENTED (Django, psycopg2, etc.)
/.env                     ❌ TODO (environment variables)
/Dockerfile               ❌ TODO (containerisation)

# PLANNED ADDITIONS:
/core/serializers.py     ❌ TODO (DRF serializers for API endpoints)
/core/reports.py         ❌ TODO (CSV/PDF reporting logic)
/core/utils.py           ❌ TODO (shared utility functions)
```

## Implementation Status Summary

### ✅ **COMPLETED** (feature/core-mvp branch)
- **Complete Django project structure** (28 Python files)
- **Full database schema** with 7 migrations
- **Enhanced asset type system** (5 categories, 86 subtypes)
- **Complete Nessus parser** with field mapping engine
- **Enhanced Django admin interface**
- **6 management commands** for setup and data operations
- **Successfully tested** with real Nessus imports

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

### 7. LLM/AI Usage
- When using an LLM to generate code, always specify the file and function/class to edit.
- Do not allow the LLM to move, rename, or split files unless explicitly instructed.
- LLM should always check for existing conventions before introducing new patterns.

---

## Reference Documents

- Always refer to `BACKEND_DEVELOPMENT_GUIDELINES.md` and `PRODUCT_REQUIREMENTS_DOCUMENT.md` before suggesting or making backend changes.
- These documents define the canonical structure and conventions for the backend. 