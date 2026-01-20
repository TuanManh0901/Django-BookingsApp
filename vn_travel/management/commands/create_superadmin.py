from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Setup admin permissions - manh0 only'

    def handle(self, *args, **options):
        # 1. Give admin rights to manh0
        try:
            manh0_user = User.objects.get(username='manh0')
            manh0_user.is_staff = True
            manh0_user.is_superuser = True
            manh0_user.save()
            self.stdout.write(self.style.SUCCESS('✅ manh0 is now admin'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ manh0 user not found!'))
            return
        
        # 2. Delete 'admin' user(s)
        admin_deleted = User.objects.filter(username__iexact='admin').delete()[0]
        if admin_deleted > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ Deleted {admin_deleted} "admin" user(s)'))
        
        # 3. Delete 'superadmin' user(s)
        superadmin_deleted = User.objects.filter(username__iexact='superadmin').delete()[0]
        if superadmin_deleted > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ Deleted {superadmin_deleted} "superadmin" user(s)'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ DONE! Only manh0 has admin rights now.'))



