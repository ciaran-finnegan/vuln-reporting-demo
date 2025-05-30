Vulcan Cyber ExposureOS – Feature Summary
Vulcan Cyber ExposureOS is a comprehensive vulnerability and exposure management platform. It provides rich integration (“connectors”) with scanners and cloud tools, a unified asset/vulnerability database, contextual business mapping, risk prioritisation, automated remediation workflows, and SLA tracking. From a developer’s viewpoint, key features include:
Connectors & Data Ingestion: Vulcan ingests data from existing tools (vulnerability scanners, SCA/SAST tools, cloud providers, ticketing systems, etc.) via “connectors”
help.vulcancyber.com
help.vulcancyber.com
. Once configured, a connector pulls assets and vulnerability findings into the platform. Vulcan then correlates and consolidates this data (across tools and assets) to compute risk and remediation priority
help.vulcancyber.com
. Notably, Vulcan provides a Nessus File Connector that accepts Tenable’s .nessus XML reports (no direct Tenable API support)
help.vulcancyber.com
. This connector lets users upload a .nessus scan file (max 300 MB, UTF-8) and automatically integrates its data into Vulcan’s views
help.vulcancyber.com
help.vulcancyber.com
. In general, any connector can import asset and vuln data and feed Vulcan’s unified database.
Assets and Vulnerabilities Management: All ingested data is modelled as assets and vulnerabilities (findings). Assets represent systems or entities (hosts, code projects, images, websites, cloud resources, etc.) and are classified by type. For example, Hosts cover any networked device (PCs, servers, VMs, NAS, routers, IoT devices, etc.)
help.vulcancyber.com
. Code Projects are source-code repositories (GitHub, GitLab, SAST/SCA apps)
help.vulcancyber.com
. Websites are web apps (typically identified by domain or URL)
help.vulcancyber.com
. Images are container images/registries (Docker, OCI images)
help.vulcancyber.com
. Cloud Resources cover cloud assets (storage, networking, databases, etc.)
help.vulcancyber.com
. Each asset record can include identifiers (IP, hostname, resource ID) and tags. Vulnerabilities (CVE findings, scanner plugins, etc.) are linked to assets as “instances” (if the same vulnerability appears on multiple assets, each is a separate instance). Vulcan allows tracking each vuln instance’s details (severity, plugin ID, port, service, description, etc.) and the linkage to the asset. In sum, Vulcan’s data model lets developers query “assets” and their associated “vulnerabilities” seamlessly across all integrated sources.
Tagging and Business Context: Vulcan emphasizes business context via Asset Tags and Business Groups
help.vulcancyber.com
help.vulcancyber.com
help.vulcancyber.com
. Asset tags are simple labels (e.g. #external-facing or #linux-server) attached to assets to help filter and categorize them
help.vulcancyber.com
. Tags can be imported from connectors or created manually. Crucially, Vulcan can convert tags into dynamic “Business Groups,” which are named collections of assets (e.g. Finance, Production, or DevOps)
help.vulcancyber.com
. Business Groups segment the environment into organizational or functional units. They are used throughout Vulcan: for filtering vulnerabilities/assets, defining SLA policies, and driving reports. The platform supports rule-based tagging – for example, dynamic tags of the form key:value (like bizowner:alice@example.com) enable automated asset-owner assignment
help.vulcancyber.com
. In practice, developers can create Business Groups (via the UI or API) and associate assets by tag rules. Business Group membership then affects risk prioritisation, reporting, and workflows.
Risk Prioritisation and SPR: Vulcan computes a unified risk score for each vulnerability instance by correlating asset criticality, vulnerability severity, exploitability, and business context
help.vulcancyber.com
. An asset’s Security Posture Rating (SPR) and custom risk weights can be configured (per organisation) to influence scoring. This allows fine-tuning which issues get top priority. From a developer standpoint, the platform provides endpoints to retrieve risk scores and to configure risk weightings (e.g. adjusting the weight of a CVSS factor). Overall, risk prioritisation ensures that critical vulns on high-value assets bubble to the top.
SLA Management and Reporting: Teams can define Service-Level Agreement (SLA) policies for vulnerabilities by severity
help.vulcancyber.com
. For example, “Critical” issues might have a 3-day SLA, “High” 7 days, etc. Vulcan also supports SLAs per Business Group (different deadlines for different units)
help.vulcancyber.com
. The system tracks each vulnerability instance’s “time to remediation” against its SLA, marking it as “Exceeding” if not fixed in time
help.vulcancyber.com
. Analytics and dashboards show SLA compliance metrics. For example, analytic reports include metrics like “Vulnerability Instances Exceeded SLA by Business Group and Risk Level”
help.vulcancyber.com
, and “Campaign due-date compliance by Business Group”
help.vulcancyber.com
. This lets developers (and managers) measure how well remediation is keeping pace.
Remediation Campaigns and Automation: Every attempt to remediate a vulnerability (manual or automated) generates a remediation campaign
help.vulcancyber.com
. Developers can “take action” on one or more vulnerabilities or assets, opening tickets in integrated ticketing systems (JIRA, ServiceNow, email, Slack, etc.)
help.vulcancyber.com
. A campaign aggregates those actions and tracks their progress. Campaigns show which vulnerabilities/assets have been addressed and calculate a progress percentage (dynamic as fixes are made)
help.vulcancyber.com
. Campaigns can be created manually via the UI/API or automatically via Playbook Automations: for example, a Playbook rule might say “whenever a new Critical vuln is discovered in Business Group X, open a JIRA ticket automatically”
help.vulcancyber.com
. Thus, developers can use API/automation to auto-create campaigns and tickets under defined conditions. (Each campaign can include related data: assets affected, remediation solutions, due dates, SLA info, etc.)
Dashboard and Analytics: Vulcan provides a home dashboard of risk trends and quick stats, plus a Reports (Analytics) module
help.vulcancyber.com
. It offers pre-built widgets (e.g. Top Business Groups by Risk, SPR Compliance by Group, Assets by Business Group) as well as the ability to build custom reports (self-service analytics)
help.vulcancyber.com
. Developers can retrieve these via API or embed them in custom UIs. The system also provides SQL-based “magic search” and exportable CSVs for raw data.
API and Extensibility: The platform exposes a REST API (currently v1 and v2) for all operations
help.vulcancyber.com
. The APIs allow programmatic management of assets, vulnerabilities, groups, tags, campaigns, tickets, etc. Developers obtain an API token via the UI (OAuth2)
help.vulcancyber.com
 and then make authenticated requests. Documentation includes full OpenAPI specs (see [17†L39-L47]). This allows integration into custom tools or automated pipelines.
Security and Administration: Vulcan supports single sign-on (SSO) via SAML (e.g. Azure AD, Okta)
help.vulcancyber.com
 and role-based access control for fine-grained permissions. Audit logs track all activity
help.vulcancyber.com
. From a developer perspective, these ensure secure multi-user access.
In summary, Vulcan’s developer-facing features cover data ingestion (connectors), data model (assets/vulns), contextual tagging/groups, risk/SLA configuration, automation (playbooks, campaigns), reporting, and APIs
help.vulcancyber.com
help.vulcancyber.com
.
MVP Feature Subset
For the MVP demo, we focus on a core subset of features (drawing from Vulcan’s capabilities) that support Nessus import and basic vulnerability management. Specifically:
Tenable Nessus File Upload: Allow the user to upload a Tenable .nessus scan file (via the Nessus File Connector approach)
help.vulcancyber.com
. The backend should parse the file and ingest its data. This covers Connecting with Tenable scan data as a source.
Asset & Vulnerability Data Management: The system must display and manage the resulting asset and vulnerability data. This includes storing each asset and its details, and each vulnerability instance. Developers should be able to list and filter assets and vulnerabilities via the UI/API. Under the hood, the ingestion step will create asset records and vuln-instance records (as Vulcan does), so that existing and new data appear in all views
help.vulcancyber.com
help.vulcancyber.com
.
Support for All Asset Types: Even if the initial data is from Nessus hosts, the system’s data model should accommodate all asset types that Vulcan uses: Hosts, Code Projects, Websites, Container Images, Cloud Resources (and any others)
help.vulcancyber.com
help.vulcancyber.com
help.vulcancyber.com
. For completeness, the schema will include an asset type field or lookup so future connectors (SAST, DAST, CSPM, etc.) can feed in Code, Website, Image, or Cloud assets.
Business Groups & Asset Tagging: Implement asset tags and business groups. The user should be able to define tags on assets (free-form or imported). Asset tags can be used to create Business Groups, grouping assets by department or environment
help.vulcancyber.com
help.vulcancyber.com
. The system should support dynamic tag rules (e.g. tags of the form key:value) for auto-assignment of owners or groups
help.vulcancyber.com
. In practice, this means storing tag data and allowing simple rules/filters that assign assets to groups.
SLA and Remediation Reporting: Enable SLA configuration per severity and per business group
help.vulcancyber.com
, and report on SLA compliance. Also support tracking remediation campaigns. For MVP reporting, we will at least include: (a) tracking when each vuln instance was opened and whether it exceeds its SLA target, and (b) the ability to view or export remediation campaign status. These correspond to Vulcan’s reporting features like “Campaign due-date compliance” and “Instances Exceeded SLA”
help.vulcancyber.com
.
In summary, the MVP must handle Nessus import, show assets & vulns, cover Vulcan’s asset categories, implement business-group/tag context, and include basic SLA/campaign reporting as listed above
help.vulcancyber.com
help.vulcancyber.com
help.vulcancyber.com
.
Naming Conventions (for Developers)
To ensure clarity and consistency, we will choose developer-friendly names for tables and features:
Asset (asset) – instead of Vulcan’s “VCP-Host” etc. Fields include name, type, ip_address, etc.
AssetType (asset_type) – lookup table for types (Host, Code, Website, Image, Cloud).
Vulnerability (vulnerability) – represents a unique vulnerability (CVE or plugin).
VulnInstance (vulnerability_instance) – a specific finding on an asset (linking asset_id to vulnerability_id plus details like port, severity, description). This replaces Vulcan’s “finding instance.”
BusinessGroup (business_group) – a named collection of assets.
AssetTag (asset_tag) – tags (labels) attached to assets; include a flag or separate fields for dynamic key/value (e.g. dynamic_key, dynamic_value) if implementing owner tags
help.vulcancyber.com
.
AssetTagAssignment (asset_asset_tag) – many-to-many linking assets to tags.
SLAPolicy (sla_policy) – defines days-per-severity for SLAs (global or per BusinessGroup).
RemediationCampaign (campaign) – tracks a remediation effort (with name, start_date, due_date, progress_percent, etc.).
CampaignVuln (campaign_vulnerability) – links campaigns to the vuln instances it covers.
Connector (connector) and Upload (upload) – representing a data source and uploaded Nessus file metadata (e.g. upload_date, file_url).
This naming aligns with typical Django conventions (snake_case, clear nouns) and is a one-to-one rename of Vulcan’s UI terms into DB model terms. For example, Vulcan’s “Tag” and “Business Group” become asset_tag and business_group tables, respectively.
Implementation Plan
Shared Database Schema (Postgres)
We will use a single Postgres database (managed by Supabase) shared by the Django backend and Supabase’s auth/storage. The schema includes tables for assets, vulnerabilities, groups, etc. A proposed schema (DDL) is below:
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
    ip_address       INET NULL,            -- optional IP
    hostname         VARCHAR(255) NULL,
    business_group_id INTEGER REFERENCES business_group(id),
    UNIQUE(name, asset_type_id)
);

-- Asset tags (static or dynamic)
CREATE TABLE asset_tag (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    dynamic_key   VARCHAR(100) NULL,  -- e.g. 'bizowner'
    dynamic_value VARCHAR(255) NULL   -- e.g. 'alice@example.com'
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
    external_id VARCHAR(100) NULL,  -- e.g. pluginID or CVE
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    severity    VARCHAR(10) NULL,   -- e.g. 'Critical', 'High' etc.
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
    -- Status (e.g. Open, Fixed) could be added if needed
    UNIQUE(asset_id, vulnerability_id, port, service)
);

-- SLA policies (global or per group/severity)
CREATE TABLE sla_policy (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    severity     VARCHAR(10) NOT NULL,  -- 'Critical', 'High', etc.
    days_allowed INTEGER NOT NULL,
    business_group_id INTEGER REFERENCES business_group(id)
);
-- (Optionally unique on name or (group,severity))

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
    uploader      UUID,           -- Supabase user ID of uploader
    file_url      TEXT NOT NULL   -- e.g. Supabase storage URL
    -- Additional metadata (scan name, etc.) can be stored if desired
);
This schema covers the MVP scope. We renamed tables and fields for developer clarity (e.g. campaign instead of “campaigns”, vulnerability_instance for findings, etc.). Asset ownership (dynamic tags) are captured via asset_tag.dynamic_key/value.
Backend (Django)
Django Models & Migrations: Implement models corresponding to the above schema in Django. Use Django ORM with the shared Postgres database (the same one Supabase uses, but in a separate schema or with careful migrations). Supabase’s auth.users table will manage user accounts; we will reference uploader UUID in upload to link to Supabase user IDs.
Authentication (Supabase): Use Supabase Auth. The frontend will authenticate via Supabase (email/password or SSO) and include the user’s JWT in API requests. The Django backend will verify Supabase JWTs (using Supabase’s public keys) or use Supabase’s HTTP middleware to authenticate requests. No separate Django auth models are needed.
Connectors – Nessus Upload: Implement an endpoint (e.g. POST /uploads/nessus) to receive a .nessus file. The uploaded file will be stored via the Supabase Storage API, returning a secure file_url. We then insert a record into upload and trigger processing.
ETL/Parsing Logic: After storing the file, parse it (XML) to extract host and vuln data. Key mapping (see “ETL Mapping” below) will create or find asset records and vulnerability records, then create vulnerability_instance rows. Use Django ORM within a transaction to populate the database.
Business Groups & Tags: Provide endpoints (and admin UI) to create and manage business_group and asset_tag records. Also implement logic so that when assets are tagged (or new uploads occur), any dynamic tag like key:value can assign properties (e.g. set business_group_id or another field). For MVP, we might simply allow manual assignment of assets to groups/tags.
SLA Policies: Endpoints to create/read sla_policy entries. A service can automatically check each instance’s first_seen against its SLA (and business group) and mark it as exceeding SLA.
Campaigns: CRUD endpoints for campaign and the linking table. When a campaign is created (e.g. via API or “take action” UI), it should allow specifying related vuln instances. (Automated playbooks can add to existing campaigns, but initial MVP can assume manual creation of a campaign.)
API Endpoints (OpenAPI): Develop REST endpoints for all above. Key endpoints include:
POST /uploads/nessus – upload Nessus file (multipart form-data).
GET /assets, GET /assets/{id} – list assets and view asset details (including linked vulnerabilities).
GET /vulnerabilities, GET /vulnerabilities/{id} – list unique vulnerabilities.
GET /asset-types – list supported types (Host, Code, …).
GET/POST /business-groups – manage Business Groups.
GET/POST /asset-tags – manage asset tags (static or dynamic).
GET/POST /campaigns – manage remediation campaigns.
GET/POST /sla-policies – manage SLA definitions.
A sample OpenAPI 3.1 spec (YAML) is provided below for these endpoints. This spec can be imported or extended by developers to auto-generate client/server code.
openapi: 3.1.0
info:
  title: Vulcan Cyber MVP API
  version: 1.0.0
  description: API for asset/vulnerability management and Nessus upload.
paths:
  /uploads/nessus:
    post:
      summary: Upload Tenable .nessus file
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      responses:
        '200':
          description: Nessus file accepted and data imported

  /assets:
    get:
      summary: List assets
      responses:
        '200':
          description: List of assets
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Asset'
  /assets/{assetId}:
    get:
      summary: Get asset details
      parameters:
        - name: assetId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Asset detail
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Asset'
  /vulnerabilities:
    get:
      summary: List vulnerabilities
      responses:
        '200':
          description: List of vulnerabilities
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Vulnerability'
  /vulnerabilities/{vulnId}:
    get:
      summary: Get vulnerability details
      parameters:
        - name: vulnId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Vulnerability detail
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Vulnerability'
  /asset-types:
    get:
      summary: List asset types
      responses:
        '200':
          description: Supported asset types
          content:
            application/json:
              schema:
                type: array
                items:
                  type: string

  /business-groups:
    get:
      summary: List business groups
      responses:
        '200':
          description: Business groups
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/BusinessGroup'
    post:
      summary: Create a new business group
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BusinessGroupCreate'
      responses:
        '201':
          description: Business group created

  /asset-tags:
    get:
      summary: List asset tags
      responses:
        '200':
          description: Asset tags
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/AssetTag'
    post:
      summary: Create a new asset tag
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AssetTagCreate'
      responses:
        '201':
          description: Asset tag created

  /campaigns:
    get:
      summary: List remediation campaigns
      responses:
        '200':
          description: Campaigns
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Campaign'
    post:
      summary: Create a remediation campaign
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CampaignCreate'
      responses:
        '201':
          description: Campaign created

  /sla-policies:
    get:
      summary: List SLA policies
      responses:
        '200':
          description: SLA policies
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/SlaPolicy'
    post:
      summary: Create SLA policy
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SlaPolicyCreate'
      responses:
        '201':
          description: SLA policy created

components:
  schemas:
    Asset:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        type:
          type: string
        business_group_id:
          type: integer
        tags:
          type: array
          items:
            type: string
    Vulnerability:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        description:
          type: string
        severity:
          type: string
    BusinessGroup:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
    BusinessGroupCreate:
      type: object
      properties:
        name:
          type: string
      required:
        - name
    AssetTag:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
    AssetTagCreate:
      type: object
      properties:
        name:
          type: string
        dynamic_key:
          type: string
        dynamic_value:
          type: string
      required:
        - name
    Campaign:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        status:
          type: string
        start_date:
          type: string
          format: date
        due_date:
          type: string
          format: date
    CampaignCreate:
      type: object
      properties:
        name:
          type: string
        description:
          type: string
        due_date:
          type: string
          format: date
      required:
        - name
    SlaPolicy:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        severity:
          type: string
        days_allowed:
          type: integer
    SlaPolicyCreate:
      type: object
      properties:
        name:
          type: string
        severity:
          type: string
        days_allowed:
          type: integer
      required:
        - name
        - severity
        - days_allowed
This OpenAPI snippet defines all required MVP endpoints and data schemas. Developers can use it with tools like Swagger or Redoc, or generate client/server stubs.
ETL Mapping Strategy (Nessus to Schema)
The ETL process will parse the .nessus XML and map fields into our schema. A repeatable pattern will be used for future connectors as well. For Nessus specifically:
Asset Extraction: Each <ReportHost> corresponds to an asset. The name attribute (often an IP or hostname) is mapped to asset.name. Within <HostProperties>, tags like <tag name="host-fqdn">, <tag name="hostname">, and <tag name="host-ip"> provide supplementary info (asset.hostname, asset.ip_address). Use these to match existing assets or create new ones. (E.g. if an asset with that IP/name already exists, reuse it.)
Vulnerability Extraction: Each <ReportItem> under a host is one vulnerability instance. Fields map as follows:
pluginID → vulnerability.external_id (or just create unique ID).
pluginName → vulnerability.name.
severity (0–4 or text) → vulnerability.severity.
pluginFamily and other tags can go into vulnerability.description or left out.
Other fields like svc_name, protocol, port → store in vulnerability_instance.service, .protocol, .port.
Any <description> or plugin output in the XML becomes vulnerability_instance.plugin_output.
If a vulnerability (by external_id) already exists in the table, link to it; otherwise insert a new vulnerability. Then always insert a new vulnerability_instance linking it to the current asset.
SLA and Groups: If the Nessus file or configured business logic indicates an asset should belong to a group or have tags, apply those rules here. For MVP, we can allow manual tag assignment after import, but dynamic tags (key:value) could be detected here too (e.g. parse any Nessus “tag” that starts with “#”).
Repeatability: This parsing code should be modular so that adding a new source (e.g. a JSON report from Qualys) only requires writing a similar mapping for that source. The core logic always results in Assets and VulnInstances inserted into the same schema.
By following this ETL pattern, data from Nessus will populate the asset, vulnerability, and vulnerability_instance tables correctly. Future connectors (CSV/XML/JSON) will follow analogous mappings (map fields to columns, insert or update records).
Frontend (React)
Stack: Use React with Vite, Tailwind CSS, and shadcn/ui components for a clean developer-friendly UI.
Auth: Integrate Supabase Auth. Upon login, the app receives a JWT which it includes in API requests.
Pages/Components:
Login: (via Supabase UI).
Asset List/View: Table of assets with filters (type, group, tags). Clicking an asset shows its details and linked vulnerabilities.
Vulnerability List/View: List of unique vulnerabilities (CVE or plugin-based) with basic details.
Nessus Upload: A form to select and upload a .nessus file. On success, show a message and refresh asset/vuln lists.
Business Groups/Tags Management: Simple forms to create/edit groups and tags, and to assign tags to assets.
Campaign Dashboard: Interface to create a new campaign (specify name, due date, select vulnerabilities/assets to include) and list existing campaigns with progress.
Reports: A page showing SLA compliance metrics (e.g. number of overdue issues per group). Could fetch data from /vulnerability_instances with SLA logic on frontend or a custom report endpoint.
API Integration: Use the OpenAPI spec to generate TypeScript clients or call endpoints directly (with fetch/axios including the Supabase JWT in headers).
Backlog of Tasks
To implement the above, a structured backlog of tasks is:
Project Setup: Initialize Git repo, set up Django project and React project (Vite + Tailwind + shadcn/ui). Configure Python virtualenv, node environment.
Database Setup:
Create the Postgres database (on Supabase) and run initial schema migrations.
Populate asset_type table with required types (Host, Code, Website, Image, Cloud).
Django Models: Implement models for Asset, AssetType, Vulnerability, VulnerabilityInstance, BusinessGroup, AssetTag, SLApolicies, Campaign, etc., matching the schema above. Generate and run migrations.
Authentication Integration: Configure Supabase Auth. In Django, implement JWT verification middleware (or use a library) to authenticate requests against Supabase.
Nessus Upload Endpoint:
Write the POST /uploads/nessus endpoint in Django. It should accept a multipart file.
Integrate with Supabase Storage: upload the file to a bucket, get the URL, and save upload record.
Trigger the ETL parser on the file (synchronously or via background job). Return success/failure.
ETL Parser: Implement XML parsing of the .nessus file (use Python’s xml.etree or lxml). Map fields to Django models as described (asset lookup/insert, vulnerability lookup/insert, instance insert).
API Endpoints: Implement the rest of the endpoints in Django REST Framework (or FastAPI) according to the OpenAPI spec. Ensure to apply authentication. Endpoints include:
GET/POST for assets, vulnerabilities (CRUD as needed).
GET asset-types (static list).
GET/POST for business-groups and asset-tags.
GET/POST for campaigns.
GET/POST for sla-policies.
Frontend UI – Authentication: Set up Supabase client in React. Create login/signup flows. Ensure tokens are stored and sent.
Frontend – Asset & Vuln Pages:
Build AssetList and AssetDetail components. Fetch from /assets endpoints.
Build VulnerabilityList/VulnDetail similarly.
Frontend – Upload Form: Create an upload form to POST to /uploads/nessus. Handle file selection and show progress/confirmation.
Frontend – Tags/Groups Management: Build simple forms to list and create Business Groups (/business-groups) and Asset Tags (/asset-tags). Add ability to assign tags to an asset (e.g. multi-select on AssetDetail).
Frontend – Campaigns: Build CampaignList and CampaignCreate components. Allow selecting multiple vulnerability instances or assets and adding to a campaign.
Reporting/SLA: Implement a basic dashboard or reports page. For MVP, this could be:
List of overdue vulnerabilities (computed by frontend by comparing each instance’s first_seen + SLA to today).
Chart or count of instances per group.
Alternatively, add an endpoint (GET /reports/sla) that returns SLA stats, and call that.
Testing: Write unit and integration tests for backend (Django) and frontend. Ensure CSV/XML exports (if any) work. Test the Nessus upload and parsing with a sample file.
Documentation: Document API endpoints (the OpenAPI spec helps), data models, and setup instructions.
Deployment: Containerize or otherwise prepare the application for deployment. Ensure the Django backend can connect to Supabase DB and Storage.
Each task above is scoped as a clear unit of work (schema design, API implementation, UI component, etc.). By following this plan, developers can build the MVP in a modular, testable way. Sources: Information on Vulcan features is drawn from the official documentation
help.vulcancyber.com
help.vulcancyber.com
help.vulcancyber.com
help.vulcancyber.com
help.vulcancyber.com
. The API spec and schema above are designed based on those docs and the MVP requirements.
Citations
Favicon
Connectors and Supported Integrations | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/3438569-connectors-and-supported-integrations
Favicon
Connectors and Supported Integrations | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/3438569-connectors-and-supported-integrations
Favicon
Nessus File Connector | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/5179523-nessus-file-connector
Favicon
Nessus File Connector | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/5179523-nessus-file-connector
Favicon
Nessus File Connector | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/5179523-nessus-file-connector
Favicon
Assets Categorization into Types | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/9117819-assets-categorization-into-types
Favicon
Assets Categorization into Types | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/9117819-assets-categorization-into-types
Favicon
Assets Categorization into Types | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/9117819-assets-categorization-into-types
Favicon
Assets Categorization into Types | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/9117819-assets-categorization-into-types
Favicon
Assets Categorization into Types | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/9117819-assets-categorization-into-types
Favicon
Business Groups and Asset Tags | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/6394698-business-groups-and-asset-tags
Favicon
Business Groups and Asset Tags | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/6394698-business-groups-and-asset-tags
Favicon
Business Groups and Asset Tags | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/6394698-business-groups-and-asset-tags
Favicon
Dynamic properties and ticket assignment | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/6870472-dynamic-properties-and-ticket-assignment
Favicon
Risk Calculation and Prioritization | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/6224809-risk-calculation-and-prioritization
Favicon
SLA Policies | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/5957728-sla-policies
Favicon
SLA Policies | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/5957728-sla-policies
Favicon
Business Groups and Asset Tags | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/6394698-business-groups-and-asset-tags
Favicon
Campaigns - Create, Track and Manage Remediation Campaigns | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/5352974-campaigns-create-track-and-manage-remediation-campaigns
Favicon
Campaigns - Create, Track and Manage Remediation Campaigns | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/5352974-campaigns-create-track-and-manage-remediation-campaigns
Favicon
Campaigns - Create, Track and Manage Remediation Campaigns | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/5352974-campaigns-create-track-and-manage-remediation-campaigns
Favicon
Campaigns - Create, Track and Manage Remediation Campaigns | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/5352974-campaigns-create-track-and-manage-remediation-campaigns
Favicon
Dashboard and Reports | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/collections/4027995-dashboard-and-reports
Favicon
Working with Vulcan Cyber ExposureOS API v1 | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/3438656-working-with-vulcan-cyber-exposureos-api-v1
Favicon
Working with Vulcan Cyber ExposureOS API v1 | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/3438656-working-with-vulcan-cyber-exposureos-api-v1
Favicon
Settings and Account | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/collections/4028009-settings-and-account
Favicon
Settings and Account | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/collections/4028009-settings-and-account
Favicon
Assets Categorization into Types | Vulcan Cyber ExposureOS™

https://help.vulcancyber.com/en/articles/9117819-assets-categorization-into-types
All Sources
