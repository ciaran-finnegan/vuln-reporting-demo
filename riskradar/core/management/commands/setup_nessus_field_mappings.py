from django.core.management.base import BaseCommand
from core.models import ScannerIntegration, FieldMapping, SeverityMapping

class Command(BaseCommand):
    help = 'Set up Nessus scanner integration with field mappings'

    def handle(self, *args, **options):
        # Create or update Nessus integration
        nessus, created = ScannerIntegration.objects.update_or_create(
            name='Nessus',
            defaults={
                'description': 'Tenable Nessus vulnerability scanner',
                'version': '10.x',
                'type': 'vuln_scanner',
                'is_active': True
            }
        )
        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} Nessus integration'))

        # Clear existing mappings
        FieldMapping.objects.filter(integration=nessus).delete()
        SeverityMapping.objects.filter(integration=nessus).delete()

        # Asset field mappings
        asset_mappings = [
            {
                'source_field': 'host-ip',
                'target_model': 'asset',
                'target_field': 'ip_address',
                'field_type': 'string',
                'is_required': True,
                'description': 'Host IP address'
            },
            {
                'source_field': 'name',
                'target_model': 'asset',
                'target_field': 'hostname',
                'field_type': 'string',
                'is_required': False,
                'description': 'Host FQDN or NetBIOS name'
            },
            {
                'source_field': 'operating-system',
                'target_model': 'asset',
                'target_field': 'operating_system',
                'field_type': 'string',
                'is_required': False,
                'description': 'Detected operating system'
            },
            {
                'source_field': 'host-fqdn',
                'target_model': 'asset',
                'target_field': 'extra.fqdn',
                'field_type': 'string',
                'is_required': False,
                'description': 'Fully qualified domain name'
            },
            {
                'source_field': 'netbios-name',
                'target_model': 'asset',
                'target_field': 'extra.netbios_name',
                'field_type': 'string',
                'is_required': False,
                'description': 'NetBIOS name'
            }
        ]

        # Vulnerability field mappings
        vuln_mappings = [
            {
                'source_field': 'ReportItem@pluginID',
                'target_model': 'vulnerability',
                'target_field': 'external_id',
                'field_type': 'string',
                'is_required': True,
                'description': 'Nessus plugin ID'
            },
            {
                'source_field': 'ReportItem@pluginName',
                'target_model': 'vulnerability',
                'target_field': 'title',
                'field_type': 'string',
                'is_required': True,
                'description': 'Vulnerability title'
            },
            {
                'source_field': 'synopsis',
                'target_model': 'vulnerability',
                'target_field': 'description',
                'field_type': 'string',
                'is_required': False,
                'description': 'Brief description of the issue'
            },
            {
                'source_field': 'solution',
                'target_model': 'vulnerability',
                'target_field': 'fix_info',
                'field_type': 'string',
                'is_required': False,
                'description': 'Remediation information'
            },
            {
                'source_field': 'cve',
                'target_model': 'vulnerability',
                'target_field': 'cve_id',
                'field_type': 'string',
                'is_required': False,
                'description': 'CVE identifier',
                'transformation_rule': "value.split(',')[0] if value and ',' in value else value"
            },
            {
                'source_field': 'cvss_base_score',
                'target_model': 'vulnerability',
                'target_field': 'cvss_score',
                'field_type': 'decimal',
                'is_required': False,
                'description': 'CVSS base score'
            },
            {
                'source_field': 'see_also',
                'target_model': 'vulnerability',
                'target_field': 'references',
                'field_type': 'json',
                'is_required': False,
                'description': 'External references',
                'transformation_rule': "[ref.strip() for ref in value.split('\\n')] if value else []"
            },
            {
                'source_field': 'cvss_vector',
                'target_model': 'vulnerability',
                'target_field': 'cvss.vector',
                'field_type': 'string',
                'is_required': False,
                'description': 'CVSS vector string'
            }
        ]

        # Finding field mappings
        finding_mappings = [
            {
                'source_field': 'ReportItem@port',
                'target_model': 'finding',
                'target_field': 'port',
                'field_type': 'integer',
                'is_required': False,
                'description': 'Port number'
            },
            {
                'source_field': 'ReportItem@protocol',
                'target_model': 'finding',
                'target_field': 'protocol',
                'field_type': 'string',
                'is_required': False,
                'description': 'Protocol (tcp/udp)'
            },
            {
                'source_field': 'ReportItem@svc_name',
                'target_model': 'finding',
                'target_field': 'service',
                'field_type': 'string',
                'is_required': False,
                'description': 'Service name'
            },
            {
                'source_field': 'plugin_output',
                'target_model': 'finding',
                'target_field': 'plugin_output',
                'field_type': 'string',
                'is_required': False,
                'description': 'Detailed plugin output'
            }
        ]

        # Create all field mappings
        all_mappings = asset_mappings + vuln_mappings + finding_mappings
        for i, mapping_data in enumerate(all_mappings):
            mapping_data['integration'] = nessus
            mapping_data['sort_order'] = i
            FieldMapping.objects.create(**mapping_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(all_mappings)} field mappings'))

        # Create severity mappings with normalised levels
        severity_mappings = [
            # Info/None severity
            {'external_severity': '0', 'internal_severity_label': 'Info', 'internal_severity_level': 0, 
             'description': 'Nessus None severity'},
            {'external_severity': 'None', 'internal_severity_label': 'Info', 'internal_severity_level': 0, 
             'description': 'Nessus None severity'},
            
            # Low severity
            {'external_severity': '1', 'internal_severity_label': 'Low', 'internal_severity_level': 2, 
             'description': 'Nessus Low severity'},
            {'external_severity': 'Low', 'internal_severity_label': 'Low', 'internal_severity_level': 2, 
             'description': 'Nessus Low severity'},
            
            # Medium severity
            {'external_severity': '2', 'internal_severity_label': 'Medium', 'internal_severity_level': 5, 
             'description': 'Nessus Medium severity'},
            {'external_severity': 'Medium', 'internal_severity_label': 'Medium', 'internal_severity_level': 5, 
             'description': 'Nessus Medium severity'},
            
            # High severity
            {'external_severity': '3', 'internal_severity_label': 'High', 'internal_severity_level': 8, 
             'description': 'Nessus High severity'},
            {'external_severity': 'High', 'internal_severity_label': 'High', 'internal_severity_level': 8, 
             'description': 'Nessus High severity'},
            
            # Critical severity
            {'external_severity': '4', 'internal_severity_label': 'Critical', 'internal_severity_level': 10, 
             'description': 'Nessus Critical severity'},
            {'external_severity': 'Critical', 'internal_severity_label': 'Critical', 'internal_severity_level': 10, 
             'description': 'Nessus Critical severity'},
        ]
        
        for mapping_data in severity_mappings:
            mapping_data['integration'] = nessus
            mapping_data['is_active'] = True
            SeverityMapping.objects.create(**mapping_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(severity_mappings)} severity mappings'))
        self.stdout.write(self.style.SUCCESS('Nessus field mappings setup complete!'))
