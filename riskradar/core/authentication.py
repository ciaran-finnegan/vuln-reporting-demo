import jwt
import logging
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)

class SupabaseJWTAuthentication(BaseAuthentication):
    """
    Custom authentication backend for validating Supabase JWT tokens.
    
    This allows Django to authenticate users via Supabase Auth tokens
    sent from the lovable.dev frontend.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using Supabase JWT token.
        
        Returns:
            (user, token) tuple if authentication successful, None otherwise
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        
        try:
            # Validate and decode the JWT token
            user_data = self.validate_supabase_token(token)
            
            # Get or create Django user
            user = self.get_or_create_user(user_data)
            
            return (user, token)
            
        except Exception as e:
            logger.warning(f"Supabase JWT authentication failed: {str(e)}")
            raise AuthenticationFailed('Invalid authentication credentials.')
    
    def validate_supabase_token(self, token):
        """
        Validate JWT token against Supabase.
        
        Args:
            token: JWT token string
            
        Returns:
            dict: User data from token
        """
        try:
            # Decode JWT using Supabase secret from environment
            if not hasattr(settings, 'SUPABASE_JWT_SECRET') or not settings.SUPABASE_JWT_SECRET:
                raise AuthenticationFailed('Supabase JWT secret not configured.')
                
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=['HS256'],
                audience='authenticated'
            )
            
            # Validate token claims
            if payload.get('aud') != 'authenticated':
                raise AuthenticationFailed('Invalid token audience.')
                
            # Check if token is expired
            import time
            if payload.get('exp', 0) < time.time():
                raise AuthenticationFailed('Token has expired.')
                
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')
    
    def get_or_create_user(self, user_data):
        """
        Get or create Django user from Supabase user data.
        
        Args:
            user_data: Decoded JWT payload
            
        Returns:
            User: Django user instance
        """
        email = user_data.get('email')
        user_id = user_data.get('sub')  # Supabase user ID
        
        if not email or not user_id:
            raise AuthenticationFailed('Token missing required user information.')
        
        # Try to find existing user by email
        try:
            user = User.objects.get(email=email)
            # Update user data if needed
            if not user.username or user.username != email:
                user.username = email
                user.save()
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=user_data.get('user_metadata', {}).get('first_name', ''),
                last_name=user_data.get('user_metadata', {}).get('last_name', ''),
            )
            
            # Create user profile
            from .models import UserProfile, BusinessGroup
            try:
                # Try to get default business group
                default_group = BusinessGroup.objects.filter(name='Default').first()
                UserProfile.objects.create(
                    user=user,
                    supabase_user_id=user_id,
                    business_group=default_group
                )
            except Exception as e:
                logger.warning(f"Could not create user profile: {e}")
        
        return user


class OptionalSupabaseJWTAuthentication(SupabaseJWTAuthentication):
    """
    Optional authentication that doesn't fail if no token is provided.
    Used for endpoints that work with or without authentication.
    """
    
    def authenticate(self, request):
        """
        Same as parent but returns None instead of failing when no auth header.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        # If auth header exists, validate it
        return super().authenticate(request)
