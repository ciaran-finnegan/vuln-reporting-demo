from django.shortcuts import render
import os
import tempfile
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.response import Response
from rest_framework import status
from .nessus_scanreport_import import ScannerImporter
from .utils import calculate_upload_hash, check_duplicate_upload, get_duplicate_info
from .models import ScannerUpload, ScannerIntegration
from django.utils import timezone

logger = logging.getLogger(__name__)

# Create your views here.

@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FileUploadParser])
def upload_nessus_file(request):
    """
    Upload and parse a Nessus .nessus file.
    
    Query Parameters:
        force_reimport (bool): Set to 'true' to bypass duplicate detection
    
    Returns:
        JSON response with import statistics, duplicate info, or error details
    """
    try:
        # Validate request
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided. Please upload a .nessus file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        force_reimport = request.query_params.get('force_reimport', '').lower() == 'true'
        
        # Validate file type
        if not uploaded_file.name.lower().endswith('.nessus'):
            return Response(
                {'error': 'Invalid file type. Please upload a .nessus file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (100MB limit)
        max_size = 100 * 1024 * 1024  # 100MB
        if uploaded_file.size > max_size:
            return Response(
                {'error': f'File too large. Maximum size is {max_size // (1024*1024)}MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate file hash for duplicate detection
        try:
            file_hash = calculate_upload_hash(uploaded_file)
            logger.info(f"Calculated hash for {uploaded_file.name}: {file_hash}")
        except Exception as e:
            logger.error(f"Error calculating file hash for {uploaded_file.name}: {str(e)}")
            return Response(
                {'error': 'Error processing file. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Check for duplicates
        is_duplicate, existing_upload = check_duplicate_upload(file_hash, 'Nessus')
        
        if is_duplicate and not force_reimport:
            duplicate_info = get_duplicate_info(existing_upload)
            logger.info(f"Duplicate file detected: {uploaded_file.name} matches upload ID {existing_upload.id}")
            
            return Response(
                {
                    'error': 'Duplicate file detected',
                    'message': 'This file has already been uploaded and processed.',
                    'duplicate_info': duplicate_info,
                    'solution': 'Use force_reimport=true query parameter to bypass duplicate detection.',
                    'filename': uploaded_file.name,
                    'file_hash': file_hash,
                    'is_duplicate': True
                },
                status=status.HTTP_409_CONFLICT
            )
        
        # Save file temporarily
        temp_file_path = None
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(
                suffix='.nessus',
                dir=settings.FILE_UPLOAD_TEMP_DIR,
                delete=False
            ) as temp_file:
                temp_file_path = temp_file.name
                
                # Write uploaded file content to temp file
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
            
            logger.info(f"Processing Nessus file: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            # Get or create Nessus integration
            nessus_integration, created = ScannerIntegration.objects.get_or_create(
                name='Nessus',
                defaults={
                    'type': 'vuln_scanner',
                    'description': 'Nessus vulnerability scanner'
                }
            )
            
            # Create or update upload record with hash
            if is_duplicate and force_reimport:
                # Force re-import: update existing record
                upload_record = existing_upload
                upload_record.filename = uploaded_file.name
                upload_record.file_size = uploaded_file.size
                upload_record.file_path = temp_file_path
                upload_record.status = 'processing'
                upload_record.error_message = ''
                upload_record.processed_at = None
                upload_record.save()
                logger.info(f"Force re-import: updating existing upload record ID {upload_record.id}")
            else:
                # New upload: create new record
                upload_record = ScannerUpload.objects.create(
                    integration=nessus_integration,
                    filename=uploaded_file.name,
                    file_size=uploaded_file.size,
                    file_hash=file_hash,
                    file_path=temp_file_path,
                    status='processing'
                )
            
            # Import the file using existing parser
            importer = ScannerImporter(integration_name='Nessus')
            import_stats = importer.import_file(temp_file_path)
            
            # Update upload record with results
            upload_record.processed_at = timezone.now()
            upload_record.status = 'completed' if not import_stats.get('errors') else 'completed_with_errors'
            upload_record.stats = import_stats
            upload_record.save()
            
            # Check authentication status
            authenticated_user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                authenticated_user = request.user.email
            
            # Prepare response
            response_data = {
                'success': True,
                'message': 'File uploaded and processed successfully',
                'filename': uploaded_file.name,
                'file_size': uploaded_file.size,
                'file_hash': file_hash,
                'upload_id': upload_record.id,
                'force_reimport_used': force_reimport,
                'authenticated': authenticated_user is not None,
                'uploaded_by': authenticated_user or 'Anonymous',
                'statistics': {
                    'assets_processed': import_stats.get('assets', 0),
                    'vulnerabilities_processed': import_stats.get('vulnerabilities', 0),
                    'findings_processed': import_stats.get('findings', 0),
                    'errors': import_stats.get('errors', [])
                },
                'parser_details': {
                    'assets_created': importer.created_assets,
                    'vulnerabilities_created': importer.created_vulnerabilities,
                    'findings_created': importer.created_findings,
                    'findings_updated': importer.updated_findings
                }
            }
            
            # Log successful import
            logger.info(f"Successfully imported {uploaded_file.name}: {import_stats}")
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Update upload record with error
            if 'upload_record' in locals():
                upload_record.status = 'failed'
                upload_record.error_message = str(e)
                upload_record.save()
            
            logger.error(f"Error processing Nessus file {uploaded_file.name}: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': f'Error processing file: {str(e)}',
                    'filename': uploaded_file.name,
                    'file_hash': file_hash
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    logger.warning(f"Could not delete temporary file: {temp_file_path}")
    
    except Exception as e:
        logger.error(f"Unexpected error in upload_nessus_file: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An unexpected error occurred while processing your request.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def api_status(request):
    """
    Simple API status endpoint to verify the API is working.
    """
    return Response({
        'status': 'ok',
        'message': 'Risk Radar API is operational',
        'endpoints': {
            'upload_nessus': '/api/v1/upload/nessus',
            'upload_history': '/api/v1/upload/history',
            'status': '/api/v1/status',
            'upload_info': '/api/v1/upload/info'
        }
    })

@api_view(['GET'])
def upload_info(request):
    """
    Provide information about file upload requirements and limits.
    """
    return Response({
        'file_upload_limits': {
            'max_file_size_mb': settings.FILE_UPLOAD_MAX_MEMORY_SIZE // (1024 * 1024),
            'allowed_extensions': ['.nessus'],
            'max_memory_size_mb': settings.DATA_UPLOAD_MAX_MEMORY_SIZE // (1024 * 1024)
        },
        'supported_scanners': ['Nessus'],
        'upload_endpoint': '/api/v1/upload/nessus'
    })

@api_view(['GET'])
def upload_history(request):
    """
    Get upload history with optional filtering.
    
    Query Parameters:
        status: Filter by status (pending, processing, completed, failed)
        integration: Filter by integration name
        limit: Number of records to return (default: 50)
        offset: Number of records to skip (default: 0)
    """
    try:
        # Get query parameters
        status_filter = request.query_params.get('status')
        integration_filter = request.query_params.get('integration')
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        # Validate limit
        if limit > 200:
            limit = 200
        
        # Build query
        uploads = ScannerUpload.objects.all()
        
        if status_filter:
            uploads = uploads.filter(status=status_filter)
        
        if integration_filter:
            uploads = uploads.filter(integration__name__icontains=integration_filter)
        
        # Get total count and paginated results
        total_count = uploads.count()
        uploads = uploads[offset:offset + limit]
        
        # Format response
        upload_list = []
        for upload in uploads:
            upload_data = {
                'upload_id': upload.id,
                'filename': upload.filename,
                'file_size': upload.file_size,
                'file_hash': upload.file_hash,
                'integration': upload.integration.name,
                'status': upload.status,
                'uploaded_at': upload.uploaded_at.isoformat(),
                'processed_at': upload.processed_at.isoformat() if upload.processed_at else None,
                'error_message': upload.error_message if upload.error_message else None,
                'stats': upload.stats
            }
            upload_list.append(upload_data)
        
        return Response({
            'success': True,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'uploads': upload_list
        })
        
    except ValueError as e:
        return Response(
            {'error': f'Invalid parameter value: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error in upload_history: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An error occurred while retrieving upload history.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def auth_status(request):
    """
    Check if the current request is authenticated.
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'email': request.user.email,
                'is_admin': request.user.is_staff
            }
        })
    else:
        return Response({
            'authenticated': False,
            'user': None
        })

@api_view(['GET'])
def auth_profile(request):
    """
    Get detailed user profile and permissions.
    Requires authentication.
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user = request.user
    
    # Get user profile if exists
    try:
        from .models import UserProfile
        profile = UserProfile.objects.get(user=user)
        profile_data = {
            'business_group': profile.business_group.name if profile.business_group else None,
            'supabase_user_id': profile.supabase_user_id
        }
    except UserProfile.DoesNotExist:
        profile_data = {
            'business_group': None,
            'supabase_user_id': None
        }
    
    return Response({
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat()
        },
        'profile': profile_data,
        'permissions': {
            'is_admin': user.is_staff,
            'can_upload': True,
            'can_view_logs': user.is_staff
        }
    })
