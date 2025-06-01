import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

# Configurable parameters
default_assets = [
    {'hostname': 'qa3app01', 'ip': '10.31.112.21'},
    {'hostname': 'qa3app02', 'ip': '10.31.112.22'},
    {'hostname': 'qa3app03', 'ip': '10.31.112.23'},
    {'hostname': 'qa3app04', 'ip': '10.31.112.24'},
    {'hostname': 'qa3app05', 'ip': '10.31.112.25'},
    {'hostname': 'qa3app06', 'ip': '10.31.112.26'},
]
default_vulns = [
    {
        'pluginID': str(10000 + i),
        'pluginName': f"Sample Vulnerability {i+1}",
        'pluginFamily': random.choice(['Windows', 'Web Servers', 'Databases', 'Network']),
        'severity': random.choice(['0', '1', '2', '3', '4']),
        'cvss_base_score': round(random.uniform(2.0, 10.0), 1),
        'description': f"This is a description for vulnerability {i+1}.",
        'solution': f"Apply the recommended patch for vulnerability {i+1}.",
        'synopsis': f"Synopsis for vulnerability {i+1}.",
        'risk_factor': random.choice(['Low', 'Medium', 'High', 'Critical']),
        'cve': [f"CVE-2024-{1000+i}"],
        'bid': [str(50000+i)],
        'xref': [f"OSVDB:{60000+i}"],
        'see_also': [f"https://vuln.example.com/{i+1}"],
        'exploitability_ease': random.choice(['No exploit available', 'Exploits are available']),
        'exploit_available': random.choice(['true', 'false']),
        'cvss_vector': "CVSS2#AV:N/AC:M/Au:N/C:P/I:P/A:P",
        'cvss_temporal_score': round(random.uniform(1.0, 10.0), 1),
        'plugin_modification_date': None,  # Will be set per week
        'plugin_publication_date': None,   # Will be set per week
        'patch_publication_date': None,    # Will be set per week
        'vuln_publication_date': None,     # Will be set per week
    }
    for i in range(20)
]

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 5, 31)
OUTPUT_DIR = Path('./generated_nessus_files')
OUTPUT_DIR.mkdir(exist_ok=True)

# Helper to create Nessus XML

def create_nessus_file(week_start, assets, vulns, asset_vuln_map, filename):
    root = Element('NessusClientData')
    # Policy (minimal)
    policy = SubElement(root, 'Policy')
    SubElement(policy, 'policyName').text = f"Weekly Policy {week_start.strftime('%Y-%m-%d')}"
    # Report
    report = SubElement(root, 'Report', name=f"Weekly Scan {week_start.strftime('%Y-%m-%d')}" )
    for asset in assets:
        host = SubElement(report, 'ReportHost', name=asset['ip'])
        host_props = SubElement(host, 'HostProperties')
        SubElement(host_props, 'tag', name='host-fqdn').text = asset['hostname']
        SubElement(host_props, 'tag', name='host-ip').text = asset['ip']
        SubElement(host_props, 'tag', name='HOST_START').text = (week_start + timedelta(hours=9)).strftime('%a %b %d %H:%M:%S %Y')
        SubElement(host_props, 'tag', name='HOST_END').text = (week_start + timedelta(hours=10)).strftime('%a %b %d %H:%M:%S %Y')
        # Add vulnerabilities for this asset
        for vuln in asset_vuln_map[asset['ip']]:
            item = SubElement(host, 'ReportItem',
                port=str(random.choice([0, 22, 80, 135, 3389, 443, 445, 3306, 5432, 8080])),
                svc_name=random.choice(['general', 'http', 'cifs', 'rdp', 'ssh', 'mssql', 'postgres']),
                protocol=random.choice(['tcp', 'udp']),
                severity=vuln['severity'],
                pluginID=vuln['pluginID'],
                pluginName=vuln['pluginName'],
                pluginFamily=vuln['pluginFamily']
            )
            SubElement(item, 'description').text = vuln['description']
            SubElement(item, 'solution').text = vuln['solution']
            SubElement(item, 'synopsis').text = vuln['synopsis']
            SubElement(item, 'cvss_base_score').text = str(vuln['cvss_base_score'])
            SubElement(item, 'risk_factor').text = vuln['risk_factor']
            for cve in vuln['cve']:
                SubElement(item, 'cve').text = cve
            for bid in vuln['bid']:
                SubElement(item, 'bid').text = bid
            for xref in vuln['xref']:
                SubElement(item, 'xref').text = xref
            for see in vuln['see_also']:
                SubElement(item, 'see_also').text = see
            SubElement(item, 'exploitability_ease').text = vuln['exploitability_ease']
            SubElement(item, 'exploit_available').text = vuln['exploit_available']
            SubElement(item, 'cvss_vector').text = vuln['cvss_vector']
            SubElement(item, 'cvss_temporal_score').text = str(vuln['cvss_temporal_score'])
            # Dates
            SubElement(item, 'plugin_modification_date').text = vuln['plugin_modification_date']
            SubElement(item, 'plugin_publication_date').text = vuln['plugin_publication_date']
            SubElement(item, 'patch_publication_date').text = vuln['patch_publication_date']
            SubElement(item, 'vuln_publication_date').text = vuln['vuln_publication_date']
    # Write file
    tree = ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)

# Main simulation loop
def main():
    week = 0
    current_date = START_DATE
    assets = default_assets.copy()
    vulns = [v.copy() for v in default_vulns]
    # Set initial vuln dates
    for v in vulns:
        v['plugin_modification_date'] = (START_DATE - timedelta(days=random.randint(30, 180))).strftime('%Y/%m/%d')
        v['plugin_publication_date'] = (START_DATE - timedelta(days=random.randint(30, 180))).strftime('%Y/%m/%d')
        v['patch_publication_date'] = (START_DATE - timedelta(days=random.randint(0, 60))).strftime('%Y/%m/%d')
        v['vuln_publication_date'] = (START_DATE - timedelta(days=random.randint(30, 180))).strftime('%Y/%m/%d')
    # Track which vulns are present on which assets
    asset_vuln_map = {a['ip']: set(random.sample(vulns, random.randint(3, 6))) for a in assets}
    while current_date <= END_DATE:
        # Each week, randomly fix some vulns and introduce new ones
        for asset in assets:
            # Fix some existing vulns
            if asset_vuln_map[asset['ip']]:
                to_fix = random.sample(list(asset_vuln_map[asset['ip']]), k=random.randint(0, 2))
                for v in to_fix:
                    asset_vuln_map[asset['ip']].remove(v)
            # Add new vulns
            new_vulns = random.sample(vulns, k=random.randint(0, 2))
            for v in new_vulns:
                asset_vuln_map[asset['ip']].add(v)
        # Update vuln dates for realism
        for v in vulns:
            v['plugin_modification_date'] = (current_date - timedelta(days=random.randint(0, 30))).strftime('%Y/%m/%d')
            v['plugin_publication_date'] = (current_date - timedelta(days=random.randint(30, 180))).strftime('%Y/%m/%d')
            v['patch_publication_date'] = (current_date - timedelta(days=random.randint(0, 60))).strftime('%Y/%m/%d')
            v['vuln_publication_date'] = (current_date - timedelta(days=random.randint(30, 180))).strftime('%Y/%m/%d')
        # Prepare mapping for this week
        week_asset_vulns = {ip: list(vs) for ip, vs in asset_vuln_map.items()}
        filename = OUTPUT_DIR / f"nessus_scan_{current_date.strftime('%Y-%m-%d')}.nessus"
        create_nessus_file(current_date, assets, vulns, week_asset_vulns, filename)
        print(f"Generated {filename}")
        current_date += timedelta(weeks=1)
        week += 1

if __name__ == "__main__":
    main() 