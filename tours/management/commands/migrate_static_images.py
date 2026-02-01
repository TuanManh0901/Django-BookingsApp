from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from tours.models import Tour, TourImage
from django.contrib.staticfiles import finders
import os

class Command(BaseCommand):
    help = 'Migrates static fallback images to actual TourImage database records'

    def handle(self, *args, **options):
        tours = Tour.objects.all()
        created_count = 0
        
        self.stdout.write(f"Found {tours.count()} tours. Checking for missing images...")
        
        for tour in tours:
            # Check if tour already has images
            if tour.images.exists():
                self.stdout.write(f"Skipping {tour.name[:30]}... (already has images)")
                continue
                
            # Get fallback image path (e.g., 'images/ha_long_bay.png')
            # remove 'static/' prefix if present in return value (though model returns raw path)
            fallback_path = tour.get_fallback_image()
            
            # Find absolute path of the static file
            absolute_path = finders.find(fallback_path)
            
            if not absolute_path:
                # Try explicit path in static folder
                possible_path = os.path.join(settings.BASE_DIR, 'static', fallback_path)
                if os.path.exists(possible_path):
                    absolute_path = possible_path
            
            if absolute_path and os.path.exists(absolute_path):
                try:
                    # Read binary content
                    with open(absolute_path, 'rb') as f:
                        image_content = f.read()
                        
                    # Create unique filename
                    from django.utils.text import slugify
                    filename = f"migrated_{slugify(tour.name)}_{os.path.basename(absolute_path)}"
                    
                    # Create TourImage
                    tour_image = TourImage(
                        tour=tour,
                        alt_text=f"Ảnh {tour.name} (Tự động cập nhật)"
                    )
                    # Save image file
                    tour_image.image.save(filename, ContentFile(image_content), save=True)
                    
                    self.stdout.write(self.style.SUCCESS(f"✅ Created image for: {tour.name}"))
                    created_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error migrating {tour.name}: {e}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Could not find static file: {fallback_path}"))
                
        self.stdout.write(self.style.SUCCESS(f"\nMigration complete! Created {created_count} new TourImage records."))
