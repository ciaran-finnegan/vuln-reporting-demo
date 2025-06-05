import json
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db.models.functions import TruncHour, TruncDay
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
import subprocess
import docker

from .models import SystemLog

logger = logging.getLogger(__name__)

class IsAdminUser(BasePermission):
    """
    Custom permission to only allow admin users to access log endpoints.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_staff

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_logs(request):
    """Get filtered logs with pagination"""
    try:
        # Parse query parameters
        level = request.GET.get('level')
        source = request.GET.get('source')
        search = request.GET.get('search')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        user_id = request.GET.get('user_id')
        request_id = request.GET.get('request_id')
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        
        # Build query
        queryset = SystemLog.objects.all()
        
        # Apply filters
        if level and level != 'ALL':
            queryset = queryset.filter(level=level)
            
        if source and source != 'ALL':
            queryset = queryset.filter(source=source)
            
        if search:
            queryset = queryset.filter(
                Q(message__icontains=search) |
                Q(module__icontains=search)
            )
            
        if start_time:
            start_dt = parse_datetime(start_time)
            if start_dt:
                queryset = queryset.filter(timestamp__gte=start_dt)
                
        if end_time:
            end_dt = parse_datetime(end_time)
            if end_dt:
                queryset = queryset.filter(timestamp__lte=end_dt)
                
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        if request_id:
            queryset = queryset.filter(request_id=request_id)
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Apply pagination
        logs = queryset[offset:offset + limit]
        
        # Format response
        logs_data = []
        for log in logs:
            log_data = {
                'id': log.id,
                'timestamp': log.timestamp.isoformat(),
                'level': log.level,
                'source': log.source,
                'module': log.module,
                'message': log.message,
                'metadata': log.metadata,
                'request_id': log.request_id,
                'user': {
                    'id': log.user.id,
                    'email': log.user.email
                } if log.user else None
            }
            logs_data.append(log_data)
        
        response_data = {
            'logs': logs_data,
            'total_count': total_count,
            'has_more': offset + limit < total_count,
            'next_offset': offset + limit if offset + limit < total_count else None
        }
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_log_analytics_error_rate(request):
    """Get error rate trending data with level counts"""
    try:
        time_range = request.GET.get('timeRange', '24h')
        
        # Calculate time range
        now = timezone.now()
        if time_range == '1h':
            start_time = now - timedelta(hours=1)
            trunc_func = TruncHour
        elif time_range == '24h':
            start_time = now - timedelta(days=1)
            trunc_func = TruncHour
        elif time_range == '7d':
            start_time = now - timedelta(days=7)
            trunc_func = TruncDay
        else:
            start_time = now - timedelta(days=1)
            trunc_func = TruncHour
        
        # Get error counts by time period
        error_data = SystemLog.objects.filter(
            timestamp__gte=start_time,
            level__in=['ERROR', 'CRITICAL']
        ).extra(
            select={'time_bucket': f"date_trunc('hour', timestamp)"}
        ).values('time_bucket').annotate(
            error_count=Count('id')
        ).order_by('time_bucket')
        
        # Get total log counts for rate calculation
        total_data = SystemLog.objects.filter(
            timestamp__gte=start_time
        ).extra(
            select={'time_bucket': f"date_trunc('hour', timestamp)"}
        ).values('time_bucket').annotate(
            total_count=Count('id')
        ).order_by('time_bucket')
        
        # Get level counts for the chart
        level_counts = SystemLog.objects.filter(
            timestamp__gte=start_time
        ).values('level').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Combine error and total counts
        data_points = []
        total_dict = {item['time_bucket']: item['total_count'] for item in total_data}
        
        for error_item in error_data:
            time_bucket = error_item['time_bucket']
            error_count = error_item['error_count']
            total_count = total_dict.get(time_bucket, 0)
            error_rate = (error_count / total_count * 100) if total_count > 0 else 0
            
            data_points.append({
                'time': time_bucket.isoformat(),
                'error_count': error_count,
                'total_count': total_count,
                'error_rate': round(error_rate, 2)
            })
        
        return Response({
            'data': data_points,
            'level_counts': list(level_counts),  # Add level counts for frontend
            'time_range': time_range
        })
        
    except Exception as e:
        logger.error(f"Error getting error rate data: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_log_analytics_by_level(request):
    """Get log counts by level"""
    try:
        time_range = request.GET.get('timeRange', '24h')
        
        # Calculate time range
        now = timezone.now()
        if time_range == '1h':
            start_time = now - timedelta(hours=1)
        elif time_range == '24h':
            start_time = now - timedelta(days=1)
        elif time_range == '7d':
            start_time = now - timedelta(days=7)
        else:
            start_time = now - timedelta(days=1)
        
        # Get log counts by level
        level_data = SystemLog.objects.filter(
            timestamp__gte=start_time
        ).values('level').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'data': list(level_data),
            'time_range': time_range
        })
        
    except Exception as e:
        logger.error(f"Error getting level data: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_log_analytics_by_source(request):
    """Get log counts by source"""
    try:
        time_range = request.GET.get('timeRange', '24h')
        
        # Calculate time range
        now = timezone.now()
        if time_range == '1h':
            start_time = now - timedelta(hours=1)
        elif time_range == '24h':
            start_time = now - timedelta(days=1)
        elif time_range == '7d':
            start_time = now - timedelta(days=7)
        else:
            start_time = now - timedelta(days=1)
        
        # Get log counts by source
        source_data = SystemLog.objects.filter(
            timestamp__gte=start_time
        ).values('source').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'data': list(source_data),
            'time_range': time_range
        })
        
    except Exception as e:
        logger.error(f"Error getting source data: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_log_analytics_top_errors(request):
    """Get most frequent error messages"""
    try:
        limit = int(request.GET.get('limit', 10))
        time_range = request.GET.get('timeRange', '24h')
        
        # Calculate time range
        now = timezone.now()
        if time_range == '1h':
            start_time = now - timedelta(hours=1)
        elif time_range == '24h':
            start_time = now - timedelta(days=1)
        elif time_range == '7d':
            start_time = now - timedelta(days=7)
        else:
            start_time = now - timedelta(days=1)
        
        # Get top error messages
        top_errors = SystemLog.objects.filter(
            timestamp__gte=start_time,
            level__in=['ERROR', 'CRITICAL']
        ).values('message').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
        
        return Response({
            'data': list(top_errors),
            'time_range': time_range,
            'limit': limit
        })
        
    except Exception as e:
        logger.error(f"Error getting top errors: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_docker_logs(request, container_name):
    """Get Docker container logs (if enabled via ENABLE_DOCKER_LOGS env var)"""
    try:
        lines = int(request.GET.get('lines', 100))
        lines = min(lines, 1000)  # Cap at 1000 lines for performance
        
        # Check if Docker logs are enabled via environment variable
        import os
        docker_logs_enabled = os.getenv('ENABLE_DOCKER_LOGS', 'false').lower() == 'true'
        
        if not docker_logs_enabled:
            # Return informative message when Docker logs are disabled
            now = timezone.now()
            disabled_logs = [
                {
                    'timestamp': now.isoformat(),
                    'message': f'[INFO] Docker logs access is disabled'
                },
                {
                    'timestamp': (now - timedelta(seconds=30)).isoformat(),
                    'message': f'[INFO] Set ENABLE_DOCKER_LOGS=true in environment to enable'
                },
                {
                    'timestamp': (now - timedelta(seconds=60)).isoformat(),
                    'message': f'[INFO] Container: {container_name}'
                }
            ]
            
            return Response({
                'container': container_name,
                'logs': disabled_logs,
                'total_lines': len(disabled_logs),
                'lines_requested': lines,
                'docker_logs_enabled': False,
                'message': 'Docker logs disabled via ENABLE_DOCKER_LOGS environment variable'
            })
        
        # Use Docker API to get container logs
        try:
            client = docker.from_env()
            container = client.containers.get(container_name)
            logs = container.logs(tail=lines, timestamps=True).decode('utf-8')
            
            # Parse logs into structured format
            log_lines = []
            for line in logs.split('\n'):
                if line.strip():
                    # Try to parse timestamp
                    parts = line.split(' ', 1)
                    if len(parts) >= 2:
                        timestamp_str = parts[0]
                        message = parts[1]
                        log_lines.append({
                            'timestamp': timestamp_str,
                            'message': message
                        })
            
            return Response({
                'container': container_name,
                'logs': log_lines[-lines:],  # Return last N lines
                'total_lines': len(log_lines),
                'lines_requested': lines,
                'container_status': container.status,
                'docker_logs_enabled': True
            })
            
        except docker.errors.NotFound:
            return Response({'error': f'Container {container_name} not found'}, status=status.HTTP_404_NOT_FOUND)
        except (ConnectionError, FileNotFoundError, PermissionError) as docker_error:
            # Handle Docker socket access issues gracefully
            logger.warning(f"Docker socket access error for container {container_name}: {str(docker_error)}")
            
            # Return informative fallback message when Docker socket isn't accessible
            now = timezone.now()
            fallback_logs = [
                {
                    'timestamp': now.isoformat(),
                    'message': f'[WARNING] Docker socket not accessible: {str(docker_error)}'
                },
                {
                    'timestamp': (now - timedelta(seconds=30)).isoformat(),
                    'message': f'[INFO] ENABLE_DOCKER_LOGS is enabled but Docker socket is not mounted'
                },
                {
                    'timestamp': (now - timedelta(seconds=60)).isoformat(),
                    'message': f'[INFO] Container: {container_name} - Socket access required for real logs'
                }
            ]
            
            return Response({
                'container': container_name,
                'logs': fallback_logs,
                'total_lines': len(fallback_logs),
                'lines_requested': lines,
                'docker_logs_enabled': True,
                'docker_socket_accessible': False,
                'error_message': f'Docker socket access error: {str(docker_error)}'
            })
        except Exception as docker_error:
            logger.error(f"Docker API error for container {container_name}: {str(docker_error)}")
            return Response({'error': f'Docker error: {str(docker_error)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error getting Docker logs: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_system_health(request):
    """Get system health metrics"""
    try:
        now = timezone.now()
        last_24h = now - timedelta(days=1)
        
        # Calculate metrics
        total_logs_24h = SystemLog.objects.filter(timestamp__gte=last_24h).count()
        error_logs_24h = SystemLog.objects.filter(
            timestamp__gte=last_24h,
            level__in=['ERROR', 'CRITICAL']
        ).count()
        
        error_rate = (error_logs_24h / total_logs_24h * 100) if total_logs_24h > 0 else 0
        
        # Get active users (last hour)
        last_hour = now - timedelta(hours=1)
        active_users = SystemLog.objects.filter(
            timestamp__gte=last_hour,
            user__isnull=False
        ).values('user').distinct().count()
        
        # Calculate average response time from request logs (if available)
        avg_response_time = None  # Would need to implement request timing
        
        health_data = {
            'total_logs_24h': total_logs_24h,
            'error_rate': round(error_rate, 2),
            'active_users': active_users,
            'avg_response_time': avg_response_time,
            'timestamp': now.isoformat()
        }
        
        return Response(health_data)
        
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 