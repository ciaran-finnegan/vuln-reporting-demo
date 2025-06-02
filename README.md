# Risk Radar Backend

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](.) [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Status](https://img.shields.io/badge/status-MVP--active-green)]()

## Overview

Risk Radar is a hybrid Django + Supabase vulnerability management platform. It ingests Nessus scan files, manages assets and vulnerabilities, tracks remediation, and provides compliance reporting. The backend is built with Django and connects to a Supabase-hosted PostgreSQL database, with a React (lovable.dev) frontend for rapid UI development.

---

## Key Features

- Nessus file import and parsing (configurable field mapping)
- Asset and vulnerability management (all asset types)
- SLA tracking and compliance reporting
- Remediation campaign management
- Business groups and asset tagging
- REST API for complex logic and reporting
- Supabase for authentication, storage, and direct CRUD
- Django Admin for backend management

---

## Quick Start

### 1. Prerequisites
- Python 3.10+
- Supabase project (with database and storage bucket)
- Node.js (for frontend, if using lovable.dev)

### 2. Backend Setup
```bash
# Clone the repo
# (Assume you are in the project root)
pip install -r requirements.txt
cp .env.example .env  # Add your Supabase credentials
python manage.py migrate
python manage.py createsuperuser
```

### 3. Database Setup
- Run the schema in Supabase SQL Editor (see architecture docs)
- Enable Row Level Security and create policies
- Insert default data (asset types, SLA policy, Nessus integration)

### 4. Run the Server
```bash
python manage.py runserver
```

### 5. Frontend (lovable.dev)
- Connect to Supabase and Django API endpoints
- Use built-in auth and storage components

---

## Project Structure

```
/riskradar/                # Django project root
  /core/                   # Main Django app
    models.py              # ORM models
    views.py               # API endpoints
    authentication.py      # Supabase JWT auth
    nessus_scanreport_import.py  # Nessus import logic
    management/commands/   # Django management commands
    migrations/            # Database migrations
    ...
  manage.py                # Django management script
  requirements.txt         # Python dependencies
  .env                     # Environment variables
/commands/                 # Utility scripts and tools
  testing/                 # Test scripts
    test_upload_api.py     # API authentication testing
  data_generation/         # Test data generation
    generate_weekly_nessus_files.py  # Synthetic Nessus data
/docs/                     # Architecture & design docs
/data/                     # Sample Nessus files, CSVs
```

---

## Commands & Scripts

The `/commands` directory contains utility scripts organised by function:

### Testing Scripts (`/commands/testing/`)
```bash
# Test upload API with authentication
cd commands/testing
python test_upload_api.py
```

**Features:**
- Tests both authenticated and unauthenticated uploads
- Validates JWT token handling
- Tests error scenarios (invalid files, tokens)
- Requires Django server running and `.env` configured

### Data Generation (`/commands/data_generation/`)
```bash
# Generate synthetic test data
cd commands/data_generation
python generate_weekly_nessus_files.py
```

**Features:**
- Creates 4 weeks of realistic Nessus scan data
- Multiple scan profiles (production, DMZ, development)
- Progressive data growth simulation
- Outputs to `data/synthetic_nessus/`

### Environment Setup
Scripts automatically load environment variables from `riskradar/.env`:
- `SUPABASE_JWT_SECRET` - For authentication testing
- `SUPABASE_PROJECT_ID`, `SUPABASE_URL`, `SUPABASE_ANON_KEY` - For API integration

For detailed usage instructions, see `commands/README.md` and subdirectory README files.

---

## Release Management

- See [CHANGES.md](./CHANGES.md) for version history and release notes.

---

## Onboarding Checklist

- [ ] Read `BACKEND_DEVELOPMENT_GUIDELINES.md` and `Rapid_MVP_App_Architecture.md`
- [ ] Use the documented file layout and naming conventions
- [ ] Check if changes are allowed by the guidelines before making them
- [ ] For LLM/AI: Always specify file and function/class to edit

---

## AI Usage

- Always reference the guidelines and architecture docs when generating or editing code.
- Do not introduce new files or patterns unless justified in the docs.

---

## License

MIT

> For Nessus field extraction and mapping, see [nessus_extractor.py extraction script](https://github.com/ciaran-finnegan/nessus-reporting-metrics-demo/blob/main/etl/extractors/nessus_extractor.py). 