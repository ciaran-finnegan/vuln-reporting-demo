from django.core.management.base import BaseCommand
from core.models import ScannerIntegration, FieldMapping, SeverityMapping

class Command(BaseCommand):
    help = "Setup default field and severity mappings for Nessus integration"

    def handle(self, *args, **options):
        integration, _ = ScannerIntegration.objects.get_or_create(name="Nessus", defaults={"version": "v0.1", "description": "Tenable Nessus XML"})

        # Field mappings (expanded for generic schema)
        field_mappings = [
            # Asset fields
            {"source_field": "host-fqdn", "target_model": "asset", "target_field": "hostname", "field_type": "string"},
            {"source_field": "host-ip", "target_model": "asset", "target_field": "ip_address", "field_type": "string"},
            {"source_field": "Type", "target_model": "asset", "target_field": "asset_type", "field_type": "string", "default_value": "Host"},
            # Finding fields
            {"source_field": "@port", "target_model": "finding", "target_field": "port", "field_type": "integer"},
            {"source_field": "@protocol", "target_model": "finding", "target_field": "protocol", "field_type": "string", "default_value": "tcp"},
            {"source_field": "svc_name", "target_model": "finding", "target_field": "service", "field_type": "string"},
            {"source_field": "plugin_output", "target_model": "finding", "target_field": "plugin_output", "field_type": "string"},
            # Vulnerability fields (generic/extensible)
            {"source_field": "@pluginID", "target_model": "vulnerability", "target_field": "external_id", "field_type": "string"},
            {"source_field": "@pluginName", "target_model": "vulnerability", "target_field": "name", "field_type": "string"},
            {"source_field": "cvss_base_score", "target_model": "vulnerability", "target_field": "cvss_score", "field_type": "decimal"},
            {"source_field": "pluginFamily", "target_model": "vulnerability", "target_field": "metadata.family", "field_type": "string"},
            {"source_field": "description", "target_model": "vulnerability", "target_field": "description", "field_type": "string"},
            {"source_field": "solution", "target_model": "vulnerability", "target_field": "solution", "field_type": "string"},
            {"source_field": "synopsis", "target_model": "vulnerability", "target_field": "metadata.synopsis", "field_type": "string"},
            # Generic/extensible fields
            {"source_field": "cve", "target_model": "vulnerability", "target_field": "references", "field_type": "json"},
            {"source_field": "bid", "target_model": "vulnerability", "target_field": "references", "field_type": "json"},
            {"source_field": "xref", "target_model": "vulnerability", "target_field": "references", "field_type": "json"},
            {"source_field": "see_also", "target_model": "vulnerability", "target_field": "references", "field_type": "json"},
            {"source_field": "risk_factor", "target_model": "vulnerability", "target_field": "risk_factor", "field_type": "string"},
            {"source_field": "exploitability_ease", "target_model": "vulnerability", "target_field": "exploit", "field_type": "json"},
            {"source_field": "exploit_available", "target_model": "vulnerability", "target_field": "exploit", "field_type": "json"},
            {"source_field": "exploit_framework_core", "target_model": "vulnerability", "target_field": "exploit", "field_type": "json"},
            {"source_field": "exploit_framework_canvas", "target_model": "vulnerability", "target_field": "exploit", "field_type": "json"},
            {"source_field": "exploit_framework_metasploit", "target_model": "vulnerability", "target_field": "exploit", "field_type": "json"},
            {"source_field": "cvss_vector", "target_model": "vulnerability", "target_field": "cvss", "field_type": "json"},
            {"source_field": "cvss_temporal_score", "target_model": "vulnerability", "target_field": "cvss", "field_type": "json"},
            {"source_field": "plugin_modification_date", "target_model": "vulnerability", "target_field": "modified_at", "field_type": "datetime"},
            {"source_field": "plugin_publication_date", "target_model": "vulnerability", "target_field": "published_at", "field_type": "datetime"},
            {"source_field": "patch_publication_date", "target_model": "vulnerability", "target_field": "metadata.patch_publication_date", "field_type": "datetime"},
            {"source_field": "vuln_publication_date", "target_model": "vulnerability", "target_field": "metadata.vuln_publication_date", "field_type": "datetime"},
        ]

        for i, mapping in enumerate(field_mappings):
            FieldMapping.objects.update_or_create(
                integration=integration,
                source_field=mapping["source_field"],
                target_model=mapping["target_model"],
                target_field=mapping["target_field"],
                defaults={
                    "field_type": mapping["field_type"],
                    "is_required": False,
                    "default_value": mapping.get("default_value", ""),
                    "transformation_rule": mapping.get("transformation_rule", ""),
                    "description": "",
                    "is_active": True,
                    "sort_order": i,
                }
            )

        # Severity mappings
        severity_map = {
            "0": "Info",
            "1": "Low",
            "2": "Medium",
            "3": "High",
            "4": "Critical",
        }
        for source, target in severity_map.items():
            SeverityMapping.objects.update_or_create(
                integration=integration,
                source_value=source,
                defaults={
                    "target_value": target,
                    "description": "",
                    "is_active": True,
                }
            )

        self.stdout.write(self.style.SUCCESS("Nessus field and severity mappings have been set up (extended for generic schema)."))
