from django.core.management.base import BaseCommand
from core.models import Asset, Vulnerability, Finding, AssetType, BusinessGroup, SLAPolicy, RemediationCampaign, CampaignFinding, ScannerUpload, FieldMapping, SeverityMapping, ScannerIntegration, AssetTag
from django.db import transaction

class Command(BaseCommand):
    help = 'Delete all demo data: assets, vulnerabilities, findings, and related tables.'

    def add_arguments(self, parser):
        parser.add_argument('--noinput', action='store_true', help='Do not prompt for confirmation')
        parser.add_argument('--keep-asset-types', action='store_true', help='Do not delete AssetType records')
        parser.add_argument('--keep-mappings', action='store_true', help='Do not delete FieldMapping, SeverityMapping, ScannerIntegration')

    @transaction.atomic
    def handle(self, *args, **options):
        if not options['noinput']:
            confirm = input('Are you sure you want to delete ALL asset, vulnerability, finding, and related data? Type "yes" to continue: ')
            if confirm.strip().lower() != 'yes':
                self.stdout.write(self.style.WARNING('Aborted.'))
                return
        # Delete in dependency order
        CampaignFinding.objects.all().delete()
        RemediationCampaign.objects.all().delete()
        Finding.objects.all().delete()
        Vulnerability.objects.all().delete()
        Asset.objects.all().delete()
        if not options['keep_asset_types']:
            AssetType.objects.all().delete()
        BusinessGroup.objects.all().delete()
        SLAPolicy.objects.all().delete()
        ScannerUpload.objects.all().delete()
        if not options['keep_mappings']:
            FieldMapping.objects.all().delete()
            SeverityMapping.objects.all().delete()
            ScannerIntegration.objects.all().delete()
        AssetTag.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All demo data deleted.')) 