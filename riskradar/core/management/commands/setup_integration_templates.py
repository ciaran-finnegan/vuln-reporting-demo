from django.core.management.base import BaseCommand
from core.models import IntegrationTemplate
from django.utils import timezone


class Command(BaseCommand):
    help = 'Set up comprehensive integration templates for the Integration Management System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Delete existing templates and recreate',
        )

    def handle(self, *args, **options):
        if options['force']:
            self.stdout.write('🗑️  Deleting existing integration templates...')
            IntegrationTemplate.objects.all().delete()

        templates = [
            # ===============================
            # AVAILABLE INTEGRATIONS
            # ===============================
            {
                'name': 'Nessus Professional',
                'vendor': 'Tenable',
                'integration_type': 'file_upload',
                'logo_url': '/static/logos/nessus.png',
                'description': 'Import Nessus .nessus scan files with comprehensive vulnerability data including plugin output, CVSS scores, and asset information.',
                'status': 'available',
                'default_config': {
                    'upload_directory': '/uploads/nessus/',
                    'allowed_extensions': ['.nessus'],
                    'max_file_size': '100MB',
                    'auto_import': True,
                    'duplicate_detection': True
                },
                'required_fields': ['upload_directory'],
                'optional_fields': ['auto_import', 'duplicate_detection', 'max_file_size'],
                'field_mappings_template': 'nessus_enhanced_mappings',
                'setup_instructions': '''
# Nessus Integration Setup

## Prerequisites
- Nessus Professional or Nessus Manager
- Export permissions for .nessus files
- Network access to RiskRadar platform

## Configuration Steps
1. Configure upload directory path
2. Set file size limits (recommended: 100MB)
3. Enable auto-import for seamless processing
4. Test with a small scan file first

## Supported Data
- Asset discovery and classification
- Vulnerability details with plugin output
- CVSS v2 and v3 scores
- Network service information
- Compliance check results
                ''',
                'documentation_url': 'https://docs.tenable.com/nessus/',
                'support_contact': 'support@riskradar.com',
                'validation_rules': {
                    'upload_directory': {'required': True, 'type': 'string'},
                    'allowed_extensions': {'required': True, 'type': 'array'}
                },
                'capabilities': ['vulnerability_scanning', 'asset_discovery', 'compliance_checking', 'network_discovery']
            },
            
            # ===============================
            # COMING SOON INTEGRATIONS
            # ===============================
            {
                'name': 'Qualys VMDR',
                'vendor': 'Qualys',
                'integration_type': 'api',
                'logo_url': '/static/logos/qualys.png',
                'description': 'Real-time vulnerability data from Qualys Vulnerability Management, Detection and Response platform with continuous monitoring.',
                'status': 'coming_soon',
                'default_config': {
                    'api_endpoint': 'https://qualysapi.qg2.apps.qualys.com',
                    'auth_type': 'basic_auth',
                    'sync_frequency': 'daily',
                    'include_info_vulnerabilities': False
                },
                'required_fields': ['api_endpoint', 'username', 'password'],
                'optional_fields': ['sync_frequency', 'include_info_vulnerabilities', 'asset_group_filter'],
                'capabilities': ['vulnerability_scanning', 'asset_discovery', 'compliance_scanning', 'web_application_scanning']
            },
            
            {
                'name': 'Tenable.io',
                'vendor': 'Tenable',
                'integration_type': 'api',
                'logo_url': '/static/logos/tenable.png',
                'description': 'Cloud-based vulnerability management from Tenable.io with comprehensive asset discovery and modern vulnerability intelligence.',
                'status': 'coming_soon',
                'default_config': {
                    'api_endpoint': 'https://cloud.tenable.com',
                    'auth_type': 'api_key',
                    'sync_frequency': 'hourly'
                },
                'required_fields': ['access_key', 'secret_key'],
                'optional_fields': ['sync_frequency', 'folder_filter', 'tag_filter'],
                'capabilities': ['vulnerability_scanning', 'asset_discovery', 'web_application_scanning', 'container_scanning']
            },
            
            {
                'name': 'CrowdStrike Spotlight',
                'vendor': 'CrowdStrike',
                'integration_type': 'api',
                'logo_url': '/static/logos/crowdstrike.png',
                'description': 'Endpoint vulnerability assessment from CrowdStrike Falcon platform with real-time threat intelligence and zero-day protection.',
                'status': 'coming_soon',
                'default_config': {
                    'api_endpoint': 'https://api.crowdstrike.com',
                    'auth_type': 'oauth2',
                    'sync_frequency': 'real_time'
                },
                'required_fields': ['client_id', 'client_secret'],
                'optional_fields': ['sync_frequency', 'host_group_filter'],
                'capabilities': ['endpoint_vulnerability_scanning', 'threat_intelligence', 'real_time_monitoring']
            },
            
            {
                'name': 'Microsoft Defender TVM',
                'vendor': 'Microsoft',
                'integration_type': 'api',
                'logo_url': '/static/logos/microsoft-defender.png',
                'description': 'Threat and Vulnerability Management from Microsoft Defender with integrated Windows ecosystem vulnerability detection.',
                'status': 'coming_soon',
                'default_config': {
                    'api_endpoint': 'https://api.securitycenter.microsoft.com',
                    'auth_type': 'oauth2',
                    'tenant_id': '',
                    'sync_frequency': 'daily'
                },
                'required_fields': ['tenant_id', 'client_id', 'client_secret'],
                'optional_fields': ['sync_frequency', 'device_group_filter'],
                'capabilities': ['endpoint_vulnerability_scanning', 'microsoft_ecosystem', 'configuration_assessment']
            },
            
            {
                'name': 'Rapid7 InsightVM',
                'vendor': 'Rapid7',
                'integration_type': 'api',
                'logo_url': '/static/logos/rapid7.png',
                'description': 'Vulnerability management and analytics from Rapid7 InsightVM with risk-based prioritization and remediation guidance.',
                'status': 'coming_soon',
                'default_config': {
                    'api_endpoint': 'https://us.api.insight.rapid7.com',
                    'auth_type': 'api_key',
                    'sync_frequency': 'daily'
                },
                'required_fields': ['api_key'],
                'optional_fields': ['sync_frequency', 'site_filter', 'asset_group_filter'],
                'capabilities': ['vulnerability_scanning', 'asset_discovery', 'risk_analytics', 'remediation_planning']
            },
            
            {
                'name': 'Amazon Inspector',
                'vendor': 'Amazon Web Services',
                'integration_type': 'api',
                'logo_url': '/static/logos/aws-inspector.png',
                'description': 'Automated security assessment service for AWS workloads with container and EC2 vulnerability scanning.',
                'status': 'coming_soon',
                'default_config': {
                    'region': 'us-east-1',
                    'auth_type': 'aws_credentials',
                    'sync_frequency': 'daily'
                },
                'required_fields': ['access_key_id', 'secret_access_key', 'region'],
                'optional_fields': ['sync_frequency', 'account_filter'],
                'capabilities': ['aws_vulnerability_scanning', 'container_scanning', 'ec2_scanning', 'lambda_scanning']
            },
            
            {
                'name': 'Google Cloud Security Command Center',
                'vendor': 'Google Cloud',
                'integration_type': 'api',
                'logo_url': '/static/logos/gcp-scc.png',
                'description': 'Centralized vulnerability and threat detection for Google Cloud Platform with native GCP integration.',
                'status': 'coming_soon',
                'default_config': {
                    'project_id': '',
                    'auth_type': 'service_account',
                    'sync_frequency': 'daily'
                },
                'required_fields': ['project_id', 'service_account_key'],
                'optional_fields': ['sync_frequency', 'organization_filter'],
                'capabilities': ['gcp_vulnerability_scanning', 'cloud_security_posture', 'asset_inventory']
            },
            
            {
                'name': 'Azure Security Center',
                'vendor': 'Microsoft',
                'integration_type': 'api',
                'logo_url': '/static/logos/azure-security-center.png',
                'description': 'Unified security management and advanced threat protection for Azure workloads with policy compliance monitoring.',
                'status': 'coming_soon',
                'default_config': {
                    'subscription_id': '',
                    'auth_type': 'oauth2',
                    'sync_frequency': 'daily'
                },
                'required_fields': ['subscription_id', 'tenant_id', 'client_id', 'client_secret'],
                'optional_fields': ['sync_frequency', 'resource_group_filter'],
                'capabilities': ['azure_vulnerability_scanning', 'policy_compliance', 'security_recommendations']
            },
            
            {
                'name': 'OpenVAS',
                'vendor': 'Greenbone',
                'integration_type': 'api',
                'logo_url': '/static/logos/openvas.png',
                'description': 'Open-source vulnerability scanner with comprehensive network vulnerability detection and customizable scan configurations.',
                'status': 'coming_soon',
                'default_config': {
                    'gmp_endpoint': 'https://localhost:9390',
                    'auth_type': 'basic_auth',
                    'sync_frequency': 'weekly'
                },
                'required_fields': ['gmp_endpoint', 'username', 'password'],
                'optional_fields': ['sync_frequency', 'scan_config_filter'],
                'capabilities': ['vulnerability_scanning', 'network_discovery', 'open_source']
            },
            
            {
                'name': 'Nuclei',
                'vendor': 'ProjectDiscovery',
                'integration_type': 'file_upload',
                'logo_url': '/static/logos/nuclei.png',
                'description': 'Fast and customizable vulnerability scanner with community-driven templates for modern web applications.',
                'status': 'coming_soon',
                'default_config': {
                    'upload_directory': '/uploads/nuclei/',
                    'allowed_extensions': ['.json', '.txt'],
                    'template_source': 'community'
                },
                'required_fields': ['upload_directory'],
                'optional_fields': ['template_source', 'severity_filter'],
                'capabilities': ['web_vulnerability_scanning', 'template_based_scanning', 'community_driven']
            },
            
            {
                'name': 'GitHub Security Advisories',
                'vendor': 'GitHub',
                'integration_type': 'api',
                'logo_url': '/static/logos/github.png',
                'description': 'Repository vulnerability scanning and dependency analysis with GitHub\'s security advisory database.',
                'status': 'coming_soon',
                'default_config': {
                    'api_endpoint': 'https://api.github.com',
                    'auth_type': 'personal_access_token',
                    'sync_frequency': 'daily'
                },
                'required_fields': ['personal_access_token'],
                'optional_fields': ['sync_frequency', 'organization_filter', 'repository_filter'],
                'capabilities': ['dependency_scanning', 'code_vulnerability_scanning', 'supply_chain_security']
            },
            
            {
                'name': 'MITRE ATT&CK Framework',
                'vendor': 'MITRE Corporation',
                'integration_type': 'api',
                'logo_url': '/static/logos/mitre-attack.png',
                'description': 'Threat intelligence and attack pattern mapping with MITRE ATT&CK framework for enhanced threat context.',
                'status': 'coming_soon',
                'default_config': {
                    'api_endpoint': 'https://attack.mitre.org/api',
                    'sync_frequency': 'weekly',
                    'include_techniques': True
                },
                'required_fields': [],
                'optional_fields': ['sync_frequency', 'include_techniques', 'include_tactics'],
                'capabilities': ['threat_intelligence', 'attack_pattern_mapping', 'threat_context']
            },
            
            {
                'name': 'National Vulnerability Database',
                'vendor': 'NIST',
                'integration_type': 'api',
                'logo_url': '/static/logos/nvd.png',
                'description': 'Official U.S. government repository of vulnerability management data with comprehensive CVE information.',
                'status': 'coming_soon',
                'default_config': {
                    'api_endpoint': 'https://services.nvd.nist.gov/rest/json',
                    'sync_frequency': 'daily',
                    'include_historical': False
                },
                'required_fields': [],
                'optional_fields': ['sync_frequency', 'include_historical', 'severity_filter'],
                'capabilities': ['vulnerability_intelligence', 'cve_enrichment', 'government_authoritative']
            },
            
            # ===============================
            # BETA INTEGRATIONS
            # ===============================
            {
                'name': 'Custom Webhook Integration',
                'vendor': 'RiskRadar',
                'integration_type': 'webhook',
                'logo_url': '/static/logos/webhook.png',
                'description': 'Flexible webhook-based integration for custom vulnerability scanners and third-party security tools.',
                'status': 'beta',
                'default_config': {
                    'webhook_url': '',
                    'secret_key': '',
                    'event_types': ['scan_complete', 'new_vulnerability'],
                    'retry_attempts': 3
                },
                'required_fields': ['webhook_url', 'secret_key'],
                'optional_fields': ['event_types', 'retry_attempts', 'custom_headers'],
                'capabilities': ['custom_integration', 'real_time_data', 'flexible_format']
            }
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = IntegrationTemplate.objects.get_or_create(
                name=template_data['name'],
                vendor=template_data['vendor'],
                defaults=template_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created template: {template.vendor} {template.name}')
                )
            else:
                # Update existing template with new data
                for key, value in template_data.items():
                    setattr(template, key, value)
                template.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Updated template: {template.vendor} {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Integration templates setup complete!\n'
                f'   Created: {created_count} new templates\n'
                f'   Updated: {updated_count} existing templates\n'
                f'   Total: {len(templates)} templates configured\n'
            )
        )
        
        # Print summary by status
        for status, label in IntegrationTemplate.STATUS_CHOICES:
            count = IntegrationTemplate.objects.filter(status=status).count()
            if count > 0:
                self.stdout.write(f'   {label}: {count} templates') 