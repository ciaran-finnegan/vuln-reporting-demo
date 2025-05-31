# Rapid MVP Todo List for Risk Radar (Hybrid Supabase + Django)

## 1. Supabase Project Setup (20 mins)
- [ ] Create Supabase project at https://app.supabase.com
- [ ] Note down:
  ```bash
  SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
  SUPABASE_ANON_KEY=eyJ...
  SUPABASE_SERVICE_ROLE_KEY=eyJ...
  DB_HOST=db.xxxxxxxxxxxx.supabase.co
  DB_PASSWORD=your-password
  ```
- [ ] Create storage bucket for Nessus files:
  ```sql
  -- In Supabase SQL Editor
  INSERT INTO storage.buckets (id, name, public) 
  VALUES ('nessus-files', 'nessus-files', true);
  ```

## 2. Django Project Setup (20 mins)
- [ ] Create Django project and core app
  ```bash
  django-admin startproject riskradar
  cd riskradar
  python manage.py startapp core
  ```
- [ ] Install dependencies
  ```bash
  pip install django djangorestframework django-cors-headers
  pip install psycopg2-binary reportlab requests
  pip install python-dotenv  # For environment variables
  ```
- [ ] Create .env file with Supabase credentials:
  ```bash
  SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
  SUPABASE_SERVICE_KEY=eyJ...
  DATABASE_URL=postgresql://postgres:password@db.xxxxxxxxxxxx.supabase.co:5432/postgres
  ```
- [ ] Update settings.py:
  ```python
  import os
  from dotenv import load_dotenv
  load_dotenv()
  
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'HOST': os.getenv('DB_HOST'),
          'PORT': '5432',
          'NAME': 'postgres',
          'USER': 'postgres',
          'PASSWORD': os.getenv('DB_PASSWORD'),
      }
  }
  
  # Only need CORS for Django API endpoints
  CORS_ALLOWED_ORIGINS = [
      "https://lovable.dev",
      "http://localhost:3000",
  ]
  ```

## 3. Database Setup in Supabase (1 hour)
- [ ] Run schema in Supabase SQL Editor (from architecture doc Section 1)
- [ ] Enable Row Level Security:
  ```sql
  -- Enable RLS on all tables
  ALTER TABLE asset ENABLE ROW LEVEL SECURITY;
  ALTER TABLE finding ENABLE ROW LEVEL SECURITY;
  ALTER TABLE vulnerability ENABLE ROW LEVEL SECURITY;
  ALTER TABLE remediation_campaign ENABLE ROW LEVEL SECURITY;
  
  -- Create basic policies
  CREATE POLICY "Enable read for authenticated users" ON asset
      FOR SELECT USING (auth.role() = 'authenticated');
  
  CREATE POLICY "Enable all for service role" ON asset
      FOR ALL USING (auth.role() = 'service_role');
  
  -- Repeat for other tables
  ```
- [ ] Create helper views (sla_status, mttr_summary)
- [ ] Create additional remediation metric views:
  ```sql
  -- Create all views from architecture doc:
  -- daily_remediation_stats
  -- remediation_capacity  
  -- mttr_by_asset_type
  -- mttr_history table
  -- capture_mttr_snapshot function
  ```
- [ ] Insert default data:
  ```sql
  INSERT INTO asset_type (name) VALUES ('Host'), ('Code'), ('Website'), ('Image'), ('Cloud');
  INSERT INTO sla_policy (name, is_default, severity_days) VALUES 
    ('Default SLA', TRUE, '{"Critical": 1, "High": 7, "Medium": 30, "Low": 90, "Info": 365}');
  
  -- Create Nessus integration
  INSERT INTO scanner_integration (name, description, is_active) VALUES 
    ('Nessus', 'Tenable Nessus vulnerability scanner integration', TRUE);
  
  -- Create Nessus severity mappings
  INSERT INTO severity_mapping (integration_id, source_value, target_value) 
  SELECT id, '0', 'Info' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, '1', 'Low' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, '2', 'Medium' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, '3', 'High' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, '4', 'Critical' FROM scanner_integration WHERE name = 'Nessus';
  
  -- Create Nessus field mappings for Assets
  INSERT INTO field_mapping (integration_id, source_field, target_model, target_field, field_type, sort_order, description) 
  SELECT id, 'host-ip', 'asset', 'ip_address', 'string', 1, 'Host IP address' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, 'host-fqdn', 'asset', 'hostname', 'string', 2, 'Host FQDN' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, 'host-name', 'asset', 'name', 'string', 3, 'Host name from XML attribute' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, 'operating-system', 'asset', 'metadata.os', 'string', 10, 'Operating system' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, 'mac-address', 'asset', 'metadata.mac_address', 'string', 11, 'MAC address' FROM scanner_integration WHERE name = 'Nessus';
  
  -- Create Nessus field mappings for Vulnerabilities  
  INSERT INTO field_mapping (integration_id, source_field, target_model, target_field, field_type, sort_order, description)
  SELECT id, '@pluginID', 'vulnerability', 'external_id', 'string', 1, 'Nessus plugin ID' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, '@pluginName', 'vulnerability', 'name', 'string', 2, 'Vulnerability name' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, 'description', 'vulnerability', 'description', 'string', 3, 'Vulnerability description' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, 'solution', 'vulnerability', 'solution', 'string', 4, 'Remediation solution' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, 'cve', 'vulnerability', 'cve_id', 'string', 5, 'CVE ID', 'first(split(value, ","))' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, 'cvss3_base_score', 'vulnerability', 'cvss_score', 'decimal', 6, 'CVSS v3 base score' FROM scanner_integration WHERE name = 'Nessus';
  
  -- Create Nessus field mappings for Findings
  INSERT INTO field_mapping (integration_id, source_field, target_model, target_field, field_type, sort_order, description)
  SELECT id, '@port', 'finding', 'port', 'integer', 1, 'Service port' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, '@protocol', 'finding', 'protocol', 'string', 2, 'Network protocol' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, '@svc_name', 'finding', 'service', 'string', 3, 'Service name' FROM scanner_integration WHERE name = 'Nessus'
  UNION ALL
  SELECT id, 'plugin_output', 'finding', 'plugin_output', 'string', 4, 'Plugin output details' FROM scanner_integration WHERE name = 'Nessus';
  ```

## 4. Django Models & Admin (45 mins)
- [ ] Copy model definitions from architecture doc (Section 2) including new models:
  ```python
  # New models for configurable mappings:
  class ScannerIntegration(models.Model): ...
  class FieldMapping(models.Model): ...  
  class SeverityMapping(models.Model): ...
  class ScannerUpload(models.Model): ...  # Replaces NessusUpload
  ```
- [ ] Add db_table to match Supabase tables:
  ```python
  class Asset(models.Model):
      # ... fields ...
      class Meta:
          db_table = 'asset'  # Match Supabase table names
  ```
- [ ] Run Django migrations (for admin tables only):
  ```bash
  python manage.py migrate  # Only migrates Django admin tables
  python manage.py createsuperuser
  ```
- [ ] Configure admin.py (copy from Section 4)
- [ ] Test field mapping management in Django admin:
  - Navigate to /admin/core/scannerintegration/
  - Verify Nessus integration is created
  - Navigate to /admin/core/fieldmapping/ 
  - Test adding/editing field mappings
  - Navigate to /admin/core/severitymapping/
  - Test severity mappings

## 5. Scanner Import API (1.5 hours)
- [ ] Create core/scanner_import.py (from Section 3) with new ScannerImporter class
- [ ] Add method to download from Supabase Storage:
  ```python
  def import_from_url(self, file_url):
      response = requests.get(file_url)
      with tempfile.NamedTemporaryFile(suffix='.nessus') as tmp:
          tmp.write(response.content)
          tmp.flush()
          return self.import_file(tmp.name)
  ```
- [ ] Create API endpoint for lovable.dev to trigger:
  ```python
  # views.py
  from rest_framework.decorators import api_view
  from rest_framework.response import Response
  
  @api_view(['POST'])
  def parse_nessus(request):
      file_path = request.data['file_path']
      integration_name = request.data.get('integration', 'Nessus')
      supabase_url = os.getenv('SUPABASE_URL')
      file_url = f"{supabase_url}/storage/v1/object/public/nessus-files/{file_path}"
      
      importer = ScannerImporter(integration_name)
      stats = importer.import_from_url(file_url)
      
      return Response(stats)
  ```
- [ ] Add URL pattern:
  ```python
  path('api/parse-nessus/', parse_nessus, name='parse_nessus'),
  ```
- [ ] Test field mapping configuration by:
  - Adding a new field mapping in Django admin
  - Uploading a test file
  - Verifying the new field is extracted

## 6. Minimal Django API Endpoints (30 mins)
- [ ] Create only complex logic endpoints:
  ```python
  # Only endpoints that need Python logic
  urlpatterns = [
      path('api/parse-nessus/', parse_nessus),
      path('api/generate-sla-report/', generate_sla_report),
      path('api/generate-campaign-report/<int:id>/', generate_campaign_report),
      path('api/calculate-risk-scores/', calculate_risk_scores),
      path('api/findings/remediation-metrics/', FindingViewSet.as_view({'get': 'remediation_metrics'})),
  ]
  ```
- [ ] Simple CRUD operations will use Supabase directly from lovable.dev

## 7. lovable.dev Setup with Supabase (1.5 hours)
- [ ] Create new lovable.dev project
- [ ] Connect to Supabase project (automatic integration)
- [ ] Configure environment variables:
  ```
  NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
  NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
  NEXT_PUBLIC_DJANGO_API_URL=http://localhost:8000
  ```

## 8. lovable.dev Authentication (15 mins)
- [ ] Use lovable.dev's built-in auth components:
  - Login page (auto-generated)
  - Signup page (auto-generated)
  - Password reset (auto-generated)
  - Profile management (auto-generated)
- [ ] Configure auth redirects and guards

## 9. lovable.dev Screens (2 hours)
### File Upload Screen
- [ ] Supabase Storage upload component
- [ ] After upload, call Django API to parse:
  ```javascript
  // Upload to Supabase Storage
  const { data } = await supabase.storage
    .from('nessus-files')
    .upload(`uploads/${file.name}`, file)
  
  // Trigger Django parser
  await fetch(`${DJANGO_API_URL}/api/parse-nessus/`, {
    method: 'POST',
    body: JSON.stringify({ file_path: data.path })
  })
  ```

### Asset Dashboard
- [ ] Direct Supabase query:
  ```javascript
  const { data: assets } = await supabase
    .from('asset')
    .select(`
      *,
      asset_type(*),
      findings:finding(count)
    `)
    .order('name')
  ```

### Findings Management
- [ ] Real-time subscriptions for updates:
  ```javascript
  const findings = supabase
    .channel('findings-changes')
    .on('postgres_changes', 
      { event: '*', schema: 'public', table: 'finding' },
      (payload) => {
        // Update UI automatically
      }
    )
    .subscribe()
  ```

### SLA Dashboard
- [ ] Query the sla_status view directly
- [ ] Download button calls Django API for PDF/CSV

### Campaign Management
- [ ] CRUD operations direct to Supabase
- [ ] Progress tracking with computed columns

### Remediation Performance Dashboard
- [ ] Create KPI cards showing:
  - Overall MTTR in days
  - Average daily remediation count
  - Remediation capacity percentage
- [ ] MTTR trend chart over time (query mttr_history table)
- [ ] MTTR breakdown by:
  - Business Group (from mttr_summary view)
  - Asset Type (from mttr_by_asset_type view)
  - Severity level
- [ ] Call Django API for complex metrics:
  ```javascript
  const { data: metrics } = await fetch(`${DJANGO_API_URL}/api/findings/remediation-metrics/`)
  ```

## 10. Reporting Implementation (45 mins)
- [ ] Keep reports in Django (complex logic):
  ```python
  @api_view(['GET'])
  def generate_sla_report(request):
      # Query Supabase DB via Django ORM
      # Generate CSV/PDF
      return FileResponse(...)
  ```

## 11. Testing & Data Import (45 mins)
- [ ] Test auth flow in lovable.dev
- [ ] Upload test Nessus file via lovable.dev
- [ ] Verify parsing via Django
- [ ] Check data appears in lovable.dev screens
- [ ] Import your full .nessus file collection:
  ```bash
  # Can still use Django management command
  python manage.py import_nessus /path/to/files/
  ```

## 12. Quick Deployment (30 mins)
- [ ] Deploy Django API to Railway/Render:
  ```dockerfile
  FROM python:3.11
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["gunicorn", "riskradar.wsgi"]
  ```
- [ ] Deploy lovable.dev to Vercel (automatic)
- [ ] Update environment variables in both services
- [ ] Set up daily MTTR snapshot job:
  ```bash
  # Add to crontab or use platform scheduler
  0 0 * * * python manage.py capture_mttr_snapshot
  ```

---

## Revised Time Estimates
- **Total Development Time**: 10-12 hours (1.5-2 days)
- **With Testing & Polish**: 2.5-3 days
- **Time Saved**: 
  - Auth setup: -2 hours (Supabase auth)
  - Database hosting: -1 hour (Supabase managed)
  - File storage: -30 mins (Supabase Storage)
  - Simple CRUD API: -1 hour (direct Supabase)
- **Additional Time for Configurable Mappings**: +1.5 hours
  - Database schema: 30 mins
  - Django models: 30 mins
  - Admin interfaces: 30 mins
- **Additional Time for Remediation Metrics**: +1 hour
  - Create additional views: 30 mins
  - Add API endpoint: 15 mins
  - Dashboard UI: 15 mins

## Architecture Benefits
1. **Instant Auth**: lovable.dev + Supabase = login/signup in minutes
2. **Real-time Updates**: Live dashboards without polling
3. **Direct Database**: Faster queries for simple operations
4. **Django Admin**: Still available for backend management
5. **Managed Infrastructure**: Database, auth, and storage hosted

## Critical Path Items
1. Supabase project setup (enables everything else)
2. Database schema in Supabase (including new mapping tables)
3. Django scanner parser API with configurable mappings
4. lovable.dev screens with Supabase integration
5. Testing the full flow

## Adding New Scanner Integrations (Future)
With the configurable mapping system, adding new scanners becomes trivial:

1. **Create Scanner Integration** (Django Admin):
   ```
   Name: OpenVAS
   Description: OpenVAS vulnerability scanner
   ```

2. **Add Severity Mappings** (Django Admin):
   ```
   OpenVAS: High → High
   OpenVAS: Medium → Medium
   OpenVAS: Low → Low
   ```

3. **Add Field Mappings** (Django Admin):
   ```
   host@ip → asset.ip_address
   nvt@oid → vulnerability.external_id
   description → vulnerability.description
   ```

4. **Use Existing API**:
   ```python
   importer = ScannerImporter('OpenVAS')
   stats = importer.import_file(openvas_file)
   ```

No code changes required - all configuration through Django admin!

## Where This Approach Shines
- **Auth**: 15 mins vs 2 hours
- **File Storage**: Drag-and-drop vs custom implementation
- **Real-time**: Built-in vs polling/websockets
- **Database Hosting**: Zero configuration
- **Frontend-Database**: Direct queries without API layer
- **Configurable Mappings**: Add new scanners without code changes
- **Field Management**: Non-technical users can modify mappings via admin 