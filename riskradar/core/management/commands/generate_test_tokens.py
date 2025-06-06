import jwt
import time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):
    help = 'Generate JWT tokens for test users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Generate token for specific user email',
        )

    def handle(self, *args, **options):
        # Get JWT secret from settings
        jwt_secret = getattr(settings, 'SUPABASE_JWT_SECRET', None)
        if not jwt_secret:
            self.stdout.write(
                self.style.ERROR('❌ SUPABASE_JWT_SECRET not found in settings')
            )
            return

        test_users = [
            'admin@riskradar.com',
            'user@riskradar.com'
        ]

        # Filter to specific user if requested
        if options['user']:
            if options['user'] in test_users:
                test_users = [options['user']]
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ User {options["user"]} not found in test users')
                )
                return

        self.stdout.write('🔑 Generating JWT tokens for test users...')
        self.stdout.write('')

        for email in test_users:
            try:
                user = User.objects.get(email=email)
                
                # Create JWT payload matching Supabase format
                now = int(time.time())
                exp = now + 3600  # 1 hour expiry
                
                payload = {
                    'aud': 'authenticated',
                    'exp': exp,
                    'sub': f'test-user-{user.id}',
                    'email': user.email,
                    'role': 'authenticated',
                    'iat': now,
                    'user_metadata': {
                        'email_verified': True,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                    }
                }

                # Generate token
                token = jwt.encode(payload, jwt_secret, algorithm='HS256')

                # Display user info and token
                role = 'Admin' if user.is_staff else 'Regular User'
                self.stdout.write(f'👤 {user.email} ({role})')
                self.stdout.write(f'   Token: {token}')
                self.stdout.write('')

            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  User {email} not found - run create_test_users first')
                )

        self.stdout.write(self.style.SUCCESS('🎉 JWT tokens generated!'))
        self.stdout.write('')
        self.stdout.write('📋 Usage:')
        self.stdout.write('   Copy the token and use it in API calls:')
        self.stdout.write('   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/auth/profile')
        self.stdout.write('')
        self.stdout.write('💡 Tokens expire in 1 hour. Re-run this command to generate fresh tokens.') 