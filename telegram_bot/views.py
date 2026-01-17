"""
Telegram Bot Webhook Views
"""
import json
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from telegram import Update
from telegram.ext import Application

logger = logging.getLogger(__name__)


@csrf_exempt
def telegram_webhook(request):
    """
    Webhook endpoint cho Telegram Bot.
    Telegram sẽ gửi POST request với JSON update đến endpoint này.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Parse JSON từ request body
        update_data = json.loads(request.body.decode('utf-8'))
        
        logger.info(f"Received webhook update: {update_data.get('update_id', 'unknown')}")
        
        # Process update với bot application
        # Sử dụng asyncio để chạy async function
        import asyncio
        from .bot_app import process_telegram_update
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(process_telegram_update(update_data))
        finally:
            loop.close()
        
        # Trả về 200 OK cho Telegram
        return HttpResponse('OK', status=200)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


def webhook_info(request):
    """
    Endpoint để kiểm tra webhook info (chỉ cho admin/testing).
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    try:
        from telegram import Bot
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        # Lấy webhook info từ Telegram
        webhook_info = bot.get_webhook_info()
        
        info = {
            'url': webhook_info.url,
            'has_custom_certificate': webhook_info.has_custom_certificate,
            'pending_update_count': webhook_info.pending_update_count,
            'last_error_date': str(webhook_info.last_error_date) if webhook_info.last_error_date else None,
            'last_error_message': webhook_info.last_error_message,
            'max_connections': webhook_info.max_connections,
            'allowed_updates': webhook_info.allowed_updates,
        }
        
        return JsonResponse(info)
        
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return JsonResponse({'error': str(e)}, status=500)
