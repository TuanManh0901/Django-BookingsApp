from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    cccd = models.CharField(max_length=20, blank=True, null=True, verbose_name="CCCD/CMND")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Ngày sinh")
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name="Giới tính"
    )
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"

    def __str__(self):
        return f"Profile of {self.user.username}"
