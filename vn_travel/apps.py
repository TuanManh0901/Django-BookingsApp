from django.apps import AppConfig


class VnTravelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vn_travel'
    verbose_name = 'VN Travel'

    def ready(self):
        """
        Import user_patch when Django is fully ready.
        This is the correct place to override User.get_full_name()
        """
        # Import here to avoid AppRegistryNotReady error
        from . import user_patch  # noqa
