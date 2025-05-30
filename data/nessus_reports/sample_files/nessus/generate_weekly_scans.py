#!/usr/bin/env python3
"""
Generate weekly Nessus files from April 2024 to May 2025 for realistic metrics testing.
Each file simulates a weekly scan with realistic vulnerability lifecycle including critical vulns.
"""
import re
import random
from datetime import datetime, timedelta
from pathlib import Path

NESSUS_DIR = Path(__file__).parent
TEMPLATE_FILE = NESSUS_DIR / "nessus_scan_week5.nessus"  # Use existing as template
START_DATE = datetime(2024, 5, 1, 10, 0, 0)  # Start from May 1, 2024
END_DATE = datetime(2025, 5, 27, 10, 0, 0)   # End at May 27, 2025

# Helper to update all date fields in the Nessus XML
DATE_PATTERNS = [
    (re.compile(r"HOST_START>[^<]+<"), "HOST_START>{}<"),
    (re.compile(r"HOST_END>[^<]+<"), "HOST_END>{}<"),
    (re.compile(r"Scan Start Date : [^<\n]+"), "Scan Start Date : {}"),
]

# Helper to find all ReportItem blocks
REPORT_ITEM_PATTERN = re.compile(r"(<ReportItem[\s\S]*?</ReportItem>)", re.MULTILINE)

# Helper to find pluginID and severity in ReportItem
PLUGIN_ID_PATTERN = re.compile(r'pluginID="(\d+)"')
SEVERITY_PATTERN = re.compile(r'severity="(\d+)"')

# Simulate vuln lifecycle with different rates by severity
PERSIST_PROB = {
    "4": 0.85,  # Critical: 85% persist (harder to fix)
    "3": 0.75,  # High: 75% persist
    "2": 0.65,  # Medium: 65% persist
    "1": 0.55,  # Low: 55% persist (easier to fix)
    "0": 0.90   # Info: 90% persist (usually not fixed)
}

# New vulnerability introduction rates
NEW_VULN_RATES = {
    "4": 0.02,  # Critical: 2% chance per week
    "3": 0.05,  # High: 5% chance per week
    "2": 0.10,  # Medium: 10% chance per week
    "1": 0.15,  # Low: 15% chance per week
    "0": 0.08   # Info: 8% chance per week
}

# Critical vulnerability templates
CRITICAL_VULNS = [
    {
        "name": "Remote Code Execution in Web Server",
        "description": "A critical remote code execution vulnerability was found",
        "solution": "Update to the latest version immediately"
    },
    {
        "name": "SQL Injection in Database Interface",
        "description": "SQL injection vulnerability allows data extraction",
        "solution": "Apply security patches and input validation"
    },
    {
        "name": "Buffer Overflow in Network Service",
        "description": "Buffer overflow can lead to system compromise",
        "solution": "Install security updates and restart services"
    },
    {
        "name": "Authentication Bypass Vulnerability",
        "description": "Authentication can be bypassed allowing unauthorized access",
        "solution": "Update authentication mechanisms"
    },
    {
        "name": "Privilege Escalation Vulnerability",
        "description": "Local users can escalate privileges to administrator",
        "solution": "Apply kernel patches and security updates"
    }
]

random.seed(42)  # For reproducible results

def parse_report_items(content):
    return REPORT_ITEM_PATTERN.findall(content)

def get_severity(item):
    match = SEVERITY_PATTERN.search(item)
    return match.group(1) if match else "0"

def get_plugin_id(item):
    match = PLUGIN_ID_PATTERN.search(item)
    return match.group(1) if match else None

def update_dates(content, scan_date):
    # Format: Mon May 27 10:00:00 2025
    dt_str = scan_date.strftime("%a %b %d %H:%M:%S %Y")
    dt_short = scan_date.strftime("%Y/%m/%d %H:%M")
    for pat, repl in DATE_PATTERNS:
        if "Scan Start Date" in repl:
            content = pat.sub(repl.format(dt_short), content)
        else:
            content = pat.sub(repl.format(dt_str), content)
    return content

def create_critical_vuln(vuln_id, vuln_template, scan_date):
    """Create a critical vulnerability ReportItem"""
    return f'''<ReportItem pluginID="{vuln_id}" pluginName="{vuln_template['name']}" severity="4" port="443" protocol="tcp" svc_name="https">
<description>{vuln_template['description']}</description>
<solution>{vuln_template['solution']}</solution>
<risk_factor>Critical</risk_factor>
<cvss_base_score>9.8</cvss_base_score>
<cvss_temporal_score>8.5</cvss_temporal_score>
<cvss_vector>CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H</cvss_vector>
<plugin_publication_date>{scan_date.strftime('%Y/%m/%d')}</plugin_publication_date>
<plugin_modification_date>{scan_date.strftime('%Y/%m/%d')}</plugin_modification_date>
</ReportItem>'''

def main():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Get all unique vulnerabilities from template
    report_items = parse_report_items(template)
    vuln_by_severity = {}
    
    for item in report_items:
        plugin_id = get_plugin_id(item)
        severity = get_severity(item)
        if plugin_id:
            if severity not in vuln_by_severity:
                vuln_by_severity[severity] = []
            vuln_by_severity[severity].append((plugin_id, item))
    
    # Track which vulns are open each week
    open_vulns = {sev: set(pid for pid, _ in vulns) for sev, vulns in vuln_by_severity.items()}
    closed_vulns = {sev: set() for sev in vuln_by_severity.keys()}
    
    # Ensure we have critical severity tracking even if template doesn't have any
    if "4" not in open_vulns:
        open_vulns["4"] = set()
        closed_vulns["4"] = set()
    
    # Generate weekly scans
    current_date = START_DATE
    week_count = 0
    critical_vuln_counter = 95000  # Start critical vulns at 95000
    
    while current_date <= END_DATE:
        week_count += 1
        print(f"Generating week {week_count}: {current_date.strftime('%Y-%m-%d')}")
        
        # Simulate vulnerability lifecycle for each severity
        new_report_items = []
        total_closed = 0
        
        # Include critical severity even if not in template
        all_severities = set(vuln_by_severity.keys()) | {"4"}
        
        for severity in all_severities:
            # Close some existing vulns based on persistence probability
            closing = {pid for pid in open_vulns[severity] 
                      if random.random() > PERSIST_PROB.get(severity, 0.7)}
            open_vulns[severity] -= closing
            closed_vulns[severity] |= closing
            total_closed += len(closing)
            
            # Add new vulnerabilities
            if severity == "4":  # Critical vulns - force creation
                num_new = max(1, int(week_count * 0.1))  # Gradually increase critical vulns
                for _ in range(num_new):
                    critical_vuln_counter += 1
                    vuln_template = random.choice(CRITICAL_VULNS)
                    new_item = create_critical_vuln(critical_vuln_counter, vuln_template, current_date)
                    new_report_items.append(new_item)
                    open_vulns[severity].add(str(critical_vuln_counter))
            else:
                # For other severities, create simpler new vulns
                num_new = int(len(vuln_by_severity.get(severity, [])) * NEW_VULN_RATES.get(severity, 0.05))
                for _ in range(num_new):
                    new_id = str(90000 + int(severity) * 1000 + week_count * 10 + random.randint(0, 9))
                    if new_id not in open_vulns[severity]:
                        new_item = f'<ReportItem pluginID="{new_id}" pluginName="Simulated {severity} Severity Vuln {new_id}" severity="{severity}" port="0" protocol="tcp" svc_name="general" />'
                        new_report_items.append(new_item)
                        open_vulns[severity].add(new_id)
        
        # Add existing open vulnerabilities
        for severity, vulns in vuln_by_severity.items():
            for plugin_id, item in vulns:
                if plugin_id in open_vulns[severity]:
                    new_report_items.append(item)
        
        # Replace all ReportItems in template
        new_content = REPORT_ITEM_PATTERN.sub("", template)
        new_content = new_content.replace("</Report>", "\n".join(new_report_items) + "\n</Report>")
        
        # Update dates
        new_content = update_dates(new_content, current_date)
        
        # Write file
        out_file = NESSUS_DIR / f"nessus_scan_{current_date.strftime('%Y%m%d')}.nessus"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        total_open = sum(len(vulns) for vulns in open_vulns.values())
        critical_count = len(open_vulns.get("4", []))
        high_count = len(open_vulns.get("3", []))
        
        print(f"  Generated: {out_file.name}")
        print(f"  Total open vulns: {total_open} (Critical: {critical_count}, High: {high_count}, Closed: {total_closed})")
        
        # Move to next week
        current_date += timedelta(weeks=1)

if __name__ == "__main__":
    main() 