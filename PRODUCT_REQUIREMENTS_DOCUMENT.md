# Rapid MVP Product Requirments and Application Architecture Document for Risk Radar

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

> **Note:** This section describes the complete product vision for Risk Radar. Not all features are included in the MVP, but this provides context for future development and ensures the MVP is designed with extensibility in mind.

### Introduction
Risk Radar is a comprehensive vulnerability management platform that consolidates security data from multiple sources, prioritises risks based on business context, and tracks remediation efforts. This section describes the full feature set to provide context for our MVP implementation.

### Connectors & Data Ingestion
Risk Radar ingests data from existing tools (vulnerability scanners, SCA/SAST tools, cloud providers, ticketing systems, etc.) via "connectors". Once configured, a connector pulls assets and vulnerability findings into the platform. Risk Radar then correlates and consolidates this data (across tools and assets) to compute risk and remediation priority. Notably, Risk Radar provides a Nessus File Connector that accepts Tenable's .nessus XML reports (no direct Tenable API support). This connector lets users upload a .nessus scan file (max 300 MB, UTF-8) and automatically integrates its data into Risk Radar's views.

> For practical field extraction and mapping logic, see [nessus_extractor.py extraction script](https://github.com/ciaran-finnegan/nessus-reporting-metrics-demo/blob/main/etl/extractors/nessus_extractor.py).

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

> **Note:** This section lists the features that are in scope for the MVP demo. These are the minimum required to demonstrate value and should be fully implemented and tested. Anything not listed here is considered out of scope for the MVP.

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

## Feature Coverage Mapping: Full Product vs MVP

| Feature Area                        | Full Product (Vision) | MVP (Demo) |
|-------------------------------------|:---------------------:|:----------:|
| Nessus File Import                  |           ✓           |     ✓      |
| Other Connectors (SCA, Cloud, etc.) |           ✓           |     ✗      |
| Asset Management (all types)        |           ✓           |     ✓      |
| Vulnerability Management            |           ✓           |     ✓      |
| Asset Tagging (manual)              |           ✓           |     ✓      |
| Asset Tagging (dynamic/rules)       |           ✓           |     ✗      |
| Business Groups                     |           ✓           |     ✓      |
| Risk Scoring (advanced)             |           ✓           |  Simplified|
| SLA Policies (per group/severity)   |           ✓           |     ✓      |
| SLA Compliance Reporting            |           ✓           |     ✓      |
| Remediation Campaigns (basic)       |           ✓           |     ✓      |
| Remediation Campaigns (auto/ticket) |           ✓           |     ✗      |
| Dashboard & Analytics               |           ✓           |  Basic/UI  |
| Custom Reports/Export               |           ✓           |     ✓      |
| REST API (full)                     |           ✓           |     ✓      |
| SSO/Advanced RBAC                   |           ✓           | Django Auth|
| Audit Logs                          |           ✓           |     ✗      |
| Real-time Dashboards                |           ✓           |  Basic/UI  |

> ✓ = Fully implemented; ✗ = Not in MVP; 'Simplified' or 'Basic/UI' = MVP has a basic or reduced version

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
    integration_name = request.data.get('integration', 'Nessus')
    importer = ScannerImporter(integration_name)
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
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    tag_key       VARCHAR(100) NULL,  -- e.g. 'owner' for dynamic tags
    tag_value     VARCHAR(255) NULL   -- e.g. 'alice@example.com' for dynamic tags
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

-- Scanner Integrations (for future extensibility)
CREATE TABLE scanner_integration (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,  -- 'Nessus', 'OpenVAS', 'Qualys', etc.
    version VARCHAR(50) NULL,           -- Scanner version if relevant
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Field Mappings (configurable from Django admin)
CREATE TABLE field_mapping (
    id SERIAL PRIMARY KEY,
    integration_id INTEGER NOT NULL REFERENCES scanner_integration(id) ON DELETE CASCADE,
    source_field VARCHAR(200) NOT NULL,     -- XML path or field name from scanner
    target_model VARCHAR(50) NOT NULL,      -- 'asset', 'vulnerability', 'finding'
    target_field VARCHAR(100) NOT NULL,     -- 'name', 'ip_address', 'metadata.os', etc.
    field_type VARCHAR(20) DEFAULT 'string' CHECK (field_type IN ('string', 'integer', 'decimal', 'boolean', 'json', 'datetime')),
    is_required BOOLEAN DEFAULT FALSE,
    default_value TEXT,
    transformation_rule TEXT,               -- Python expression or function name for complex mappings
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0
);

CREATE INDEX idx_field_mapping_integration ON field_mapping(integration_id, target_model);
CREATE INDEX idx_field_mapping_active ON field_mapping(is_active, target_model);

-- Severity Mappings (scanner-specific severity translations)
CREATE TABLE severity_mapping (
    id SERIAL PRIMARY KEY,
    integration_id INTEGER NOT NULL REFERENCES scanner_integration(id) ON DELETE CASCADE,
    source_value VARCHAR(50) NOT NULL,     -- '0', '1', '2', '3', '4' for Nessus
    target_value VARCHAR(20) NOT NULL,     -- 'Info', 'Low', 'Medium', 'High', 'Critical'
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE UNIQUE INDEX idx_severity_mapping_unique ON severity_mapping(integration_id, source_value, is_active) WHERE is_active = TRUE;

-- File Upload tracking (generic for all scanner types)
CREATE TABLE scanner_upload (
    id SERIAL PRIMARY KEY,
    integration_id INTEGER NOT NULL REFERENCES scanner_integration(id),
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER,
    file_path TEXT,  -- Supabase Storage path
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ NULL,
    uploaded_by UUID REFERENCES auth.users(id),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT NULL,
    stats JSONB DEFAULT '{}',
    processing_notes TEXT
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

-- MTTR (Mean Time To Remediate) View with Date Filtering Support
CREATE OR REPLACE VIEW mttr_summary AS
SELECT 
    bg.name as business_group,
    bg.id as business_group_id,
    v.severity,
    COUNT(f.id) as fixed_count,
    AVG(EXTRACT(days FROM (f.fixed_at - f.first_seen)))::DECIMAL(10,2) as avg_days_to_fix,
    MIN(EXTRACT(days FROM (f.fixed_at - f.first_seen)))::INTEGER as min_days,
    MAX(EXTRACT(days FROM (f.fixed_at - f.first_seen)))::INTEGER as max_days,
    f.fixed_at::DATE as fix_date
FROM finding f
JOIN vulnerability v ON f.vulnerability_id = v.id
JOIN asset a ON f.asset_id = a.id
LEFT JOIN asset_business_group abg ON a.id = abg.asset_id
LEFT JOIN business_group bg ON abg.business_group_id = bg.id
WHERE f.status = 'fixed' AND f.fixed_at IS NOT NULL
GROUP BY bg.name, bg.id, v.severity, f.fixed_at::DATE;

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

-- Enhanced Metrics Functions with Time Period and Trend Support

-- Time period filter function
CREATE OR REPLACE FUNCTION get_date_range(period TEXT)
RETURNS TABLE(start_date DATE, end_date DATE) AS $$
BEGIN
    CASE period
        WHEN '7d' THEN
            RETURN QUERY SELECT (CURRENT_DATE - INTERVAL '7 days')::DATE, CURRENT_DATE;
        WHEN '30d' THEN
            RETURN QUERY SELECT (CURRENT_DATE - INTERVAL '30 days')::DATE, CURRENT_DATE;
        WHEN '90d' THEN
            RETURN QUERY SELECT (CURRENT_DATE - INTERVAL '90 days')::DATE, CURRENT_DATE;
        WHEN '1y' THEN
            RETURN QUERY SELECT (CURRENT_DATE - INTERVAL '1 year')::DATE, CURRENT_DATE;
        WHEN 'all' THEN
            RETURN QUERY SELECT '2020-01-01'::DATE, CURRENT_DATE;
        ELSE
            RETURN QUERY SELECT (CURRENT_DATE - INTERVAL '7 days')::DATE, CURRENT_DATE;
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- MTTR with time filtering and trend calculation
CREATE OR REPLACE FUNCTION get_mttr_metrics(
    time_period TEXT DEFAULT '7d',
    business_group_ids INTEGER[] DEFAULT NULL,
    asset_tag_names TEXT[] DEFAULT NULL
)
RETURNS TABLE(
    metric_name TEXT,
    current_value DECIMAL,
    previous_value DECIMAL,
    trend_percentage DECIMAL,
    trend_direction TEXT,
    business_group TEXT,
    severity TEXT,
    period_start DATE,
    period_end DATE
) AS $$
DECLARE
    current_start DATE;
    current_end DATE;
    prev_start DATE;
    prev_end DATE;
    period_days INTEGER;
BEGIN
    -- Get date ranges
    SELECT start_date, end_date INTO current_start, current_end
    FROM get_date_range(time_period);
    
    period_days := current_end - current_start;
    prev_start := current_start - INTERVAL (period_days || ' days');
    prev_end := current_start;
    
    RETURN QUERY
    WITH current_period AS (
        SELECT 
            COALESCE(bg.name, 'No Group') as bg_name,
            v.severity,
            AVG(EXTRACT(days FROM (f.fixed_at - f.first_seen)))::DECIMAL(10,2) as mttr_current,
            COUNT(f.id) as fixes_current
        FROM finding f
        JOIN vulnerability v ON f.vulnerability_id = v.id
        JOIN asset a ON f.asset_id = a.id
        LEFT JOIN asset_business_group abg ON a.id = abg.asset_id
        LEFT JOIN business_group bg ON abg.business_group_id = bg.id
        LEFT JOIN asset_asset_tag aat ON a.id = aat.asset_id
        LEFT JOIN asset_tag at ON aat.tag_id = at.id
        WHERE f.status = 'fixed' 
        AND f.fixed_at IS NOT NULL
        AND f.fixed_at::DATE BETWEEN current_start AND current_end
        AND (business_group_ids IS NULL OR bg.id = ANY(business_group_ids))
        AND (asset_tag_names IS NULL OR at.name = ANY(asset_tag_names))
        GROUP BY bg.name, v.severity
    ),
    previous_period AS (
        SELECT 
            COALESCE(bg.name, 'No Group') as bg_name,
            v.severity,
            AVG(EXTRACT(days FROM (f.fixed_at - f.first_seen)))::DECIMAL(10,2) as mttr_previous,
            COUNT(f.id) as fixes_previous
        FROM finding f
        JOIN vulnerability v ON f.vulnerability_id = v.id
        JOIN asset a ON f.asset_id = a.id
        LEFT JOIN asset_business_group abg ON a.id = abg.asset_id
        LEFT JOIN business_group bg ON abg.business_group_id = bg.id
        LEFT JOIN asset_asset_tag aat ON a.id = aat.asset_id
        LEFT JOIN asset_tag at ON aat.tag_id = at.id
        WHERE f.status = 'fixed' 
        AND f.fixed_at IS NOT NULL
        AND f.fixed_at::DATE BETWEEN prev_start AND prev_end
        AND (business_group_ids IS NULL OR bg.id = ANY(business_group_ids))
        AND (asset_tag_names IS NULL OR at.name = ANY(asset_tag_names))
        GROUP BY bg.name, v.severity
    )
    SELECT 
        'MTTR' as metric_name,
        COALESCE(cp.mttr_current, 0) as current_value,
        COALESCE(pp.mttr_previous, 0) as previous_value,
        CASE 
            WHEN pp.mttr_previous > 0 THEN 
                ROUND(((cp.mttr_current - pp.mttr_previous) / pp.mttr_previous * 100), 2)
            ELSE NULL
        END as trend_percentage,
        CASE 
            WHEN pp.mttr_previous IS NULL THEN 'new'
            WHEN cp.mttr_current < pp.mttr_previous THEN 'improving'
            WHEN cp.mttr_current > pp.mttr_previous THEN 'worsening'
            ELSE 'stable'
        END as trend_direction,
        cp.bg_name as business_group,
        cp.severity,
        current_start as period_start,
        current_end as period_end
    FROM current_period cp
    FULL OUTER JOIN previous_period pp ON cp.bg_name = pp.bg_name AND cp.severity = pp.severity
    ORDER BY cp.bg_name, cp.severity;
END;
$$ LANGUAGE plpgsql;

-- Daily Remediation Metrics with trends
CREATE OR REPLACE FUNCTION get_remediation_velocity_metrics(
    time_period TEXT DEFAULT '7d',
    business_group_ids INTEGER[] DEFAULT NULL,
    asset_tag_names TEXT[] DEFAULT NULL
)
RETURNS TABLE(
    metric_name TEXT,
    current_value DECIMAL,
    previous_value DECIMAL,
    trend_percentage DECIMAL,
    trend_direction TEXT,
    business_group TEXT,
    period_start DATE,
    period_end DATE
) AS $$
DECLARE
    current_start DATE;
    current_end DATE;
    prev_start DATE;
    prev_end DATE;
    period_days INTEGER;
BEGIN
    -- Get date ranges
    SELECT start_date, end_date INTO current_start, current_end
    FROM get_date_range(time_period);
    
    period_days := current_end - current_start;
    prev_start := current_start - INTERVAL (period_days || ' days');
    prev_end := current_start;
    
    RETURN QUERY
    WITH current_period AS (
        SELECT 
            COALESCE(bg.name, 'No Group') as bg_name,
            COUNT(f.id)::DECIMAL / GREATEST(period_days, 1) as daily_fixes_current,
            COUNT(f.id) as total_fixes_current
        FROM finding f
        JOIN asset a ON f.asset_id = a.id
        LEFT JOIN asset_business_group abg ON a.id = abg.asset_id
        LEFT JOIN business_group bg ON abg.business_group_id = bg.id
        LEFT JOIN asset_asset_tag aat ON a.id = aat.asset_id
        LEFT JOIN asset_tag at ON aat.tag_id = at.id
        WHERE f.status = 'fixed' 
        AND f.fixed_at IS NOT NULL
        AND f.fixed_at::DATE BETWEEN current_start AND current_end
        AND (business_group_ids IS NULL OR bg.id = ANY(business_group_ids))
        AND (asset_tag_names IS NULL OR at.name = ANY(asset_tag_names))
        GROUP BY bg.name
    ),
    previous_period AS (
        SELECT 
            COALESCE(bg.name, 'No Group') as bg_name,
            COUNT(f.id)::DECIMAL / GREATEST(period_days, 1) as daily_fixes_previous,
            COUNT(f.id) as total_fixes_previous
        FROM finding f
        JOIN asset a ON f.asset_id = a.id
        LEFT JOIN asset_business_group abg ON a.id = abg.asset_id
        LEFT JOIN business_group bg ON abg.business_group_id = bg.id
        LEFT JOIN asset_asset_tag aat ON a.id = aat.asset_id
        LEFT JOIN asset_tag at ON aat.tag_id = at.id
        WHERE f.status = 'fixed' 
        AND f.fixed_at IS NOT NULL
        AND f.fixed_at::DATE BETWEEN prev_start AND prev_end
        AND (business_group_ids IS NULL OR bg.id = ANY(business_group_ids))
        AND (asset_tag_names IS NULL OR at.name = ANY(asset_tag_names))
        GROUP BY bg.name
    )
    SELECT 
        'Daily Remediation Rate' as metric_name,
        ROUND(COALESCE(cp.daily_fixes_current, 0), 2) as current_value,
        ROUND(COALESCE(pp.daily_fixes_previous, 0), 2) as previous_value,
        CASE 
            WHEN pp.daily_fixes_previous > 0 THEN 
                ROUND(((cp.daily_fixes_current - pp.daily_fixes_previous) / pp.daily_fixes_previous * 100), 2)
            ELSE NULL
        END as trend_percentage,
        CASE 
            WHEN pp.daily_fixes_previous IS NULL THEN 'new'
            WHEN cp.daily_fixes_current > pp.daily_fixes_previous THEN 'improving'
            WHEN cp.daily_fixes_current < pp.daily_fixes_previous THEN 'worsening'
            ELSE 'stable'
        END as trend_direction,
        cp.bg_name as business_group,
        current_start as period_start,
        current_end as period_end
    FROM current_period cp
    FULL OUTER JOIN previous_period pp ON cp.bg_name = pp.bg_name
    ORDER BY cp.bg_name;
END;
$$ LANGUAGE plpgsql;

-- SLA Compliance Metrics with trends
CREATE OR REPLACE FUNCTION get_sla_compliance_metrics(
    time_period TEXT DEFAULT '7d',
    business_group_ids INTEGER[] DEFAULT NULL,
    asset_tag_names TEXT[] DEFAULT NULL
)
RETURNS TABLE(
    metric_name TEXT,
    current_value DECIMAL,
    previous_value DECIMAL,
    trend_percentage DECIMAL,
    trend_direction TEXT,
    business_group TEXT,
    severity TEXT,
    period_start DATE,
    period_end DATE
) AS $$
DECLARE
    current_start DATE;
    current_end DATE;
    prev_start DATE;
    prev_end DATE;
    period_days INTEGER;
BEGIN
    -- Get date ranges
    SELECT start_date, end_date INTO current_start, current_end
    FROM get_date_range(time_period);
    
    period_days := current_end - current_start;
    prev_start := current_start - INTERVAL (period_days || ' days');
    prev_end := current_start;
    
    RETURN QUERY
    WITH current_period AS (
        SELECT 
            COALESCE(bg.name, 'No Group') as bg_name,
            v.severity,
            COUNT(*) FILTER (WHERE sla_status = 'compliant')::DECIMAL / GREATEST(COUNT(*), 1) * 100 as compliance_rate_current,
            COUNT(*) as total_findings_current
        FROM sla_status ss
        JOIN finding f ON ss.finding_id = f.id
        JOIN vulnerability v ON f.vulnerability_id = v.id
        JOIN asset a ON f.asset_id = a.id
        LEFT JOIN asset_business_group abg ON a.id = abg.asset_id
        LEFT JOIN business_group bg ON abg.business_group_id = bg.id
        LEFT JOIN asset_asset_tag aat ON a.id = aat.asset_id
        LEFT JOIN asset_tag at ON aat.tag_id = at.id
        WHERE f.first_seen::DATE BETWEEN current_start AND current_end
        AND (business_group_ids IS NULL OR bg.id = ANY(business_group_ids))
        AND (asset_tag_names IS NULL OR at.name = ANY(asset_tag_names))
        GROUP BY bg.name, v.severity
    ),
    previous_period AS (
        SELECT 
            COALESCE(bg.name, 'No Group') as bg_name,
            v.severity,
            COUNT(*) FILTER (WHERE sla_status = 'compliant')::DECIMAL / GREATEST(COUNT(*), 1) * 100 as compliance_rate_previous,
            COUNT(*) as total_findings_previous
        FROM sla_status ss
        JOIN finding f ON ss.finding_id = f.id
        JOIN vulnerability v ON f.vulnerability_id = v.id
        JOIN asset a ON f.asset_id = a.id
        LEFT JOIN asset_business_group abg ON a.id = abg.asset_id
        LEFT JOIN business_group bg ON abg.business_group_id = bg.id
        LEFT JOIN asset_asset_tag aat ON a.id = aat.asset_id
        LEFT JOIN asset_tag at ON aat.tag_id = at.id
        WHERE f.first_seen::DATE BETWEEN prev_start AND prev_end
        AND (business_group_ids IS NULL OR bg.id = ANY(business_group_ids))
        AND (asset_tag_names IS NULL OR at.name = ANY(asset_tag_names))
        GROUP BY bg.name, v.severity
    )
    SELECT 
        'SLA Compliance Rate' as metric_name,
        ROUND(COALESCE(cp.compliance_rate_current, 0), 2) as current_value,
        ROUND(COALESCE(pp.compliance_rate_previous, 0), 2) as previous_value,
        CASE 
            WHEN pp.compliance_rate_previous > 0 THEN 
                ROUND(((cp.compliance_rate_current - pp.compliance_rate_previous) / pp.compliance_rate_previous * 100), 2)
            ELSE NULL
        END as trend_percentage,
        CASE 
            WHEN pp.compliance_rate_previous IS NULL THEN 'new'
            WHEN cp.compliance_rate_current > pp.compliance_rate_previous THEN 'improving'
            WHEN cp.compliance_rate_current < pp.compliance_rate_previous THEN 'worsening'
            ELSE 'stable'
        END as trend_direction,
        cp.bg_name as business_group,
        cp.severity,
        current_start as period_start,
        current_end as period_end
    FROM current_period cp
    FULL OUTER JOIN previous_period pp ON cp.bg_name = pp.bg_name AND cp.severity = pp.severity
    ORDER BY cp.bg_name, cp.severity;
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

class ScannerIntegration(models.Model):
    name = models.CharField(max_length=100, unique=True)
    version = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scanner_integration'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}" + (f" v{self.version}" if self.version else "")

class FieldMapping(models.Model):
    FIELD_TYPE_CHOICES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('decimal', 'Decimal'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('datetime', 'DateTime'),
    ]
    
    TARGET_MODEL_CHOICES = [
        ('asset', 'Asset'),
        ('vulnerability', 'Vulnerability'),
        ('finding', 'Finding'),
    ]
    
    integration = models.ForeignKey(ScannerIntegration, on_delete=models.CASCADE, related_name='field_mappings')
    source_field = models.CharField(max_length=200, help_text="XML path or field name from scanner (e.g., 'host-ip' or 'ReportItem@pluginID')")
    target_model = models.CharField(max_length=50, choices=TARGET_MODEL_CHOICES)
    target_field = models.CharField(max_length=100, help_text="Model field name (e.g., 'ip_address' or 'metadata.os')")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default='string')
    is_required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True, help_text="Default value if source field is empty")
    transformation_rule = models.TextField(blank=True, help_text="Python expression for complex transformations")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'field_mapping'
        ordering = ['integration', 'target_model', 'sort_order']
        unique_together = ['integration', 'source_field', 'target_model', 'target_field']
    
    def __str__(self):
        return f"{self.integration.name}: {self.source_field} → {self.target_model}.{self.target_field}"

class SeverityMapping(models.Model):
    integration = models.ForeignKey(ScannerIntegration, on_delete=models.CASCADE, related_name='severity_mappings')
    source_value = models.CharField(max_length=50, help_text="Scanner-specific severity value")
    target_value = models.CharField(max_length=20, choices=Vulnerability.SEVERITY_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'severity_mapping'
        ordering = ['integration', 'source_value']
        unique_together = ['integration', 'source_value']
    
    def __str__(self):
        return f"{self.integration.name}: {self.source_value} → {self.target_value}"

class ScannerUpload(models.Model):
    integration = models.ForeignKey(ScannerIntegration, on_delete=models.CASCADE, related_name='uploads')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(null=True, blank=True)
    file_path = models.TextField()  # Supabase Storage path
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    error_message = models.TextField(blank=True)
    stats = models.JSONField(default=dict, blank=True)
    processing_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'scanner_upload'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} ({self.integration.name}) - {self.status}"
```

---

## 3. Nessus Import Implementation

### Field Mapping from .nessus to Models
```python
# scanner_import.py
import xml.etree.ElementTree as ET
import json
from django.db import transaction
from django.utils import timezone
from datetime import datetime

class ScannerImporter:
    """
    Generic scanner import class that uses database-configured field mappings
    """
    
    def __init__(self, integration_name='Nessus'):
        self.integration = ScannerIntegration.objects.get(name=integration_name, is_active=True)
        self.field_mappings = self._load_field_mappings()
        self.severity_mappings = self._load_severity_mappings()
    
    def _load_field_mappings(self):
        """Load active field mappings from database"""
        mappings = {}
        for mapping in self.integration.field_mappings.filter(is_active=True).order_by('sort_order'):
            if mapping.target_model not in mappings:
                mappings[mapping.target_model] = []
            mappings[mapping.target_model].append(mapping)
        return mappings
    
    def _load_severity_mappings(self):
        """Load severity mappings from database"""
        return {
            sm.source_value: sm.target_value 
            for sm in self.integration.severity_mappings.filter(is_active=True)
        }
    
    def _apply_transformation(self, value, mapping):
        """Apply transformation rule if specified"""
        if not mapping.transformation_rule or not value:
            return value
        
        try:
            # Safe eval with limited context for simple transformations
            context = {
                'value': value,
                'str': str,
                'int': int,
                'float': float,
                'len': len,
                'strip': lambda x: x.strip() if hasattr(x, 'strip') else x,
                'lower': lambda x: x.lower() if hasattr(x, 'lower') else x,
                'upper': lambda x: x.upper() if hasattr(x, 'upper') else x,
                'split': lambda x, sep: x.split(sep) if hasattr(x, 'split') else [x],
                'first': lambda x: x[0] if x and len(x) > 0 else '',
            }
            return eval(mapping.transformation_rule, {"__builtins__": {}}, context)
        except Exception as e:
            print(f"Transformation error for {mapping.source_field}: {e}")
            return value
    
    def _convert_value(self, value, field_type):
        """Convert value to appropriate Python type"""
        if not value and value != 0:
            return None
            
        try:
            if field_type == 'integer':
                return int(float(value)) if value else 0
            elif field_type == 'decimal':
                return float(value) if value else 0.0
            elif field_type == 'boolean':
                return str(value).lower() in ('true', '1', 'yes', 'on') if value else False
            elif field_type == 'json':
                return json.loads(value) if value else {}
            elif field_type == 'datetime':
                from django.utils.dateparse import parse_datetime
                return parse_datetime(value) if value else None
            else:  # string
                return str(value) if value else ''
        except (ValueError, TypeError, json.JSONDecodeError):
            return None
    
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
        """Process a ReportHost element into an Asset using database mappings"""
        # Extract host properties
        host_props = {}
        for tag in report_host.findall('.//HostProperties/tag'):
            name = tag.get('name')
            value = tag.text
            if name and value:
                host_props[name] = value
        
        # Initialize asset data with defaults
        asset_data = {
            'asset_type': AssetType.objects.get_or_create(name='Host')[0],
            'metadata': {}
        }
        
        # Apply database field mappings for assets
        if 'asset' in self.field_mappings:
            for mapping in self.field_mappings['asset']:
                source_value = None
                
                # Get value from host properties or XML attributes
                if mapping.source_field in host_props:
                    source_value = host_props[mapping.source_field]
                elif mapping.source_field == 'host-name':
                    source_value = report_host.get('name')
                
                # Apply transformation if specified
                if source_value:
                    source_value = self._apply_transformation(source_value, mapping)
                
                # Convert and assign value
                if source_value or mapping.default_value:
                    final_value = source_value or mapping.default_value
                    converted_value = self._convert_value(final_value, mapping.field_type)
                    
                    if '.' in mapping.target_field:
                        # Handle nested fields like 'metadata.os'
                        parts = mapping.target_field.split('.')
                        if parts[0] == 'metadata':
                            asset_data['metadata'][parts[1]] = converted_value
                    else:
                        asset_data[mapping.target_field] = converted_value
        
        # Ensure required fields have values
        if 'name' not in asset_data:
            asset_data['name'] = asset_data.get('hostname') or asset_data.get('ip_address') or 'Unknown Host'
        
        # Add scan timestamp to metadata
        asset_data['metadata']['last_scan'] = datetime.now().isoformat()
        
        asset, created = Asset.objects.update_or_create(
            name=asset_data['name'],
            asset_type=asset_data['asset_type'],
            defaults=asset_data
        )
        
        return asset
    
    @transaction.atomic
    def _process_item(self, report_item, asset):
        """Process a ReportItem into Vulnerability and Finding using database mappings"""
        
        # Initialize data structures
        vuln_data = {'metadata': {}}
        finding_data = {'asset': asset, 'metadata': {}}
        
        # Get severity mapping
        severity_num = report_item.get('severity', '0')
        vuln_data['severity'] = self.severity_mappings.get(severity_num, 'Info')
        
        # Apply database field mappings for vulnerabilities
        if 'vulnerability' in self.field_mappings:
            for mapping in self.field_mappings['vulnerability']:
                source_value = None
                
                # Get value from XML element
                if mapping.source_field.startswith('@'):
                    # Attribute (e.g., '@pluginID')
                    attr_name = mapping.source_field[1:]
                    source_value = report_item.get(attr_name)
                else:
                    # Child element (e.g., 'description')
                    source_value = self._get_text(report_item, mapping.source_field)
                
                # Apply transformation if specified
                if source_value:
                    source_value = self._apply_transformation(source_value, mapping)
                
                # Convert and assign value
                if source_value or mapping.default_value:
                    final_value = source_value or mapping.default_value
                    converted_value = self._convert_value(final_value, mapping.field_type)
                    
                    if '.' in mapping.target_field:
                        # Handle nested fields like 'metadata.plugin_family'
                        parts = mapping.target_field.split('.')
                        if parts[0] == 'metadata':
                            vuln_data['metadata'][parts[1]] = converted_value
                    else:
                        vuln_data[mapping.target_field] = converted_value
        
        # Apply database field mappings for findings
        if 'finding' in self.field_mappings:
            for mapping in self.field_mappings['finding']:
                source_value = None
                
                # Get value from XML element
                if mapping.source_field.startswith('@'):
                    # Attribute (e.g., '@port')
                    attr_name = mapping.source_field[1:]
                    source_value = report_item.get(attr_name)
                else:
                    # Child element (e.g., 'plugin_output')
                    source_value = self._get_text(report_item, mapping.source_field)
                
                # Apply transformation if specified
                if source_value:
                    source_value = self._apply_transformation(source_value, mapping)
                
                # Convert and assign value
                if source_value or mapping.default_value:
                    final_value = source_value or mapping.default_value
                    converted_value = self._convert_value(final_value, mapping.field_type)
                    
                    if '.' in mapping.target_field:
                        # Handle nested fields like 'metadata.exploit_available'
                        parts = mapping.target_field.split('.')
                        if parts[0] == 'metadata':
                            finding_data['metadata'][parts[1]] = converted_value
                    else:
                        finding_data[mapping.target_field] = converted_value
        
        # Ensure required vulnerability fields
        if 'external_id' not in vuln_data:
            vuln_data['external_id'] = report_item.get('pluginID')
        if 'name' not in vuln_data:
            vuln_data['name'] = report_item.get('pluginName', 'Unknown Vulnerability')
        
        # Create or update vulnerability
        vuln, created = Vulnerability.objects.update_or_create(
            external_id=vuln_data['external_id'],
            defaults=vuln_data
        )
        
        # Complete finding data
        finding_data['vulnerability'] = vuln
        finding_data['last_seen'] = timezone.now()
        
        # Ensure port is integer
        if 'port' in finding_data and finding_data['port']:
            try:
                finding_data['port'] = int(finding_data['port'])
            except (ValueError, TypeError):
                finding_data['port'] = 0
        else:
            finding_data['port'] = 0
        
        # Create or update finding
        finding, created = Finding.objects.update_or_create(
            asset=asset,
            vulnerability=vuln,
            port=finding_data.get('port', 0),
            protocol=finding_data.get('protocol', ''),
            service=finding_data.get('service', ''),
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

# Scanner Integration Management
@admin.register(ScannerIntegration)
class ScannerIntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'is_active', 'field_mapping_count', 'severity_mapping_count', 'upload_count']
    list_filter = ['is_active', 'name']
    search_fields = ['name', 'version', 'description']
    readonly_fields = ['created_at']
    
    def field_mapping_count(self, obj):
        return obj.field_mappings.filter(is_active=True).count()
    field_mapping_count.short_description = 'Active Field Mappings'
    
    def severity_mapping_count(self, obj):
        return obj.severity_mappings.filter(is_active=True).count()
    severity_mapping_count.short_description = 'Active Severity Mappings'
    
    def upload_count(self, obj):
        return obj.uploads.count()
    upload_count.short_description = 'Total Uploads'

@admin.register(FieldMapping)
class FieldMappingAdmin(admin.ModelAdmin):
    list_display = ['integration', 'source_field', 'target_model', 'target_field', 'field_type', 'is_active', 'sort_order']
    list_filter = ['integration', 'target_model', 'field_type', 'is_active']
    search_fields = ['source_field', 'target_field', 'description']
    ordering = ['integration', 'target_model', 'sort_order']
    
    fieldsets = (
        ('Basic Mapping', {
            'fields': ('integration', 'source_field', 'target_model', 'target_field', 'field_type')
        }),
        ('Configuration', {
            'fields': ('is_required', 'default_value', 'transformation_rule', 'sort_order')
        }),
        ('Status & Documentation', {
            'fields': ('is_active', 'description')
        }),
    )

@admin.register(SeverityMapping)
class SeverityMappingAdmin(admin.ModelAdmin):
    list_display = ['integration', 'source_value', 'target_value', 'is_active']
    list_filter = ['integration', 'target_value', 'is_active']
    ordering = ['integration', 'source_value']

# File Upload Management
@admin.register(ScannerUpload)
class ScannerUploadAdmin(admin.ModelAdmin):
    list_display = ['filename', 'integration', 'uploaded_at', 'status', 'stats_summary']
    list_filter = ['integration', 'status', 'uploaded_at']
    readonly_fields = ['uploaded_at', 'processed_at', 'stats', 'error_message']
    search_fields = ['filename']
    
    def stats_summary(self, obj):
        if obj.stats:
            return f"Assets: {obj.stats.get('assets', 0)}, Findings: {obj.stats.get('findings', 0)}"
        return '-'
    stats_summary.short_description = 'Import Stats'
    
    actions = ['process_upload']
    
    def process_upload(self, request, queryset):
        for upload in queryset.filter(status='pending'):
            # In production, this would be an async task
            importer = ScannerImporter(upload.integration.name)
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
        """Get comprehensive remediation performance metrics with filtering and trends"""
        from django.db import connection
        
        # Get query parameters
        time_period = request.query_params.get('period', '7d')  # 7d, 30d, 90d, 1y, all
        business_group_ids = request.query_params.getlist('business_groups')
        asset_tag_names = request.query_params.getlist('tags')
        
        # Convert business group IDs to integers
        bg_ids = [int(bg_id) for bg_id in business_group_ids if bg_id.isdigit()] if business_group_ids else None
        tag_names = asset_tag_names if asset_tag_names else None
        
        metrics = {
            'filters': {
                'time_period': time_period,
                'business_groups': bg_ids,
                'tags': tag_names
            },
            'mttr_metrics': [],
            'remediation_velocity': [],
            'sla_compliance': []
        }
        
        with connection.cursor() as cursor:
            # Get MTTR metrics with trends
            cursor.execute("""
                SELECT * FROM get_mttr_metrics(%s, %s, %s)
                ORDER BY business_group, severity
            """, [time_period, bg_ids, tag_names])
            
            columns = [col[0] for col in cursor.description]
            metrics['mttr_metrics'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Get remediation velocity metrics
            cursor.execute("""
                SELECT * FROM get_remediation_velocity_metrics(%s, %s, %s)
                ORDER BY business_group
            """, [time_period, bg_ids, tag_names])
            
            columns = [col[0] for col in cursor.description]
            metrics['remediation_velocity'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Get SLA compliance metrics
            cursor.execute("""
                SELECT * FROM get_sla_compliance_metrics(%s, %s, %s)
                ORDER BY business_group, severity
            """, [time_period, bg_ids, tag_names])
            
            columns = [col[0] for col in cursor.description]
            metrics['sla_compliance'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Get summary statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT a.id) as total_assets,
                    COUNT(f.id) as total_findings,
                    COUNT(f.id) FILTER (WHERE f.status = 'fixed') as fixed_findings,
                    COUNT(f.id) FILTER (WHERE f.status = 'open') as open_findings
                FROM finding f
                JOIN asset a ON f.asset_id = a.id
                LEFT JOIN asset_business_group abg ON a.id = abg.asset_id
                LEFT JOIN asset_asset_tag aat ON a.id = aat.asset_id
                LEFT JOIN asset_tag at ON aat.tag_id = at.id
                WHERE (%s::INTEGER[] IS NULL OR abg.business_group_id = ANY(%s))
                AND (%s::TEXT[] IS NULL OR at.name = ANY(%s))
            """, [bg_ids, bg_ids, tag_names, tag_names])
            
            summary = cursor.fetchone()
            if summary:
                metrics['summary'] = {
                    'total_assets': summary[0],
                    'total_findings': summary[1],
                    'fixed_findings': summary[2],
                    'open_findings': summary[3],
                    'fix_rate': round((summary[2] / max(summary[1], 1)) * 100, 2)
                }
        
        return Response(metrics)
    
    @action(detail=False, methods=['get'])
    def metric_trends(self, request):
        """Get time series data for metric trends"""
        from django.db import connection
        
        time_period = request.query_params.get('period', '30d')
        metric_type = request.query_params.get('metric', 'mttr')  # mttr, velocity, sla
        business_group_ids = request.query_params.getlist('business_groups')
        
        bg_ids = [int(bg_id) for bg_id in business_group_ids if bg_id.isdigit()] if business_group_ids else None
        
        with connection.cursor() as cursor:
            if metric_type == 'mttr':
                # Daily MTTR over time period
                cursor.execute("""
                    WITH date_series AS (
                        SELECT generate_series(
                            CURRENT_DATE - INTERVAL '30 days',
                            CURRENT_DATE,
                            '1 day'::interval
                        )::DATE as date
                    )
                    SELECT 
                        ds.date,
                        COALESCE(bg.name, 'Overall') as business_group,
                        COALESCE(AVG(EXTRACT(days FROM (f.fixed_at - f.first_seen))), 0)::DECIMAL(10,2) as mttr
                    FROM date_series ds
                    LEFT JOIN finding f ON f.fixed_at::DATE = ds.date AND f.status = 'fixed'
                    LEFT JOIN asset a ON f.asset_id = a.id
                    LEFT JOIN asset_business_group abg ON a.id = abg.asset_id
                    LEFT JOIN business_group bg ON abg.business_group_id = bg.id
                    WHERE %s::INTEGER[] IS NULL OR bg.id = ANY(%s) OR bg.id IS NULL
                    GROUP BY ds.date, bg.name
                    ORDER BY ds.date, bg.name
                """, [bg_ids, bg_ids])
            
            elif metric_type == 'velocity':
                # Daily fix count over time period
                cursor.execute("""
                    WITH date_series AS (
                        SELECT generate_series(
                            CURRENT_DATE - INTERVAL '30 days',
                            CURRENT_DATE,
                            '1 day'::interval
                        )::DATE as date
                    )
                    SELECT 
                        ds.date,
                        COALESCE(bg.name, 'Overall') as business_group,
                        COUNT(f.id) as daily_fixes
                    FROM date_series ds
                    LEFT JOIN finding f ON f.fixed_at::DATE = ds.date AND f.status = 'fixed'
                    LEFT JOIN asset a ON f.asset_id = a.id
                    LEFT JOIN asset_business_group abg ON a.id = abg.asset_id
                    LEFT JOIN business_group bg ON abg.business_group_id = bg.id
                    WHERE %s::INTEGER[] IS NULL OR bg.id = ANY(%s) OR bg.id IS NULL
                    GROUP BY ds.date, bg.name
                    ORDER BY ds.date, bg.name
                """, [bg_ids, bg_ids])
            
            columns = [col[0] for col in cursor.description]
            trend_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response({
            'metric_type': metric_type,
            'time_period': time_period,
            'business_groups': bg_ids,
            'trend_data': trend_data
        })

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
from ...models import ScannerUpload, ScannerIntegration
from ...scanner_import import ScannerImporter

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
        
        # Get Nessus integration
        integration = ScannerIntegration.objects.get(name='Nessus', is_active=True)
        importer = ScannerImporter('Nessus')
        total_stats = {'assets': 0, 'vulnerabilities': 0, 'findings': 0}
        
        for i in range(0, len(nessus_files), batch_size):
            batch = nessus_files[i:i+batch_size]
            self.stdout.write(f'\nProcessing batch {i//batch_size + 1} ({len(batch)} files)...')
            
            for file_path in batch:
                self.stdout.write(f'  Importing {os.path.basename(file_path)}...')
                
                # Create upload record
                upload = ScannerUpload.objects.create(
                    integration=integration,
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

## Vulnerability Table (Updated for Extensibility)

| Field         | Type         | Description |
|---------------|--------------|-------------|
| id            | SERIAL PRIMARY KEY | Unique identifier |
| external_id   | VARCHAR(100) | Scanner/plugin/CVE ID |
| name          | VARCHAR(500) | Title/summary |
| description   | TEXT         | Full description |
| severity      | VARCHAR(20)  | Normalised severity (Info, Low, etc.) |
| cvss_score    | DECIMAL(4,2) | Main CVSS score |
| solution      | TEXT         | Remediation advice |
| published_at  | TIMESTAMPTZ  | Vulnerability publication date |
| modified_at   | TIMESTAMPTZ  | Last update date |
| references    | JSONB        | Array of URLs, CVEs, BIDs, xrefs, etc. |
| risk_factor   | VARCHAR(20)  | Scanner risk factor (if any) |
| exploit       | JSONB        | All exploitability info (availability, frameworks, etc.) |
| cvss          | JSONB        | All CVSS vectors, temporal, etc. |
| metadata      | JSONB        | All other scanner-specific/extra fields |

> Note: All scanner-specific or rarely-used fields should be stored in metadata for extensibility. Field mapping should allow mapping to any of these generic fields or to a path in metadata, exploit, cvss, or references.

---

## Nessus Field Mapping Reference (as of latest schema)

The following table shows the default field mappings created by the setup_nessus_field_mappings management command. These mappings ensure all relevant Nessus fields are captured in a generic, extensible way for future scanner support.

| SOURCE FIELD                | TARGET MODEL    | TARGET FIELD                      | FIELD TYPE |
|-----------------------------|-----------------|------------------------------------|------------|
| host-fqdn                   | Asset           | hostname                           | String     |
| host-ip                     | Asset           | ip_address                         | String     |
| Type                        | Asset           | asset_type                         | String     |
| @port                       | Finding         | port                               | Integer    |
| @protocol                   | Finding         | protocol                           | String     |
| svc_name                    | Finding         | service                            | String     |
| plugin_output               | Finding         | plugin_output                      | String     |
| @pluginID                   | Vulnerability   | external_id                        | String     |
| @pluginName                 | Vulnerability   | name                               | String     |
| cvss_base_score             | Vulnerability   | cvss_score                         | Decimal    |
| pluginFamily                | Vulnerability   | metadata.family                    | String     |
| description                 | Vulnerability   | description                        | String     |
| solution                    | Vulnerability   | solution                           | String     |
| synopsis                    | Vulnerability   | metadata.synopsis                  | String     |
| cve                         | Vulnerability   | references                         | JSON       |
| bid                         | Vulnerability   | references                         | JSON       |
| xref                        | Vulnerability   | references                         | JSON       |
| see_also                    | Vulnerability   | references                         | JSON       |
| risk_factor                 | Vulnerability   | risk_factor                        | String     |
| exploitability_ease         | Vulnerability   | exploit                            | JSON       |
| exploit_available           | Vulnerability   | exploit                            | JSON       |
| exploit_framework_core      | Vulnerability   | exploit                            | JSON       |
| exploit_framework_canvas    | Vulnerability   | exploit                            | JSON       |
| exploit_framework_metasploit| Vulnerability   | exploit                            | JSON       |
| cvss_vector                 | Vulnerability   | cvss                               | JSON       |
| cvss_temporal_score         | Vulnerability   | cvss                               | JSON       |
| plugin_modification_date    | Vulnerability   | modified_at                        | DateTime   |
| plugin_publication_date     | Vulnerability   | published_at                       | DateTime   |
| patch_publication_date      | Vulnerability   | metadata.patch_publication_date    | DateTime   |
| vuln_publication_date       | Vulnerability   | metadata.vuln_publication_date     | DateTime   |

> To update or reset these mappings, run:
> 
>     python manage.py setup_nessus_field_mappings