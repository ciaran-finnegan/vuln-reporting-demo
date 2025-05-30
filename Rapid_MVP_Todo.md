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
  ```

## 4. Django Models & Admin (30 mins)
- [ ] Copy model definitions from architecture doc (Section 2)
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

## 5. Nessus Import API (1.5 hours)
- [ ] Create core/nessus_import.py (from Section 3)
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
      supabase_url = os.getenv('SUPABASE_URL')
      file_url = f"{supabase_url}/storage/v1/object/public/nessus-files/{file_path}"
      
      importer = NessusImporter()
      stats = importer.import_from_url(file_url)
      
      return Response(stats)
  ```
- [ ] Add URL pattern:
  ```python
  path('api/parse-nessus/', parse_nessus, name='parse_nessus'),
  ```

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
- **Total Development Time**: 9-11 hours (1.5 days)
- **With Testing & Polish**: 2-2.5 days
- **Time Saved**: 
  - Auth setup: -2 hours (Supabase auth)
  - Database hosting: -1 hour (Supabase managed)
  - File storage: -30 mins (Supabase Storage)
  - Simple CRUD API: -1 hour (direct Supabase)
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
2. Database schema in Supabase
3. Django Nessus parser API
4. lovable.dev screens with Supabase integration
5. Testing the full flow

## Where This Approach Shines
- **Auth**: 15 mins vs 2 hours
- **File Storage**: Drag-and-drop vs custom implementation
- **Real-time**: Built-in vs polling/websockets
- **Database Hosting**: Zero configuration
- **Frontend-Database**: Direct queries without API layer 