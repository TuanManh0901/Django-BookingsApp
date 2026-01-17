# Override Django User's get_full_name() to Vietnamese format (Last First)
from django.contrib.auth.models import User

# Save original method
_original_get_full_name = User.get_full_name

def vietnamese_get_full_name(self):
    """
    Return the last_name plus the first_name, with a space in between.
    This is Vietnamese format: Họ + Tên (e.g., Nguyễn Văn A)
    """
    if self.last_name and self.first_name:
        return f"{self.last_name} {self.first_name}".strip()
    elif self.last_name:
        return self.last_name
    elif self.first_name:
        return self.first_name
    return ""

# Monkey patch the User model
User.get_full_name = vietnamese_get_full_name
