# Data Generation Scripts

This directory contains scripts for generating synthetic test data for the Risk Radar platform.

## Scripts

### generate_weekly_nessus_files.py
Generates realistic synthetic Nessus scan files for testing and development.

#### Purpose
- Creates multiple weeks of scan data with varying host counts
- Generates realistic vulnerability data with proper CVEs and plugin IDs
- Simulates different scan profiles (production, DMZ, development)
- Provides consistent test data for development and testing

#### Usage
```bash
# From project root
cd commands/data_generation
python generate_weekly_nessus_files.py
```

#### Output Structure
```
data/synthetic_nessus/
├── README.md
├── week_1/
│   ├── production_scan_week1.nessus
│   ├── dmz_scan_week1.nessus
│   └── development_scan_week1.nessus
├── week_2/
│   ├── production_scan_week2.nessus
│   ├── dmz_scan_week2.nessus
│   └── development_scan_week2.nessus
├── week_3/
└── week_4/
```

#### Data Characteristics

**Scan Profiles:**
- **Production**: 100+ hosts, 8+ vulnerabilities per host
- **DMZ**: 20+ hosts, 12+ vulnerabilities per host  
- **Development**: 50+ hosts, 15+ vulnerabilities per host (higher vuln count)

**Vulnerabilities Include:**
- SSH Protocol Version 1 (CVE-2001-0572)
- SMBv1 Multiple Vulnerabilities (CVE-2017-0144, CVE-2017-0145)
- SSL Version 2/3 Detection (CVE-2014-3566)
- Certificate Chain Weak RSA Keys
- Apache HTTP Server Vulnerabilities
- OpenSSL Multiple Vulnerabilities
- Windows Update Configuration Issues

**Host Details:**
- Realistic IP addresses (10.0.x.x range)
- Hostnames: `host-XXXX.example.com`
- Mixed operating systems (Windows Server, Ubuntu, RHEL, CentOS)
- Proper system-type classification
- Scan timing metadata

**Network Services:**
- SSH (port 22)
- HTTP/HTTPS (ports 80/443)
- SMB (port 445)
- RDP (port 3389)
- Database services (MySQL, PostgreSQL)
- Proxy services (port 8080)

#### Features

**Progressive Growth:**
- Host counts increase each week to simulate network expansion
- Vulnerability counts vary to simulate patching cycles
- Different profiles have different growth patterns

**Realistic Metadata:**
- Proper CVE identifiers
- Actual Nessus plugin IDs
- CVSS scores and vectors
- Risk factors and severity levels
- Plugin families and publication dates

**XML Structure:**
- Valid Nessus XML format
- Proper namespace declarations
- Compliant with Nessus file format specification
- Can be imported by standard Nessus tools

#### Requirements
- Python 3.7+
- Django environment (for model access)
- Write permissions to `data/` directory

#### Customisation

**Modify Host Counts:**
```python
# Edit scan_profiles in generate_week_data()
scan_profiles = [
    {
        'name': 'production_scan',
        'host_count': 150,  # Increase from 100
        'vulns_per_host': 10  # Increase from 8
    }
]
```

**Add New Vulnerabilities:**
```python
# Add to vuln_templates in generate_synthetic_nessus_xml()
{
    'plugin_id': 'NEW_ID',
    'title': 'New Vulnerability',
    'severity': 'High',
    'cvss_score': '8.0',
    'cve': 'CVE-YYYY-XXXX',
    'description': 'Description text',
    'fix_info': 'Remediation instructions'
}
```

**Change Output Location:**
```python
# Modify base_path in main()
base_path = "../../data/custom_location"
```

#### Integration with Risk Radar
Generated files can be imported using:
```bash
# Import a specific file
cd riskradar
python manage.py import_nessus ../data/synthetic_nessus/week_1/production_scan_week1.nessus

# Or test via upload API
curl -X POST -F "file=@data/synthetic_nessus/week_1/production_scan_week1.nessus" \
     http://localhost:8000/api/v1/upload/nessus
```

#### Adding New Generators
To add new data generation scripts:
1. Follow naming convention: `generate_[type]_[description].py`
2. Include comprehensive docstrings
3. Provide configurable parameters
4. Generate data in appropriate subdirectory under `data/`
5. Create accompanying README for generated data
6. Update this main README with new script information 