from django.core.management.base import BaseCommand
from tours.models import TourImage

class Command(BaseCommand):
    help = 'Fix TourImage paths by removing /media/ prefix'

    def handle(self, *args, **kwargs):
        """
        Fix image paths in database
        Convert: /media/tours/filename.jpg → tours/filename.jpg
        """
        images = TourImage.objects.all()
        fixed_count = 0
        
        for img in images:
            old_path = str(img.image)
            
            # If path starts with '/media/', remove it
            if old_path.startswith('/media/'):
                new_path = old_path.replace('/media/', '', 1)
                img.image.name = new_path
                img.save(update_fields=['image'])
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Fixed: {old_path} → {new_path}')
                )
            # If path starts with 'media/', remove it
            elif old_path.startswith('media/'):
                new_path = old_path.replace('media/', '', 1)
                img.image.name = new_path
                img.save(update_fields=['image'])
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Fixed: {old_path} → {new_path}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Already OK: {old_path}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Fixed {fixed_count} image paths!')
        )
