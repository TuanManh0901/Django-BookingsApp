"""Models cho AI Chatbot VN Travel."""
from django.contrib.auth.models import User
from django.db import models


class ChatMessage(models.Model):
    """Model tin nhắn chat - lưu trữ cuộc hội thoại với AI chatbot."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(
        max_length=100, 
        help_text="Session ID for anonymous users"
    )
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_ai_response = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self) -> str:
        return f"ChatMessage by {self.user or self.session_id} at {self.timestamp}"
