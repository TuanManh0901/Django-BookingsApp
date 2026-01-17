from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class NoMessagesAccountAdapter(DefaultAccountAdapter):
    """Custom adapter that suppresses allauth messages."""
    
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        """Override to prevent adding any messages."""
        pass  # Do nothing - suppress all messages


class NoMessagesSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter that suppresses allauth messages."""
    
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        """Override to prevent adding any messages."""
        pass  # Do nothing - suppress all messages
