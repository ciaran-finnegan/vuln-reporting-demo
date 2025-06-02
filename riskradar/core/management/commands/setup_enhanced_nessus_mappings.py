from django.core.management.base import BaseCommand
from core.models import ScannerIntegration, FieldMapping, AssetCategory, AssetSubtype
from django.db import transaction

class Command(BaseCommand):
    help = 'Set up enhanced Nessus field mappings with asset type detection'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                          help='Clear existing field mappings before creating new ones')

    @transaction.atomic
    def handle(self, *args, **options):
        # Get or create Nessus integration
        nessus_integration, created = ScannerIntegration.objects.get_or_create(
            name='Nessus',
            defaults={
                'type': 'vuln_scanner',
                'description': 'Tenable Nessus vulnerability scanner',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('Created Nessus scanner integration')
        
        # Set default category to Host if not already set
        if not nessus_integration.default_asset_category:
            try:
                host_category = AssetCategory.objects.get(name='Host')
                nessus_integration.default_asset_category = host_category
                nessus_integration.save()
                self.stdout.write('Set Nessus default category to Host')
            except AssetCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING('Host category not found - run setup_asset_categories first'))

        if options['clear']:
            self.stdout.write('Clearing existing Nessus field mappings...')
            FieldMapping.objects.filter(integration=nessus_integration).delete()

        # Enhanced asset mappings with priority order
        asset_mappings = [
            # Asset type detection (highest priority)
            {
                'source_field': 'system-type',
                'target_model': 'asset',
                'target_field': 'subtype_id',
                'field_type': 'string',
                'transformation_rule': 'nessus_system_type_map',
                'sort_order': 5,
                'description': 'Map Nessus system-type to asset subtype'
            },
            # Default category fallback
            {
                'source_field': '',  # Empty means use default
                'target_model': 'asset',
                'target_field': 'category_id',
                'field_type': 'string',
                'transformation_rule': 'default_scanner_category',
                'sort_order': 3,
                'description': 'Set default category from scanner integration'
            },
            # Core asset identification
            {
                'source_field': 'host-ip',
                'target_model': 'asset',
                'target_field': 'ip_address',
                'field_type': 'string',
                'sort_order': 10,
                'description': 'Primary IP address'
            },
            {
                'source_field': 'HostName',
                'target_model': 'asset',
                'target_field': 'hostname',
                'field_type': 'string',
                'sort_order': 11,
                'description': 'Hostname from ReportHost'
            },
            # Enhanced host properties
            {
                'source_field': 'host-fqdn',
                'target_model': 'asset',
                'target_field': 'extra.fqdn',
                'field_type': 'string',
                'sort_order': 12,
                'description': 'Fully qualified domain name'
            },
            {
                'source_field': 'netbios-name',
                'target_model': 'asset',
                'target_field': 'extra.netbios_name',
                'field_type': 'string',
                'sort_order': 13,
                'description': 'NetBIOS name'
            },
            {
                'source_field': 'operating-system',
                'target_model': 'asset',
                'target_field': 'operating_system',
                'field_type': 'string',
                'sort_order': 14,
                'description': 'Operating system information'
            },
            {
                'source_field': 'mac-address',
                'target_model': 'asset',
                'target_field': 'mac_address',
                'field_type': 'string',
                'sort_order': 15,
                'description': 'MAC address'
            },
            # Store original system-type for reference
            {
                'source_field': 'system-type',
                'target_model': 'asset',
                'target_field': 'extra.system_type',
                'field_type': 'string',
                'sort_order': 16,
                'description': 'Original Nessus system-type value'
            },
            # Host identification and cloud metadata
            {
                'source_field': 'host-uuid',
                'target_model': 'asset',
                'target_field': 'extra.host_uuid',
                'field_type': 'string',
                'sort_order': 17,
                'description': 'Host UUID for correlation'
            },
            {
                'source_field': 'aws-instance-id',
                'target_model': 'asset',
                'target_field': 'extra.aws_instance_id',
                'field_type': 'string',
                'sort_order': 18,
                'description': 'AWS EC2 instance ID'
            },
            {
                'source_field': 'azure-vm-id',
                'target_model': 'asset',
                'target_field': 'extra.azure_vm_id',
                'field_type': 'string',
                'sort_order': 19,
                'description': 'Azure virtual machine ID'
            },
            {
                'source_field': 'gcp-instance-id',
                'target_model': 'asset',
                'target_field': 'extra.gcp_instance_id',
                'field_type': 'string',
                'sort_order': 20,
                'description': 'Google Cloud Platform instance ID'
            },
            # Additional metadata
            {
                'source_field': 'HOST_START',
                'target_model': 'asset',
                'target_field': 'extra.scan_start_time',
                'field_type': 'datetime',
                'sort_order': 21,
                'description': 'Scan start time for this host'
            },
            {
                'source_field': 'HOST_END',
                'target_model': 'asset',
                'target_field': 'extra.scan_end_time',
                'field_type': 'datetime',
                'sort_order': 22,
                'description': 'Scan end time for this host'
            },
        ]

        # Vulnerability mappings (same as before)
        vulnerability_mappings = [
            {
                'source_field': 'ReportItem@pluginID',
                'target_model': 'vulnerability',
                'target_field': 'external_id',
                'field_type': 'string',
                'sort_order': 100,
                'description': 'Nessus plugin ID'
            },
            {
                'source_field': 'ReportItem@pluginName',
                'target_model': 'vulnerability',
                'target_field': 'title',
                'field_type': 'string',
                'sort_order': 101,
                'description': 'Vulnerability title'
            },
            {
                'source_field': 'synopsis',
                'target_model': 'vulnerability',
                'target_field': 'extra.synopsis',
                'field_type': 'string',
                'sort_order': 102,
                'description': 'Brief vulnerability synopsis'
            },
            {
                'source_field': 'description',
                'target_model': 'vulnerability',
                'target_field': 'description',
                'field_type': 'string',
                'sort_order': 103,
                'description': 'Detailed vulnerability description'
            },
            {
                'source_field': 'solution',
                'target_model': 'vulnerability',
                'target_field': 'fix_info',
                'field_type': 'string',
                'sort_order': 104,
                'description': 'Remediation information'
            },
            {
                'source_field': 'ReportItem@severity',
                'target_model': 'vulnerability',
                'target_field': 'severity_level',
                'field_type': 'string',
                'transformation_rule': 'severity_map',
                'sort_order': 105,
                'description': 'Map Nessus severity to internal scale'
            },
            {
                'source_field': 'cvss_base_score',
                'target_model': 'vulnerability',
                'target_field': 'cvss_score',
                'field_type': 'decimal',
                'sort_order': 106,
                'description': 'CVSS base score'
            },
            {
                'source_field': 'cve',
                'target_model': 'vulnerability',
                'target_field': 'cve_id',
                'field_type': 'string',
                'transformation_rule': 'first',
                'sort_order': 107,
                'description': 'First CVE ID if multiple exist'
            },
        ]

        # Finding mappings
        finding_mappings = [
            {
                'source_field': 'ReportItem@port',
                'target_model': 'finding',
                'target_field': 'port',
                'field_type': 'integer',
                'sort_order': 200,
                'description': 'Network port'
            },
            {
                'source_field': 'ReportItem@protocol',
                'target_model': 'finding',
                'target_field': 'protocol',
                'field_type': 'string',
                'sort_order': 201,
                'description': 'Network protocol'
            },
            {
                'source_field': 'ReportItem@svc_name',
                'target_model': 'finding',
                'target_field': 'service',
                'field_type': 'string',
                'sort_order': 202,
                'description': 'Service name'
            },
            {
                'source_field': 'plugin_output',
                'target_model': 'finding',
                'target_field': 'details.plugin_output',
                'field_type': 'string',
                'sort_order': 203,
                'description': 'Plugin output evidence'
            },
        ]

        # Create all mappings
        all_mappings = asset_mappings + vulnerability_mappings + finding_mappings
        
        created_count = 0
        for mapping_data in all_mappings:
            mapping, created = FieldMapping.objects.get_or_create(
                integration=nessus_integration,
                source_field=mapping_data['source_field'],
                target_model=mapping_data['target_model'],
                target_field=mapping_data['target_field'],
                defaults={
                    'field_type': mapping_data['field_type'],
                    'transformation_rule': mapping_data.get('transformation_rule', ''),
                    'sort_order': mapping_data['sort_order'],
                    'description': mapping_data['description'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Enhanced Nessus field mappings setup complete:\n'
            f'  Created: {created_count} new mappings\n'
            f'  Total: {FieldMapping.objects.filter(integration=nessus_integration).count()} mappings'
        )) 