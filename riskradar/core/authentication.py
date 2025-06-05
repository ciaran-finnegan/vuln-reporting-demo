import jwt
import logging
import os
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
        
        if not auth_header:
            logger.debug("No Authorization header found")
            return None
            
        if not auth_header.startswith('Bearer '):
            logger.debug(f"Authorization header doesn't start with 'Bearer ': {auth_header[:20]}...")
            return None
            
        token = auth_header.split(' ')[1]
        logger.debug(f"Extracted token: {token[:50]}...{token[-10:]}")
        
        try:
            # Validate and decode the JWT token
            user_data = self.validate_supabase_token(token)
            logger.info(f"Successfully validated token for user: {user_data.get('email')}")
            
            # Get or create Django user
            user = self.get_or_create_user(user_data)
            logger.info(f"Successfully authenticated user: {user.email}")
            
            return (user, token)
            
        except AuthenticationFailed:
            # Re-raise AuthenticationFailed without wrapping
            raise
        except Exception as e:
            logger.error(f"Unexpected error in JWT authentication: {str(e)}", exc_info=True)
            raise AuthenticationFailed('Authentication failed due to server error.')
    
    def validate_supabase_token(self, token):
        """
        Validate JWT token against Supabase.
        
        Args:
            token: JWT token string
            
        Returns:
            dict: User data from token
        """
        try:
            # Check if Supabase JWT secret is configured
            jwt_secret = getattr(settings, 'SUPABASE_JWT_SECRET', None)
            if not jwt_secret:
                logger.error("SUPABASE_JWT_SECRET not found in settings")
                raise AuthenticationFailed('Supabase JWT secret not configured.')
            
            logger.debug(f"Using JWT secret: {jwt_secret[:10]}...{jwt_secret[-5:]}")
            
            # Decode without verification first to inspect the token
            try:
                unverified_payload = jwt.decode(token, options={"verify_signature": False})
                logger.debug(f"Token payload (unverified): {unverified_payload}")
            except Exception as e:
                logger.error(f"Failed to decode token without verification: {e}")
                raise AuthenticationFailed('Malformed JWT token.')
            
            # Now decode with verification
            try:
                payload = jwt.decode(
                    token,
                    jwt_secret,
                    algorithms=['HS256'],
                    audience='authenticated'
                )
                logger.debug(f"Successfully decoded token with verification: {payload}")
            except jwt.ExpiredSignatureError:
                logger.warning("Token has expired")
                raise AuthenticationFailed('Token has expired.')
            except jwt.InvalidAudienceError:
                logger.warning(f"Invalid audience. Expected 'authenticated', got: {unverified_payload.get('aud')}")
                raise AuthenticationFailed('Invalid token audience.')
            except jwt.InvalidSignatureError:
                logger.error("Invalid JWT signature - check SUPABASE_JWT_SECRET")
                raise AuthenticationFailed('Invalid token signature.')
            except jwt.InvalidTokenError as e:
                logger.error(f"Invalid token error: {str(e)}")
                raise AuthenticationFailed(f'Invalid token: {str(e)}')
            
            # Validate token claims
            if payload.get('aud') != 'authenticated':
                logger.warning(f"Invalid audience: {payload.get('aud')}")
                raise AuthenticationFailed('Invalid token audience.')
                
            # Check if token is expired (double-check)
            import time
            if payload.get('exp', 0) < time.time():
                logger.warning("Token has expired (time check)")
                raise AuthenticationFailed('Token has expired.')
                
            return payload
            
        except AuthenticationFailed:
            # Re-raise AuthenticationFailed without wrapping
            raise
        except Exception as e:
            logger.error(f"Unexpected error validating token: {str(e)}", exc_info=True)
            raise AuthenticationFailed(f'Token validation failed: {str(e)}')
    
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
            logger.error(f"Token missing required user information. Email: {email}, User ID: {user_id}")
            raise AuthenticationFailed('Token missing required user information.')
        
        logger.debug(f"Looking for user with email: {email}")
        
        # Try to find existing user by email
        try:
            user = User.objects.get(email=email)
            logger.debug(f"Found existing user: {user.username}")
            # Update user data if needed
            if not user.username or user.username != email:
                user.username = email
                user.save()
                logger.debug(f"Updated username for user: {email}")
        except User.DoesNotExist:
            logger.info(f"Creating new user for email: {email}")
            # Create new user
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=user_data.get('user_metadata', {}).get('first_name', ''),
                last_name=user_data.get('user_metadata', {}).get('last_name', ''),
            )
            logger.info(f"Created new user: {user.username}")
            
            # Create user profile
            try:
                from .models import UserProfile, BusinessGroup
                # Try to get default business group
                default_group = BusinessGroup.objects.filter(name='Default').first()
                if not default_group:
                    logger.warning("No 'Default' business group found")
                    
                UserProfile.objects.create(
                    user=user,
                    supabase_user_id=user_id,
                    business_group=default_group
                )
                logger.info(f"Created user profile for: {user.username}")
            except Exception as e:
                logger.warning(f"Could not create user profile for {email}: {e}")
        
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
            logger.debug("Optional auth: No valid Authorization header, returning None")
            return None
            
        # If auth header exists, validate it
        logger.debug("Optional auth: Authorization header found, validating token")
        return super().authenticate(request)
