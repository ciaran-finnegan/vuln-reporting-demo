from django.core.management.base import BaseCommand
from core.models import AssetType, BusinessGroup, SLAPolicy

class Command(BaseCommand):
    help = 'Populate initial data for asset types, business groups, and SLA policies'

    def handle(self, *args, **options):
        # Create asset types
        asset_types = [
            'Host',
            'Website', 
            'Container',
            'Code',
            'Cloud'
        ]
        
        created_count = 0
        for asset_type_name in asset_types:
            asset_type, created = AssetType.objects.get_or_create(name=asset_type_name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created asset type: {asset_type_name}'))
            else:
                self.stdout.write(f'Asset type already exists: {asset_type_name}')
        
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} new asset types'))
        
        # Create business groups
        business_groups = [
            {
                'name': 'Production',
                'description': 'Production environment assets',
                'criticality_score': 10
            },
            {
                'name': 'Development',
                'description': 'Development environment assets',
                'criticality_score': 5
            },
            {
                'name': 'Staging',
                'description': 'Staging/UAT environment assets',
                'criticality_score': 7
            },
            {
                'name': 'Corporate',
                'description': 'Corporate IT assets',
                'criticality_score': 8
            }
        ]
        
        bg_created_count = 0
        for bg_data in business_groups:
            bg, created = BusinessGroup.objects.get_or_create(
                name=bg_data['name'],
                defaults={
                    'description': bg_data['description'],
                    'criticality_score': bg_data['criticality_score']
                }
            )
            if created:
                bg_created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created business group: {bg_data["name"]}'))
            else:
                self.stdout.write(f'Business group already exists: {bg_data["name"]}')
        
        self.stdout.write(self.style.SUCCESS(f'Created {bg_created_count} new business groups'))
        
        # Create default SLA policy
        default_sla_days = {
            'Critical': 7,
            'High': 30,
            'Medium': 90,
            'Low': 180,
            'Info': 365
        }
        
        default_sla, created = SLAPolicy.objects.get_or_create(
            name='Default SLA Policy',
            is_default=True,
            defaults={
                'severity_days': default_sla_days
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created default SLA policy'))
        else:
            self.stdout.write('Default SLA policy already exists')
        
        # Create business group specific SLA policies
        production_bg = BusinessGroup.objects.get(name='Production')
        production_sla_days = {
            'Critical': 3,
            'High': 14,
            'Medium': 30,
            'Low': 90,
            'Info': 180
        }
        
        production_sla, created = SLAPolicy.objects.get_or_create(
            name='Production SLA Policy',
            business_group=production_bg,
            defaults={
                'severity_days': production_sla_days,
                'is_default': False
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Production SLA policy'))
        else:
            self.stdout.write('Production SLA policy already exists')
        
        self.stdout.write(self.style.SUCCESS('Initial data population complete!')) 