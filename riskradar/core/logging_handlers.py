import logging
import json
import uuid
from datetime import datetime
from django.conf import settings
from django.db import transaction
import threading

class SupabaseLogHandler(logging.Handler):
    """Custom log handler that sends logs to Supabase database"""
    
    def __init__(self):
        super().__init__()
        self.local = threading.local()
        
    def emit(self, record):
        """Emit a log record to Supabase"""
        try:
            # Avoid circular imports by importing here
            from .models import SystemLog
            
            # Get request context if available
            request = getattr(self.local, 'request', None)
            user = None
            request_id = None
            
            if request:
                user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                request_id = getattr(request, 'request_id', None)
            
            # Extract user and request_id from record if available
            if hasattr(record, 'user_id') and record.user_id:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=record.user_id)
                except (User.DoesNotExist, Exception):
                    pass
                    
            if hasattr(record, 'request_id'):
                request_id = record.request_id
            
            # Prepare metadata
            metadata = {
                'pathname': record.pathname,
                'lineno': record.lineno,
                'funcName': record.funcName,
                'process': record.process,
                'thread': record.thread,
            }
            
            # Add extra fields from record
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                              'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                              'thread', 'threadName', 'processName', 'process', 'getMessage',
                              'user_id', 'request_id']:
                    metadata[key] = str(value)
            
            # Create log entry in database
            with transaction.atomic():
                SystemLog.objects.create(
                    level=record.levelname,
                    source='django',
                    module=record.name,
                    message=self.format(record),
                    metadata=metadata,
                    user=user,
                    request_id=request_id
                )
                
        except Exception as e:
            # Don't let logging errors break the application
            # Log to console as fallback
            print(f"SupabaseLogHandler error: {e}")
            
    def set_request(self, request):
        """Set the current request for context"""
        self.local.request = request
        
    def clear_request(self):
        """Clear the current request context"""
        if hasattr(self.local, 'request'):
            delattr(self.local, 'request')


class RequestLoggingMiddleware:
    """Middleware to add request context to logging and generate request IDs"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Generate unique request ID
        request.request_id = str(uuid.uuid4())[:8]
        
        # Set request context for logging
        for handler in logging.getLogger().handlers:
            if isinstance(handler, SupabaseLogHandler):
                handler.set_request(request)
        
        # Log request start
        logger = logging.getLogger('core.middleware')
        extra = {
            'request_id': request.request_id,
            'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
        }
        
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra=extra
        )
        
        try:
            response = self.get_response(request)
            
            # Log successful response
            logger.info(
                f"Request completed: {request.method} {request.path} - {response.status_code}",
                extra=extra
            )
            
            return response
            
        except Exception as e:
            # Log request error
            logger.error(
                f"Request failed: {request.method} {request.path} - {str(e)}",
                extra=extra,
                exc_info=True
            )
            raise
            
        finally:
            # Clear request context
            for handler in logging.getLogger().handlers:
                if isinstance(handler, SupabaseLogHandler):
                    handler.clear_request() 