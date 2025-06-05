from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import requests
import os


class Command(BaseCommand):
    help = 'Make a user an admin (works with Supabase authentication)'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, nargs='?', help='Email address of the user to make admin')
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='List all current Django users and their admin status',
        )
        parser.add_argument(
            '--check-user',
            action='store_true',
            help='Check user status without making changes',
        )

    def handle(self, *args, **options):
        if options['list_users']:
            self.list_all_users()
            return
            
        email = options['email']
        
        if not email:
            raise CommandError("Email is required unless using --list-users")
        
        if options['check_user']:
            self.check_user_status(email)
            return
            
        self.make_user_admin(email)

    def list_all_users(self):
        """List all Django users and their admin status"""
        self.stdout.write(self.style.HTTP_INFO("=== Current Django Users ==="))
        
        users = User.objects.all().order_by('email')
        if not users:
            self.stdout.write(self.style.WARNING("No Django users found."))
            self.stdout.write("This is normal for Supabase authentication - users are created on first API access.")
            return
            
        for user in users:
            status = "ADMIN" if user.is_staff else "USER"
            style = self.style.SUCCESS if user.is_staff else self.style.WARNING
            self.stdout.write(style(f"  {user.email:<30} | {status} | Staff: {user.is_staff} | Super: {user.is_superuser}"))

    def check_user_status(self, email):
        """Check user status and provide instructions"""
        self.stdout.write(self.style.HTTP_INFO(f"=== Checking User: {email} ==="))
        
        try:
            user = User.objects.get(email=email)
            self.stdout.write(self.style.SUCCESS(f"✅ User exists in Django database"))
            self.stdout.write(f"  Username: {user.username}")
            self.stdout.write(f"  Email: {user.email}")
            self.stdout.write(f"  Staff: {user.is_staff}")
            self.stdout.write(f"  Superuser: {user.is_superuser}")
            self.stdout.write(f"  Last login: {user.last_login}")
            self.stdout.write(f"  Date joined: {user.date_joined}")
            
            if user.is_staff:
                self.stdout.write(self.style.SUCCESS("🎉 User has admin access in Django!"))
            else:
                self.stdout.write(self.style.WARNING("⚠️  User exists but is not admin"))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"❌ User does not exist in Django database"))
            self.stdout.write("This is normal for Supabase authentication - users are created on first API access.")
            
        # Always show Supabase instructions
        self.show_supabase_instructions(email)

    def make_user_admin(self, email):
        """Make user admin in Django and show Supabase instructions"""
        self.stdout.write(self.style.HTTP_INFO(f"=== Making {email} an Admin ==="))
        
        try:
            user = User.objects.get(email=email)
            
            # Make the user staff and superuser
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Successfully made {email} an admin in Django'))
            
            # Show user details
            self.stdout.write(f'Updated Django user details:')
            self.stdout.write(f'  Username: {user.username}')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Staff: {user.is_staff}')
            self.stdout.write(f'  Superuser: {user.is_superuser}')
            
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'❌ User with email "{email}" does not exist in Django yet.'))
            self.stdout.write("This is normal for Supabase authentication - Django users are created on first API access.")
            
        # Always show Supabase instructions since that's the real source of truth
        self.show_supabase_instructions(email)

    def show_supabase_instructions(self, email):
        """Show instructions for setting admin status in Supabase"""
        self.stdout.write(self.style.HTTP_INFO("\n" + "="*60))
        self.stdout.write(self.style.HTTP_INFO("🔧 IMPORTANT: Set Admin Status in Supabase"))
        self.stdout.write(self.style.HTTP_INFO("="*60))
        
        self.stdout.write(self.style.WARNING("\n⚠️  Django admin status is secondary to Supabase user metadata!"))
        self.stdout.write("The real admin permissions come from JWT tokens with user_metadata.")
        
        self.stdout.write(self.style.HTTP_INFO(f"\n📋 Steps to make {email} admin:"))
        self.stdout.write("1. 🌐 Go to your Supabase Dashboard: https://supabase.com/dashboard")
        self.stdout.write("2. 📁 Select your Risk Radar project")
        self.stdout.write("3. 👥 Go to Authentication > Users")
        self.stdout.write(f"4. 🔍 Find user: {email}")
        self.stdout.write("5. ✏️  Click the user to edit")
        self.stdout.write("6. 📝 In 'User Metadata' section, add this JSON:")
        self.stdout.write(self.style.SUCCESS('   {'))
        self.stdout.write(self.style.SUCCESS('     "is_staff": true,'))
        self.stdout.write(self.style.SUCCESS('     "is_superuser": false'))
        self.stdout.write(self.style.SUCCESS('   }'))
        self.stdout.write("7. 💾 Click 'Update User'")
        self.stdout.write("8. 🔄 Log out and log back in to get new JWT token")
        
        self.stdout.write(self.style.HTTP_INFO("\n🧪 Test admin access:"))
        self.stdout.write("   python manage.py make_admin --check-user " + email)
        
        self.stdout.write(self.style.WARNING(f"\n💡 Why both Django AND Supabase?"))
        self.stdout.write("   - Supabase user_metadata determines real admin access")
        self.stdout.write("   - Django admin flags are synced from JWT tokens on each request")
        self.stdout.write("   - Setting both ensures consistency") 