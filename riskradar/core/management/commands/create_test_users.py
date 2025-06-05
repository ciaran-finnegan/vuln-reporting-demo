from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Create test users for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing test users before creating new ones',
        )

    def handle(self, *args, **options):
        test_users = [
            {
                'username': 'admin@riskradar.com',
                'email': 'admin@riskradar.com',
                'password': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'user@riskradar.com',
                'email': 'user@riskradar.com',
                'password': 'notadmin',
                'first_name': 'Regular',
                'last_name': 'User',
                'is_staff': False,
                'is_superuser': False,
            }
        ]

        if options['reset']:
            self.stdout.write('🗑️  Removing existing test users...')
            for user_data in test_users:
                try:
                    user = User.objects.get(username=user_data['username'])
                    user.delete()
                    self.stdout.write(f'   Deleted: {user_data["username"]}')
                except User.DoesNotExist:
                    pass

        self.stdout.write('👥 Creating test users...')
        
        for user_data in test_users:
            username = user_data['username']
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'   User {username} already exists - skipping')
                )
                continue

            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_staff=user_data['is_staff'],
                is_superuser=user_data['is_superuser'],
            )

            # Create or update user profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'supabase_user_id': f'test-user-{user.id}',
                    'business_group': None,
                }
            )

            # Success message with role
            role = 'Admin' if user.is_staff else 'Regular User'
            self.stdout.write(
                self.style.SUCCESS(f'   ✅ Created: {username} ({role})')
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Test users created successfully!'))
        self.stdout.write('')
        self.stdout.write('📋 Login Details:')
        self.stdout.write('   Admin User:')
        self.stdout.write('     Email: admin@riskradar.com')
        self.stdout.write('     Password: admin')
        self.stdout.write('     Permissions: Staff, Superuser')
        self.stdout.write('')
        self.stdout.write('   Regular User:')
        self.stdout.write('     Email: user@riskradar.com')
        self.stdout.write('     Password: notadmin')
        self.stdout.write('     Permissions: Standard user')
        self.stdout.write('')
        self.stdout.write('🔐 You can now log into Django admin at /admin/ with these credentials') 