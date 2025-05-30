# Risk Radar – MVP Architecture

## Introduction: Detailed Feature Overview

### Connectors & Data Ingestion
Risk Radar ingests data from existing tools (vulnerability scanners, SCA/SAST tools, cloud providers, ticketing systems, etc.) via "connectors" ([docs](https://help.vulcancyber.com)). Once configured, a connector pulls assets and vulnerability findings into the platform. Risk Radar then correlates and consolidates this data (across tools and assets) to compute risk and remediation priority. Notably, Risk Radar provides a Nessus File Connector that accepts Tenable's .nessus XML reports (no direct Tenable API support). This connector lets users upload a .nessus scan file (max 300 MB, UTF-8) and automatically integrates its data into Risk Radar's views. In general, any connector can import asset and vuln data and feed Risk Radar's unified database.

### Assets and Vulnerabilities Management
All ingested data is modelled as assets and vulnerabilities (findings). Assets represent systems or entities (hosts, code projects, images, websites, cloud resources, etc.) and are classified by type. For example, Hosts cover any networked device (PCs, servers, VMs, NAS, routers, IoT devices, etc.). Code Projects are source-code repositories (GitHub, GitLab, SAST/SCA apps). Websites are web apps (typically identified by domain or URL). Images are container images/registries (Docker, OCI images). Cloud Resources cover cloud assets (storage, networking, databases, etc.). Each asset record can include identifiers (IP, hostname, resource ID) and tags. Vulnerabilities (CVE findings, scanner plugins, etc.) are linked to assets as "instances" (if the same vulnerability appears on multiple assets, each is a separate instance). Risk Radar allows tracking each vuln instance's details (severity, plugin ID, port, service, description, etc.) and the linkage to the asset. In sum, Risk Radar's data model lets developers query "assets" and their associated "vulnerabilities" seamlessly across all integrated sources.

### Tagging and Business Context
Risk Radar emphasises business context via Asset Tags and Business Groups ([docs](https://help.vulcancyber.com)). Asset tags are simple labels (e.g. #external-facing or #linux-server) attached to assets to help filter and categorise them. Tags can be imported from connectors or created manually. Crucially, Risk Radar can convert tags into dynamic "Business Groups," which are named collections of assets (e.g. Finance, Production, or DevOps). Business Groups segment the environment into organisational or functional units. They are used throughout Risk Radar: for filtering vulnerabilities/assets, defining SLA policies, and driving reports. The platform supports rule-based tagging – for example, dynamic tags of the form key:value (like bizowner:alice@example.com) enable automated asset-owner assignment. In practice, developers can create Business Groups (via the UI or API) and associate assets by tag rules. Business Group membership then affects risk prioritisation, reporting, and workflows.

### Risk Prioritisation and SPR
Risk Radar computes a unified risk score for each vulnerability instance by correlating asset criticality, vulnerability severity, exploitability, and business context ([docs](https://help.vulcancyber.com)). An asset's Security Posture Rating (SPR) and custom risk weights can be configured (per organisation) to influence scoring. This allows fine-tuning which issues get top priority. From a developer standpoint, the platform provides endpoints to retrieve risk scores and to configure risk weightings (e.g. adjusting the weight of a CVSS factor). Overall, risk prioritisation ensures that critical vulns on high-value assets bubble to the top.

### SLA Management and Reporting
Teams can define Service-Level Agreement (SLA) policies for vulnerabilities by severity ([docs](https://help.vulcancyber.com)). For example, "Critical" issues might have a 3-day SLA, "High" 7 days, etc. Risk Radar also supports SLAs per Business Group (different deadlines for different units). The system tracks each vulnerability instance's "time to remediation" against its SLA, marking it as "Exceeding" if not fixed in time. Analytics and dashboards show SLA compliance metrics. For example, analytic reports include metrics like "Vulnerability Instances Exceeded SLA by Business Group and Risk Level", and "Campaign due-date compliance by Business Group". This lets developers (and managers) measure how well remediation is keeping pace.

### Remediation Campaigns and Automation
Every attempt to remediate a vulnerability (manual or automated) generates a remediation campaign ([docs](https://help.vulcancyber.com)). Developers can "take action" on one or more vulnerabilities or assets, opening tickets in integrated ticketing systems (JIRA, ServiceNow, email, Slack, etc.). A campaign aggregates those actions and tracks their progress. Campaigns show which vulnerabilities/assets have been addressed and calculate a progress percentage (dynamic as fixes are made). Campaigns can be created manually via the UI/API or automatically via Playbook Automations: for example, a Playbook rule might say "whenever a new Critical vuln is discovered in Business Group X, open a JIRA ticket automatically". Thus, developers can use API/automation to auto-create campaigns and tickets under defined conditions. (Each campaign can include related data: assets affected, remediation solutions, due dates, SLA info, etc.)

### Dashboard and Analytics
Risk Radar provides a home dashboard of risk trends and quick stats, plus a Reports (Analytics) module ([docs](https://help.vulcancyber.com)). It offers pre-built widgets (e.g. Top Business Groups by Risk, SPR Compliance by Group, Assets by Business Group) as well as the ability to build custom reports (self-service analytics). Developers can retrieve these via API or embed them in custom UIs. The system also provides SQL-based "magic search" and exportable CSVs for raw data.

### API and Extensibility
The platform exposes a REST API (currently v1 and v2) for all operations ([docs](https://help.vulcancyber.com)). The APIs allow programmatic management of assets, vulnerabilities, groups, tags, campaigns, tickets, etc. Developers obtain an API token via the UI (OAuth2) and then make authenticated requests. Documentation includes full OpenAPI specs. This allows integration into custom tools or automated pipelines.

### Security and Administration
Risk Radar supports single sign-on (SSO) via SAML (e.g. Azure AD, Okta) and role-based access control for fine-grained permissions. Audit logs track all activity. From a developer perspective, these ensure secure multi-user access.

---

## MVP Feature Subset (Detailed)
For the MVP demo, we focus on a core subset of features (drawing from Risk Radar's capabilities) that support Nessus import and basic vulnerability management. Specifically:

- **Tenable Nessus File Upload**: Allow the user to upload a Tenable .nessus scan file (via the Nessus File Connector approach). The backend should parse the file and ingest its data. This covers connecting with Tenable scan data as a source. The upload endpoint will accept a .nessus file (max 300 MB, UTF-8), store it in Supabase Storage, and trigger parsing and ingestion.

- **Asset & Vulnerability Data Management**: The system must display and manage the resulting asset and vulnerability data. This includes storing each asset and its details, and each vulnerability instance. Developers should be able to list and filter assets and vulnerabilities via the UI/API. Under the hood, the ingestion step will create asset records and vuln-instance records (as Risk Radar does), so that existing and new data appear in all views.

- **Support for All Asset Types**: Even if the initial data is from Nessus hosts, the system's data model should accommodate all asset types that Risk Radar uses: Hosts, Code Projects, Websites, Container Images, Cloud Resources (and any others). For completeness, the schema will include an asset type field or lookup so future connectors (SAST, DAST, CSPM, etc.) can feed in Code, Website, Image, or Cloud assets.

- **Business Groups & Asset Tagging**: Implement asset tags and business groups. The user should be able to define tags on assets (free-form or imported). Asset tags can be used to create Business Groups, grouping assets by department or environment. The system should support dynamic tag rules (e.g. tags of the form key:value) for auto-assignment of owners or groups. In practice, this means storing tag data and allowing simple rules/filters that assign assets to groups.

- **SLA and Remediation Reporting**: Enable SLA configuration per severity and per business group, and report on SLA compliance. Also support tracking remediation campaigns. For MVP reporting, we will at least include: (a) tracking when each vuln instance was opened and whether it exceeds its SLA target, and (b) the ability to view or export remediation campaign status. These correspond to Risk Radar's reporting features like "Campaign due-date compliance" and "Instances Exceeded SLA".

In summary, the MVP must handle Nessus import, show assets & vulns, cover Risk Radar's asset categories, implement business-group/tag context, and include basic SLA/campaign reporting as listed above.

---

## Naming Conventions (for Developers)
To ensure clarity and consistency, we will choose developer-friendly names for tables and features:
- **Asset (asset)** – instead of Risk Radar's "VCP-Host" etc. Fields include name, type, ip_address, etc.
- **AssetType (asset_type)** – lookup table for types (Host, Code, Website, Image, Cloud).
- **Vulnerability (vulnerability)** – represents a unique vulnerability (CVE or plugin).
- **VulnInstance (vulnerability_instance)** – a specific finding on an asset (linking asset_id to vulnerability_id plus details like port, severity, description). This replaces Risk Radar's "finding instance."
- **BusinessGroup (business_group)** – a named collection of assets.
- **AssetTag (asset_tag)** – tags (labels) attached to assets; include a flag or separate fields for dynamic key/value (e.g. dynamic_key, dynamic_value) if implementing owner tags.
- **AssetTagAssignment (asset_asset_tag)** – many-to-many linking assets to tags.
- **SLAPolicy (sla_policy)** – defines days-per-severity for SLAs (global or per BusinessGroup).
- **RemediationCampaign (campaign)** – tracks a remediation effort (with name, start_date, due_date, progress_percent, etc.).
- **CampaignVuln (campaign_vulnerability)** – links campaigns to the vuln instances it covers.
- **Connector (connector)** and **Upload (upload)** – representing a data source and uploaded Nessus file metadata (e.g. upload_date, file_url).

This naming aligns with typical Django conventions (snake_case, clear nouns) and is a one-to-one rename of Risk Radar's UI terms into DB model terms. For example, Risk Radar's "Tag" and "Business Group" become asset_tag and business_group tables, respectively.

---

# Risk Radar - MVP Architecture
## Fast-Track Implementation with Enterprise Migration Path

### Table of Contents
1. [Architecture Philosophy](#architecture-philosophy)
2. [Core Features & Implementation](#core-features--implementation)
3. [Technical Stack](#technical-stack)
4. [Database Design](#database-design)
5. [Service Architecture](#service-architecture)
6. [API Design](#api-design)
7. [Analytics & Metrics](#analytics--metrics)
8. [Migration Strategy](#migration-strategy)
9. [Security & Performance](#security--performance)

---

## Architecture Philosophy

This MVP architecture follows a "Database-First, Service-Ready" approach:
- **Leverage PostgreSQL** for heavy lifting (materialized views, JSONB)
- **Thin service layer** that can be expanded later
- **Clear interfaces** between components for future refactoring
- **Supabase-native** features to minimize infrastructure
- **Progressive enhancement** path to enterprise architecture

### Key Principles
1. **Start Simple**: Use database views and functions for complex logic
2. **Stay Flexible**: Use JSONB for extensible data
3. **Build Modular**: Each feature in its own module/service
4. **Plan for Growth**: Use patterns that scale

---

## Core Features & Implementation

### 1. Findings Management
Based on [Risk Radar's documentation](https://help.vulcancyber.com/en/), a finding is a vulnerability-asset connection.

**Implementation:**
```sql
-- Simple but extensible schema
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vulnerability_id UUID NOT NULL,
    asset_id UUID NOT NULL,
    status VARCHAR(50) DEFAULT 'vulnerable',
    risk_score DECIMAL(5,2),
    metadata JSONB DEFAULT '{}', -- Extensible for future fields
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    fixed_at TIMESTAMPTZ,
    UNIQUE(vulnerability_id, asset_id, (metadata->>'port'), (metadata->>'protocol'))
);

-- Index for performance
CREATE INDEX idx_findings_risk ON findings(status, risk_score DESC);
CREATE INDEX idx_findings_metadata ON findings USING GIN(metadata);
```

**Service Layer (Thin):**
```python
# services/findings.py
class FindingsService:
    """Thin wrapper that can be expanded later"""
    
    @staticmethod
    def create_finding(vuln_id, asset_id, **kwargs):
        # Start with direct SQL
        metadata = {k: v for k, v in kwargs.items() 
                   if k in ['port', 'protocol', 'service']}
        
        # Later: Add business logic, validations, events
        return Finding.objects.create(
            vulnerability_id=vuln_id,
            asset_id=asset_id,
            metadata=metadata
        )
    
    @staticmethod
    def calculate_risk(finding):
        # MVP: Simple calculation
        # Later: Complex risk engine
        return finding.vulnerability.cvss_score * 10
```

### 2. Business Context
[Business Groups and Tags](https://help.vulcancyber.com/en/) provide organizational context.

**Implementation:**
```sql
-- Flexible business context
CREATE TABLE business_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'business_unit' or 'tag'
    impact_level VARCHAR(20) DEFAULT 'medium',
    rules JSONB DEFAULT '[]', -- Dynamic rules for assignment
    parent_id UUID REFERENCES business_contexts(id),
    metadata JSONB DEFAULT '{}'
);

-- Simple many-to-many
CREATE TABLE asset_contexts (
    asset_id UUID NOT NULL,
    context_id UUID NOT NULL,
    assigned_by VARCHAR(50) DEFAULT 'manual', -- manual, rule, import
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (asset_id, context_id)
);

-- Database function for rule evaluation (start simple)
CREATE OR REPLACE FUNCTION evaluate_context_rules() 
RETURNS TRIGGER AS $$
BEGIN
    -- MVP: Simple pattern matching
    -- Later: Move to Python service
    PERFORM assign_contexts_by_rules(NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Progressive Enhancement Path:**
```python
# services/business_context.py
class BusinessContextService:
    def apply_rules(self, asset):
        # MVP: Call database function
        cursor.execute("SELECT apply_context_rules(%s)", [asset.id])
        
        # Future: Python rule engine
        # rules = Rule.objects.filter(active=True)
        # for rule in rules:
        #     if self.rule_engine.evaluate(rule, asset):
        #         asset.contexts.add(rule.context)
```

### 3. SLA Management
[SLA tracking](https://help.vulcancyber.com/en/) ensures timely remediation.

**Implementation:**
```sql
-- SLA policies linked to contexts
CREATE TABLE sla_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    context_id UUID REFERENCES business_contexts(id),
    severity_days JSONB NOT NULL DEFAULT '{
        "critical": 1,
        "high": 7,
        "medium": 30,
        "low": 90
    }',
    is_default BOOLEAN DEFAULT FALSE
);

-- Materialized view for SLA status (refreshed hourly)
CREATE MATERIALIZED VIEW sla_status AS
WITH policy_mapping AS (
    SELECT DISTINCT ON (f.id)
        f.id as finding_id,
        f.first_seen,
        v.severity,
        sp.severity_days->>(v.severity) as sla_days,
        f.first_seen + ((sp.severity_days->>(v.severity))::int || ' days')::interval as due_date
    FROM findings f
    JOIN vulnerabilities v ON f.vulnerability_id = v.id
    JOIN assets a ON f.asset_id = a.id
    LEFT JOIN asset_contexts ac ON a.id = ac.asset_id
    LEFT JOIN sla_policies sp ON sp.context_id = ac.context_id
    WHERE f.status != 'fixed'
    ORDER BY f.id, sp.is_default
)
SELECT 
    finding_id,
    sla_days::int,
    due_date,
    CASE 
        WHEN NOW() > due_date THEN 'breached'
        WHEN NOW() > due_date - (sla_days::int * 0.2 || ' days')::interval THEN 'approaching'
        ELSE 'compliant'
    END as sla_status,
    EXTRACT(days FROM (due_date - NOW()))::int as days_remaining
FROM policy_mapping;

CREATE INDEX idx_sla_status ON sla_status(sla_status, days_remaining);
```

### 4. Risk Calculation
[Risk calculation](https://help.vulcancyber.com/en/) uses three factors: technical severity, threats, and business impact.

**Implementation:**
```sql
-- Risk calculation as a database function (can migrate to Python later)
CREATE OR REPLACE FUNCTION calculate_finding_risk(
    p_finding_id UUID
) RETURNS DECIMAL AS $$
DECLARE
    v_technical_score DECIMAL;
    v_threat_score DECIMAL;
    v_business_score DECIMAL;
    v_weights JSONB;
    v_final_score DECIMAL;
BEGIN
    -- Get base scores
    SELECT 
        v.cvss_score * 10,
        CASE WHEN v.metadata->>'exploitable' = 'true' THEN 100 ELSE 0 END,
        COALESCE(MAX(bc.impact_level::int), 0)
    INTO v_technical_score, v_threat_score, v_business_score
    FROM findings f
    JOIN vulnerabilities v ON f.vulnerability_id = v.id
    JOIN assets a ON f.asset_id = a.id
    LEFT JOIN asset_contexts ac ON a.id = ac.asset_id
    LEFT JOIN business_contexts bc ON ac.context_id = bc.id
    WHERE f.id = p_finding_id
    GROUP BY v.cvss_score, v.metadata;
    
    -- Get weights (hardcoded for MVP, configurable later)
    v_weights := '{"technical": 0.4, "threat": 0.4, "business": 0.2}'::jsonb;
    
    -- Calculate final score
    v_final_score := (
        v_technical_score * (v_weights->>'technical')::decimal +
        v_threat_score * (v_weights->>'threat')::decimal +
        v_business_score * (v_weights->>'business')::decimal
    );
    
    RETURN ROUND(v_final_score, 2);
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-calculate risk
CREATE TRIGGER calculate_risk_on_finding
    AFTER INSERT OR UPDATE ON findings
    FOR EACH ROW
    EXECUTE FUNCTION update_finding_risk();
```

### 5. Metrics Generation
MTTR and SLA compliance metrics are critical KPIs.

**Implementation:**
```sql
-- MTTR calculation view
CREATE MATERIALIZED VIEW mttr_metrics AS
WITH remediation_times AS (
    SELECT 
        a.business_contexts->>'primary' as business_unit,
        v.severity,
        EXTRACT(epoch FROM (f.fixed_at - f.first_seen))/86400 as days_to_fix,
        DATE_TRUNC('month', f.fixed_at) as fix_month
    FROM findings f
    JOIN vulnerabilities v ON f.vulnerability_id = v.id
    JOIN assets a ON f.asset_id = a.id
    WHERE f.status = 'fixed'
    AND f.fixed_at >= NOW() - INTERVAL '6 months'
)
SELECT 
    business_unit,
    severity,
    fix_month,
    COUNT(*) as fixed_count,
    AVG(days_to_fix)::decimal(10,2) as mean_ttr,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY days_to_fix)::decimal(10,2) as median_ttr,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY days_to_fix)::decimal(10,2) as p90_ttr
FROM remediation_times
GROUP BY business_unit, severity, fix_month;

-- SLA compliance summary
CREATE MATERIALIZED VIEW sla_compliance_summary AS
SELECT 
    ac.context_id,
    bc.name as business_unit,
    COUNT(*) as total_findings,
    COUNT(*) FILTER (WHERE ss.sla_status = 'compliant') as compliant,
    COUNT(*) FILTER (WHERE ss.sla_status = 'approaching') as approaching,
    COUNT(*) FILTER (WHERE ss.sla_status = 'breached') as breached,
    ROUND(100.0 * COUNT(*) FILTER (WHERE ss.sla_status = 'compliant') / COUNT(*), 2) as compliance_rate
FROM sla_status ss
JOIN findings f ON ss.finding_id = f.id
JOIN assets a ON f.asset_id = a.id
JOIN asset_contexts ac ON a.id = ac.asset_id
JOIN business_contexts bc ON ac.context_id = bc.id
WHERE bc.type = 'business_unit'
GROUP BY ac.context_id, bc.name;
```

### 6. Nessus Import
Fast, reliable import with field mapping.

**Implementation:**
```python
# importers/nessus.py
import xml.etree.ElementTree as ET
from contextlib import contextmanager

class NessusImporter:
    """Stream-based importer for large files"""
    
    # Configurable field mappings
    FIELD_MAPPINGS = {
        'ReportHost.name': 'asset.name',
        'HostProperties.host-ip': 'asset.metadata.ip_address',
        'ReportItem.pluginID': 'vulnerability.external_id',
        'ReportItem.risk_factor': 'vulnerability.severity',
        'ReportItem.cvss3_base_score': 'vulnerability.cvss_score',
        'ReportItem.port': 'finding.metadata.port',
        'ReportItem.protocol': 'finding.metadata.protocol',
        'ReportItem.svc_name': 'finding.metadata.service'
    }
    
    @contextmanager
    def parse_file(self, file_path):
        """Stream parse to handle large files"""
        for event, elem in ET.iterparse(file_path, events=('start', 'end')):
            if event == 'end' and elem.tag == 'ReportHost':
                yield self._parse_host(elem)
                elem.clear()  # Free memory
    
    def import_file(self, file_path):
        """Import with progress tracking"""
        with self.parse_file(file_path) as hosts:
            for host_data in hosts:
                # Create or update asset
                asset = self._upsert_asset(host_data)
                
                # Process vulnerabilities
                for vuln_data in host_data['vulnerabilities']:
                    vuln = self._upsert_vulnerability(vuln_data)
                    finding = self._upsert_finding(asset, vuln, vuln_data)
                    
                yield {
                    'asset': asset.id,
                    'vulnerabilities': len(host_data['vulnerabilities'])
                }
```

---

## Technical Stack

### Core Stack (MVP)
- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL 15 (via Supabase)
- **Auth**: Supabase Auth
- **File Storage**: Supabase Storage
- **Task Queue**: Django-Q (simpler than Celery for MVP)
- **Frontend**: [lovable.dev](https://lovable.dev) (no-code/low-code builder for rapid UI delivery)

### Migration-Ready Components
```python
# settings.py
INSTALLED_APPS = [
    # ...
    'django_q',  # Start with Django-Q
    # 'celery',  # Ready to switch
]

# Use dependency injection
RISK_CALCULATOR = 'services.risk.DatabaseRiskCalculator'  # MVP
# RISK_CALCULATOR = 'services.risk.PythonRiskCalculator'  # Future
```

---

## Database Design

### Core Schema (Developer-Friendly Naming)
```sql
-- Asset types (Host, Code, Website, Image, Cloud, etc.)
CREATE TABLE asset_type (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Business groups
CREATE TABLE business_group (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Assets 
CREATE TABLE asset (
    id               SERIAL PRIMARY KEY,
    name             VARCHAR(255) NOT NULL,
    asset_type_id    INTEGER NOT NULL REFERENCES asset_type(id),
    ip_address       INET NULL,
    hostname         VARCHAR(255) NULL,
    business_group_id INTEGER REFERENCES business_group(id),
    UNIQUE(name, asset_type_id)
);

-- Asset tags (static or dynamic)
CREATE TABLE asset_tag (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    dynamic_key   VARCHAR(100) NULL,
    dynamic_value VARCHAR(255) NULL
);

-- Linking assets to tags (many-to-many)
CREATE TABLE asset_asset_tag (
    asset_id INTEGER NOT NULL REFERENCES asset(id),
    tag_id   INTEGER NOT NULL REFERENCES asset_tag(id),
    PRIMARY KEY (asset_id, tag_id)
);

-- Vulnerabilities (unique issues)
CREATE TABLE vulnerability (
    id          SERIAL PRIMARY KEY,
    external_id VARCHAR(100) NULL,
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    severity    VARCHAR(10) NULL,
    UNIQUE(external_id, name)
);

-- Vulnerability instances (findings on assets)
CREATE TABLE vulnerability_instance (
    id               SERIAL PRIMARY KEY,
    asset_id         INTEGER NOT NULL REFERENCES asset(id) ON DELETE CASCADE,
    vulnerability_id INTEGER NOT NULL REFERENCES vulnerability(id) ON DELETE CASCADE,
    port             INTEGER NULL,
    protocol         VARCHAR(20) NULL,
    service          VARCHAR(50) NULL,
    plugin_output    TEXT,
    first_seen       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(asset_id, vulnerability_id, port, service)
);

-- SLA policies (global or per group/severity)
CREATE TABLE sla_policy (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    severity     VARCHAR(10) NOT NULL,
    days_allowed INTEGER NOT NULL,
    business_group_id INTEGER REFERENCES business_group(id)
);

-- Remediation campaigns
CREATE TABLE campaign (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(255) NOT NULL,
    description   TEXT,
    status        VARCHAR(20) NOT NULL DEFAULT 'Open',
    start_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date      DATE NULL,
    progress_pct  NUMERIC(5,2) NULL
);

-- Link campaigns to vulnerability instances
CREATE TABLE campaign_vulnerability (
    campaign_id              INTEGER NOT NULL REFERENCES campaign(id) ON DELETE CASCADE,
    vulnerability_instance_id INTEGER NOT NULL REFERENCES vulnerability_instance(id) ON DELETE CASCADE,
    PRIMARY KEY (campaign_id, vulnerability_instance_id)
);

-- Nessus file uploads (metadata)
CREATE TABLE upload (
    id            SERIAL PRIMARY KEY,
    uploaded_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    uploader      UUID,
    file_url      TEXT NOT NULL
);
```

### ETL Mapping Strategy (Nessus to Schema)
- Each <ReportHost> → asset (name, hostname, ip_address)
- <HostProperties> tags → asset fields
- <ReportItem> → vulnerability_instance (link to asset, vulnerability)
- pluginID → vulnerability.external_id
- pluginName → vulnerability.name
- severity → vulnerability.severity
- svc_name, protocol, port → vulnerability_instance fields
- plugin output/description → plugin_output
- Always insert new vulnerability_instance for each asset/vuln combo
- Modular code for future connectors (map fields to columns, insert/update records)

---

## Service Architecture

### Layered but Lightweight

┌─────────────────────────────────────────────┐
│ lovable.dev Frontend (auto-generated UI)    │
├─────────────────────────────────────────────┤
│ Django REST API                            │
├─────────────────────────────────────────────┤
│ Thin Service Layer                         │
│ ┌─────────┬──────────┬─────────┐           │
│ │Findings │Business  │ Import  │           │
│ │Service  │Context   │ Service │           │
│ └─────────┴──────────┴─────────┘           │
├─────────────────────────────────────────────┤
│ Django Models (Minimal Logic)               │
├─────────────────────────────────────────────┤
│ PostgreSQL (Heavy Lifting)                  │
│ - Materialized Views                        │
│ - Stored Functions                          │
│ - Triggers                                  │
└─────────────────────────────────────────────┘

#### lovable.dev Integration
- **lovable.dev** connects directly to Supabase and Django REST API endpoints.
- UI is built visually, mapping API endpoints to forms, tables, and dashboards.
- Auth, file upload, and data management are handled via Supabase integration.
- Custom logic and advanced workflows can be added via Django API endpoints, which lovable.dev can consume.
- When ready, the frontend can be migrated to a custom React/Vite/shadcn/ui stack with minimal backend changes.

### Service Pattern
```python
# Base service class for consistency
class BaseService:
    def __init__(self, user=None):
        self.user = user
        self.db = connections['default']
    
    def execute_sql(self, sql, params=None):
        """Direct SQL execution with logging"""
        with self.db.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def call_db_function(self, func_name, *args):
        """Call PostgreSQL functions"""
        placeholders = ','.join(['%s'] * len(args))
        sql = f"SELECT {func_name}({placeholders})"
        return self.execute_sql(sql, args)[0][0]
```

---

## API Design

### RESTful API (OpenAPI-aligned, Developer-Friendly)
- Endpoints use clear, developer-friendly names (e.g. /assets, /vulnerabilities, /business-groups, /asset-tags, /campaigns, /sla-policies, /uploads/nessus)
- Follows the OpenAPI spec pattern from temp.md for easy client/server codegen and lovable.dev integration

### RESTful with GraphQL-Ready Structure
```python
# views.py - Structured for easy GraphQL migration
class FindingsViewSet(viewsets.ModelViewSet):
    queryset = Finding.objects.all()
    serializer_class = FindingSerializer
    
    def get_queryset(self):
        # Start with ORM
        qs = super().get_queryset()
        
        # Can switch to raw SQL for performance
        if self.request.GET.get('use_optimized'):
            return Finding.objects.raw("""
                SELECT f.*, 
                       v.title as vulnerability_title,
                       a.name as asset_name,
                       ss.sla_status,
                       ss.days_remaining
                FROM findings f
                JOIN vulnerabilities v ON f.vulnerability_id = v.id
                JOIN assets a ON f.asset_id = a.id
                LEFT JOIN sla_status ss ON f.id = ss.finding_id
                WHERE f.status = %s
            """, [self.request.GET.get('status', 'vulnerable')])
        
        return qs
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Metrics endpoint that can grow"""
        metrics_type = request.GET.get('type', 'summary')
        
        if metrics_type == 'summary':
            # MVP: Query materialized view
            data = self.get_summary_metrics()
        elif metrics_type == 'detailed':
            # Future: Complex calculations
            data = MetricsService().calculate_detailed()
        
        return Response(data)
```

---

## Analytics & Metrics

### Database-Driven Analytics (MVP)
```sql
-- Single source of truth for metrics
CREATE OR REPLACE FUNCTION refresh_analytics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mttr_metrics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY sla_compliance_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY risk_distribution;
    
    -- Store snapshot for trending
    INSERT INTO analytics_snapshots (snapshot_date, metrics)
    SELECT NOW(), jsonb_build_object(
        'mttr', (SELECT jsonb_agg(row_to_json(m)) FROM mttr_metrics m),
        'sla', (SELECT jsonb_agg(row_to_json(s)) FROM sla_compliance_summary s),
        'risk', (SELECT jsonb_agg(row_to_json(r)) FROM risk_distribution r)
    );
END;
$$ LANGUAGE plpgsql;

-- Schedule in Supabase or Django-Q
SELECT cron.schedule('refresh-analytics', '0 * * * *', 'SELECT refresh_analytics()');
```

### Progressive Analytics Enhancement
```python
# analytics/service.py
class AnalyticsService:
    def get_dashboard_metrics(self):
        # MVP: Direct query to materialized views
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM findings WHERE status = 'vulnerable') as open_findings,
                    (SELECT compliance_rate FROM sla_compliance_summary WHERE context_id IS NULL) as overall_sla,
                    (SELECT mean_ttr FROM mttr_metrics WHERE business_unit IS NULL AND severity IS NULL) as overall_mttr
            """)
            return cursor.fetchone()
    
    # Future: Add caching, complex calculations
    @cache_result(timeout=300)
    def get_advanced_metrics(self):
        # Complex Python-based calculations
        pass
```

---

## Migration Strategy

### 1. Database Migration Path
```python
# migrations/prepare_for_enterprise.py
from django.db import migrations

class Migration(migrations.Migration):
    operations = [
        # Add fields needed for enterprise features
        migrations.AddField('findings', 'assigned_to', models.UUIDField(null=True)),
        migrations.AddField('findings', 'due_date', models.DateTimeField(null=True)),
        migrations.AddField('assets', 'owner_email', models.EmailField(null=True)),
        
        # Create new tables for future features
        migrations.RunSQL("""
            CREATE TABLE IF NOT EXISTS remediation_campaigns (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """),
    ]
```

### 2. Service Migration Path
```python
# Gradual migration from SQL to Python
class RiskCalculationService:
    def __init__(self):
        self.use_python = settings.FEATURES.get('python_risk_calc', False)
    
    def calculate_risk(self, finding_id):
        if self.use_python:
            # New Python implementation
            return self._python_calculate_risk(finding_id)
        else:
            # Current SQL implementation
            return self._sql_calculate_risk(finding_id)
    
    def _sql_calculate_risk(self, finding_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT calculate_finding_risk(%s)", [finding_id])
            return cursor.fetchone()[0]
    
    def _python_calculate_risk(self, finding_id):
        # Future complex logic
        finding = Finding.objects.get(id=finding_id)
        # ... complex calculations
```

### 3. API Evolution
```python
# Support both REST and GraphQL
urlpatterns = [
    path('api/v1/', include('api.urls')),  # REST
    path('graphql/', GraphQLView.as_view()),  # Future
]
```

---

## Security & Performance

### Security Measures
1. **Row Level Security (RLS)** in Supabase
2. **API Rate Limiting** with Django-ratelimit
3. **Input Validation** with serializers
4. **SQL Injection Prevention** via parameterized queries

### Performance Optimization
1. **Materialized Views** refreshed hourly
2. **JSONB Indexes** for fast queries
3. **Connection Pooling** with pgbouncer
4. **API Response Caching** with Redis

### Monitoring (Light)
```python
# Simple performance tracking
import time
from django.core.cache import cache

def track_query_performance(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        # Store in cache for monitoring
        cache.set(f'perf:{func.__name__}:last', duration)
        
        # Log slow queries
        if duration > 1.0:
            logger.warning(f'{func.__name__} took {duration:.2f}s')
        
        return result
    return wrapper
```

---

## Frontend Architecture

### lovable.dev-Driven UI
- All user-facing features (asset upload, findings management, dashboards, reports) are built in lovable.dev's visual builder.
- UI components (tables, forms, charts) are mapped to Django REST API endpoints and Supabase data sources.
- Auth, file upload, and permissions are managed via Supabase integration.
- Custom actions (e.g., trigger import, recalculate risk) are exposed as API endpoints and wired up in lovable.dev.
- For advanced customisation, lovable.dev supports embedding custom code blocks or widgets if needed.

#### Migration Path
- When requirements outgrow lovable.dev, migrate to a custom React/Vite frontend by reusing the same API endpoints and data models.

### Component Structure

src/
├── components/
│ ├── findings/
│ │ ├── FindingsList.tsx
│ │ ├── FindingDetail.tsx
│ │ └── FindingRiskBadge.tsx
│ ├── assets/
│ ├── reports/
│ └── shared/
├── hooks/
│ ├── useFindings.ts # React Query hooks
│ ├── useSLAStatus.ts
│ └── useMetrics.ts
├── services/
│ ├── api.ts # Axios client
│ └── auth.ts # Supabase auth
└── pages/
├── Dashboard.tsx
├── Findings.tsx
└── Reports.tsx


### Data Fetching Pattern
```typescript
// hooks/useFindings.ts
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';

export const useFindings = (filters?: FindingFilters) => {
  return useQuery({
    queryKey: ['findings', filters],
    queryFn: () => api.findings.list(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useUpdateFindingStatus = () => {
  return useMutation({
    mutationFn: ({ id, status }: UpdateStatusParams) => 
      api.findings.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries(['findings']);
      queryClient.invalidateQueries(['metrics']);
    },
  });
};
```