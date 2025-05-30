TODO – Detailed Backlog & File Map (MVP)

Branch naming rule: feat/T-NN-slug, where T-NN matches the table below.
File paths use a monorepo layout:
	•	/backend – Django 5 + worker code
	•	/frontend – React/Vite SPA
	•	/infra – SQL, docker-compose, Supabase config
	•	/.github/workflows – CI pipelines
	•	/docs – architecture, OpenAPI, ADRs

⸻

0  Repository Bootstrap

ID	Deliverable	Files / Folders	Acceptance
T-00	Initialise Git, dev-container, pre-commit	.devcontainer.json, .pre-commit-config.yaml, .editorconfig	devcontainer up boots; pre-commit run --all-files clean.
T-01	CI skeleton	/.github/workflows/backend.yml, /.github/workflows/frontend.yml	PR triggers lint + tests for both stacks.

backend.yml (excerpt)

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      db:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install poetry
      - run: poetry install
      - run: poetry run pytest -q


⸻

1  Database Layer

ID	Deliverable	Files (under /infra)	Acceptance
T-10	Core schema DDL	schema.sql	psql -f schema.sql executes with no errors.
T-11	Analytics views	analytics_views.sql	REFRESH … <1 s on seed dataset.
T-12	Nightly roll-up function	nightly_job.sql	Supabase Task scheduled 02:00, verified in dashboard.

infra/schema.sql contains the full CREATE TYPE/TABLE/INDEX statements previously documented.

⸻

2  Backend – Django API

ID	Deliverable	Files	Acceptance
T-20	Django project skeleton	/backend/api, settings.py wired to Supabase DB creds via env	manage.py check passes.
T-21	Models + migrations	/backend/api/models/*.py, migrations/*.py	pytest backend/api/tests/test_models.py green.
T-22	Supabase JWT Middleware	/backend/api/middleware/supabase_jwt.py	Invalid or expired JWT → HTTP 401.
T-23	Serializers & ViewSets	/backend/api/views/*.py, /backend/api/serializers/*.py	/assets endpoint returns paginated JSON.
T-24	OpenAPI generation	/backend/api/openapi.yml (committed)	redoc-cli bundle renders with no warnings.

Code – middleware/supabase_jwt.py

import os, requests, jwt
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

JWKS_URL = f"{os.environ['SUPABASE_URL']}/auth/v1/keys"

class SupabaseJWTMiddleware(MiddlewareMixin):
    _jwks_cache = None

    def _fetch_jwks(self):
        if not self._jwks_cache:
            self._jwks_cache = requests.get(JWKS_URL, timeout=5).json()
        return self._jwks_cache

    def process_request(self, request):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return JsonResponse({'detail': 'Auth header missing'}, status=401)
        token = auth.split()[1]
        try:
            kid = jwt.get_unverified_header(token)['kid']
            key = next(key for key in self._fetch_jwks()['keys'] if key['kid'] == kid)
            user = jwt.decode(token, jwk=key, algorithms=['RS256'], audience='authenticated')
            request.user_id = user['sub']
        except Exception as exc:
            return JsonResponse({'detail': 'Invalid token', 'error': str(exc)}, status=401)


⸻

3  Backend – ETL Worker

ID	Deliverable	Files	Acceptance
T-30	Base DTO + utils	/backend/etl/dto.py	MyPy passes.
T-31	Nessus Parser	/backend/etl/nessus_parser.py	Parses 10 k-host sample in <90 s.
T-32	Tests & fixture	/backend/etl/tests/test_nessus_parser.py, /backend/etl/tests/fixtures/*.nessus	pytest -q green.
T-33	Celery beat worker	celery.py, tasks.py	Upload triggers parse task asynchronously.

Code – nessus_parser.py (core loop)

from lxml import etree
from .dto import AssetDTO, VulnDTO, InstanceDTO

class NessusParser:
    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.assets, self.vulns, self.instances = {}, {}, []

    def parse(self):
        ctx = etree.iterparse(self.xml_path, events=('start', 'end'))
        for event, elem in ctx:
            if event == 'start' and elem.tag == 'ReportHost':
                host_name = elem.get('name')
                asset = self.assets.setdefault(host_name, AssetDTO(name=host_name, type='host'))
            if event == 'end' and elem.tag == 'ReportItem':
                vid = elem.get('pluginID')
                vdto = self.vulns.setdefault(vid, VulnDTO(ext_id=vid, name=elem.get('pluginName'), severity=elem.get('severity')))
                inst = InstanceDTO(asset_name=host_name, vuln_ext_id=vid, port=int(elem.get('port') or 0), service=elem.get('svc_name'))
                self.instances.append(inst)
                elem.clear();
        return self.assets.values(), self.vulns.values(), self.instances


⸻

4  Analytics Job

ID	Deliverable	Files	Acceptance
T-40	SQL scheduled function	infra/nightly_job.sql	Supabase task calls function, snapshot row count increases.
T-41	DRF reports endpoints	/backend/api/views/report_views.py	/reports/mttr returns JSON [ {bg_id,mean_days_to_fix} ].


⸻

5  Frontend

ID	Deliverable	Files	Acceptance
T-50	Vite + Tailwind scaffold	/frontend/src	npm run dev up.
T-51	Supabase provider & route guard	lib/supabaseClient.ts, AuthProvider.tsx	Redirect to login on missing session.
T-52	API hooks (TanStack Query)	hooks/useAssets.ts, useVulns.ts	Hooks typed via openapi-generated client.
T-53	Upload page	pages/Upload.tsx	Upload succeeds, toast shows.
T-54	DataTable components	components/DataTable.tsx	Supports column drag & drop.
T-55	Reports page	pages/Reports.tsx	MTTR & SLA cards + line chart.


⸻

6  Dev & Ops

ID	Deliverable	Files	Acceptance
T-60	Docker compose	/docker-compose.yml (backend, worker, db)	docker compose up API ready on :8000.
T-61	Makefile / scripts	Makefile targets: dev, test, lint, init-db	One-liner dev bootstrap.
T-62	Seed script	/infra/seed_demo_data.py	Inserts demo BGs, SLA, sample Nessus upload.


⸻

7  Docs

ID	Deliverable	Files	Acceptance
T-70	Architecture doc	docs/application_architecture.md (already present ✅)	Reviewed & up-to-date.
T-71	API doc	docs/openapi.yml → published via Redoc GitHub Pages	URL accessible.
T-72	ETL guide	docs/ETL.md – field mapping tables	Future connector devs can replicate pattern.
T-73	ADR-001	Architectural Decision Record: “Single schema vs micro-service”	Merged.


⸻

Post-MVP backlog (not in initial sprint)
	•	Multi-tenant RLS.
	•	Playbook automation engine.
	•	Additional connectors (Qualys, Snyk).
	•	RBAC role editor UI.

⸻

Note for LLM agents: Each task includes explicit file paths and acceptance tests; generate code only within those boundaries.