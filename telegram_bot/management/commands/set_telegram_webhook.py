"""
Management command to set Telegram webhook
Usage:
    python manage.py set_telegram_webhook --url https://yourdomain.com/telegram/webhook/
    python manage.py set_telegram_webhook --delete  # Delete webhook and use polling
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set or delete Telegram webhook'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='Webhook URL (must be HTTPS)',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete webhook (switch to polling mode)',
        )
        parser.add_argument(
            '--info',
            action='store_true',
            help='Show current webhook info',
        )

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        
        if not token:
            self.stdout.write(self.style.ERROR('TELEGRAM_BOT_TOKEN not configured'))
            return

        bot = Bot(token=token)

        # Show webhook info
        if options['info']:
            self.show_webhook_info(bot)
            return

        # Delete webhook
        if options['delete']:
            self.delete_webhook(bot)
            return

        # Set webhook
        webhook_url = options.get('url')
        if not webhook_url:
            # Try to get from settings
            webhook_url = getattr(settings, 'TELEGRAM_WEBHOOK_URL', None)
        
        if not webhook_url:
            self.stdout.write(
                self.style.ERROR(
                    'Please provide webhook URL:\n'
                    '  python manage.py set_telegram_webhook --url https://yourdomain.com/telegram/webhook/\n'
                    'Or set TELEGRAM_WEBHOOK_URL in settings.py'
                )
            )
            return

        self.set_webhook(bot, webhook_url)

    def show_webhook_info(self, bot):
        """Show current webhook configuration"""
        try:
            info = bot.get_webhook_info()
            
            self.stdout.write(self.style.SUCCESS('Webhook Info:'))
            self.stdout.write(f'  URL: {info.url or "(not set)"}')
            self.stdout.write(f'  Pending updates: {info.pending_update_count}')
            self.stdout.write(f'  Max connections: {info.max_connections}')
            
            if info.last_error_date:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Last error: {info.last_error_message} at {info.last_error_date}'
                    )
                )
            
            if not info.url:
                self.stdout.write(
                    self.style.WARNING(
                        '\nWebhook not set. Bot is using polling mode.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        '\nWebhook is active. Bot will receive updates via webhook.'
                    )
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting webhook info: {e}'))

    def delete_webhook(self, bot):
        """Delete webhook (switch to polling mode)"""
        try:
            result = bot.delete_webhook()
            
            if result:
                self.stdout.write(
                    self.style.SUCCESS(
                        'Webhook deleted successfully.\n'
                        'Bot is now in polling mode.\n'
                        'Run: python manage.py run_telegram_bot'
                    )
                )
            else:
                self.stdout.write(self.style.ERROR('Failed to delete webhook'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error deleting webhook: {e}'))

    def set_webhook(self, bot, url):
        """Set webhook URL"""
        # Validate URL
        if not url.startswith('https://'):
            self.stdout.write(
                self.style.ERROR(
                    'Webhook URL must use HTTPS protocol.\n'
                    'For local testing, use ngrok: https://ngrok.com/'
                )
            )
            return

        try:
            self.stdout.write(f'Setting webhook to: {url}')
            
            # Set webhook
            result = bot.set_webhook(
                url=url,
                max_connections=100,
                allowed_updates=['message', 'callback_query']
            )
            
            if result:
                self.stdout.write(self.style.SUCCESS('✓ Webhook set successfully!'))
                
                # Verify
                info = bot.get_webhook_info()
                self.stdout.write(f'\nWebhook URL: {info.url}')
                self.stdout.write(f'Pending updates: {info.pending_update_count}')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        '\n✓ Bot is now in webhook mode.\n'
                        '  Make sure your Django server is running and accessible from the internet.'
                    )
                )
            else:
                self.stdout.write(self.style.ERROR('Failed to set webhook'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error setting webhook: {e}'))
            logger.error(f'Webhook setup error: {e}', exc_info=True)
