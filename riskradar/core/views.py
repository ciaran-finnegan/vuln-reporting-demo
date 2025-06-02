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

logger = logging.getLogger(__name__)

# Create your views here.

@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FileUploadParser])
def upload_nessus_file(request):
    """
    Upload and parse a Nessus .nessus file.
    
    Returns:
        JSON response with import statistics or error details
    """
    try:
        # Validate request
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided. Please upload a .nessus file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
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
            
            # Import the file using existing parser
            importer = ScannerImporter(integration_name='Nessus')
            import_stats = importer.import_file(temp_file_path)
            
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
            logger.error(f"Error processing Nessus file {uploaded_file.name}: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': f'Error processing file: {str(e)}',
                    'filename': uploaded_file.name
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
            'status': '/api/v1/status'
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
