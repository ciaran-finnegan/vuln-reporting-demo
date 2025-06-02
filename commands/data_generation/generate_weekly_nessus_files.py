import os
import random
import xml.etree.ElementTree as ET
import datetime
from pathlib import Path
import django
from django.utils import timezone

# Simple Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riskradar.settings')
import django
django.setup()

from riskradar.core.models import Asset, Vulnerability, Finding, AssetType, ScannerIntegration, BusinessGroup, FieldMapping, SeverityMapping
import shutil

def clear_directory(directory_path):
    """Clear all files in the specified directory."""
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
    os.makedirs(directory_path, exist_ok=True)

def generate_synthetic_nessus_xml(output_file, host_count=50, vulns_per_host=10):
    """
    Generate synthetic Nessus XML data with realistic vulnerabilities.
    """
    root = ET.Element("NessusClientData_v2")
    
    # Define realistic vulnerability templates
    vuln_templates = [
        {
            'plugin_id': '10881',
            'title': 'SSH Protocol Version 1 Detection',
            'severity': 'Medium',
            'cvss_score': '5.0',
            'cve': 'CVE-2001-0572',
            'description': 'The remote SSH server supports SSH protocol version 1',
            'fix_info': 'Disable SSH protocol version 1 and use only SSH protocol version 2'
        },
        {
            'plugin_id': '11219',
            'title': 'Microsoft Windows SMBv1 Multiple Vulnerabilities',
            'severity': 'Critical',
            'cvss_score': '9.3',
            'cve': 'CVE-2017-0144,CVE-2017-0145',
            'description': 'The remote Windows host is affected by multiple vulnerabilities in SMBv1',
            'fix_info': 'Apply the appropriate patches from Microsoft or disable SMBv1'
        },
        {
            'plugin_id': '20007',
            'title': 'SSL Version 2 and 3 Protocol Detection',
            'severity': 'High',
            'cvss_score': '7.5',
            'cve': 'CVE-2014-3566',
            'description': 'The remote service encrypts traffic using an obsolete version of SSL',
            'fix_info': 'Disable SSL version 2 and 3, and enable TLS 1.2 or higher'
        },
        {
            'plugin_id': '42873',
            'title': 'SSL Certificate Chain Contains Weak RSA Keys',
            'severity': 'Medium',
            'cvss_score': '4.3',
            'cve': '',
            'description': 'The X.509 certificate chain used by this service contains certificates with RSA keys shorter than 2048 bits',
            'fix_info': 'Replace the certificate with one using at least 2048-bit RSA keys'
        },
        {
            'plugin_id': '10863',
            'title': 'Apache HTTP Server Multiple Vulnerabilities',
            'severity': 'High',
            'cvss_score': '7.5',
            'cve': 'CVE-2021-44790,CVE-2021-44224',
            'description': 'The remote Apache HTTP Server is affected by multiple vulnerabilities',
            'fix_info': 'Upgrade to Apache HTTP Server 2.4.52 or later'
        },
        {
            'plugin_id': '10287',
            'title': 'Traceroute Information',
            'severity': 'Info',
            'cvss_score': '0.0',
            'cve': '',
            'description': 'It was possible to obtain traceroute information',
            'fix_info': 'Block outgoing ICMP time exceeded packets'
        },
        {
            'plugin_id': '56984',
            'title': 'Microsoft Windows Update Not Configured',
            'severity': 'Low',
            'cvss_score': '2.6',
            'cve': '',
            'description': 'Windows Update is not configured to automatically install updates',
            'fix_info': 'Configure Windows Update to automatically download and install updates'
        },
        {
            'plugin_id': '104743',
            'title': 'OpenSSL Multiple Vulnerabilities',
            'severity': 'Critical',
            'cvss_score': '9.8',
            'cve': 'CVE-2022-0778',
            'description': 'The remote host has an installation of OpenSSL that is affected by multiple vulnerabilities',
            'fix_info': 'Upgrade to OpenSSL 1.1.1n or later'
        }
    ]
    
    # Define realistic services
    services = [
        {'port': '22', 'protocol': 'tcp', 'svc_name': 'ssh'},
        {'port': '80', 'protocol': 'tcp', 'svc_name': 'http'},
        {'port': '443', 'protocol': 'tcp', 'svc_name': 'https'},
        {'port': '445', 'protocol': 'tcp', 'svc_name': 'microsoft-ds'},
        {'port': '3389', 'protocol': 'tcp', 'svc_name': 'ms-wbt-server'},
        {'port': '3306', 'protocol': 'tcp', 'svc_name': 'mysql'},
        {'port': '5432', 'protocol': 'tcp', 'svc_name': 'postgresql'},
        {'port': '8080', 'protocol': 'tcp', 'svc_name': 'http-proxy'},
    ]
    
    # Create Report element
    report = ET.SubElement(root, "Report", name="Weekly Security Scan", xmlns="http://www.nessus.org/cm")
    
    # Generate hosts
    for i in range(host_count):
        host_ip = f"10.0.{i // 256}.{i % 256}"
        hostname = f"host-{i:04d}.example.com"
        
        # Create ReportHost element
        report_host = ET.SubElement(report, "ReportHost", name=hostname)
        
        # Add HostProperties
        host_properties = ET.SubElement(report_host, "HostProperties")
        
        # Add host properties
        props = [
            ("tag", {"name": "host-ip", "value": host_ip}),
            ("tag", {"name": "host-fqdn", "value": hostname}),
            ("tag", {"name": "operating-system", "value": random.choice([
                "Microsoft Windows Server 2019 Standard",
                "Microsoft Windows Server 2016 Datacenter",
                "Ubuntu 20.04.3 LTS",
                "Red Hat Enterprise Linux Server release 8.5",
                "CentOS Linux release 7.9.2009"
            ])}),
            ("tag", {"name": "system-type", "value": "server"}),
            ("tag", {"name": "HOST_START", "value": datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")}),
            ("tag", {"name": "HOST_END", "value": (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%a %b %d %H:%M:%S %Y")}),
        ]
        
        for tag_name, attrs in props:
            ET.SubElement(host_properties, tag_name, **attrs)
        
        # Add vulnerabilities
        selected_vulns = random.sample(vuln_templates, min(vulns_per_host, len(vuln_templates)))
        
        for vuln in selected_vulns:
            # Randomly select a service for this vulnerability
            service = random.choice(services)
            
            # Map severity to risk factor
            risk_factor_map = {
                'Critical': 'Critical',
                'High': 'High',
                'Medium': 'Medium',
                'Low': 'Low',
                'Info': 'None'
            }
            
            report_item = ET.SubElement(
                report_host, "ReportItem",
                port=service['port'],
                svc_name=service['svc_name'],
                protocol=service['protocol'],
                severity=str(['Info', 'Low', 'Medium', 'High', 'Critical'].index(vuln['severity'])),
                pluginID=vuln['plugin_id'],
                pluginName=vuln['title'],
                pluginFamily="General"
            )
            
            # Add vulnerability details
            elements = [
                ("agent", "all"),
                ("cvss_base_score", vuln['cvss_score']),
                ("cvss_vector", "CVSS2#AV:N/AC:L/Au:N/C:P/I:P/A:P"),
                ("risk_factor", risk_factor_map[vuln['severity']]),
                ("description", vuln['description']),
                ("synopsis", f"The remote host is affected by {vuln['title']}"),
                ("solution", vuln['fix_info']),
                ("plugin_publication_date", "2022/01/15"),
                ("plugin_modification_date", datetime.datetime.now().strftime("%Y/%m/%d")),
                ("plugin_output", f"Plugin output for {vuln['title']}\nDetected on {hostname}:{service['port']}/{service['protocol']}"),
            ]
            
            # Add CVE if present
            if vuln['cve']:
                elements.append(("cve", vuln['cve']))
            
            # Add see_also references
            elements.append(("see_also", f"https://plugins.nessus.org/plugins/{vuln['plugin_id']}"))
            
            for elem_name, elem_text in elements:
                elem = ET.SubElement(report_item, elem_name)
                elem.text = elem_text
    
    # Write to file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"Generated {output_file}")

def generate_week_data(week_num, base_path):
    """Generate data for a specific week."""
    week_path = os.path.join(base_path, f"week_{week_num}")
    os.makedirs(week_path, exist_ok=True)
    
    # Define different scan profiles
    scan_profiles = [
        {
            'name': 'production_scan',
            'host_count': 100 + week_num * 5,  # Gradually increase hosts
            'vulns_per_host': 8 + (week_num % 3)  # Vary vulnerability count
        },
        {
            'name': 'dmz_scan',
            'host_count': 20 + week_num * 2,
            'vulns_per_host': 12 + (week_num % 4)
        },
        {
            'name': 'development_scan',
            'host_count': 50 + week_num * 3,
            'vulns_per_host': 15 + (week_num % 5)  # Dev typically has more vulns
        }
    ]
    
    for profile in scan_profiles:
        output_file = os.path.join(week_path, f"{profile['name']}_week{week_num}.nessus")
        generate_synthetic_nessus_xml(
            output_file,
            host_count=profile['host_count'],
            vulns_per_host=profile['vulns_per_host']
        )

def main():
    """Generate weekly Nessus files in organized directory structure."""
    base_path = "../../data/synthetic_nessus"
    clear_directory(base_path)
    
    print(f"Generating synthetic Nessus data in {base_path}")
    
    # Generate 4 weeks of data
    for week in range(1, 5):
        print(f"\nGenerating Week {week} data...")
        generate_week_data(week, base_path)
    
    print(f"\nGeneration complete! Files saved in {base_path}")
    
    # Create a README
    readme_content = """# Synthetic Nessus Test Data

This directory contains synthetic Nessus scan data generated for testing purposes.

## Directory Structure:
- week_1/ - First week scan data
  - production_scan_week1.nessus
  - dmz_scan_week1.nessus
  - development_scan_week1.nessus
- week_2/ - Second week scan data
- week_3/ - Third week scan data
- week_4/ - Fourth week scan data

## Data Characteristics:
- Gradually increasing number of hosts per week
- Varying vulnerability counts
- Mix of Critical, High, Medium, Low, and Info findings
- Realistic CVEs and plugin IDs
- Different scan profiles (Production, DMZ, Development)

Generated on: {}
""".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with open(os.path.join(base_path, "README.md"), "w") as f:
        f.write(readme_content)

if __name__ == "__main__":
    main() 