Application Architecture – Vulcan-Clone MVP (Full Detail)

Table of Contents
	1.	Overview & Goals
	2.	Technology Stack & Rationale
	3.	Database Schema (DDL)
	4.	Analytics Layer (Materialised Views & Jobs)
	5.	API Contract (OpenAPI 3.1)
	6.	Backend Services
6.1 Supabase JWT Middleware (Python)
6.2 Nessus ETL Parser (Python)
	7.	CI/CD & Dev Environment
	8.	Front-end Architecture
	9.	UX Wireframes
	10.	Security Notes & Compliance
	11.	Future Extensibility

⸻

1 Overview & Goals

Build a minimal but production-ready clone of key Vulcan Cyber workflows:
	•	Upload Tenable .nessus files.
	•	Ingest assets & vulnerabilities across all five asset types (Host, Code, WebSite, Image, Cloud).
	•	Tag & group assets dynamically; attach SLA policies.
	•	Show SLA breach & 30-day MTTR metrics.
	•	Let analysts open remediation campaigns.

The system is single-tenant today (easy multi-tenant pivot by adding tenant_id + RLS).

⸻

2 Technology Stack & Rationale

Layer	Tech	Reason
Auth / Storage	Supabase (Auth, Storage, Scheduled Jobs)	SaaS-managed Postgres, JWT out-of-box, signed URLs, no infra.
API / Worker	Django 5 + DRF	Mature ORM, great OpenAPI generation, Celery support.
DB	PostgreSQL 16 (managed by Supabase)	JSONB, materialised views, partitioning ready.
ETL	Python (lxml, sqlalchemy)	Stream-parse 300 MB XML without RAM blow-up.
SPA	React 18, Vite, Tailwind, shadcn/ui, TanStack Query	Modern, extremely fast cold build.
CI/CD	GitHub Actions + Netlify	Free tier good enough for demo.


⸻

3 Database Schema (DDL)

3.1 Enumerations

-- asset_kind covers every Vulcan asset tab
CREATE TYPE asset_kind AS ENUM ('host','code_project','website','image','cloud_resource');
CREATE TYPE vuln_severity AS ENUM ('critical','high','medium','low','info');
CREATE TYPE finding_status AS ENUM ('vulnerable','in_progress','fixed','risk_acknowledged','false_positive');
CREATE TYPE campaign_state AS ENUM ('open','closed');
CREATE TYPE campaign_origin AS ENUM ('manual','automation');

3.2 Core Tables

---------------------------  lookup ---------------------------
CREATE TABLE asset_type (
  id   SERIAL PRIMARY KEY,
  name asset_kind NOT NULL UNIQUE
);
INSERT INTO asset_type(name)
VALUES ('host'),('code_project'),('website'),('image'),('cloud_resource');

---------------------------  business context ----------------
CREATE TABLE business_group (
  id   SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE asset_tag (
  id          SERIAL PRIMARY KEY,
  name        VARCHAR(120) NOT NULL UNIQUE,
  dyn_key     VARCHAR(64),     -- nullable => static tag
  dyn_val     VARCHAR(256)
);

CREATE TABLE sla_policy (
  id              SERIAL PRIMARY KEY,
  business_group_id INT REFERENCES business_group(id), -- NULL = global
  severity        vuln_severity NOT NULL,
  days_allowed    INTEGER       NOT NULL,
  UNIQUE(business_group_id,severity)
);

---------------------------  assets & vulns ------------------
CREATE TABLE asset (
  id              BIGSERIAL PRIMARY KEY,
  name            VARCHAR(255) NOT NULL,
  asset_type_id   INT NOT NULL REFERENCES asset_type(id),
  ip_address      INET,
  hostname        VARCHAR(255),
  business_group_id INT REFERENCES business_group(id),
  first_seen      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(name, asset_type_id)
);

CREATE TABLE asset_asset_tag (
  asset_id INT NOT NULL REFERENCES asset(id) ON DELETE CASCADE,
  tag_id   INT NOT NULL REFERENCES asset_tag(id) ON DELETE CASCADE,
  PRIMARY KEY(asset_id,tag_id)
);

CREATE TABLE vulnerability (
  id          BIGSERIAL PRIMARY KEY,
  ext_id      VARCHAR(64),
  name        VARCHAR(255) NOT NULL,
  description TEXT,
  severity    vuln_severity NOT NULL,
  UNIQUE(ext_id,name)
);

CREATE TABLE vulnerability_instance (
  id               BIGSERIAL PRIMARY KEY,
  asset_id         INT NOT NULL REFERENCES asset(id) ON DELETE CASCADE,
  vulnerability_id INT NOT NULL REFERENCES vulnerability(id) ON DELETE CASCADE,
  port             INT,
  protocol         VARCHAR(12),
  service          VARCHAR(32),
  status           finding_status NOT NULL DEFAULT 'vulnerable',
  first_seen       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
  last_seen        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
  UNIQUE(asset_id,vulnerability_id,port,service)
);

---------------------------  remediation ---------------------
CREATE TABLE campaign (
  id            BIGSERIAL PRIMARY KEY,
  name          VARCHAR(255) NOT NULL,
  origin        campaign_origin NOT NULL DEFAULT 'manual',
  state         campaign_state  NOT NULL DEFAULT 'open',
  start_date    DATE           NOT NULL DEFAULT CURRENT_DATE,
  due_date      DATE
);

CREATE TABLE campaign_vulnerability (
  campaign_id              INT NOT NULL REFERENCES campaign(id) ON DELETE CASCADE,
  vulnerability_instance_id INT NOT NULL REFERENCES vulnerability_instance(id) ON DELETE CASCADE,
  PRIMARY KEY(campaign_id,vulnerability_instance_id)
);

---------------------------  metrics -------------------------
CREATE TABLE vuln_status_change (
  id          BIGSERIAL PRIMARY KEY,
  instance_id INT NOT NULL REFERENCES vulnerability_instance(id) ON DELETE CASCADE,
  old_status  finding_status,
  new_status  finding_status NOT NULL,
  changed_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE daily_metrics_snapshot (
  snap_date        DATE          NOT NULL,
  business_group_id INT NOT NULL REFERENCES business_group(id),
  mean_ttr         NUMERIC(6,2),
  sla_breaches     INT,
  open_instances   INT,
  fixed_instances  INT,
  PRIMARY KEY(snap_date,business_group_id)
);

3.3 Indexes

CREATE INDEX idx_asset_ip        ON asset(ip_address);
CREATE INDEX idx_asset_bg        ON asset(business_group_id);
CREATE INDEX idx_instance_status ON vulnerability_instance(status);
CREATE INDEX idx_change_instance ON vuln_status_change(instance_id);

3.4 Materialised Views

views/analytics.sql (excerpt)

CREATE MATERIALIZED VIEW sla_instance_status AS
SELECT vi.id AS instance_id,
       a.business_group_id,
       v.severity,
       vi.first_seen,
       p.days_allowed,
       vi.first_seen + (p.days_allowed || ' days')::INTERVAL AS due_at,
       NOW() > vi.first_seen + (p.days_allowed || ' days')::INTERVAL AS is_overdue
FROM vulnerability_instance vi
JOIN vulnerability v ON v.id=vi.vulnerability_id
JOIN asset a ON a.id=vi.asset_id
LEFT JOIN sla_policy p ON p.business_group_id IS NOT DISTINCT FROM a.business_group_id
                        AND p.severity = v.severity
WHERE vi.status <> 'fixed';

CREATE MATERIALIZED VIEW mttr_30d AS
SELECT a.business_group_id,
       AVG(EXTRACT(EPOCH FROM (vs.fixed_at - vi.first_seen))/86400)::NUMERIC(6,2) AS mean_days_to_fix,
       COUNT(*) AS fixes
FROM (
  SELECT instance_id,
         MAX(CASE WHEN new_status='fixed' THEN changed_at END) AS fixed_at
  FROM vuln_status_change
  WHERE changed_at >= NOW() - INTERVAL '30 days'
  GROUP BY instance_id
) vs
JOIN vulnerability_instance vi ON vi.id = vs.instance_id
JOIN asset a ON a.id = vi.asset_id
WHERE vs.fixed_at IS NOT NULL
GROUP BY a.business_group_id;


⸻

4 Analytics Job (SQL)

CREATE FUNCTION nightly_rollup() RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY sla_instance_status;
  REFRESH MATERIALIZED VIEW CONCURRENTLY mttr_30d;

  INSERT INTO daily_metrics_snapshot(snap_date,business_group_id,mean_ttr,sla_breaches,
                                     open_instances,fixed_instances)
  SELECT CURRENT_DATE,
         bg_id,
         mttr.mean_days_to_fix,
         SUM(is_overdue::INT),
         COUNT(*) FILTER (WHERE status!='fixed'),
         COUNT(*) FILTER (WHERE status='fixed')
  FROM sla_instance_status sis
  CROSS JOIN LATERAL (SELECT mean_days_to_fix FROM mttr_30d m WHERE m.business_group_id=sis.business_group_id) mttr
  GROUP BY bg_id,mttr.mean_days_to_fix;
END;$$;

-- Supabase scheduled task: "call nightly_rollup();" at 02:00 Asia/Makassar


⸻

5 API Contract (complete OpenAPI 3.1)

<details>
<summary>openapi.yml (click)</summary>


openapi: 3.1.0
info:
  title: Vulcan-Clone MVP API
  version: 1.0.0
servers:
  - url: https://api.demo.local/v1
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
  schemas:
    Asset: { $ref: '#/components/schemas/_Asset' }
    # … (omitted here for brevity – full schemas mirror DB) …
paths:
  /uploads/nessus:
    post:
      summary: Upload Tenable .nessus file and trigger ETL
      security: [ bearerAuth: [] ]
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              required: [file]
              properties:
                file: { type: string, format: binary }
      responses:
        '200':
          description: Signed URL returned
          content:
            application/json:
              schema:
                type: object
                properties:
                  upload_url: { type: string, format: uri }
  /assets:
    get:
      summary: List assets
      security: [ bearerAuth: [] ]
      parameters:
        - in: query
          name: asset_type
          schema: { type: string, enum: [host,code_project,website,image,cloud_resource] }
        - in: query
          name: page
          schema: { type: integer, default: 1 }
        - in: query
          name: page_size
          schema: { type: integer, default: 50, maximum: 1000 }
      responses:
        '200': { description...