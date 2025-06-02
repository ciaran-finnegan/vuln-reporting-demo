import hashlib
import os
from typing import Optional, Tuple
from .models import ScannerUpload

def calculate_file_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA-256 hash as hexadecimal string
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    
    return sha256_hash.hexdigest()

def calculate_upload_hash(uploaded_file) -> str:
    """
    Calculate SHA-256 hash of an uploaded Django file.
    
    Args:
        uploaded_file: Django UploadedFile object
        
    Returns:
        SHA-256 hash as hexadecimal string
    """
    sha256_hash = hashlib.sha256()
    
    # Reset file pointer to beginning
    uploaded_file.seek(0)
    
    # Read file in chunks
    for chunk in uploaded_file.chunks():
        sha256_hash.update(chunk)
    
    # Reset file pointer for subsequent processing
    uploaded_file.seek(0)
    
    return sha256_hash.hexdigest()

def check_duplicate_upload(file_hash: str, integration_name: str = None) -> Tuple[bool, Optional[ScannerUpload]]:
    """
    Check if a file with the same hash has already been uploaded.
    
    Args:
        file_hash: SHA-256 hash of the file
        integration_name: Optional scanner integration name for filtering
        
    Returns:
        Tuple of (is_duplicate, existing_upload_record)
    """
    query = ScannerUpload.objects.filter(file_hash=file_hash)
    
    if integration_name:
        query = query.filter(integration__name=integration_name)
    
    existing_upload = query.first()
    
    return existing_upload is not None, existing_upload

def get_duplicate_info(existing_upload: ScannerUpload) -> dict:
    """
    Get detailed information about an existing duplicate upload.
    
    Args:
        existing_upload: ScannerUpload record of the duplicate
        
    Returns:
        Dictionary with duplicate upload information
    """
    return {
        'upload_id': existing_upload.id,
        'original_filename': existing_upload.filename,
        'original_upload_date': existing_upload.uploaded_at.isoformat(),
        'file_size': existing_upload.file_size,
        'integration': existing_upload.integration.name,
        'processing_status': existing_upload.status,
        'stats': existing_upload.stats
    } 