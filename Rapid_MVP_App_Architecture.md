# Rapid MVP App Architecture for Risk Radar

## Overview
This architecture uses a hybrid Supabase + Django approach for the fastest possible MVP delivery:
- **Supabase**: Database hosting, authentication, file storage, and direct integration with lovable.dev
- **Django**: Nessus parsing, business logic, Django Admin for backend management
- **lovable.dev**: Rapid UI development with built-in Supabase auth and data bindings

This approach combines Supabase's excellent frontend integration with Django's powerful backend capabilities.

**Core Features:**
- Nessus file import with full field mapping
- Asset and vulnerability management (all asset types supported)
- SLA tracking and compliance reporting
- Remediation campaign management
- Risk scoring (simplified)
- Business groups and tagging

---

## Risk Radar Full Feature Set

### Introduction
Risk Radar is a comprehensive vulnerability management platform that consolidates security data from multiple sources, prioritises risks based on business context, and tracks remediation efforts. This section describes the full feature set to provide context for our MVP implementation.

### Connectors & Data Ingestion
Risk Radar ingests data from existing tools (vulnerability scanners, SCA/SAST tools, cloud providers, ticketing systems, etc.) via "connectors". Once configured, a connector pulls assets and vulnerability findings into the platform. Risk Radar then correlates and consolidates this data (across tools and assets) to compute risk and remediation priority. Notably, Risk Radar provides a Nessus File Connector that accepts Tenable's .nessus XML reports (no direct Tenable API support). This connector lets users upload a .nessus scan file (max 300 MB, UTF-8) and automatically integrates its data into Risk Radar's views.

### Assets and Vulnerabilities Management
All ingested data is modelled as assets and vulnerabilities (findings). Assets represent systems or entities and are classified by type:
- **Hosts**: Any networked device (PCs, servers, VMs, NAS, routers, IoT devices, etc.)
- **Code Projects**: Source-code repositories (GitHub, GitLab, SAST/SCA apps)
- **Websites**: Web apps (typically identified by domain or URL)
- **Images**: Container images/registries (Docker, OCI images)
- **Cloud Resources**: Cloud assets (storage, networking, databases, etc.)

Vulnerabilities (CVE findings, scanner plugins, etc.) are linked to assets as "instances" - if the same vulnerability appears on multiple assets, each is a separate instance. Risk Radar tracks each vuln instance's details (severity, plugin ID, port, service, description, etc.) and the linkage to the asset.

### Tagging and Business Context
Risk Radar emphasises business context via Asset Tags and Business Groups:
- **Asset Tags**: Simple labels (e.g. #external-facing or #linux-server) attached to assets
- **Business Groups**: Named collections of assets (e.g. Finance, Production, or DevOps)
- **Dynamic Tags**: Rule-based tags of the form key:value (like bizowner:alice@example.com)

Business Groups segment the environment into organisational units and are used throughout Risk Radar for filtering, SLA policies, and reporting.

### Risk Prioritisation and SPR
Risk Radar computes a unified risk score for each vulnerability instance by correlating:
- Asset criticality
- Vulnerability severity
- Exploitability
- Business context

An asset's Security Posture Rating (SPR) and custom risk weights can be configured per organisation to fine-tune which issues get top priority.

### SLA Management and Reporting
Teams can define Service-Level Agreement (SLA) policies for vulnerabilities by severity. For example:
- Critical issues: 3-day SLA
- High issues: 7-day SLA
- Medium issues: 30-day SLA

Risk Radar supports different SLAs per Business Group and tracks each vulnerability instance's "time to remediation" against its SLA, marking it as "Exceeding" if not fixed in time.

### Remediation Campaigns and Automation
Every remediation effort generates a remediation campaign that:
- Tracks which vulnerabilities/assets are being addressed
- Calculates progress percentage as fixes are made
- Can be created manually or automatically via Playbook rules
- Integrates with ticketing systems (JIRA, ServiceNow, Slack, etc.)

### Dashboard and Analytics
Risk Radar provides:
- Home dashboard with risk trends and quick stats
- Pre-built widgets (Top Business Groups by Risk, SPR Compliance, etc.)
- Custom report builder (self-service analytics)
- SQL-based "magic search"
- Exportable CSVs for raw data

### API and Extensibility
The platform exposes a REST API (v1 and v2) for all operations, allowing programmatic management of assets, vulnerabilities, groups, tags, campaigns, etc. Full OpenAPI specs are provided for integration.

### Security and Administration
- Single sign-on (SSO) via SAML (Azure AD, Okta)
- Role-based access control (RBAC)
- Comprehensive audit logs

---

## MVP Feature Subset

For this rapid MVP demo, we focus on a core subset that demonstrates value while remaining buildable in 2-3 days:

### 1. Tenable Nessus File Upload
- Upload .nessus scan files (max 300 MB, UTF-8)
- Parse and ingest asset and vulnerability data
- Track upload status and import statistics

### 2. Asset & Vulnerability Data Management
- Store and display all asset types (Hosts, Code, Websites, Images, Cloud)
- Track vulnerability instances (findings) on assets
- List, filter, and search capabilities via UI/API

### 3. Business Groups & Asset Tagging
- Define tags on assets (manual for MVP)
- Create Business Groups to segment assets
- Support for future dynamic tag rules (schema ready)

### 4. SLA and Remediation Reporting
- Configure SLA policies per severity
- Track SLA compliance (compliant/at-risk/breached)
- Create and track remediation campaigns
- Export SLA compliance and campaign reports (CSV/PDF)

### What's Deferred from Full Product
- Multiple connector types (only Nessus for MVP)
- Automated playbooks and ticket creation
- Complex risk scoring algorithms (simplified for MVP)
- SSO and advanced RBAC (using Django auth)
- Real-time dashboards (using simple views)

---

## Remediation Performance Metrics Support

Based on [Vulcan Cyber's Remediation Performance Report](https://help.vulcancyber.com/en/articles/6093169-remediation-performance-report), our MVP supports the following key metrics:

### ✅ Fully Supported Metrics

| Vulcan Metric | Our Implementation | Database View/Table |
|---------------|-------------------|-------------------|
| **MTTR in Days** | Average days from first_seen to fixed_at | `mttr_summary` view |
| **MTTR by Business Group** | MTTR grouped by business group | `mttr_summary` view |
| **MTTR by Risk Level** | MTTR grouped by severity | `mttr_summary` view |
| **MTTR by Asset Type** | MTTR grouped by asset type | `mttr_by_asset_type` view |
| **Average Daily Remediation** | Average count of daily fixed findings | `daily_remediation_stats` view |
| **Remediation Capacity** | Remediated/Introduced percentage | `remediation_capacity` view |
| **MTTR Over Time** | Historical MTTR tracking | `mttr_history` table |

### 📊 How Metrics Are Calculated

1. **MTTR (Mean Time to Remediate)**
   - Formula: `AVG(fixed_at - first_seen)` in days
   - Calculated only for findings with status='fixed'
   - Grouped by various dimensions (business group, severity, asset type)

2. **Average Daily Remediation**
   - Counts findings fixed per day
   - Calculates average across all days with fixes
   - Provides period start/end dates

3. **Remediation Capacity**
   - Daily introduced: Count of new findings (by first_seen date)
   - Daily remediated: Count of fixed findings (by fixed_at date)
   - Capacity %: (Avg remediated / Avg introduced) × 100

4. **Historical Tracking**
   - Daily snapshots via `capture_mttr_snapshot()` function
   - Stores MTTR by business group and asset type
   - Enables trend analysis over time

### 🔌 API Endpoints

Access all metrics via single endpoint:
```
GET /api/findings/remediation-metrics/
```

Returns:
```json
{
  "overall_mttr": 15.5,
  "total_fixed": 1250,
  "avg_daily_remediation": 42.3,
  "remediation_capacity_percent": 85.7,
  "avg_introduced": 49.4,
  "avg_remediated": 42.3,
  "mttr_by_asset_type": [...]
}
```

### ⚠️ MVP Limitations vs Full Vulcan

- No campaign-specific metrics (campaigns are basic in MVP)
- No automated remediation tracking
- No integration with ticketing systems
- No real-time metric updates (use scheduled snapshots)

---

## Architecture Diagrams

### System Architecture Overview
```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Interface Layer                        │
├─────────────────────────────┬───────────────────────────────────────┤
│      Django Admin           │         lovable.dev                   │
│  (Backend Management)       │    (User-Facing Dashboards)          │
└─────────────────────────────┴───────────────────────────────────────┘
                    │                           │
                    └───────────┬───────────────┘
                                │
┌───────────────────────────────┴─────────────────────────────────────┐
│                        Django REST API                               │
│  /api/assets/  /api/findings/  /api/campaigns/  /api/reports/       │
└─────────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────────┐
│                        Service Layer                                 │
├──────────────┬────────────────┬─────────────────┬──────────────────┤
│   Nessus     │   Finding      │   SLA           │   Campaign       │
│   Importer   │   Service      │   Service       │   Service        │
└──────────────┴────────────────┴─────────────────┴──────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────────┐
│                     Django Models (ORM)                              │
│  Asset, Vulnerability, Finding, BusinessGroup, SLAPolicy, Campaign  │
└─────────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                               │
│            Tables, Views, Indexes, JSON Storage                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Nessus Import Data Flow
```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│              │     │                 │     │                  │
│ .nessus File │────▶│ Upload Endpoint │────▶│ NessusImporter   │
│              │     │                 │     │                  │
└──────────────┘     └─────────────────┘     └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌────────────────┐
                                              │ Parse XML      │
                                              │ Extract:       │
                                              │ - Hosts        │
                                              │ - Vulns        │
                                              │ - Findings     │
                                              └────────┬───────┘
                                                       │
                    ┌──────────────────────────────────┼──────────────────────────────────┐
                    │                                  │                                  │
                    ▼                                  ▼                                  ▼
           ┌────────────────┐                ┌─────────────────┐              ┌──────────────┐
           │ Create/Update  │                │ Create/Update   │              │   Create     │
           │    Assets      │                │ Vulnerabilities │              │  Findings    │
           └────────────────┘                └─────────────────┘              └──────────────┘
                    │                                  │                                  │
                    └──────────────────────────────────┴──────────────────────────────────┘
                                                       │
                                                       ▼
                                              ┌────────────────┐
                                              │ Update Stats   │
                                              │ Record         │
                                              └────────────────┘
```

### Entity Relationship Diagram
```
┌─────────────┐       ┌──────────────┐       ┌────────────────┐
│   Asset     │       │ Asset_Type   │       │ Business_Group │
├─────────────┤       ├──────────────┤       ├────────────────┤
│ id          │◀──────│ id           │       │ id             │
│ name        │       │ name         │       │ name           │
│ asset_type  │       └──────────────┘       │ criticality    │
│ ip_address  │                              └────────┬───────┘
│ hostname    │                                       │
│ metadata    │                                       │ Many-to-Many
└──────┬──────┘                              ┌────────┴───────┐
       │                                     │ Asset_BG       │
       │ One-to-Many                         ├────────────────┤
       │                                     │ asset_id       │
       │                                     │ bg_id          │
       ▼                                     └────────────────┘
┌─────────────┐       ┌──────────────┐
│  Finding    │       │ Vulnerability│       ┌────────────────┐
├─────────────┤       ├──────────────┤       │  SLA_Policy    │
│ id          │◀──────│ id           │       ├────────────────┤
│ asset_id    │       │ external_id  │       │ id             │
│ vuln_id     │       │ cve_id       │       │ bg_id          │
│ status      │       │ name         │       │ severity_days  │
│ port        │       │ severity     │       │ is_default     │
│ service     │       │ cvss_score   │       └────────────────┘
│ first_seen  │       └──────────────┘
│ risk_score  │
└──────┬──────┘                              ┌────────────────┐
       │                                     │   Campaign     │
       │ Many-to-Many                        ├────────────────┤
       │                                     │ id             │
       ▼                                     │ name           │
┌─────────────┐                              │ status         │
│ Campaign_   │                              │ due_date       │
│ Finding     │                              └────────────────┘
├─────────────┤
│ campaign_id │
│ finding_id  │
│ status      │
└─────────────┘
```

### SLA Tracking Flow
```
┌────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Finding   │────▶│ Check       │────▶│ Apply SLA    │────▶│ Calculate   │
│  Created   │     │ Business    │     │ Policy       │     │ Due Date    │
│            │     │ Group       │     │ (Days)       │     │             │
└────────────┘     └─────────────┘     └──────────────┘     └──────┬───────┘
                                                                    │
                                                                    ▼
                                                           ┌─────────────────┐
                                                           │ Monitor Status  │
                                                           ├─────────────────┤
                                                           │ ✓ Compliant     │
                                                           │ ⚠ At Risk       │
                                                           │ ✗ Breached      │
                                                           └─────────────────┘
                                                                    │
                                                                    ▼
                                                           ┌─────────────────┐
                                                           │ Generate        │
                                                           │ SLA Reports     │
                                                           └─────────────────┘
```

---

## Hybrid Architecture (Supabase + Django)

### Architecture Overview
```
┌─────────────────────────────────────────────────────────────────────┐
│                        lovable.dev                                   │
│  - User authentication (Supabase Auth)                              │
│  - Asset/Finding/Campaign views (Supabase direct)                   │
│  - File uploads (Supabase Storage)                                  │
│  - Real-time updates (Supabase Realtime)                           │
└─────────────────────┬───────────────────────┬───────────────────────┘
                      │                       │
           Supabase Client                Django API
              Direct                    (Complex Logic)
                      │                       │
┌─────────────────────▼───────────────────────▼───────────────────────┐
│                          Supabase                                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Database   │  │     Auth     │  │   Storage    │              │
│  │ (PostgreSQL) │  │  (Built-in)  │  │ (.nessus)    │              │
│  └─────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                      ▲                       ▲
                      │                       │
                Django Backend          Django Admin
               (Nessus Parser)        (Staff Interface)
```

### Data Flow
1. **User Auth**: lovable.dev → Supabase Auth (no Django needed)
2. **File Upload**: lovable.dev → Supabase Storage → Django parser → Supabase DB
3. **CRUD Operations**: lovable.dev → Supabase DB (direct, no Django)
4. **Complex Logic**: lovable.dev → Django API → Supabase DB
5. **Admin Operations**: Django Admin → Supabase DB

### Key Integration Points

#### 1. Supabase Database Configuration
```python
# settings.py - Django connects to Supabase PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'db.xxxxxxxxxxxx.supabase.co',
        'PORT': '5432',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'your-supabase-password',
    }
}
```

#### 2. Supabase Auth Integration
```javascript
// lovable.dev - Built-in Supabase auth
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

// Login/signup handled by lovable.dev components
```

#### 3. File Upload Flow
```javascript
// lovable.dev - Upload to Supabase Storage
const { data, error } = await supabase.storage
  .from('nessus-files')
  .upload(`uploads/${file.name}`, file)

// Trigger Django parser via API
await fetch('/api/parse-nessus/', {
  method: 'POST',
  body: JSON.stringify({ file_path: data.path })
})
```

#### 4. Django Parser Service
```python
# views.py - Django handles complex parsing
@api_view(['POST'])
def parse_nessus(request):
    file_path = request.data['file_path']
    
    # Download from Supabase Storage
    supabase_url = settings.SUPABASE_URL
    file_url = f"{supabase_url}/storage/v1/object/public/nessus-files/{file_path}"
    
    # Parse and insert directly to Supabase DB
    importer = NessusImporter()
    stats = importer.import_from_url(file_url)
    
    return Response(stats)
```

### Row Level Security (RLS) Setup
```sql
-- Enable RLS for multi-tenant security
ALTER TABLE asset ENABLE ROW LEVEL SECURITY;
ALTER TABLE finding ENABLE ROW LEVEL SECURITY;
ALTER TABLE remediation_campaign ENABLE ROW LEVEL SECURITY;

-- Policies for authenticated users
CREATE POLICY "Users can view all assets" ON asset
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Users can manage their campaigns" ON remediation_campaign
    FOR ALL USING (auth.uid() = created_by OR auth.role() = 'admin');
```

### Advantages of Hybrid Approach
1. **Faster Auth Setup**: lovable.dev + Supabase Auth = instant login/signup pages
2. **Real-time Updates**: Supabase subscriptions for live dashboards
3. **Direct Database Access**: lovable.dev can query without Django for simple CRUD
4. **Django Admin**: Still get free backend management interface
5. **Python for Complex Logic**: Nessus parsing stays in Python
6. **Hosted Database**: No database management needed

---

## 1. Database Schema (PostgreSQL via Supabase)

### Modified Schema for Supabase
```sql
-- Add auth tracking to relevant tables
CREATE TABLE asset (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    asset_type_id INTEGER NOT NULL REFERENCES asset_type(id),
    ip_address INET NULL,
    hostname VARCHAR(255) NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)  -- Supabase auth integration
);

-- Insert default asset types
INSERT INTO asset_type (name) VALUES 
    ('Host'), ('Code'), ('Website'), ('Image'), ('Cloud');

-- Vulnerabilities
CREATE TABLE vulnerability (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100) NULL,  -- Plugin ID from Nessus
    cve_id VARCHAR(50) NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Info', 'Low', 'Medium', 'High', 'Critical')),
    cvss_score DECIMAL(3,1) NULL,
    solution TEXT,
    metadata JSONB DEFAULT '{}'
);

CREATE UNIQUE INDEX idx_vuln_external ON vulnerability(external_id) WHERE external_id IS NOT NULL;
CREATE INDEX idx_vuln_severity ON vulnerability(severity);

-- Findings (vulnerability instances on assets)
CREATE TABLE finding (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES asset(id) ON DELETE CASCADE,
    vulnerability_id INTEGER NOT NULL REFERENCES vulnerability(id),
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'fixed', 'accepted', 'false_positive')),
    port INTEGER NULL,
    protocol VARCHAR(20) NULL,
    service VARCHAR(100) NULL,
    plugin_output TEXT,
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    fixed_at TIMESTAMPTZ NULL,
    risk_score DECIMAL(5,2) DEFAULT 0,
    metadata JSONB DEFAULT '{}'
);

CREATE UNIQUE INDEX idx_finding_unique ON finding(asset_id, vulnerability_id, port, protocol, service);
CREATE INDEX idx_finding_status ON finding(status, risk_score DESC);

-- Business Groups
CREATE TABLE business_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    criticality_score INTEGER DEFAULT 5 CHECK (criticality_score BETWEEN 1 AND 10)
);

-- Asset to Business Group mapping
CREATE TABLE asset_business_group (
    asset_id INTEGER NOT NULL REFERENCES asset(id) ON DELETE CASCADE,
    business_group_id INTEGER NOT NULL REFERENCES business_group(id) ON DELETE CASCADE,
    PRIMARY KEY (asset_id, business_group_id)
);

-- Asset Tags
CREATE TABLE asset_tag (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    tag_type VARCHAR(20) DEFAULT 'static' CHECK (tag_type IN ('static', 'dynamic')),
    tag_key VARCHAR(100) NULL,  -- For dynamic tags like 'owner:email'
    tag_value VARCHAR(255) NULL
);

CREATE UNIQUE INDEX idx_tag_name ON asset_tag(name);

-- Asset to Tag mapping
CREATE TABLE asset_asset_tag (
    asset_id INTEGER NOT NULL REFERENCES asset(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES asset_tag(id) ON DELETE CASCADE,
    PRIMARY KEY (asset_id, tag_id)
);

-- SLA Policies
CREATE TABLE sla_policy (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    business_group_id INTEGER REFERENCES business_group(id),
    is_default BOOLEAN DEFAULT FALSE,
    severity_days JSONB NOT NULL DEFAULT '{
        "Critical": 1,
        "High": 7,
        "Medium": 30,
        "Low": 90,
        "Info": 365
    }'
);

-- Remediation Campaigns
CREATE TABLE remediation_campaign (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    due_date DATE NULL,
    completed_at TIMESTAMPTZ NULL,
    created_by UUID REFERENCES auth.users(id)  -- For RLS policies
);

-- Campaign to Finding mapping
CREATE TABLE campaign_finding (
    campaign_id INTEGER NOT NULL REFERENCES remediation_campaign(id) ON DELETE CASCADE,
    finding_id INTEGER NOT NULL REFERENCES finding(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed')),
    PRIMARY KEY (campaign_id, finding_id)
);

-- Nessus Upload tracking
CREATE TABLE nessus_upload (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER,
    file_path TEXT,  -- Supabase Storage path
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ NULL,
    uploaded_by UUID REFERENCES auth.users(id),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT NULL,
    stats JSONB DEFAULT '{}'
);
```

### Helper Views for Rapid Development
```sql
-- SLA Status View (for quick reporting)
CREATE OR REPLACE VIEW sla_status AS
WITH policy_assignments AS (
    SELECT 
        f.id as finding_id,
        f.vulnerability_id,
        f.asset_id,
        f.first_seen,
        f.status,
        v.severity,
        COALESCE(sp.severity_days->v.severity, sp_default.severity_days->v.severity)::INTEGER as sla_days
    FROM finding f
    JOIN vulnerability v ON f.vulnerability_id = v.id
    LEFT JOIN asset_business_group abg ON f.asset_id = abg.asset_id
    LEFT JOIN sla_policy sp ON sp.business_group_id = abg.business_group_id AND sp.is_default = FALSE
    LEFT JOIN sla_policy sp_default ON sp_default.is_default = TRUE
    WHERE f.status = 'open'
)
SELECT 
    finding_id,
    vulnerability_id,
    asset_id,
    severity,
    sla_days,
    first_seen + (sla_days || ' days')::INTERVAL as due_date,
    CASE 
        WHEN NOW() > first_seen + (sla_days || ' days')::INTERVAL THEN 'breached'
        WHEN NOW() > first_seen + ((sla_days * 0.8) || ' days')::INTERVAL THEN 'at_risk'
        ELSE 'compliant'
    END as sla_status,
    EXTRACT(days FROM (first_seen + (sla_days || ' days')::INTERVAL - NOW()))::INTEGER as days_remaining
FROM policy_assignments;

-- MTTR (Mean Time To Remediate) View
CREATE OR REPLACE VIEW mttr_summary AS
SELECT 
    bg.name as business_group,
    v.severity,
    COUNT(f.id) as fixed_count,
    AVG(EXTRACT(days FROM (f.fixed_at - f.first_seen)))::DECIMAL(10,2) as avg_days_to_fix,
    MIN(EXTRACT(days FROM (f.fixed_at - f.first_seen)))::INTEGER as min_days,
    MAX(EXTRACT(days FROM (f.fixed_at - f.first_seen)))::INTEGER as max_days
FROM finding f
JOIN vulnerability v ON f.vulnerability_id = v.id
JOIN asset a ON f.asset_id = a.id
LEFT JOIN asset_business_group abg ON a.id = abg.asset_id
LEFT JOIN business_group bg ON abg.business_group_id = bg.id
WHERE f.status = 'fixed' AND f.fixed_at IS NOT NULL
GROUP BY bg.name, v.severity;

-- Average Daily Remediation View
CREATE OR REPLACE VIEW daily_remediation_stats AS
WITH daily_counts AS (
    SELECT 
        DATE(fixed_at) as fix_date,
        COUNT(*) as daily_fixed
    FROM finding
    WHERE status = 'fixed' 
    AND fixed_at IS NOT NULL
    GROUP BY DATE(fixed_at)
)
SELECT 
    AVG(daily_fixed)::DECIMAL(10,2) as avg_daily_remediation,
    MIN(fix_date) as period_start,
    MAX(fix_date) as period_end,
    COUNT(DISTINCT fix_date) as days_with_fixes
FROM daily_counts;

-- Remediation Capacity View
CREATE OR REPLACE VIEW remediation_capacity AS
WITH daily_stats AS (
    -- Count newly introduced findings per day
    SELECT 
        DATE(first_seen) as date,
        COUNT(*) as introduced,
        0 as remediated
    FROM finding
    GROUP BY DATE(first_seen)
    
    UNION ALL
    
    -- Count remediated findings per day
    SELECT 
        DATE(fixed_at) as date,
        0 as introduced,
        COUNT(*) as remediated
    FROM finding
    WHERE status = 'fixed' AND fixed_at IS NOT NULL
    GROUP BY DATE(fixed_at)
),
aggregated AS (
    SELECT 
        date,
        SUM(introduced) as daily_introduced,
        SUM(remediated) as daily_remediated
    FROM daily_stats
    GROUP BY date
),
averages AS (
    SELECT 
        AVG(daily_introduced) as avg_introduced,
        AVG(daily_remediated) as avg_remediated
    FROM aggregated
)
SELECT 
    avg_introduced,
    avg_remediated,
    CASE 
        WHEN avg_introduced > 0 
        THEN ROUND((avg_remediated / avg_introduced) * 100, 2)
        ELSE 100
    END as remediation_capacity_percent
FROM averages;

-- MTTR by Asset Type View
CREATE OR REPLACE VIEW mttr_by_asset_type AS
SELECT 
    at.name as asset_type,
    v.severity,
    COUNT(f.id) as fixed_count,
    AVG(EXTRACT(days FROM (f.fixed_at - f.first_seen)))::DECIMAL(10,2) as avg_days_to_fix,
    MIN(EXTRACT(days FROM (f.fixed_at - f.first_seen)))::INTEGER as min_days,
    MAX(EXTRACT(days FROM (f.fixed_at - f.first_seen)))::INTEGER as max_days
FROM finding f
JOIN vulnerability v ON f.vulnerability_id = v.id
JOIN asset a ON f.asset_id = a.id
JOIN asset_type at ON a.asset_type_id = at.id
WHERE f.status = 'fixed' AND f.fixed_at IS NOT NULL
GROUP BY at.name, v.severity;

-- Historical MTTR Tracking Table
CREATE TABLE mttr_history (
    id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    business_group VARCHAR(100),
    asset_type VARCHAR(50),
    severity VARCHAR(20),
    mttr_days DECIMAL(10,2),
    fixed_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mttr_history_date ON mttr_history(snapshot_date);
CREATE INDEX idx_mttr_history_group ON mttr_history(business_group, severity);

-- Function to capture MTTR snapshot
CREATE OR REPLACE FUNCTION capture_mttr_snapshot() RETURNS void AS $$
BEGIN
    -- Capture by business group
    INSERT INTO mttr_history (snapshot_date, business_group, severity, mttr_days, fixed_count)
    SELECT CURRENT_DATE, business_group, severity, avg_days_to_fix, fixed_count
    FROM mttr_summary;
    
    -- Capture by asset type
    INSERT INTO mttr_history (snapshot_date, asset_type, severity, mttr_days, fixed_count)
    SELECT CURRENT_DATE, asset_type, severity, avg_days_to_fix, fixed_count
    FROM mttr_by_asset_type;
END;
$$ LANGUAGE plpgsql;
```

---

## 2. Django Models (Simplified for Rapid Development)

```python
# models.py
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

class AssetType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'asset_type'
    
    def __str__(self):
        return self.name

class Asset(models.Model):
    name = models.CharField(max_length=255)
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    hostname = models.CharField(max_length=255, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'asset'
        unique_together = ['name', 'asset_type']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.asset_type.name})"

class Vulnerability(models.Model):
    SEVERITY_CHOICES = [
        ('Info', 'Info'),
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    
    external_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    cve_id = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    cvss_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    solution = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'vulnerability'
        ordering = ['-severity', '-cvss_score']
    
    def __str__(self):
        return f"{self.external_id or self.cve_id}: {self.name[:50]}"

class Finding(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('fixed', 'Fixed'),
        ('accepted', 'Risk Accepted'),
        ('false_positive', 'False Positive'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='findings')
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.CASCADE, related_name='findings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    port = models.IntegerField(null=True, blank=True)
    protocol = models.CharField(max_length=20, null=True, blank=True)
    service = models.CharField(max_length=100, null=True, blank=True)
    plugin_output = models.TextField(blank=True)
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    fixed_at = models.DateTimeField(null=True, blank=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'finding'
        unique_together = ['asset', 'vulnerability', 'port', 'protocol', 'service']
        ordering = ['-risk_score', '-vulnerability__severity']
    
    def __str__(self):
        return f"{self.vulnerability.name} on {self.asset.name}"
    
    def save(self, *args, **kwargs):
        # Simple risk calculation for MVP
        if not self.risk_score:
            severity_scores = {'Critical': 10, 'High': 8, 'Medium': 5, 'Low': 2, 'Info': 1}
            self.risk_score = severity_scores.get(self.vulnerability.severity, 0) * 10
        
        # Auto-set fixed_at when status changes to fixed
        if self.status == 'fixed' and not self.fixed_at:
            self.fixed_at = timezone.now()
        
        super().save(*args, **kwargs)

class BusinessGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    criticality_score = models.IntegerField(default=5, 
        help_text="1-10, where 10 is most critical")
    assets = models.ManyToManyField(Asset, related_name='business_groups', blank=True)
    
    class Meta:
        db_table = 'business_group'
    
    def __str__(self):
        return self.name

class SLAPolicy(models.Model):
    name = models.CharField(max_length=100)
    business_group = models.ForeignKey(BusinessGroup, on_delete=models.CASCADE, 
                                     null=True, blank=True, related_name='sla_policies')
    is_default = models.BooleanField(default=False)
    severity_days = models.JSONField(default=dict, 
        help_text='{"Critical": 1, "High": 7, "Medium": 30, "Low": 90, "Info": 365}')
    
    class Meta:
        db_table = 'sla_policy'
        verbose_name = 'SLA Policy'
        verbose_name_plural = 'SLA Policies'
    
    def __str__(self):
        return f"{self.name} ({'Default' if self.is_default else self.business_group})"

class RemediationCampaign(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    findings = models.ManyToManyField(Finding, through='CampaignFinding', related_name='campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'remediation_campaign'
    
    def __str__(self):
        return self.name
    
    @property
    def progress_percentage(self):
        total = self.findings.count()
        if total == 0:
            return 0
        fixed = self.findings.filter(status='fixed').count()
        return round((fixed / total) * 100, 2)

class CampaignFinding(models.Model):
    campaign = models.ForeignKey(RemediationCampaign, on_delete=models.CASCADE)
    finding = models.ForeignKey(Finding, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    
    class Meta:
        db_table = 'campaign_finding'
        unique_together = ['campaign', 'finding']

class NessusUpload(models.Model):
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(null=True, blank=True)
    file_path = models.TextField()  # Supabase Storage path
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    error_message = models.TextField(blank=True)
    stats = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'nessus_upload'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} ({self.status})"
```

---

## 3. Nessus Import Implementation

### Field Mapping from .nessus to Models
```python
# nessus_import.py
import xml.etree.ElementTree as ET
from django.db import transaction
from datetime import datetime

class NessusImporter:
    """
    Maps Nessus XML fields to our data model
    Based on Tenable .nessus file format
    """
    
    # Nessus severity to our severity mapping
    SEVERITY_MAP = {
        '0': 'Info',
        '1': 'Low',
        '2': 'Medium',
        '3': 'High',
        '4': 'Critical'
    }
    
    # Core field mappings from Nessus XML
    FIELD_MAPPINGS = {
        # Asset fields
        'host-ip': 'ip_address',
        'host-fqdn': 'hostname',
        'operating-system': 'metadata.os',
        'mac-address': 'metadata.mac_address',
        
        # Vulnerability fields
        'pluginID': 'external_id',
        'pluginName': 'name',
        'description': 'description',
        'solution': 'solution',
        'risk_factor': 'severity',
        'cvss3_base_score': 'cvss_score',
        'cve': 'cve_id',
        
        # Finding fields
        'port': 'port',
        'protocol': 'protocol',
        'svc_name': 'service',
        'plugin_output': 'plugin_output'
    }
    
    def import_file(self, file_path, upload_record=None):
        """Import a .nessus file"""
        stats = {'assets': 0, 'vulnerabilities': 0, 'findings': 0, 'errors': []}
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Process each ReportHost (asset)
            for report_host in root.findall('.//ReportHost'):
                try:
                    asset = self._process_host(report_host)
                    stats['assets'] += 1
                    
                    # Process each ReportItem (vulnerability/finding)
                    for report_item in report_host.findall('ReportItem'):
                        vuln, finding = self._process_item(report_item, asset)
                        if vuln:
                            stats['vulnerabilities'] += 1
                        if finding:
                            stats['findings'] += 1
                            
                except Exception as e:
                    stats['errors'].append(f"Error processing host: {str(e)}")
                    
        except Exception as e:
            stats['errors'].append(f"Error parsing file: {str(e)}")
        
        # Update upload record
        if upload_record:
            upload_record.status = 'completed' if not stats['errors'] else 'failed'
            upload_record.processed_at = timezone.now()
            upload_record.stats = stats
            upload_record.error_message = '\n'.join(stats['errors'])
            upload_record.save()
        
        return stats
    
    @transaction.atomic
    def _process_host(self, report_host):
        """Process a ReportHost element into an Asset"""
        # Extract host properties
        host_props = {}
        for tag in report_host.findall('.//HostProperties/tag'):
            name = tag.get('name')
            value = tag.text
            if name and value:
                host_props[name] = value
        
        # Create or update asset
        ip = host_props.get('host-ip', report_host.get('name'))
        hostname = host_props.get('host-fqdn') or host_props.get('hostname')
        
        asset_data = {
            'name': hostname or ip,
            'ip_address': ip if self._is_valid_ip(ip) else None,
            'hostname': hostname,
            'asset_type': AssetType.objects.get_or_create(name='Host')[0],
            'metadata': {
                'os': host_props.get('operating-system', ''),
                'mac_address': host_props.get('mac-address', ''),
                'netbios_name': host_props.get('netbios-name', ''),
                'system_type': host_props.get('system-type', ''),
                'last_scan': datetime.now().isoformat()
            }
        }
        
        asset, created = Asset.objects.update_or_create(
            name=asset_data['name'],
            asset_type=asset_data['asset_type'],
            defaults=asset_data
        )
        
        return asset
    
    @transaction.atomic
    def _process_item(self, report_item, asset):
        """Process a ReportItem into Vulnerability and Finding"""
        # Extract vulnerability data
        plugin_id = report_item.get('pluginID')
        severity_num = report_item.get('severity', '0')
        
        vuln_data = {
            'external_id': plugin_id,
            'name': report_item.get('pluginName', 'Unknown'),
            'description': self._get_text(report_item, 'description'),
            'solution': self._get_text(report_item, 'solution'),
            'severity': self.SEVERITY_MAP.get(severity_num, 'Info'),
            'metadata': {
                'plugin_family': report_item.get('pluginFamily', ''),
                'plugin_type': self._get_text(report_item, 'plugin_type'),
                'plugin_publication_date': self._get_text(report_item, 'plugin_publication_date'),
                'plugin_modification_date': self._get_text(report_item, 'plugin_modification_date')
            }
        }
        
        # Extract CVE if present
        cve = self._get_text(report_item, 'cve')
        if cve:
            vuln_data['cve_id'] = cve.split(',')[0].strip()  # Take first CVE if multiple
        
        # Extract CVSS score
        cvss3 = self._get_text(report_item, 'cvss3_base_score')
        cvss = self._get_text(report_item, 'cvss_base_score')
        vuln_data['cvss_score'] = float(cvss3 or cvss or 0)
        
        # Create or update vulnerability
        vuln, created = Vulnerability.objects.update_or_create(
            external_id=plugin_id,
            defaults=vuln_data
        )
        
        # Create finding
        finding_data = {
            'asset': asset,
            'vulnerability': vuln,
            'port': int(report_item.get('port', 0)),
            'protocol': report_item.get('protocol', ''),
            'service': report_item.get('svc_name', ''),
            'plugin_output': self._get_text(report_item, 'plugin_output'),
            'last_seen': timezone.now(),
            'metadata': {
                'exploit_available': self._get_text(report_item, 'exploit_available') == 'true',
                'exploit_ease': self._get_text(report_item, 'exploit_ease'),
                'patch_publication_date': self._get_text(report_item, 'patch_publication_date')
            }
        }
        
        finding, created = Finding.objects.update_or_create(
            asset=asset,
            vulnerability=vuln,
            port=finding_data['port'],
            protocol=finding_data['protocol'],
            service=finding_data['service'],
            defaults=finding_data
        )
        
        if not created:
            finding.last_seen = timezone.now()
            finding.save()
        
        return vuln, finding
    
    def _get_text(self, element, tag_name):
        """Safely get text from XML element"""
        tag = element.find(tag_name)
        return tag.text if tag is not None and tag.text else ''
    
    def _is_valid_ip(self, ip):
        """Check if string is valid IP"""
        try:
            import ipaddress
            ipaddress.ip_address(ip)
            return True
        except:
            return False
```

---

## 4. Admin Configuration for Rapid Development

```python
# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from .models import *

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'asset_type', 'ip_address', 'finding_count', 'critical_count', 'high_count']
    list_filter = ['asset_type', 'business_groups']
    search_fields = ['name', 'ip_address', 'hostname']
    filter_horizontal = ['business_groups']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _finding_count=Count('findings'),
            _critical_count=Count('findings', filter=Q(findings__vulnerability__severity='Critical')),
            _high_count=Count('findings', filter=Q(findings__vulnerability__severity='High'))
        )
    
    def finding_count(self, obj):
        return obj._finding_count
    finding_count.admin_order_field = '_finding_count'
    
    def critical_count(self, obj):
        if obj._critical_count:
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', obj._critical_count)
        return 0
    critical_count.admin_order_field = '_critical_count'
    
    def high_count(self, obj):
        if obj._high_count:
            return format_html('<span style="color: orange; font-weight: bold;">{}</span>', obj._high_count)
        return 0
    high_count.admin_order_field = '_high_count'

@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'severity_badge', 'status', 'risk_score', 'port', 'service', 'sla_status_badge', 'age_days']
    list_filter = ['status', 'vulnerability__severity', 'asset__asset_type']
    search_fields = ['vulnerability__name', 'asset__name', 'vulnerability__cve_id']
    readonly_fields = ['first_seen', 'last_seen', 'fixed_at', 'risk_score']
    raw_id_fields = ['asset', 'vulnerability']
    
    def severity_badge(self, obj):
        colors = {
            'Critical': 'red',
            'High': 'orange',
            'Medium': 'yellow',
            'Low': 'blue',
            'Info': 'gray'
        }
        color = colors.get(obj.vulnerability.severity, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.vulnerability.severity
        )
    severity_badge.short_description = 'Severity'
    
    def sla_status_badge(self, obj):
        # Quick SLA check (simplified for admin)
        if obj.status != 'open':
            return '-'
        
        days_open = (timezone.now() - obj.first_seen).days
        severity_limits = {'Critical': 1, 'High': 7, 'Medium': 30, 'Low': 90, 'Info': 365}
        limit = severity_limits.get(obj.vulnerability.severity, 90)
        
        if days_open > limit:
            return format_html('<span style="color: red;">⚠️ Breached ({}d)</span>', days_open)
        elif days_open > limit * 0.8:
            return format_html('<span style="color: orange;">⚠️ At Risk ({}d)</span>', days_open)
        else:
            return format_html('<span style="color: green;">✓ OK ({}d)</span>', days_open)
    sla_status_badge.short_description = 'SLA Status'
    
    def age_days(self, obj):
        return (timezone.now() - obj.first_seen).days
    age_days.short_description = 'Age (days)'
    
    actions = ['mark_as_fixed', 'create_campaign']
    
    def mark_as_fixed(self, request, queryset):
        count = queryset.filter(status='open').update(status='fixed', fixed_at=timezone.now())
        self.message_user(request, f'{count} findings marked as fixed')
    mark_as_fixed.short_description = 'Mark selected findings as fixed'
    
    def create_campaign(self, request, queryset):
        # Create a new campaign with selected findings
        campaign = RemediationCampaign.objects.create(
            name=f'Campaign - {timezone.now().strftime("%Y-%m-%d %H:%M")}',
            description=f'Created from admin for {queryset.count()} findings'
        )
        campaign.findings.set(queryset)
        
        url = reverse('admin:core_remediationcampaign_change', args=[campaign.id])
        self.message_user(request, format_html('Campaign created: <a href="{}">View campaign</a>', url))
    create_campaign.short_description = 'Create remediation campaign'

@admin.register(RemediationCampaign)
class RemediationCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'finding_count', 'progress_bar', 'created_at', 'due_date']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['findings']
    readonly_fields = ['created_at', 'completed_at', 'progress_percentage']
    
    def finding_count(self, obj):
        return obj.findings.count()
    finding_count.short_description = 'Findings'
    
    def progress_bar(self, obj):
        percent = obj.progress_percentage
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border: 1px solid #ccc;">'
            '<div style="width: {}px; background-color: #4CAF50; height: 20px;"></div>'
            '</div> {}%',
            percent, percent
        )
    progress_bar.short_description = 'Progress'

# Register remaining models with basic admin
admin.site.register(AssetType)
admin.site.register(Vulnerability)
admin.site.register(BusinessGroup)
admin.site.register(SLAPolicy)

# Add custom admin action for Nessus import
@admin.register(NessusUpload)
class NessusUploadAdmin(admin.ModelAdmin):
    list_display = ['filename', 'uploaded_at', 'status', 'stats_summary']
    list_filter = ['status', 'uploaded_at']
    readonly_fields = ['uploaded_at', 'processed_at', 'stats', 'error_message']
    
    def stats_summary(self, obj):
        if obj.stats:
            return f"Assets: {obj.stats.get('assets', 0)}, Findings: {obj.stats.get('findings', 0)}"
        return '-'
    stats_summary.short_description = 'Import Stats'
    
    actions = ['process_upload']
    
    def process_upload(self, request, queryset):
        for upload in queryset.filter(status='pending'):
            # In production, this would be an async task
            importer = NessusImporter()
            importer.import_file(upload.file_path, upload)
        self.message_user(request, f'Processing {queryset.count()} uploads')
    process_upload.short_description = 'Process selected uploads'
```

---

## 5. Django REST Framework API

```python
# serializers.py
from rest_framework import serializers
from .models import *

class AssetSerializer(serializers.ModelSerializer):
    asset_type_name = serializers.CharField(source='asset_type.name', read_only=True)
    finding_count = serializers.IntegerField(read_only=True)
    critical_findings = serializers.IntegerField(read_only=True)
    business_groups = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Asset
        fields = '__all__'

class VulnerabilitySerializer(serializers.ModelSerializer):
    finding_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Vulnerability
        fields = '__all__'

class FindingSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    vulnerability_name = serializers.CharField(source='vulnerability.name', read_only=True)
    severity = serializers.CharField(source='vulnerability.severity', read_only=True)
    sla_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Finding
        fields = '__all__'
    
    def get_sla_status(self, obj):
        # Simple SLA calculation
        if obj.status != 'open':
            return 'N/A'
        
        days_open = (timezone.now() - obj.first_seen).days
        severity_limits = {'Critical': 1, 'High': 7, 'Medium': 30, 'Low': 90, 'Info': 365}
        limit = severity_limits.get(obj.vulnerability.severity, 90)
        
        if days_open > limit:
            return 'breached'
        elif days_open > limit * 0.8:
            return 'at_risk'
        return 'compliant'

class RemediationCampaignSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()
    finding_count = serializers.IntegerField(source='findings.count', read_only=True)
    
    class Meta:
        model = RemediationCampaign
        fields = '__all__'

# views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.annotate(
        finding_count=Count('findings'),
        critical_findings=Count('findings', filter=Q(findings__vulnerability__severity='Critical'))
    )
    serializer_class = AssetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset_type', 'business_groups']
    search_fields = ['name', 'ip_address', 'hostname']
    ordering_fields = ['name', 'finding_count', 'critical_findings']

class FindingViewSet(viewsets.ModelViewSet):
    queryset = Finding.objects.select_related('asset', 'vulnerability')
    serializer_class = FindingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'vulnerability__severity', 'asset']
    search_fields = ['vulnerability__name', 'asset__name']
    ordering_fields = ['risk_score', 'first_seen']
    
    @action(detail=False, methods=['get'])
    def sla_report(self, request):
        """Generate SLA compliance report"""
        # Using raw SQL for performance
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    sla_status,
                    severity,
                    COUNT(*) as count
                FROM sla_status
                GROUP BY sla_status, severity
                ORDER BY 
                    CASE severity 
                        WHEN 'Critical' THEN 1 
                        WHEN 'High' THEN 2 
                        WHEN 'Medium' THEN 3 
                        WHEN 'Low' THEN 4 
                        ELSE 5 
                    END,
                    sla_status
            """)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'sla_status': row[0],
                    'severity': row[1],
                    'count': row[2]
                })
        
        return Response({'sla_summary': results})
    
    @action(detail=False, methods=['get'])
    def mttr_report(self, request):
        """Generate MTTR report"""
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM mttr_summary")
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response({'mttr_summary': results})

    @action(detail=False, methods=['get'])
    def remediation_metrics(self, request):
        """Get comprehensive remediation performance metrics"""
        from django.db import connection
        
        metrics = {}
        
        with connection.cursor() as cursor:
            # Get average daily remediation
            cursor.execute("SELECT * FROM daily_remediation_stats")
            daily_stats = cursor.fetchone()
            if daily_stats:
                metrics['avg_daily_remediation'] = float(daily_stats[0])
                metrics['period_start'] = daily_stats[1]
                metrics['period_end'] = daily_stats[2]
                metrics['days_with_fixes'] = daily_stats[3]
            
            # Get remediation capacity
            cursor.execute("SELECT * FROM remediation_capacity")
            capacity = cursor.fetchone()
            if capacity:
                metrics['avg_introduced'] = float(capacity[0]) if capacity[0] else 0
                metrics['avg_remediated'] = float(capacity[1]) if capacity[1] else 0
                metrics['remediation_capacity_percent'] = float(capacity[2]) if capacity[2] else 0
            
            # Get MTTR by asset type
            cursor.execute("SELECT * FROM mttr_by_asset_type ORDER BY asset_type, severity")
            columns = [col[0] for col in cursor.description]
            metrics['mttr_by_asset_type'] = [
                dict(zip(columns, row)) for row in cursor.fetchall()
            ]
            
            # Get overall MTTR (no grouping)
            cursor.execute("""
                SELECT 
                    AVG(EXTRACT(days FROM (fixed_at - first_seen)))::DECIMAL(10,2) as overall_mttr,
                    COUNT(*) as total_fixed
                FROM finding
                WHERE status = 'fixed' AND fixed_at IS NOT NULL
            """)
            overall = cursor.fetchone()
            if overall:
                metrics['overall_mttr'] = float(overall[0]) if overall[0] else 0
                metrics['total_fixed'] = overall[1]
        
        return Response(metrics)

class RemediationCampaignViewSet(viewsets.ModelViewSet):
    queryset = RemediationCampaign.objects.all()
    serializer_class = RemediationCampaignSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'due_date']

# urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('assets', AssetViewSet)
router.register('vulnerabilities', VulnerabilityViewSet)
router.register('findings', FindingViewSet)
router.register('campaigns', RemediationCampaignViewSet)

urlpatterns = router.urls
```

---

## 6. Reporting Implementation

```python
# reports.py
import csv
from django.http import HttpResponse
from django.db import connection
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class ReportGenerator:
    """Generate CSV and PDF reports"""
    
    @staticmethod
    def sla_compliance_csv(response):
        """Generate SLA compliance CSV"""
        writer = csv.writer(response)
        writer.writerow(['Asset', 'Vulnerability', 'Severity', 'First Seen', 'Due Date', 
                        'Days Remaining', 'SLA Status'])
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    a.name as asset_name,
                    v.name as vuln_name,
                    s.severity,
                    s.first_seen,
                    s.due_date,
                    s.days_remaining,
                    s.sla_status
                FROM sla_status s
                JOIN finding f ON s.finding_id = f.id
                JOIN asset a ON s.asset_id = a.id
                JOIN vulnerability v ON s.vulnerability_id = v.id
                ORDER BY 
                    s.sla_status DESC,
                    s.days_remaining ASC
            """)
            
            for row in cursor.fetchall():
                writer.writerow(row)
        
        return response
    
    @staticmethod
    def remediation_campaign_pdf(campaign, response):
        """Generate campaign PDF report"""
        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph(f"Remediation Campaign: {campaign.name}", styles['Title']))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph(f"Status: {campaign.status}", styles['Normal']))
        story.append(Paragraph(f"Progress: {campaign.progress_percentage}%", styles['Normal']))
        story.append(Paragraph(f"Total Findings: {campaign.findings.count()}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Findings table
        data = [['Asset', 'Vulnerability', 'Severity', 'Status', 'Port/Service']]
        
        for finding in campaign.findings.select_related('asset', 'vulnerability'):
            data.append([
                finding.asset.name[:30],
                finding.vulnerability.name[:40],
                finding.vulnerability.severity,
                finding.status,
                f"{finding.port}/{finding.service}" if finding.port else 'N/A'
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
        
        return response

# Add to views.py or create report_views.py
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def download_sla_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sla_compliance_report.csv"'
    
    ReportGenerator.sla_compliance_csv(response)
    return response

def download_campaign_report(request, campaign_id):
    campaign = get_object_or_404(RemediationCampaign, id=campaign_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="campaign_{campaign_id}_report.pdf"'
    
    ReportGenerator.remediation_campaign_pdf(campaign, response)
    return response
```

---

## 7. Management Commands for Batch Operations

```python
# management/commands/import_nessus.py
from django.core.management.base import BaseCommand
from django.utils import timezone
import os
from ...models import NessusUpload
from ...nessus_import import NessusImporter

class Command(BaseCommand):
    help = 'Import Nessus files from a directory'
    
    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory containing .nessus files')
        parser.add_argument('--batch-size', type=int, default=10, help='Number of files to process in one batch')
    
    def handle(self, *args, **options):
        directory = options['directory']
        batch_size = options['batch_size']
        
        # Find all .nessus files
        nessus_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.nessus'):
                    nessus_files.append(os.path.join(root, file))
        
        self.stdout.write(f'Found {len(nessus_files)} .nessus files')
        
        # Process in batches
        importer = NessusImporter()
        total_stats = {'assets': 0, 'vulnerabilities': 0, 'findings': 0}
        
        for i in range(0, len(nessus_files), batch_size):
            batch = nessus_files[i:i+batch_size]
            self.stdout.write(f'\nProcessing batch {i//batch_size + 1} ({len(batch)} files)...')
            
            for file_path in batch:
                self.stdout.write(f'  Importing {os.path.basename(file_path)}...')
                
                # Create upload record
                upload = NessusUpload.objects.create(
                    filename=os.path.basename(file_path),
                    file_size=os.path.getsize(file_path),
                    status='processing'
                )
                
                # Import file
                stats = importer.import_file(file_path, upload)
                
                # Update totals
                total_stats['assets'] += stats['assets']
                total_stats['vulnerabilities'] += stats['vulnerabilities']
                total_stats['findings'] += stats['findings']
                
                if stats['errors']:
                    self.stdout.write(f'    Errors: {", ".join(stats["errors"])}')
                else:
                    self.stdout.write(f'    Success: {stats["findings"]} findings imported')
        
        self.stdout.write(f'\n\nImport complete:')
        self.stdout.write(f'  Total assets: {total_stats["assets"]}')
        self.stdout.write(f'  Total vulnerabilities: {total_stats["vulnerabilities"]}')
        self.stdout.write(f'  Total findings: {total_stats["findings"]}')

# management/commands/generate_sla_report.py
class Command(BaseCommand):
    help = 'Generate and email SLA compliance report'
    
    def handle(self, *args, **options):
        from django.core.mail import EmailMessage
        from io import StringIO
        
        # Generate CSV in memory
        output = StringIO()
        ReportGenerator.sla_compliance_csv(output)
        
        # Email report
        email = EmailMessage(
            subject=f'SLA Compliance Report - {timezone.now().date()}',
            body='Please find attached the SLA compliance report.',
            to=['security-team@example.com']
        )
        email.attach('sla_report.csv', output.getvalue(), 'text/csv')
        email.send()
        
        self.stdout.write('SLA report sent successfully')

# management/commands/capture_mttr_snapshot.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Capture MTTR snapshot for historical tracking'
    
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT capture_mttr_snapshot()")
            
        self.stdout.write(self.style.SUCCESS(
            f'MTTR snapshot captured for {timezone.now().date()}'
        ))
        
        # Optional: Show summary
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM mttr_history 
                WHERE snapshot_date = CURRENT_DATE
            """)
            count = cursor.fetchone()[0]
            
        self.stdout.write(f'Captured {count} MTTR records')
```

---

## 8. Simplified Settings for Rapid Development

```python
# settings.py additions
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'corsheaders',  # For lovable.dev integration
    'core',  # Your main app
]

# Enable CORS for lovable.dev
CORS_ALLOWED_ORIGINS = [
    "https://lovable.dev",
    "http://localhost:3000",  # For local testing
]

# REST Framework config
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',  # For Django admin
        'rest_framework.authentication.TokenAuthentication',     # For API
    ]
}

# File upload settings for Nessus files
FILE_UPLOAD_MAX_MEMORY_SIZE = 314572800  # 300MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 314572800  # 300MB
```

---

## 9. Quick Start Guide

1. **Setup Django Project**
```bash
django-admin startproject riskradar
cd riskradar
python manage.py startapp core
```

2. **Install Dependencies**
```bash
pip install django djangorestframework django-filter django-cors-headers
pip install psycopg2-binary reportlab
```

3. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

4. **Load Sample Data**
```bash
# Create default SLA policy
python manage.py shell
>>> from core.models import SLAPolicy
>>> SLAPolicy.objects.create(name="Default SLA", is_default=True)
```

5. **Import Nessus Files**
```bash
# Single file via admin
# Go to /admin/core/nessusupload/add/

# Batch import
python manage.py import_nessus /path/to/nessus/files/
```

6. **Access the System**
- Django Admin: http://localhost:8000/admin/
- API: http://localhost:8000/api/
- Connect lovable.dev to API endpoints

---

## 10. lovable.dev Integration Points

1. **Asset Dashboard**
   - Connect to `/api/assets/` endpoint
   - Display table with sorting/filtering
   - Show finding counts with color coding

2. **Finding Management**
   - Connect to `/api/findings/` endpoint
   - Add status update buttons
   - Show SLA status badges

3. **Reports Page**
   - Add buttons to trigger `/api/findings/sla_report/`
   - Download links for CSV/PDF exports

4. **Campaign Tracker**
   - Connect to `/api/campaigns/` endpoint
   - Show progress bars
   - Allow adding/removing findings

5. **Remediation Performance Dashboard**
   - Fetch metrics from `/api/findings/remediation-metrics/`
   - Display KPI cards for MTTR, daily remediation, capacity %
   - Charts showing:
     - MTTR trends over time (from mttr_history)
     - MTTR by business group (from mttr_summary) 
     - MTTR by asset type (from mttr_by_asset_type)
   - Use Supabase real-time subscriptions for live updates when findings are fixed

This architecture provides everything needed to build a working MVP in 3-5 days while maintaining a clear path to scale up to the full enterprise solution.