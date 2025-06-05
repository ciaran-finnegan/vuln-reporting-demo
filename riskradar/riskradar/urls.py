"""
URL configuration for riskradar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.log_views import (
    get_logs, get_log_analytics_error_rate, get_log_analytics_by_source,
    get_log_analytics_by_level, get_log_analytics_top_errors, get_docker_logs, get_system_health
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Include core app URLs for API endpoints
    
    # Log Management API Endpoints
    path('api/v1/logs/', get_logs, name='get_logs'),
    path('api/v1/logs/analytics/error-rate/', get_log_analytics_error_rate, name='log_analytics_error_rate'),
    path('api/v1/logs/analytics/by-source/', get_log_analytics_by_source, name='log_analytics_by_source'),
    path('api/v1/logs/analytics/by-level/', get_log_analytics_by_level, name='log_analytics_by_level'),
    path('api/v1/logs/analytics/top-errors/', get_log_analytics_top_errors, name='log_analytics_top_errors'),
    path('api/v1/logs/docker/<str:container_name>/', get_docker_logs, name='docker_logs'),
    path('api/v1/logs/health/', get_system_health, name='system_health'),
]
