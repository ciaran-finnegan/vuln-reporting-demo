from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # API v1 endpoints
    path('api/v1/upload/nessus', views.upload_nessus_file, name='upload_nessus'),
    path('api/v1/upload/history', views.upload_history, name='upload_history'),
    path('api/v1/status', views.api_status, name='api_status'),
    path('api/v1/upload/info', views.upload_info, name='upload_info'),
    
    # Authentication endpoints
    path('api/v1/auth/status', views.auth_status, name='auth_status'),
    path('api/v1/auth/profile', views.auth_profile, name='auth_profile'),
] 