"""Models cho Telegram Bot VN Travel."""
from django.conf import settings
from django.db import models


class TelegramUser(models.Model):
    """Model người dùng Telegram - tích hợp bot."""
    
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Username"
    )
    first_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Tên"
    )
    last_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Họ"
    )
    django_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="telegram_accounts",
        verbose_name="User liên kết",
    )
    conversation_state = models.CharField(
        max_length=50, 
        blank=True, 
        default="", 
        verbose_name="Trạng thái hội thoại"
    )
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"
        ordering = ['-created_at']

    def __str__(self) -> str:
        if self.username:
            return f"@{self.username} ({self.telegram_id})"
        return f"{self.first_name or ''} {self.last_name or ''} ({self.telegram_id})"


class Conversation(models.Model):
    """Model lịch sử hội thoại Telegram."""
    
    MESSAGE_TYPES = (
        ("user", "User"),
        ("bot", "Bot"),
        ("system", "System"),
    )

    telegram_user = models.ForeignKey(
        TelegramUser, 
        on_delete=models.CASCADE, 
        related_name="conversations"
    )
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    message_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.message_type}: {self.message_text[:40]}"
