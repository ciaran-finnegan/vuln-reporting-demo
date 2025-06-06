import os
import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Create test users in Supabase Auth for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing test users before creating new ones',
        )

    def handle(self, *args, **options):
        # Load .env file to ensure environment variables are available
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            self.stdout.write(
                self.style.WARNING('Note: python-dotenv not installed. Ensure environment variables are set manually.')
            )
        
        # Check if we have the required Supabase configuration
        service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        supabase_url = settings.SUPABASE_URL
        
        if not service_role_key:
            self.stdout.write(
                self.style.ERROR(
                    '❌ SUPABASE_SERVICE_ROLE_KEY environment variable is required.\n'
                    'Get it from your Supabase dashboard: Settings > API > service_role key'
                )
            )
            return

        if not supabase_url:
            self.stdout.write(
                self.style.ERROR('❌ SUPABASE_URL is not configured in settings')
            )
            return

        test_users = [
            {
                'email': 'admin@riskradar.com',
                'password': 'admin123!',  # More secure password
                'user_metadata': {
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'is_staff': True,
                    'is_superuser': True,
                },
                'email_confirm': True,  # Skip email confirmation
            },
            {
                'email': 'user@riskradar.com',
                'password': 'notadmin123!',  # More secure password
                'user_metadata': {
                    'first_name': 'Regular',
                    'last_name': 'User',
                    'is_staff': False,
                    'is_superuser': False,
                },
                'email_confirm': True,  # Skip email confirmation
            }
        ]

        headers = {
            'Authorization': f'Bearer {service_role_key}',
            'Content-Type': 'application/json',
            'apikey': service_role_key,
        }

        if options['reset']:
            self.stdout.write('🗑️  Removing existing test users...')
            self._delete_test_users(supabase_url, headers, test_users)

        self.stdout.write('👥 Creating test users in Supabase Auth...')
        
        for user_data in test_users:
            email = user_data['email']
            
            # Check if user already exists
            if self._user_exists(supabase_url, headers, email):
                self.stdout.write(
                    self.style.WARNING(f'   User {email} already exists - skipping')
                )
                continue

            # Create user in Supabase Auth
            success = self._create_supabase_user(supabase_url, headers, user_data)
            
            if success:
                role = 'Admin' if user_data['user_metadata']['is_staff'] else 'Regular User'
                self.stdout.write(
                    self.style.SUCCESS(f'   ✅ Created: {email} ({role})')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Failed to create: {email}')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Supabase test users created successfully!'))
        self.stdout.write('')
        self.stdout.write('📋 Login Details:')
        self.stdout.write('   Admin User:')
        self.stdout.write('     Email: admin@riskradar.com')
        self.stdout.write('     Password: admin123!')
        self.stdout.write('     Permissions: Staff, Superuser')
        self.stdout.write('')
        self.stdout.write('   Regular User:')
        self.stdout.write('     Email: user@riskradar.com')
        self.stdout.write('     Password: notadmin123!')
        self.stdout.write('     Permissions: Standard user')
        self.stdout.write('')
        self.stdout.write('🔐 These users can now:')
        self.stdout.write('   - Log into the frontend application')
        self.stdout.write('   - Generate JWT tokens for API testing')
        self.stdout.write('   - Access Django admin (auto-created on first API request)')

    def _user_exists(self, supabase_url, headers, email):
        """Check if a user already exists in Supabase Auth"""
        try:
            url = f'{supabase_url}/auth/v1/admin/users'
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                
                # Check if any user has this email
                for user in users:
                    if user.get('email') == email:
                        return True
                return False
            else:
                self.stdout.write(f'   Warning: Could not check users: {response.status_code} - {response.text[:100]}')
                return False
        except Exception as e:
            self.stdout.write(f'   Warning: Could not check if user exists: {e}')
            return False

    def _create_supabase_user(self, supabase_url, headers, user_data):
        """Create a user in Supabase Auth"""
        try:
            url = f'{supabase_url}/auth/v1/admin/users'
            response = requests.post(url, headers=headers, json=user_data)
            
            if response.status_code in [200, 201]:
                return True
            else:
                error_msg = response.text[:200] if response.text else 'No error message'
                self.stdout.write(f'   Error creating user {user_data["email"]}: {response.status_code} - {error_msg}')
                return False
        except Exception as e:
            self.stdout.write(f'   Exception creating user {user_data["email"]}: {e}')
            return False

    def _delete_test_users(self, supabase_url, headers, test_users):
        """Delete existing test users from Supabase Auth"""
        for user_data in test_users:
            email = user_data['email']
            try:
                # First, find the user ID
                list_url = f'{supabase_url}/auth/v1/admin/users'
                response = requests.get(list_url, headers=headers, params={'email': email})
                
                if response.status_code == 200:
                    users = response.json().get('users', [])
                    for user in users:
                        if user.get('email') == email:
                            # Delete the user
                            user_id = user['id']
                            delete_url = f'{supabase_url}/auth/v1/admin/users/{user_id}'
                            delete_response = requests.delete(delete_url, headers=headers)
                            
                            if delete_response.status_code == 200:
                                self.stdout.write(f'   Deleted: {email}')
                            else:
                                self.stdout.write(f'   Failed to delete: {email}')
                            break
            except Exception as e:
                self.stdout.write(f'   Warning: Could not delete {email}: {e}') 