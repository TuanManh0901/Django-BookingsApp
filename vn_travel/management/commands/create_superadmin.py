from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a superuser for production and manage admin permissions'

    def handle(self, *args, **options):
        # 1. Give admin rights to manh0
        try:
            manh0_user = User.objects.get(username='manh0')
            manh0_user.is_staff = True
            manh0_user.is_superuser = True
            manh0_user.save()
            self.stdout.write(self.style.SUCCESS('✅ Gave admin rights to manh0'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('manh0 user not found'))
        
        # 2. Delete all users named 'admin' or 'Admin' (case-insensitive)
        deleted_count = User.objects.filter(username__iexact='admin').delete()[0]
        if deleted_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ Deleted {deleted_count} admin user(s)'))
        else:
            self.stdout.write('No admin users found to delete')
        
        # 3. Create/update superadmin as backup
        username = 'superadmin'
        email = 'admin@vntravel.com'
        password = 'VNTravel@2026'
        
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Updated superadmin'))
        else:
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'✅ Created superadmin'))
        
        self.stdout.write(self.style.SUCCESS(f'\n📋 Admin accounts:'))
        self.stdout.write(f'   - manh0 (your main admin)')
        self.stdout.write(f'   - superadmin / VNTravel@2026 (backup)')


