# Risk Radar Commands & Scripts

This directory contains utility scripts, test tools, and data generation scripts for the Risk Radar platform. All scripts are organised by function to maintain clarity and ease of use.

## Directory Structure

```
/commands/
├── README.md                    # This file
├── testing/                     # Test and validation scripts
│   ├── test_upload_api.py      # Upload API authentication testing
│   └── README.md               # Testing scripts documentation
└── data_generation/            # Synthetic data generation
    ├── generate_weekly_nessus_files.py  # Generate test Nessus files
    └── README.md               # Data generation documentation
```

## Quick Start

### Prerequisites
- Ensure you're in the project root directory (`/Users/Ciaran/Dev/vuln-reporting-demo`)
- Activate your virtual environment: `source venv/bin/activate`
- Ensure Django server is running: `cd riskradar && python manage.py runserver 8000`

### Testing Scripts

#### Upload API Testing
```bash
# Test upload API with authentication
cd commands/testing
python test_upload_api.py
```

**Requirements:**
- Django server running on localhost:8000
- Valid `.env` file in `riskradar/.env` with `SUPABASE_JWT_SECRET`
- Sample Nessus file in `data/nessus_reports/sample_files/nessus/`

**What it tests:**
- ✅ API status endpoints
- ✅ Unauthenticated file uploads
- ✅ Authenticated file uploads with JWT tokens
- ✅ Invalid token handling
- ✅ Error scenarios (invalid files, missing files)

### Data Generation Scripts

#### Synthetic Nessus Data Generation
```bash
# Generate weekly test Nessus files
cd commands/data_generation
python generate_weekly_nessus_files.py
```

**Output:**
- Creates `data/synthetic_nessus/` directory structure
- Generates 4 weeks of realistic scan data
- Each week contains production, DMZ, and development scans
- Includes realistic CVEs, plugin IDs, and vulnerability descriptions

## Usage Guidelines

### For Developers
1. Always run scripts from the project root directory
2. Ensure virtual environment is activated
3. Check script-specific README files for detailed requirements
4. Scripts automatically handle relative paths from their subdirectories

### For AI/LLM Agents
- **ALWAYS** place new scripts in appropriate `/commands` subdirectories
- **NEVER** create scripts in the project root
- Follow the existing directory structure:
  - `/commands/testing/` - Test and validation scripts
  - `/commands/data_generation/` - Synthetic data creation
  - `/commands/maintenance/` - Database and system maintenance (future)
  - `/commands/deployment/` - Deployment and setup scripts (future)

### Environment Variables
Scripts that need environment variables will automatically load from `riskradar/.env`:
- `SUPABASE_JWT_SECRET` - For authentication testing
- `SUPABASE_PROJECT_ID` - For Supabase integration
- `SUPABASE_URL` - For API connections
- `SUPABASE_ANON_KEY` - For anonymous access

## Common Issues & Solutions

### "SUPABASE_JWT_SECRET not found"
**Solution:** Ensure `riskradar/.env` exists and contains your Supabase credentials.

### "Connection refused" errors
**Solution:** Make sure Django development server is running: `cd riskradar && python manage.py runserver 8000`

### "File not found" errors
**Solution:** Ensure you're running scripts from the project root directory, not from within subdirectories.

### Django import errors
**Solution:** Ensure you're in the correct Python virtual environment and all dependencies are installed.

## Adding New Scripts

### Directory Assignment
- **Testing/Validation**: `/commands/testing/`
- **Data Generation**: `/commands/data_generation/`
- **Database Operations**: `/commands/maintenance/` (create if needed)
- **Deployment/Setup**: `/commands/deployment/` (create if needed)

### Naming Conventions
- Use descriptive names: `test_upload_api.py` not `test.py`
- Include functionality: `generate_weekly_nessus_files.py`
- Use snake_case for Python scripts

### Path Handling
- Always use relative paths from project root
- Scripts in subdirectories should use `../../` to reach project root
- Test paths work from both subdirectory and project root

---

*For more information, see individual README files in each subdirectory.* 