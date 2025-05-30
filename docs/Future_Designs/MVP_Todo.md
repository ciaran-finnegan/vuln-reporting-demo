## **MVP_Todo.md**

## Risk Radar – MVP Implementation Plan

### Full Feature Set (for Future Enterprise Migration)
Risk Radar provides:
- **Connectors & Data Ingestion** (scanners, SCA/SAST, cloud, ticketing, etc.)
- **Unified Asset & Vulnerability Database** (all asset types, findings)
- **Business Context** (tags, business groups)
- **Risk Prioritisation** (risk scoring, custom weights)
- **SLA Management & Reporting** (per severity/group, compliance tracking)
- **Remediation Campaigns & Automation** (campaigns, playbooks)
- **Dashboard & Analytics** (pre-built/custom reports)
- **API & Extensibility** (REST API, OpenAPI spec)
- **Security & Administration** (SSO, RBAC, audit logs)

### MVP Feature Subset
For the MVP, we will implement:
- **Nessus File Upload** (user uploads .nessus scan, data ingested)
- **Asset & Vulnerability Data Management** (store, display, manage assets and findings)
- **Support for All Asset Types** (hosts, code, websites, images, cloud)
- **Business Groups & Asset Tagging** (define tags/groups, dynamic tag rules)
- **SLA and Remediation Reporting** (configure SLA, track compliance, basic campaigns)

---

## **MVP_Todo.md**

```markdown
# Risk Radar - MVP Implementation Todo
## Fast-Track Development with Migration Path

### Quick Start Checklist
- [ ] Fork this repository
- [ ] Set up Supabase project
- [ ] Configure environment variables
- [ ] Run initial setup script
- [ ] Deploy to Vercel/Netlify

---

## Week 1: Foundation & Setup

### Day 1-2: Project Initialization

#### Backend Setup (4 hours)
- [ ] Create Django project
  ```bash
  django-admin startproject vulnmgmt
  cd vulnmgmt
  python -m venv venv
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  ```

- [ ] Install core dependencies
  ```bash
  pip install django djangorestframework django-cors-headers
  pip install psycopg2-binary django-environ supabase
  pip install django-q redis django-redis
  pip install lxml openpyxl  # For file parsing
  ```

- [ ] Create Django apps
  ```bash
  python manage.py startapp core
  python manage.py startapp assets
  python manage.py startapp vulnerabilities
  python manage.py startapp analytics
  ```

- [ ] Configure settings.py
  ```python
  # settings.py
  import environ
  env = environ.Env()
  
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': env('DB_NAME'),
          'USER': env('DB_USER'),
          'PASSWORD': env('DB_PASSWORD'),
          'HOST': env('DB_HOST'),
          'PORT': env('DB_PORT', default='5432'),
      }
  }
  
  # Django-Q for background tasks
  Q_CLUSTER = {
      'name': 'vulnmgmt',
      'workers': 2,
      'recycle': 500,
      'timeout': 60,
      'compress': True,
      'save_limit': 250,
      'queue_limit': 500,
      'cpu_affinity': 1,
      'label': 'Django Q',
      'redis': env('REDIS_URL', default='redis://localhost:6379/0')
  }
  ```

#### Supabase Setup (2 hours)
- [ ] Create Supabase project
- [ ] Save connection details
- [ ] Enable Row Level Security
- [ ] Create initial RLS policies
  ```sql
  -- Enable RLS on all tables
  ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
  ALTER TABLE vulnerabilities ENABLE ROW LEVEL SECURITY;
  ALTER TABLE findings ENABLE ROW LEVEL SECURITY;
  
  -- Basic read policy (refine later)
  CREATE POLICY "Enable read for authenticated users" ON assets
    FOR SELECT USING (auth.role() = 'authenticated');
  ```

- [ ] Set up storage bucket for file uploads
  ```sql
  INSERT INTO storage.buckets (id, name, public) 
  VALUES ('nessus-uploads', 'nessus-uploads', false);
  ```

#### Frontend Setup (2 hours)
- [ ] Set up lovable.dev project
  - Sign up at [lovable.dev](https://lovable.dev)
  - Create a new project and connect it to your Supabase instance (for auth, file storage, and direct DB access)
  - Connect Django REST API endpoints (for business logic, findings, reports, etc.)
  - Configure environment variables for API URLs and Supabase keys

- [ ] Build UI in lovable.dev
  - Use the visual builder to create pages for asset management, findings, dashboards, and reports
  - Map API endpoints to tables, forms, and charts
  - Set up authentication and permissions using Supabase integration
  - Configure file upload components for Nessus import (using Supabase Storage)
  - Add custom actions to trigger imports, recalculate risk, or generate reports via API endpoints

- [ ] Test end-to-end flows in lovable.dev
  - Ensure all CRUD operations, imports, and reports work via the lovable.dev UI
  - Refine UI/UX as needed using lovable.dev's design tools

### Day 3-4: Database Schema

#### Create Migration Files (4 hours)
- [ ] Use developer-friendly naming conventions for all tables and fields (asset, asset_type, vulnerability_instance, business_group, asset_tag, campaign, etc.) as per the schema in temp.md and MVP_App_Architecture.md
- [ ] Run initial database setup
  ```sql
  -- 001_initial_schema.sql
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
  
  -- Core tables with JSONB for flexibility
  CREATE TABLE assets (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name VARCHAR(255) NOT NULL,
      asset_type VARCHAR(50) NOT NULL CHECK (asset_type IN ('host', 'code_project', 'website', 'image', 'cloud_resource')),
      status VARCHAR(50) DEFAULT 'active',
      metadata JSONB DEFAULT '{}',
      created_at TIMESTAMPTZ DEFAULT NOW(),
      updated_at TIMESTAMPTZ DEFAULT NOW()
  );
  
  CREATE TABLE vulnerabilities (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      external_id VARCHAR(255) UNIQUE,
      title VARCHAR(500) NOT NULL,
      description TEXT,
      severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
      cvss_score DECIMAL(3,1),
      metadata JSONB DEFAULT '{}',
      created_at TIMESTAMPTZ DEFAULT NOW()
  );
  
  CREATE TABLE findings (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      vulnerability_id UUID REFERENCES vulnerabilities(id),
      asset_id UUID REFERENCES assets(id),
      status VARCHAR(50) DEFAULT 'vulnerable',
      risk_score DECIMAL(5,2),
      metadata JSONB DEFAULT '{}',
      first_seen TIMESTAMPTZ DEFAULT NOW(),
      last_seen TIMESTAMPTZ DEFAULT NOW(),
      fixed_at TIMESTAMPTZ,
      UNIQUE(vulnerability_id, asset_id, (metadata->>'port'), (metadata->>'protocol'))
  );
  ```

#### Create Django Models (2 hours)
- [ ] Create base model class
  ```python
  # core/models.py
  from django.db import models
  import uuid
  
  class BaseModel(models.Model):
      id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)
      
      class Meta:
          abstract = True
  ```

- [ ] Create Asset model
  ```python
  # assets/models.py
  from django.contrib.postgres.fields import JSONField
  from core.models import BaseModel
  
  class Asset(BaseModel):
      ASSET_TYPES = [
          ('host', 'Host'),
          ('code_project', 'Code Project'),
          ('website', 'Website'),
          ('image', 'Container Image'),
          ('cloud_resource', 'Cloud Resource'),
      ]
      
      name = models.CharField(max_length=255)
      asset_type = models.CharField(max_length=50, choices=ASSET_TYPES)
      status = models.CharField(max_length=50, default='active')
      metadata = models.JSONField(default=dict)
      
      class Meta:
          db_table = 'assets'
          indexes = [
              models.Index(fields=['asset_type', 'status']),
          ]
  ```

#### Create Materialized Views (2 hours)
- [ ] Create views for analytics
  ```sql
  -- 002_analytics_views.sql
  -- SLA Status View
  CREATE MATERIALIZED VIEW sla_status AS
  WITH policy_mapping AS (
      -- ... (see architecture doc)
  );
  
  -- MTTR Metrics View
  CREATE MATERIALIZED VIEW mttr_metrics AS
  WITH remediation_times AS (
      -- ... (see architecture doc)
  );
  
  -- Create refresh function
  CREATE OR REPLACE FUNCTION refresh_analytics()
  RETURNS void AS $$
  BEGIN
      REFRESH MATERIALIZED VIEW CONCURRENTLY sla_status;
      REFRESH MATERIALIZED VIEW CONCURRENTLY mttr_metrics;
  END;
  $$ LANGUAGE plpgsql;
  ```

### Day 5: Core Services

#### Authentication Service (3 hours)
- [ ] Create Supabase middleware
  ```python
  # core/middleware.py
  from django.utils.deprecation import MiddlewareMixin
  from supabase import create_client
  import os
  
  class SupabaseAuthMiddleware(MiddlewareMixin):
      def __init__(self, get_response):
          self.get_response = get_response
          self.supabase = create_client(
              os.environ.get('SUPABASE_URL'),
              os.environ.get('SUPABASE_ANON_KEY')
          )
      
      def process_request(self, request):
          auth_header = request.headers.get('Authorization', '')
          if auth_header.startswith('Bearer '):
              token = auth_header.split(' ')[1]
              try:
                  user = self.supabase.auth.get_user(token)
                  request.user = user
              except Exception:
                  request.user = None
  ```

#### Base Service Class (2 hours)
- [ ] Create service foundation
  ```python
  # core/services.py
  from django.db import connection
  from django.core.cache import cache
  import logging
  
  class BaseService:
      def __init__(self, user=None):
          self.user = user
          self.logger = logging.getLogger(self.__class__.__name__)
      
      def execute_sql(self, sql, params=None):
          with connection.cursor() as cursor:
              cursor.execute(sql, params or [])
              columns = [col[0] for col in cursor.description]
              return [dict(zip(columns, row)) for row in cursor.fetchall()]
      
      def call_db_function(self, func_name, *args):
          placeholders = ','.join(['%s'] * len(args))
          sql = f"SELECT {func_name}({placeholders})"
          return self.execute_sql(sql, args)[0]
  ```

---

## Week 2: Nessus Import & Asset Management

### Day 6-7: Nessus Parser

#### Create Parser Service (6 hours)
- [ ] Implement ETL mapping strategy:
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

#### Create Import Service (4 hours)
- [ ] Implement import pipeline
  ```python
  # vulnerabilities/services/import_service.py
  from django.db import transaction
  from assets.models import Asset
  from vulnerabilities.models import Vulnerability, Finding
  
  class NessusImportService(BaseService):
      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.parser = NessusParser()
          self.stats = {'assets': 0, 'vulnerabilities': 0, 'findings': 0}
      
      @transaction.atomic
      def import_file(self, file_path: str, job_id: str):
          """Import Nessus file with progress tracking"""
          try:
              for host_data in self.parser.parse_file(file_path):
                  asset = self._process_asset(host_data)
                  self.stats['assets'] += 1
                  
                  for vuln_data in host_data['vulnerabilities']:
                      vuln = self._process_vulnerability(vuln_data)
                      finding = self._process_finding(asset, vuln, vuln_data)
                      self.stats['findings'] += 1
                  
                  # Update progress
                  self._update_job_progress(job_id, self.stats)
                  
          except Exception as e:
              self.logger.error(f"Import failed: {e}")
              raise
      
      def _process_asset(self, host_data):
          # Create or update asset
          asset, created = Asset.objects.update_or_create(
              name=host_data['name'],
              asset_type='host',
              defaults={
                  'metadata': {
                      'ip_address': host_data['properties'].get('host-ip'),
                      'os': host_data['properties'].get('operating-system'),
                      'fqdn': host_data['properties'].get('host-fqdn'),
                  }
              }
          )
          return asset
  ```

### Day 8-9: Asset Management APIs

#### Create Asset ViewSet (4 hours)
- [ ] Ensure endpoints and serializers use developer-friendly names and schema (asset, asset_type, business_group, asset_tag, etc.) for easy mapping in lovable.dev
- [ ] Implement REST endpoints
  ```python
  # assets/views.py
  from rest_framework import viewsets, filters
  from rest_framework.decorators import action
  from rest_framework.response import Response
  
  class AssetViewSet(viewsets.ModelViewSet):
      queryset = Asset.objects.all()
      serializer_class = AssetSerializer
      filter_backends = [filters.SearchFilter, filters.OrderingFilter]
      search_fields = ['name', 'metadata']
      ordering_fields = ['name', 'created_at', 'updated_at']
      
      @action(detail=True, methods=['get'])
      def vulnerabilities(self, request, pk=None):
          """Get vulnerabilities for an asset"""
          asset = self.get_object()
          findings = Finding.objects.filter(
              asset=asset,
              status='vulnerable'
          ).select_related('vulnerability')
          
          data = [{
              'id': f.vulnerability.id,
              'title': f.vulnerability.title,
              'severity': f.vulnerability.severity,
              'risk_score': f.risk_score,
              'first_seen': f.first_seen
          } for f in findings]
          
          return Response(data)
      
      @action(detail=False, methods=['post'])
      def bulk_tag(self, request):
          """Apply tags to multiple assets"""
          asset_ids = request.data.get('asset_ids', [])
          tag_id = request.data.get('tag_id')
          
          # Use raw SQL for performance
          with connection.cursor() as cursor:
              cursor.execute("""
                  INSERT INTO asset_contexts (asset_id, context_id, assigned_by)
                  SELECT unnest(%s::uuid[]), %s, 'manual'
                  ON CONFLICT DO NOTHING
              """, [asset_ids, tag_id])
          
          return Response({'status': 'success'})
  ```

#### Create Business Context APIs (4 hours)
- [ ] Tag and Business Unit management
  ```python
  # assets/views.py
  class BusinessContextViewSet(viewsets.ModelViewSet):
      queryset = BusinessContext.objects.all()
      serializer_class = BusinessContextSerializer
      
      @action(detail=True, methods=['post'])
      def add_rule(self, request, pk=None):
          """Add dynamic assignment rule"""
          context = self.get_object()
          rule_data = request.data
          
          # Validate rule
          rule_type = rule_data.get('type')
          if rule_type == 'ip_range':
              # Validate IP range
              pass
          elif rule_type == 'name_pattern':
              # Validate regex
              pass
          
          # Store rule in JSONB
          context.rules = context.rules or []
          context.rules.append(rule_data)
          context.save()
          
          # Apply rule to existing assets
          self._apply_rule_to_assets(context, rule_data)
          
          return Response({'status': 'rule added'})
  ```

### Day 10: Frontend Asset Views

#### Asset List Component (4 hours)
- [ ] Build asset list/table in lovable.dev
  - Use the table component to display assets from the API
  - Add columns for name, type, IP address, vulnerabilities, etc.
  - Enable search, filtering, and sorting using lovable.dev's built-in features
  - Add actions for viewing asset details, tagging, and bulk operations

#### File Upload Component (2 hours)
- [ ] Build file upload interface in lovable.dev
  - Use the file upload widget, connect it to Supabase Storage
  - On upload, trigger the Django API endpoint to start Nessus import
  - Show progress and import results in the UI

### Day 11-12: Risk Calculation

#### Implement Risk Service (4 hours)
- [ ] Create risk calculation
  ```python
  # vulnerabilities/services/risk_service.py
  class RiskCalculationService(BaseService):
      def calculate_finding_risk(self, finding_id: str) -> float:
          """Calculate risk score for a finding"""
          # For MVP, use database function
          result = self.call_db_function('calculate_finding_risk', finding_id)
          
          # Update finding
          Finding.objects.filter(id=finding_id).update(
              risk_score=result['risk_score']
          )
          
          return result['risk_score']
      
      def bulk_recalculate_risks(self, context_id: str = None):
          """Recalculate risks after context changes"""
          sql = """
              UPDATE findings f
              SET risk_score = calculate_finding_risk(f.id)
              FROM assets a
              WHERE f.asset_id = a.id
              AND f.status = 'vulnerable'
          """
          
          if context_id:
              sql += " AND EXISTS (SELECT 1 FROM asset_contexts ac WHERE ac.asset_id = a.id AND ac.context_id = %s)"
              self.execute_sql(sql, [context_id])
          else:
              self.execute_sql(sql)
  ```

#### Create Database Functions (2 hours)
- [ ] Implement risk calculation in SQL
  ```sql
  -- 003_risk_functions.sql
  CREATE OR REPLACE FUNCTION calculate_finding_risk(p_finding_id UUID)
  RETURNS TABLE(risk_score DECIMAL) AS $$
  DECLARE
      v_technical DECIMAL;
      v_threat DECIMAL;
      v_business DECIMAL;
  BEGIN
      -- Get scores
      SELECT 
          COALESCE(v.cvss_score * 10, 0),
          CASE 
              WHEN v.metadata->>'exploitable' = 'true' THEN 100 
              WHEN v.metadata->>'cisa_known' = 'true' THEN 100
              ELSE 0 
          END,
          COALESCE(MAX(CASE 
              WHEN bc.impact_level = 'high' THEN 100
              WHEN bc.impact_level = 'medium' THEN 50
              ELSE 0
          END), 0)
      INTO v_technical, v_threat, v_business
      FROM findings f
      JOIN vulnerabilities v ON f.vulnerability_id = v.id
      JOIN assets a ON f.asset_id = a.id
      LEFT JOIN asset_contexts ac ON a.id = ac.asset_id
      LEFT JOIN business_contexts bc ON ac.context_id = bc.id
      WHERE f.id = p_finding_id
      GROUP BY v.cvss_score, v.metadata;
      
      -- Calculate weighted score
      RETURN QUERY
      SELECT ROUND(
          v_technical * 0.4 + 
          v_threat * 0.4 + 
          v_business * 0.2, 
          2
      )::DECIMAL;
  END;
  $$ LANGUAGE plpgsql;
  ```

### Day 13-14: SLA Implementation

#### Create SLA Service (4 hours)
- [ ] Implement SLA tracking
  ```python
  # vulnerabilities/services/sla_service.py
  class SLAService(BaseService):
      def apply_sla_policy(self, finding_id: str):
          """Apply SLA policy to a finding"""
          # Get applicable policy
          sql = """
              SELECT sp.*, bc.name as context_name
              FROM findings f
              JOIN assets a ON f.asset_id = a.id
              JOIN vulnerabilities v ON f.vulnerability_id = v.id
              LEFT JOIN asset_contexts ac ON a.id = ac.asset_id
              LEFT JOIN sla_policies sp ON sp.context_id = ac.context_id
              LEFT JOIN business_contexts bc ON sp.context_id = bc.id
              WHERE f.id = %s
              ORDER BY sp.is_default
              LIMIT 1
          """
          
          policy = self.execute_sql(sql, [finding_id])[0]
          
          if policy:
              days = policy['severity_days'].get(
                  Finding.objects.get(id=finding_id).vulnerability.severity
              )
              
              # Store SLA info
              self.execute_sql("""
                  INSERT INTO finding_sla (finding_id, policy_id, due_date)
                  VALUES (%s, %s, NOW() + INTERVAL '%s days')
                  ON CONFLICT (finding_id) 
                  DO UPDATE SET policy_id = %s, due_date = NOW() + INTERVAL '%s days'
              """, [finding_id, policy['id'], days, policy['id'], days])
      
      def get_sla_summary(self, context_id: str = None):
          """Get SLA compliance summary"""
          return self.execute_sql("""
              SELECT * FROM sla_compliance_summary
              WHERE (%s::UUID IS NULL OR context_id = %s)
          """, [context_id, context_id])
  ```

#### Create SLA Views (2 hours)
- [ ] Build SLA UI components
  ```typescript
  // components/sla/SLADashboard.tsx
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { Progress } from '@/components/ui/progress';
  
  export function SLADashboard() {
    const { data: summary } = useQuery({
      queryKey: ['sla-summary'],
      queryFn: () => api.sla.getSummary(),
    });
    
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Compliance Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary?.compliance_rate}%
            </div>
            <Progress
              value={summary?.compliance_rate}
              className="mt-2"
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Breached
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {summary?.breached}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }
  ```

### Day 15: Basic Dashboard

#### Create Dashboard Page (4 hours)
- [ ] Build dashboard in lovable.dev
  - Use chart and metric widgets to display SLA, MTTR, and risk metrics
  - Connect widgets to API endpoints and materialized views
  - Add recent findings and compliance summaries as tables or cards

### Day 16-17: Reporting

#### Create Report Service (4 hours)
- [ ] Implement report generation
  ```python
  # analytics/services/report_service.py
  from django.http import HttpResponse
  from reportlab.lib import colors
  from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
  
  class ReportService(BaseService):
      def generate_sla_report(self, start_date, end_date, format='pdf'):
          """Generate SLA compliance report"""
          data = self.execute_sql("""
              SELECT 
                  bc.name as business_unit,
                  COUNT(*) as total_findings,
                  COUNT(*) FILTER (WHERE sla_status = 'compliant') as compliant,
                  COUNT(*) FILTER (WHERE sla_status = 'breached') as breached,
                  ROUND(100.0 * COUNT(*) FILTER (WHERE sla_status = 'compliant') / COUNT(*), 2) as compliance_rate
              FROM sla_status ss
              JOIN findings f ON ss.finding_id = f.id
              JOIN assets a ON f.asset_id = a.id
              JOIN asset_contexts ac ON a.id = ac.asset_id
              JOIN business_contexts bc ON ac.context_id = bc.id
              WHERE f.first_seen BETWEEN %s AND %s
              GROUP BY bc.name
              ORDER BY compliance_rate DESC
          """, [start_date, end_date])
          
          if format == 'pdf':
              return self._generate_pdf_report(data)
          else:
              return self._generate_csv_report(data)
      
      def _generate_pdf_report(self, data):
          """Create PDF report"""
          response = HttpResponse(content_type='application/pdf')
          response['Content-Disposition'] = 'attachment; filename="sla_report.pdf"'
          
          doc = SimpleDocTemplate(response)
          elements = []
          
          # Create table
          table_data = [['Business Unit', 'Total', 'Compliant', 'Breached', 'Rate']]
          for row in data:
              table_data.append([
                  row['business_unit'],
                  row['total_findings'],
                  row['compliant'],
                  row['breached'],
                  f"{row['compliance_rate']}%"
              ])
          
          table = Table(table_data)
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
          
          elements.append(table)
          doc.build(elements)
          
          return response
  ```

#### Create Report UI (4 hours)
- [ ] Build report interface in lovable.dev
  - Add date range picker and report generation buttons
  - Connect to Django API endpoints for report generation
  - Display/download generated reports (PDF/CSV) via lovable.dev's file viewer or download action

### Day 18-19: Performance & Testing

#### Add Caching (3 hours)
- [ ] Implement Redis caching
  ```python
  # core/decorators.py
  from django.core.cache import cache
  from functools import wraps
  import hashlib
  
  def cache_result(timeout=300):
      def decorator(func):
          @wraps(func)
          def wrapper(*args, **kwargs):
              # Create cache key
              cache_key = f"{func.__module__}.{func.__name__}:{hashlib.md5(str(args).encode()).hexdigest()}"
              
              # Try cache
              result = cache.get(cache_key)
              if result is not None:
                  return result
              
              # Calculate and cache
              result = func(*args, **kwargs)
              cache.set(cache_key, result, timeout)
              
              return result
          return wrapper
      return decorator
  
  # Use in services
  class MetricsService(BaseService):
      @cache_result(timeout=900)  # 15 minutes
      def get_dashboard_metrics(self):
          # Expensive calculation
          pass
  ```

#### Add Basic Tests (3 hours)
- [ ] Create test suite
  ```python
  # tests/test_import.py
  from django.test import TestCase
  from vulnerabilities.services import NessusImportService
  
  class NessusImportTest(TestCase):
      def setUp(self):
          self.service = NessusImportService()
      
      def test_parse_nessus_file(self):
          # Test with sample file
          with open('tests/fixtures/sample.nessus', 'r') as f:
              results = list(self.service.parser.parse_file(f))
          
          self.assertEqual(len(results), 5)  # 5 hosts
          self.assertEqual(results[0]['name'], 'test-host-1')
      
      def test_import_creates_assets(self):
          # Import file
          self.service.import_file('tests/fixtures/sample.nessus', 'test-job')
          
          # Check assets created
          self.assertEqual(Asset.objects.count(), 5)
          self.assertEqual(Finding.objects.count(), 25)
  ```

### Day 20: Deployment

#### Docker Setup (2 hours)
- [ ] Create Docker configuration
  ```dockerfile
  # Dockerfile
  FROM python:3.11-slim
  
  WORKDIR /app
  
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  
  COPY . .
  
  CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
  ```

  ```yaml
  # docker-compose.yml
  version: '3.8'
  
  services:
    backend:
      build: .
      ports:
        - "8000:8000"
      environment:
        - DATABASE_URL=${DATABASE_URL}
        - REDIS_URL=redis://redis:6379
        - SUPABASE_URL=${SUPABASE_URL}
        - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      depends_on:
        - redis
    
    redis:
      image: redis:7-alpine
    
    frontend:
      build: ./frontend
      ports:
        - "3000:3000"
      environment:
        - VITE_API_URL=http://localhost:8000
        - VITE_SUPABASE_URL=${SUPABASE_URL}
  ```

#### Production Checklist (2 hours)
- [ ] Environment configuration
  ```bash
  # .env.production
  DEBUG=False
  ALLOWED_HOSTS=your-domain.com
  SECRET_KEY=generate-new-key
  DATABASE_URL=your-supabase-db-url
  SUPABASE_URL=your-supabase-url
  SUPABASE_ANON_KEY=your-anon-key
  REDIS_URL=redis://localhost:6379
  ```

- [ ] Security settings
  ```python
  # settings/production.py
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  SECURE_BROWSER_XSS_FILTER = True
  SECURE_CONTENT_TYPE_NOSNIFF = True
  ```

- [ ] Deploy to cloud
  ```bash
  # Deploy backend to Railway/Render
  # Deploy frontend to Vercel/Netlify
  # Set up monitoring with Sentry
  ```

---

## Post-MVP Tasks

### Security Hardening
- [ ] Add rate limiting
- [ ] Implement API versioning
- [ ] Add request validation
- [ ] Set up security headers
- [ ] Enable audit logging

### Performance Optimization
- [ ] Add database connection pooling
- [ ] Implement query optimization
- [ ] Add CDN for static assets
- [ ] Enable gzip compression
- [ ] Add browser caching headers

### Monitoring Setup
- [ ] Configure Sentry for error tracking
- [ ] Set up application metrics
- [ ] Add health check endpoints
- [ ] Configure log aggregation
- [ ] Set up uptime monitoring

### Documentation
- [ ] API documentation with Swagger
- [ ] User guide
- [ ] Deployment guide
- [ ] Development setup guide
- [ ] Architecture decision records

---

## Migration Preparation

### Database Migrations
- [ ] Add fields for future features
  ```sql
  -- Add columns that will be needed later
  ALTER TABLE findings ADD COLUMN IF NOT EXISTS campaign_id UUID;
  ALTER TABLE findings ADD COLUMN IF NOT EXISTS assigned_to UUID;
  ALTER TABLE assets ADD COLUMN IF NOT EXISTS owner_email VARCHAR(255);
  ```

### Code Structure
- [ ] Use interfaces for services
  ```python
  # Prepare for dependency injection
  from abc import ABC, abstractmethod
  
  class RiskCalculatorInterface(ABC):
      @abstractmethod
      def calculate_risk(self, finding_id: str) -> float:
          pass
  
  # Easy to swap implementations
  RISK_CALCULATOR_CLASS = 'services.DatabaseRiskCalculator'  # or PythonRiskCalculator
  ```

### API Versioning
- [ ] Implement versioned URLs
  ```python
  urlpatterns = [
      path('api/v1/', include('api.v1.urls')),
      # Ready for v2
  ]
  ```

### Frontend Migration Path
- [ ] When requirements outgrow lovable.dev, migrate to a custom React/Vite frontend:
  - Reuse all Django REST API endpoints and Supabase integration
  - Replicate lovable.dev UI flows in React components
  - Gradually replace lovable.dev widgets with custom code as needed

---

## Success Metrics

### Week 1 Milestone
- [ ] Database schema deployed
- [ ] Basic auth working
- [ ] Can create assets manually

### Week 2 Milestone
- [ ] Nessus import working
- [ ] Assets and vulnerabilities visible
- [ ] Basic risk scores calculated

### Week 3 Milestone
- [ ] SLA tracking functional
- [ ] Dashboard showing metrics
- [ ] Reports generating

### Week 4 Milestone
- [ ] Deployed to production
- [ ] Documentation complete
- [ ] Handoff ready
```