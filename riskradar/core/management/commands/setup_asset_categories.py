from django.core.management.base import BaseCommand
from core.models import AssetCategory, AssetSubtype, ScannerIntegration
from django.db import transaction

class Command(BaseCommand):
    help = 'Set up standard asset categories and subtypes from ASSET_TYPES.md'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                          help='Clear existing categories and subtypes before creating new ones')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing asset categories and subtypes...')
            AssetSubtype.objects.all().delete()
            AssetCategory.objects.all().delete()

        # Create standard categories
        categories_data = [
            ('Host', 'Physical servers, VMs, workstations, network devices, IoT'),
            ('Code Project', 'Software codebases, repositories, development projects'),
            ('Website', 'Web-based applications and services'),
            ('Image', 'Container images, running containers, registries'),
            ('Cloud Resource', 'Cloud provider resources and services'),
        ]

        categories = {}
        for name, description in categories_data:
            category, created = AssetCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            categories[name] = category
            if created:
                self.stdout.write(f'Created category: {name}')
            else:
                self.stdout.write(f'Category already exists: {name}')

        # Host subtypes
        host_subtypes = [
            'Server', 'Workstation', 'NAS Device', 'Printer', 'Scanner', 
            'IoT Device', 'Network Device', 'Virtual Machine', 'Physical Machine',
            'Laptop', 'Desktop', 'Firewall', 'Router', 'Switch', 'Load Balancer',
            'Storage Device', 'Mobile Device', 'Appliance'
        ]

        for subtype_name in host_subtypes:
            subtype, created = AssetSubtype.objects.get_or_create(
                category=categories['Host'],
                name=subtype_name,
                defaults={'description': f'Host subtype: {subtype_name}'}
            )
            if created:
                self.stdout.write(f'  Created Host subtype: {subtype_name}')

        # Code Project subtypes
        code_subtypes = [
            'Repository', 'SAST Project', 'SCA Project', 'IAC Project',
            'GitHub Repository', 'GitLab Repository', 'Bitbucket Repository',
            'Source Code', 'Application Project', 'Library', 'Framework'
        ]

        for subtype_name in code_subtypes:
            subtype, created = AssetSubtype.objects.get_or_create(
                category=categories['Code Project'],
                name=subtype_name,
                defaults={'description': f'Code project subtype: {subtype_name}'}
            )
            if created:
                self.stdout.write(f'  Created Code Project subtype: {subtype_name}')

        # Website subtypes
        website_subtypes = [
            'Web Application', 'Internet Service', 'Main Domain',
            'Base URL', 'Subdomain', 'API Endpoint'
        ]

        for subtype_name in website_subtypes:
            subtype, created = AssetSubtype.objects.get_or_create(
                category=categories['Website'],
                name=subtype_name,
                defaults={'description': f'Website subtype: {subtype_name}'}
            )
            if created:
                self.stdout.write(f'  Created Website subtype: {subtype_name}')

        # Image subtypes
        image_subtypes = [
            'Container Image', 'Container', 'Registry', 'Docker Image',
            'OCI Image', 'Virtual Machine Image', 'Base Image', 'Application Image'
        ]

        for subtype_name in image_subtypes:
            subtype, created = AssetSubtype.objects.get_or_create(
                category=categories['Image'],
                name=subtype_name,
                defaults={'description': f'Image subtype: {subtype_name}'}
            )
            if created:
                self.stdout.write(f'  Created Image subtype: {subtype_name}')

        # Cloud Resource subtypes for each provider
        aws_subtypes = [
            'EC2 Instance', 'Lambda Function', 'S3 Bucket', 'RDS Instance',
            'VPC', 'Subnet', 'Security Group', 'IAM User', 'IAM Role',
            'CloudFront Distribution', 'ELB', 'ECS Cluster', 'EKS Cluster'
        ]

        azure_subtypes = [
            'Virtual Machine', 'VM Scale Set', 'App Service', 'Function App',
            'Storage Account', 'SQL Database', 'Virtual Network', 'Subnet',
            'Public IP Address', 'Network Security Group', 'Key Vault',
            'Kubernetes Service (AKS)', 'Resource Group'
        ]

        gcp_subtypes = [
            'Compute Engine VM', 'Cloud Function', 'Cloud Run Service',
            'Cloud Storage Bucket', 'Cloud SQL Instance', 'VPC Network',
            'Subnet', 'Firewall Rule', 'GKE Cluster', 'Service Account',
            'Project', 'Load Balancer'
        ]

        # Create cloud subtypes
        for provider, subtypes in [('AWS', aws_subtypes), ('Azure', azure_subtypes), ('GCP', gcp_subtypes)]:
            for subtype_name in subtypes:
                subtype, created = AssetSubtype.objects.get_or_create(
                    category=categories['Cloud Resource'],
                    name=subtype_name,
                    cloud_provider=provider,
                    defaults={'description': f'{provider} cloud resource: {subtype_name}'}
                )
                if created:
                    self.stdout.write(f'  Created {provider} Cloud Resource subtype: {subtype_name}')

        # Set default category for Nessus integration (Host)
        try:
            nessus_integration = ScannerIntegration.objects.get(name='Nessus')
            if not nessus_integration.default_asset_category:
                nessus_integration.default_asset_category = categories['Host']
                nessus_integration.save()
                self.stdout.write('Set Nessus default category to Host')
        except ScannerIntegration.DoesNotExist:
            self.stdout.write(self.style.WARNING('Nessus integration not found - will be set when integration is created'))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully set up asset categories:\n'
            f'  Categories: {AssetCategory.objects.count()}\n'
            f'  Subtypes: {AssetSubtype.objects.count()}'
        )) 