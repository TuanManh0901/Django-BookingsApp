from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a superuser for production if not exists'

    def handle(self, *args, **options):
        username = 'superadmin'
        email = 'admin@vntravel.com'
        password = 'VNTravel@2026'
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            # Update to superuser if not already
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated existing user: {username}'))
        else:
            # Create new superuser
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {username}'))
        
        self.stdout.write(self.style.SUCCESS(f'Login: {username} / {password}'))
        
        # Remove admin rights from manh0
        try:
            manh0_user = User.objects.get(username='manh0')
            manh0_user.is_staff = False
            manh0_user.is_superuser = False
            manh0_user.save()
            self.stdout.write(self.style.SUCCESS('Removed admin rights from manh0'))
        except User.DoesNotExist:
            self.stdout.write('manh0 user not found, skipping')

