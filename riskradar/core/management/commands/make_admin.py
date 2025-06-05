from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Make a user an admin (staff + superuser)'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address of the user to make admin')

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Make the user staff and superuser
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully made {email} an admin user')
            )
            
            # Show user details
            self.stdout.write(f'User details:')
            self.stdout.write(f'  Username: {user.username}')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Staff: {user.is_staff}')
            self.stdout.write(f'  Superuser: {user.is_superuser}')
            
        except User.DoesNotExist:
            raise CommandError(f'User with email "{email}" does not exist.') 