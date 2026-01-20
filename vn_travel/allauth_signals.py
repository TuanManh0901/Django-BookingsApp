from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User


class NoMessagesAccountAdapter(DefaultAccountAdapter):
    """Custom adapter that suppresses allauth messages."""
    
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        """Override to prevent adding any messages."""
        pass  # Do nothing - suppress all messages


class NoMessagesSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for seamless Google login (no signup form)."""
    
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        """Override to prevent adding any messages."""
        pass  # Do nothing - suppress all messages
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        CRITICAL: Return True to enable auto-signup without form.
        This ensures user is created automatically without showing signup page.
        """
        return True
    
    def populate_user(self, request, sociallogin, data):
        """
        Auto-populate user data from Google account.
        Creates username automatically from email.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Get email from Google
        email = data.get('email', '')
        
        # Auto-generate username from email
        if email and not user.username:
            base_username = email.split('@')[0]
            # Clean special characters
            base_username = ''.join(c if c.isalnum() or c == '_' else '_' for c in base_username)
            
            # Ensure unique username
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user.username = username
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save user without requiring form submission.
        This is called during auto-signup.
        """
        user = sociallogin.user
        user.set_unusable_password()
        
        # Ensure username exists
        if not user.username and user.email:
            base_username = user.email.split('@')[0]
            base_username = ''.join(c if c.isalnum() or c == '_' else '_' for c in base_username)
            
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user.username = username
        
        user.save()
        return user

