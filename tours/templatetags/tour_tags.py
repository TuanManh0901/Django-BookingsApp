from django import template
from django.templatetags.static import static
from django.conf import settings
import os

register = template.Library()

@register.simple_tag
def tour_image_url(tour_image):
    """
    Generate correct URL for tour images in both dev and production
    
    In development: Uses MEDIA_URL (/media/)
    In production: Uses static files (/static/media/)
    """
    if not tour_image or not tour_image.image:
        return static('images/placeholder_tour.jpg')
    
    # Get the image path (tours/filename.jpg)
    image_path = str(tour_image.image.name)
    
    # CRITICAL: Check if in production
    # settings.DEBUG could be True/False (boolean) or "True"/"False" (string from env)
    is_production = not settings.DEBUG  # Works for boolean
    
    # Additional check: if RENDER environment variable exists, we're on Render (production)
    if os.environ.get('RENDER'):
        is_production = True
    
    if is_production:
        # Production: use static tag
        # Path: static/media/tours/filename.jpg → /static/media/tours/filename.jpg
        return static(f'media/{image_path}')
    else:
        # Development: use MEDIA_URL
        return settings.MEDIA_URL + image_path

