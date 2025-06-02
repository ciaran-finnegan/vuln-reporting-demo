
#!/usr/bin/env python3
"""
Generate a time series of Nessus files for metrics testing.
Each file simulates a weekly scan with realistic vulnerability lifecycle.
"""
import re
import random
from datetime import datetime, timedelta
from pathlib import Path

NESSUS_DIR = Path(__file__).parent
TEMPLATE_FILE = NESSUS_DIR / "nessus_scan_week5.nessus"  # Use the latest as template
START_DATE = datetime(2025, 3, 31, 10, 0, 0)  # 8 weeks before 27 May 2025
NUM_WEEKS = 8

# Helper to update all date fields in the Nessus XML
DATE_PATTERNS = [
    (re.compile(r"HOST_START>[^<]+<"), "HOST_START>{}<"),
    (re.compile(r"HOST_END>[^<]+<"), "HOST_END>{}<"),
    (re.compile(r"Scan Start Date : [^<\n]+"), "Scan Start Date : {}"),
]

# Helper to find all ReportItem blocks
REPORT_ITEM_PATTERN = re.compile(r"(<ReportItem[\s\S]*?</ReportItem>)", re.MULTILINE)

# Helper to find pluginID in ReportItem
PLUGIN_ID_PATTERN = re.compile(r'pluginID="(\d+)"')

# Simulate vuln lifecycle: some close, some persist, some new
PERSIST_PROB = 0.7  # 70% chance a vuln persists to next week
NEW_PROB = 0.2      # 20% chance of new vuln per week

random.seed(42)

def parse_report_items(content):
    return REPORT_ITEM_PATTERN.findall(content)

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

def main():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()
    # Get all unique pluginIDs in the template
    report_items = parse_report_items(template)
    all_plugin_ids = list({PLUGIN_ID_PATTERN.search(item).group(1) for item in report_items if PLUGIN_ID_PATTERN.search(item)})
    # Track which vulns are open each week
    open_vulns = set(all_plugin_ids)
    closed_vulns = set()
    for week in range(NUM_WEEKS):
        scan_date = START_DATE + timedelta(weeks=week)
        # Simulate closing some vulns
        closing = {pid for pid in open_vulns if random.random() > PERSIST_PROB}
        open_vulns -= closing
        closed_vulns |= closing
        # Simulate new vulns
        new_vulns = set()
        for _ in range(int(len(all_plugin_ids) * NEW_PROB)):
            # Fake new pluginIDs (e.g., 90000+week*10+idx)
            new_id = str(90000 + week * 10 + random.randint(0, 9))
            new_vulns.add(new_id)
        open_vulns |= new_vulns
        # Build new report items for open vulns
        new_report_items = []
        for item in report_items:
            pid_match = PLUGIN_ID_PATTERN.search(item)
            if pid_match and pid_match.group(1) in open_vulns:
                new_report_items.append(item)
        # Add new fake vulns
        for new_id in new_vulns:
            # Use a simple template for new vulns
            new_item = f'<ReportItem pluginID="{new_id}" pluginName="Simulated Vuln {new_id}" severity="2" port="0" protocol="tcp" svc_name="general" />'
            new_report_items.append(new_item)
        # Replace all ReportItems in template
        new_content = REPORT_ITEM_PATTERN.sub("", template)
        new_content = new_content.replace("</Report>", "\n".join(new_report_items) + "\n</Report>")
        # Update dates
        new_content = update_dates(new_content, scan_date)
        # Write file
        out_file = NESSUS_DIR / f"nessus_scan_{scan_date.strftime('%Y%m%d')}.nessus"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Generated: {out_file.name} with {len(new_report_items)} open vulns (closed: {len(closing)})")

if __name__ == "__main__":
    main() 