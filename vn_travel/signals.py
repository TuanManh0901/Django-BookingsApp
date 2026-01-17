from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Tạo profile cho user mới"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Lưu profile khi user được lưu - tạo profile nếu chưa có"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Tạo profile cho user cũ nếu chưa có
        UserProfile.objects.get_or_create(user=instance)
