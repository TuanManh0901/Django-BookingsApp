"""
Telegram Bot Application Singleton
Tạo một instance duy nhất của bot application để xử lý webhook updates
"""
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Global application instance
_application = None


def get_bot_application():
    """
    Lấy hoặc tạo bot application singleton
    Được sử dụng cho webhook mode
    """
    global _application
    
    if _application is None:
        logger.info("Creating Telegram bot application singleton")
        
        # Import handlers từ run_telegram_bot command
        # Tránh circular import
        from telegram_bot.management.commands.run_telegram_bot import Command
        
        # Tạo application
        token = settings.TELEGRAM_BOT_TOKEN
        _application = Application.builder().token(token).build()
        
        # Tạo instance của Command để sử dụng handlers
        cmd = Command()
        
        # Add handlers (giống như trong run_telegram_bot.py)
        _application.add_handler(CommandHandler("start", cmd.start))
        _application.add_handler(CommandHandler("help", cmd.help_command))
        _application.add_handler(CommandHandler("tours", cmd.list_tours))
        _application.add_handler(CommandHandler("book", cmd.book_tour))
        _application.add_handler(CommandHandler("menu", cmd.menu_command))
        _application.add_handler(CallbackQueryHandler(cmd.handle_menu, pattern=r"^menu_"))
        _application.add_handler(CallbackQueryHandler(cmd.handle_tour_detail, pattern=r"^tour_"))
        _application.add_handler(CallbackQueryHandler(cmd.handle_book_init, pattern=r"^book_"))
        _application.add_handler(CallbackQueryHandler(cmd.handle_booking_callback, pattern=r"^(bookdate_|bookadults_|bookchildren_)"))
        _application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd.handle_text))
        
        logger.info("Bot application initialized with handlers")
    
    return _application


async def process_telegram_update(update_data):
    """
    Process Telegram update từ webhook
    
    Args:
        update_data: Dict chứa update data từ Telegram
    """
    from telegram import Update
    
    app = get_bot_application()
    
    # Tạo Update object
    update = Update.de_json(update_data, app.bot)
    
    # Process update
    await app.process_update(update)
