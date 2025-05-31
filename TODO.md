# Risk Radar Development Roadmap & TODO

## Status: MVP in Progress

This document tracks the major phases and tasks for Risk Radar development. See [CHANGES.md](./CHANGES.md) for release notes.

---

## 🚀 Phase 1: Core MVP

- [x] Supabase project setup (database, storage, RLS)
- [x] Django project and core app setup
- [x] Database schema and default data in Supabase (including AssetTag with static and dynamic tag support via tag_key/tag_value)
- [x] Django models, admin, and migrations
- [ ] Update to support setting a default Asset_Type for each Integration, e.g. for Nessus make it Hosts
- [ ] Nessus scanner import logic (`nessus_scanreport_import.py`)
- [ ] API endpoint for Nessus parsing (`/api/parse-nessus/`)
- [ ] Minimal Django API endpoints for assets, vulnerabilities, findings, campaigns
- [ ] Connect lovable.dev frontend to Supabase and Django API
- [ ] Admin: Configure field mappings and severity mappings
- [ ] Admin: Asset, Vulnerability, Finding, Campaign, Tag management
- [x] Update Vulnerability model and schema to use generic, extensible fields (published_at, modified_at, references, risk_factor, exploit, cvss, metadata)
- [x] Expand Nessus field mapping logic to cover all relevant fields for generic, scanner-agnostic import (references, exploit, cvss, risk_factor, dates, etc.)
- [ ] Review and maintain field mappings as new scanner types are added

---

## 📊 Phase 2: Reporting & Metrics

- [ ] SLA compliance reporting (CSV/PDF export)
- [ ] Remediation campaign PDF reports
- [ ] Remediation performance metrics API (`/api/findings/remediation-metrics/`)
- [ ] Dashboard UI for metrics and trends
- [ ] MTTR and SLA analytics views in Supabase

---

## 🏗️ Phase 3: Production Readiness

- [ ] Environment variable management and secrets
- [ ] Dockerfile and deployment scripts
- [ ] Automated daily MTTR snapshot job
- [ ] Security review and hardening
- [ ] User documentation and onboarding

---

## 🟡 In Progress
- [ ] (Branch) Implement Nessus scanner import logic
- [ ] (Branch) Add API endpoint for Nessus parsing
- [ ] (Branch) Add admin configuration for field/severity mappings

## 🟢 Ready for Review
- [ ] (Branch) [Add here as features are completed]

---

## 📚 Architecture Decision Records (ADRs)

- [ ] Document major architecture decisions (database, API, integrations)
- [ ] Review and update guidelines as needed

---

## ✅ Completed Milestones

- Supabase and Django project initialised
- Database schema and default data loaded
- Django admin and models configured
- Database migrations applied successfully

---

## Notes

- Use Australian English spelling and conventions
- Reference [CHANGES.md](./CHANGES.md) for all release notes
- For detailed architecture, see `Rapid_MVP_App_Architecture.md`
- AssetTag now supports both static (name only) and dynamic (tag_key/tag_value) tags for flexible asset labelling. 