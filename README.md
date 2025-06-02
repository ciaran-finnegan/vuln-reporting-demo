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
    scanner_import.py      # Nessus import logic
    management/commands/   # Batch commands
    reports.py             # CSV/PDF reporting
    ...
  manage.py                # Django management script
  requirements.txt         # Python dependencies
  .env                     # Environment variables
  Dockerfile               # (optional)
/docs/                     # Architecture & design docs
/data/                     # Sample Nessus files, CSVs
```

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