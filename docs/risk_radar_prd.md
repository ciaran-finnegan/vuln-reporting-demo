# Risk Radar MVP – Product Requirements Document

## Overview  
**Risk Radar** is a vulnerability management platform inspired by Vulcan Cyber’s ExposureOS. This PRD focuses on high-priority MVP features: **(1)** Nessus file uploads, **(2)** Vulnerability & Asset Management, **(3)** Business Groups & Tags, and **(4)** Remediation & SLA Reports. The goal is to outline each feature from a developer’s perspective, define the supporting data model, propose an initial architecture (React + Supabase), and provide an implementation plan with step-by-step tasks. This will enable developers to rapidly build the MVP on Supabase, with an eye towards a later migration to a Django backend for advanced capabilities.

## 1. Nessus File Upload Integration  
**Description:** The MVP will allow users to upload Nessus scan report files (`.nessus` format) and ingest their contents into the Risk Radar database. Vulcan Cyber’s platform uses a “Nessus File Connector” for this purpose, and Risk Radar will implement a similar workflow without requiring an API integration.

- **Supported Format:** Accept `.nessus` XML files exported from Tenable (Tenable.io or Tenable.sc). Other formats or direct API integration are out of scope for MVP.
- **File Constraints:** Enforce file prerequisites similar to Vulcan’s: e.g. maximum size ~300 MB and UTF‑8 encoding. Large files will be processed asynchronously to avoid blocking the UI.
- **Upload Workflow:** Users upload a file; a backend function parses it and inserts or updates:
  - **Assets** (hosts) with hostname, IP, OS, etc.
  - **Vulnerability instances** on those assets with plugin ID/CVE, severity, etc.
  - Deduplicate assets by IP/hostname; deduplicate vulnerability instances by asset + plugin ID (or plugin ID + port).  
  - If a previously‑seen vulnerability instance is missing from the new scan, mark it **Resolved**.
- **Error Handling:** Validate file type/size, stream‑parse large files, and return clear success/failure messages.

---

## 2. Vulnerability & Asset Management  

### 2.1 Vulnerability Management  
Track each vulnerability **instance** (finding on an asset):

| Field | Notes |
|-------|-------|
| id | PK |
| asset_id | FK → assets |
| plugin_id / cve_id | Scanner identifiers |
| severity | Critical / High / Medium / Low |
| status | Vulnerable, In Progress, Resolved, Acknowledged |
| discovered_date | first seen |
| last_seen_date | updated on each scan |
| resolved_date | when status = Resolved |
| due_date | discovery + SLA_days |

Status transitions:

```
Vulnerable → In Progress → Resolved
Vulnerable → Acknowledged (risk accepted)
```

Automatic resolution when a subsequent scan no longer lists the finding.

### 2.2 Asset Management  
Store each asset with host data and relationships:

| Field | Notes |
|-------|-------|
| id | PK |
| name / hostname | |
| ip_address | |
| asset_type | default 'Host' |
| os / os_version | |
| source | 'Nessus File' |
| first_seen / last_seen | timestamps |

Many‑to‑many with **tags** and **business_groups**. Query filters by severity, status, tag, group, etc. Compute open‑vuln counts and SLA compliance per asset.

---

## 3. Business Groups & Tags  

* **Tags** – free‑form labels on assets (many‑to‑many).  
* **Business Groups** – organisational collections of assets (many‑to‑many).  
  * Manual assignment or tag‑based population (simplified to manual for MVP).  
  * Used for filtering and SLA policy scoping.

Schema additions:

```
tags(id, name)
asset_tags(asset_id, tag_id)
business_groups(id, name, description)
asset_groups(asset_id, business_group_id)
```

---

## 4. Remediation Tracking & SLA Reporting  

### 4.1 Remediation Tracking  
Use vulnerability **status** plus a calculated **due_date** to track remediation. No external ticket integrations for MVP, but allow notes or external ID field.

### 4.2 SLA Policies & Reports  
* Table `sla_policies(business_group_id NULLABLE, severity, days)`  
* On ingestion, compute `due_date = discovered_date + days`.  
* Reports:  
  * % Assets compliant (no overdue vulns)  
  * Count of overdue findings (global & per group)  
  * Breakdown by severity and business group  

---

## 5. Data Model (ERD)  

```
assets           1⟶n vulnerabilities
assets      n⟶n tags            via asset_tags
assets      n⟶n business_groups via asset_groups
business_groups 1⟶n sla_policies
```

Optional `uploads` table to track file batches.

---

## 6. Application Architecture (MVP)  

| Layer | Technology | Notes |
|-------|------------|-------|
| Front‑end | React + Vite, Shadcn/ui | SPA with Supabase JS client |
| Auth | Supabase Auth | Email/password |
| DB / API | Supabase Postgres | Auto REST/RPC, RLS |
| File parsing | Supabase Edge Function | Deno + fast‑xml‑parser |
| Hosting | Vercel / Netlify (FE) | Supabase hosted backend |

Later migration: Django app connecting to same Postgres; Django management commands replace Edge Function for ETL.

---

## 7. Implementation Plan  

| # | Task | Key Outputs | Review Checklist |
|---|------|-------------|------------------|
| 1 | **DB schema** | Tables, enums, indexes | All FK/PK correct, dummy insert works |
| 2 | **Auth & RLS** | Email login, policies | Unauthed blocked, authed CRUD works |
| 3 | **Upload UI** | React component, storage upload | File type/size validated, progress feedback |
| 4 | **Parsing Function** | Edge Function, XML parser | Dedupes correctly, due_date calc, idempotent |
| 5 | **Vuln Views** | API queries, Vuln table UI | Filtering + status edit, pagination |
| 6 | **Asset Views** | Asset table UI, tag/group editors | Tag & group CRUD, open‑vuln count correct |
| 7 | **Group & SLA Mgmt** | Group CRUD UI, SLA editor | New group auto‑gets SLA rows, edits persist |
| 8 | **SLA Report** | SQL view + Report page | KPI accuracy, perf OK, filters work |
| 9 | **Integr. Test** | Seed data, end‑to‑end QA | All features pass functional tests |

Each task must pass lead‑engineer review before next begins.

---

## 8. Future Enhancements (Post‑MVP)  
* Multi‑tenant support via `org_id` + RLS  
* Additional connectors (API‑based Tenable, CrowdStrike, Qualys, MDE)  
* Automated remediation campaigns & ticket integrations (JIRA, ServiceNow)  
* Dynamic group rules (tag‑driven, saved filters)  
* Risk scoring & threat intelligence enrichment  
* Notification system (Slack, email)  
* Historical SLA trend dashboards  
* Full migration to Django REST API with Celery for ETL jobs  
