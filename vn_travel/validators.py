"""
Custom password validators with Vietnamese messages
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class MinimumLengthValidator:
    """
    Validate whether the password is of a minimum length (tiếng Việt)
    """
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                f"Mật khẩu này quá ngắn. Nó phải chứa ít nhất {self.min_length} ký tự.",
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return f"Mật khẩu của bạn phải chứa ít nhất {self.min_length} ký tự."


class UserAttributeSimilarityValidator:
    """
    Validate that password is not too similar to user attributes (tiếng Việt)
    """
    def __init__(self, user_attributes=("username", "email", "first_name", "last_name"), max_similarity=0.7):
        self.user_attributes = user_attributes
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return

        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or len(value) < 3:
                continue
            value_lower = value.lower()
            password_lower = password.lower()
            if value_lower in password_lower or password_lower in value_lower:
                raise ValidationError(
                    "Mật khẩu quá giống với thông tin cá nhân của bạn.",
                    code='password_too_similar',
                )

    def get_help_text(self):
        return "Mật khẩu của bạn không được quá giống với thông tin cá nhân."


class CommonPasswordValidator:
    """
    Validate that password is not a common password (tiếng Việt)
    """
    def validate(self, password, user=None):
        # Simple check - in production you'd use a proper common password list
        common_passwords = ['password', '12345678', 'qwerty', 'abc123', 'password123']
        if password.lower() in common_passwords:
            raise ValidationError(
                "Mật khẩu này quá phổ biến.",
                code='password_too_common',
            )

    def get_help_text(self):
        return "Mật khẩu của bạn không được là mật khẩu phổ biến."


class NumericPasswordValidator:
    """
    Validate that password is not entirely numeric (tiếng Việt)
    """
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                "Mật khẩu này hoàn toàn là số.",
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return "Mật khẩu của bạn không được hoàn toàn là số."
