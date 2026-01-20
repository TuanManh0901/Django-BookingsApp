from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class NoMessagesAccountAdapter(DefaultAccountAdapter):
    """Custom adapter that suppresses allauth messages."""
    
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        """Override to prevent adding any messages."""
        pass  # Do nothing - suppress all messages


class NoMessagesSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter that suppresses allauth messages and auto-generates username."""
    
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        """Override to prevent adding any messages."""
        pass  # Do nothing - suppress all messages
    
    def populate_username(self, request, user):
        """
        Auto-generate username from Google email to skip signup form.
        Example: longviet@gmail.com → longviet
        """
        from allauth.account.utils import user_email, user_field, user_username
        
        # Get email from Google account
        email = user_email(user)
        if email:
            # Extract username from email (before @)
            base_username = email.split('@')[0]
            # Clean username (remove special chars, keep only alphanumeric and underscore)
            base_username = ''.join(c if c.isalnum() or c == '_' else '_' for c in base_username)
            
            # Ensure unique username
            username = base_username
            counter = 1
            while user_username(user, username):
                username = f"{base_username}{counter}"
                counter += 1
            
            user_username(user, username)
        else:
            # Fallback to default behavior if no email
            super().populate_username(request, user)

