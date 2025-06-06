from django.core.management.base import BaseCommand
from core.models import (
    ScannerIntegration, IntegrationSyncLog, IntegrationAlert, 
    IntegrationQuota, AssetCategory
)
from django.utils import timezone
from datetime import timedelta
import uuid
import random


class Command(BaseCommand):
    help = 'Populate realistic demo data for Integration Management System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all demo data and recreate',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️  Resetting integration management demo data...')
            IntegrationSyncLog.objects.all().delete()
            IntegrationAlert.objects.all().delete()
            IntegrationQuota.objects.all().delete()

        # ================================
        # UPDATE EXISTING NESSUS INTEGRATION
        # ================================
        self.stdout.write('🔄 Updating existing Nessus integration...')
        
        try:
            nessus = ScannerIntegration.objects.get(name='Nessus')
            
            # Update with new Integration Management fields
            nessus.integration_type = 'file_upload'
            nessus.vendor = 'Tenable'
            nessus.logo_url = '/static/logos/nessus.png'
            nessus.status = 'active'
            nessus.environment = 'production'
            
            # Set realistic sync data
            nessus.sync_enabled = True
            nessus.sync_schedule = '0 2 * * *'  # Daily at 2 AM
            nessus.sync_timezone = 'UTC'
            nessus.last_sync_at = timezone.now() - timedelta(hours=2)
            nessus.last_sync_status = 'success'
            nessus.next_sync_at = timezone.now() + timedelta(hours=22)
            
            # Health and error tracking
            nessus.consecutive_failures = 0
            nessus.total_error_count = 3
            nessus.health_score = 95
            nessus.last_error_at = timezone.now() - timedelta(days=5)
            nessus.last_error_message = "File parsing warning: Unknown plugin ID 999999"
            
            # Configuration
            nessus.connection_config = {
                'upload_directory': '/uploads/nessus/',
                'allowed_extensions': ['.nessus'],
                'max_file_size': '100MB',
                'auto_import': True,
                'duplicate_detection': True,
                'retention_days': 90
            }
            
            nessus.rate_limit_config = {
                'max_files_per_hour': 10,
                'max_concurrent_processing': 2
            }
            
            nessus.notification_config = {
                'email_alerts': True,
                'alert_recipients': ['admin@riskradar.com'],
                'alert_on_failure': True,
                'alert_on_success': False
            }
            
            # Statistics 
            nessus.total_records_processed = 15420
            nessus.total_assets_created = 1250
            nessus.total_vulnerabilities_created = 8745
            nessus.total_findings_created = 12680
            nessus.average_sync_duration = 4.5
            
            # Feature flags
            nessus.feature_flags = {
                'enable_plugin_output': True,
                'enable_compliance_data': True,
                'enable_web_app_scanning': False
            }
            
            nessus.save()
            self.stdout.write(self.style.SUCCESS('✅ Updated Nessus integration'))
            
        except ScannerIntegration.DoesNotExist:
            self.stdout.write(self.style.WARNING('⚠️  Nessus integration not found, creating new one...'))
            
            # Get or create a default asset category
            default_category, _ = AssetCategory.objects.get_or_create(
                name='Network Device',
                defaults={'description': 'Network infrastructure devices'}
            )
            
            nessus = ScannerIntegration.objects.create(
                name='Nessus',
                type='vuln_scanner',
                default_asset_category=default_category,
                version='10.6.0',
                description='Tenable Nessus vulnerability scanner integration',
                is_active=True,
                
                # Integration Management fields
                integration_type='file_upload',
                vendor='Tenable',
                logo_url='/static/logos/nessus.png',
                status='active',
                environment='production',
                
                # Sync configuration
                sync_enabled=True,
                sync_schedule='0 2 * * *',
                sync_timezone='UTC',
                last_sync_at=timezone.now() - timedelta(hours=2),
                last_sync_status='success',
                next_sync_at=timezone.now() + timedelta(hours=22),
                
                # Health metrics
                consecutive_failures=0,
                total_error_count=3,
                health_score=95,
                last_error_at=timezone.now() - timedelta(days=5),
                last_error_message="File parsing warning: Unknown plugin ID 999999",
                
                # Configuration
                connection_config={
                    'upload_directory': '/uploads/nessus/',
                    'allowed_extensions': ['.nessus'],
                    'max_file_size': '100MB',
                    'auto_import': True,
                    'duplicate_detection': True,
                    'retention_days': 90
                },
                
                rate_limit_config={
                    'max_files_per_hour': 10,
                    'max_concurrent_processing': 2
                },
                
                notification_config={
                    'email_alerts': True,
                    'alert_recipients': ['admin@riskradar.com'],
                    'alert_on_failure': True,
                    'alert_on_success': False
                },
                
                # Statistics
                total_records_processed=15420,
                total_assets_created=1250,
                total_vulnerabilities_created=8745,
                total_findings_created=12680,
                average_sync_duration=4.5,
                
                # Feature flags
                feature_flags={
                    'enable_plugin_output': True,
                    'enable_compliance_data': True,
                    'enable_web_app_scanning': False
                }
            )
            self.stdout.write(self.style.SUCCESS('✅ Created new Nessus integration'))

        # ================================
        # CREATE INTEGRATION QUOTA
        # ================================
        quota, created = IntegrationQuota.objects.get_or_create(
            integration=nessus,
            defaults={
                'monthly_api_calls_limit': None,  # File upload doesn't use API calls
                'daily_api_calls_limit': None,
                'hourly_api_calls_limit': None,
                'monthly_api_calls_used': 0,
                'daily_api_calls_used': 0,
                'hourly_api_calls_used': 0,
                'quota_exceeded': False,
                'quota_warning_sent': False
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created integration quota for Nessus'))

        # ================================
        # CREATE SYNC LOGS (LAST 30 DAYS)
        # ================================
        self.stdout.write('📊 Creating sync logs...')
        
        sync_statuses = ['success', 'success', 'success', 'success', 'error', 'partial']
        trigger_types = ['scheduled', 'manual', 'manual', 'scheduled']
        
        sync_logs_created = 0
        for i in range(25):  # Last 25 syncs
            days_ago = random.randint(0, 30)
            started_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            status = random.choice(sync_statuses)
            duration = random.uniform(2.5, 8.5) if status != 'error' else random.uniform(0.1, 1.5)
            
            sync_log = IntegrationSyncLog.objects.create(
                integration=nessus,
                sync_id=uuid.uuid4(),
                trigger_type=random.choice(trigger_types),
                started_at=started_at,
                completed_at=started_at + timedelta(minutes=duration) if status != 'error' else started_at + timedelta(seconds=duration*60),
                duration_seconds=duration * 60,
                status=status,
                records_processed=random.randint(100, 1500) if status != 'error' else random.randint(0, 50),
                records_created=random.randint(50, 800) if status != 'error' else 0,
                records_updated=random.randint(20, 200) if status != 'error' else 0,
                records_failed=random.randint(0, 5) if status == 'partial' else 0,
                error_message='Connection timeout during file processing' if status == 'error' else '',
                error_details={
                    'error_code': 'TIMEOUT_ERROR',
                    'file_size': '85MB',
                    'processed_percentage': random.randint(10, 90)
                } if status == 'error' else {},
                performance_metrics={
                    'file_size_mb': random.uniform(15.5, 120.0),
                    'parse_time_seconds': random.uniform(30, 180),
                    'database_write_time_seconds': random.uniform(60, 300),
                    'memory_peak_mb': random.uniform(256, 512)
                },
                sync_summary={
                    'new_assets': random.randint(5, 50),
                    'new_vulnerabilities': random.randint(20, 150),
                    'new_findings': random.randint(100, 800),
                    'duplicate_findings_skipped': random.randint(10, 100)
                } if status != 'error' else {}
            )
            sync_logs_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {sync_logs_created} sync logs'))

        # ================================
        # CREATE INTEGRATION ALERTS
        # ================================
        self.stdout.write('🚨 Creating integration alerts...')
        
        alerts = [
            {
                'alert_type': 'sync_failure',
                'severity': 'medium',
                'title': 'File Processing Timeout',
                'message': 'Nessus file processing timed out after 10 minutes. This may be due to large file size or system load.',
                'status': 'resolved',
                'first_occurred_at': timezone.now() - timedelta(days=5),
                'resolved_at': timezone.now() - timedelta(days=5, hours=2),
                'occurrence_count': 1,
                'alert_data': {
                    'file_name': 'enterprise_scan_20250101.nessus',
                    'file_size': '98MB',
                    'timeout_duration': '10m'
                }
            },
            {
                'alert_type': 'data_quality_issue',
                'severity': 'low',
                'title': 'Unknown Plugin IDs Detected',
                'message': 'Found 3 unknown plugin IDs during file processing. These vulnerabilities were imported with generic information.',
                'status': 'acknowledged',
                'first_occurred_at': timezone.now() - timedelta(days=2),
                'acknowledged_at': timezone.now() - timedelta(days=1),
                'occurrence_count': 3,
                'alert_data': {
                    'unknown_plugins': ['999999', '888888', '777777'],
                    'affected_findings': 15
                }
            },
            {
                'alert_type': 'performance_degraded',
                'severity': 'medium',
                'title': 'Slow File Processing',
                'message': 'Recent sync operations are taking longer than usual. Average processing time has increased by 35%.',
                'status': 'active',
                'first_occurred_at': timezone.now() - timedelta(hours=6),
                'occurrence_count': 5,
                'alert_data': {
                    'average_duration_minutes': 7.2,
                    'previous_average_minutes': 4.5,
                    'performance_degradation_percent': 35
                }
            }
        ]
        
        alerts_created = 0
        for alert_data in alerts:
            alert = IntegrationAlert.objects.create(
                integration=nessus,
                **alert_data
            )
            alerts_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {alerts_created} integration alerts'))

        # ================================
        # CREATE DEMO INTEGRATIONS FOR UI
        # ================================
        self.stdout.write('🎨 Creating demo integrations for UI showcase...')
        
        demo_integrations = [
            {
                'name': 'Qualys VMDR Demo',
                'vendor': 'Qualys',
                'integration_type': 'api',
                'status': 'testing',
                'environment': 'staging',
                'sync_enabled': False,
                'health_score': 85,
                'total_records_processed': 8420,
                'description': 'Demo Qualys VMDR integration for testing API connectivity'
            },
            {
                'name': 'Tenable.io Demo',
                'vendor': 'Tenable',
                'integration_type': 'api', 
                'status': 'inactive',
                'environment': 'development',
                'sync_enabled': False,
                'health_score': 100,
                'total_records_processed': 0,
                'description': 'Development Tenable.io integration for API testing'
            }
        ]
        
        demo_created = 0
        for demo_data in demo_integrations:
            demo_integration, created = ScannerIntegration.objects.get_or_create(
                name=demo_data['name'],
                defaults={
                    'type': 'vuln_scanner',
                    'description': demo_data['description'],
                    'is_active': demo_data['status'] == 'active',
                    **demo_data
                }
            )
            if created:
                demo_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {demo_created} demo integrations'))

        # ================================
        # SUMMARY
        # ================================
        total_integrations = ScannerIntegration.objects.count()
        total_sync_logs = IntegrationSyncLog.objects.count()
        total_alerts = IntegrationAlert.objects.count()
        total_quotas = IntegrationQuota.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Integration Management demo data setup complete!\n'
                f'   Total Integrations: {total_integrations}\n'
                f'   Sync Logs: {total_sync_logs}\n'
                f'   Active Alerts: {IntegrationAlert.objects.filter(status="active").count()}\n'
                f'   Integration Quotas: {total_quotas}\n'
                f'\n📊 Integration Status Summary:\n'
            )
        )
        
        # Status summary
        for status, label in ScannerIntegration.STATUS_CHOICES:
            count = ScannerIntegration.objects.filter(status=status).count()
            if count > 0:
                status_emoji = {
                    'active': '🟢',
                    'inactive': '⚪',
                    'testing': '🟡',
                    'error': '🔴',
                    'maintenance': '🟠',
                    'deprecated': '⚫'
                }
                self.stdout.write(f'   {status_emoji.get(status, "📍")} {label}: {count}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🚀 Ready for frontend development!\n'
                f'   The Integration Management System now has realistic demo data\n'
                f'   showcasing enterprise-grade integration capabilities.\n'
            )
        ) 