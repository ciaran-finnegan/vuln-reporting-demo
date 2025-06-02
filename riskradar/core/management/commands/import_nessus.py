import os
import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.nessus_scanreport_import import ScannerImporter
from core.models import ScannerIntegration, ScannerUpload
from core.utils import calculate_file_hash, check_duplicate_upload, get_duplicate_info

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import Nessus scan file(s) with duplicate detection'

    def add_arguments(self, parser):
        parser.add_argument(
            'path',
            type=str,
            help='Path to .nessus file or directory containing .nessus files'
        )
        parser.add_argument(
            '--force-reimport',
            action='store_true',
            help='Force re-import even if file has been uploaded before (bypasses duplicate detection)'
        )
        parser.add_argument(
            '--integration',
            type=str,
            default='Nessus',
            help='Scanner integration name (default: Nessus)'
        )

    def handle(self, *args, **options):
        path = options['path']
        force_reimport = options['force_reimport']
        integration_name = options['integration']
        
        if not os.path.exists(path):
            raise CommandError(f'Path does not exist: {path}')
        
        # Collect files to process
        files_to_process = []
        
        if os.path.isfile(path):
            if path.lower().endswith('.nessus'):
                files_to_process.append(path)
            else:
                raise CommandError(f'File must have .nessus extension: {path}')
        elif os.path.isdir(path):
            for filename in os.listdir(path):
                if filename.lower().endswith('.nessus'):
                    files_to_process.append(os.path.join(path, filename))
            
            if not files_to_process:
                raise CommandError(f'No .nessus files found in directory: {path}')
        else:
            raise CommandError(f'Path must be a file or directory: {path}')
        
        self.stdout.write(f'Found {len(files_to_process)} .nessus file(s) to process')
        
        # Get or create scanner integration
        try:
            integration = ScannerIntegration.objects.get(name=integration_name)
        except ScannerIntegration.DoesNotExist:
            integration = ScannerIntegration.objects.create(
                name=integration_name,
                type='vuln_scanner',
                description=f'{integration_name} vulnerability scanner'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created new integration: {integration_name}')
            )
        
        # Process each file
        total_stats = {
            'files_processed': 0,
            'files_skipped': 0,
            'duplicates_found': 0,
            'assets': 0,
            'vulnerabilities': 0,
            'findings': 0,
            'errors': []
        }
        
        for file_path in files_to_process:
            filename = os.path.basename(file_path)
            self.stdout.write(f'\nProcessing: {filename}')
            
            try:
                # Calculate file hash
                file_hash = calculate_file_hash(file_path)
                self.stdout.write(f'File hash: {file_hash}')
                
                # Check for duplicates
                is_duplicate, existing_upload = check_duplicate_upload(file_hash, integration_name)
                
                if is_duplicate and not force_reimport:
                    duplicate_info = get_duplicate_info(existing_upload)
                    self.stdout.write(
                        self.style.WARNING(
                            f'SKIPPED: Duplicate file detected (originally uploaded {duplicate_info["original_upload_date"]})'
                        )
                    )
                    self.stdout.write(f'Original filename: {duplicate_info["original_filename"]}')
                    self.stdout.write(f'Upload ID: {duplicate_info["upload_id"]}')
                    self.stdout.write(f'Use --force-reimport to bypass duplicate detection')
                    
                    total_stats['files_skipped'] += 1
                    total_stats['duplicates_found'] += 1
                    continue
                
                # Create or update upload record
                if is_duplicate and force_reimport:
                    # Force re-import: update existing record
                    upload_record = existing_upload
                    upload_record.filename = filename
                    upload_record.file_size = os.path.getsize(file_path)
                    upload_record.file_path = file_path
                    upload_record.status = 'processing'
                    upload_record.error_message = ''
                    upload_record.processed_at = None
                    upload_record.save()
                    self.stdout.write(self.style.WARNING(f'Force re-import: updating existing upload record ID {upload_record.id}'))
                else:
                    # New upload: create new record
                    upload_record = ScannerUpload.objects.create(
                        integration=integration,
                        filename=filename,
                        file_size=os.path.getsize(file_path),
                        file_hash=file_hash,
                        file_path=file_path,
                        status='processing'
                    )
                
                # Import the file
                importer = ScannerImporter(integration_name=integration_name)
                import_stats = importer.import_file(file_path)
                
                # Update upload record
                upload_record.processed_at = timezone.now()
                upload_record.status = 'completed' if not import_stats.get('errors') else 'completed_with_errors'
                upload_record.stats = import_stats
                upload_record.save()
                
                # Update totals
                total_stats['files_processed'] += 1
                total_stats['assets'] += import_stats.get('assets', 0)
                total_stats['vulnerabilities'] += import_stats.get('vulnerabilities', 0)
                total_stats['findings'] += import_stats.get('findings', 0)
                total_stats['errors'].extend(import_stats.get('errors', []))
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'SUCCESS: {import_stats.get("assets", 0)} assets, '
                        f'{import_stats.get("vulnerabilities", 0)} vulnerabilities, '
                        f'{import_stats.get("findings", 0)} findings'
                    )
                )
                
                if force_reimport:
                    self.stdout.write(self.style.WARNING('Note: Force re-import was used'))
                
            except Exception as e:
                error_msg = f'Error processing {filename}: {str(e)}'
                total_stats['errors'].append(error_msg)
                
                # Update upload record if it exists
                if 'upload_record' in locals():
                    upload_record.status = 'failed'
                    upload_record.error_message = str(e)
                    upload_record.save()
                
                self.stdout.write(self.style.ERROR(f'ERROR: {error_msg}'))
                logger.error(error_msg, exc_info=True)
        
        # Print summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('IMPORT SUMMARY'))
        self.stdout.write(f'Files processed: {total_stats["files_processed"]}')
        self.stdout.write(f'Files skipped (duplicates): {total_stats["files_skipped"]}')
        self.stdout.write(f'Total assets: {total_stats["assets"]}')
        self.stdout.write(f'Total vulnerabilities: {total_stats["vulnerabilities"]}')
        self.stdout.write(f'Total findings: {total_stats["findings"]}')
        
        if total_stats['errors']:
            self.stdout.write(f'Errors: {len(total_stats["errors"])}')
            for error in total_stats['errors']:
                self.stdout.write(f'  - {error}')
        
        if total_stats['duplicates_found'] > 0:
            self.stdout.write('\nNote: Use --force-reimport to process duplicate files') 