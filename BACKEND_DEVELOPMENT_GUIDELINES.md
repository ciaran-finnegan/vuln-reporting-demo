# Backend Development Guidelines for Risk Radar

## File Layout

```
/riskradar/                # Django project root (contains settings, wsgi, asgi, etc.)
    __init__.py
    settings.py
    urls.py
    wsgi.py
    asgi.py

/core/                     # Main Django app for business logic
    __init__.py
    admin.py
    apps.py
    models.py
    views.py
    serializers.py
    scanner_import.py      # Nessus and other scanner import logic
    management/
        commands/
            import_nessus.py
            generate_sla_report.py
            capture_mttr_snapshot.py
    migrations/
        __init__.py
        ...               # Migration files

    tests/
        __init__.py
        test_models.py
        test_views.py
        test_api.py

    reports.py             # CSV/PDF reporting logic
    utils.py               # Any shared utility functions

/manage.py                 # Django management script

/requirements.txt          # Python dependencies
/.env                      # Environment variables (not committed)
/Dockerfile                # For containerisation (if used)
```

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

- Always refer to `BACKEND_DEVELOPMENT_GUIDELINES.md` and `Rapid_MVP_App_Architecture.md` before suggesting or making backend changes.
- For Nessus field extraction and mapping, see [nessus_extractor.py extraction script](https://github.com/ciaran-finnegan/nessus-reporting-metrics-demo/blob/main/etl/extractors/nessus_extractor.py).
- These documents define the canonical structure and conventions for the backend. 