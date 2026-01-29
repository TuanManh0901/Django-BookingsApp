from django.core.management.base import BaseCommand
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import django
import os
from datetime import datetime, timedelta
from decimal import Decimal
from asgiref.sync import sync_to_async

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vn_travel.settings')
django.setup()

from django.contrib.auth import get_user_model
from tours.models import Tour
from bookings.models import Booking
from telegram_bot.models import TelegramUser, Conversation
from ai_chatbot.services import TravelAdvisor

class Command(BaseCommand):
    help = 'Run the Telegram bot for VN Travel Advisor'

    def handle(self, *args, **options):
        from django.conf import settings
        token = settings.TELEGRAM_BOT_TOKEN

        application = Application.builder().token(token).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("tours", self.list_tours))
        application.add_handler(CommandHandler("book", self.book_tour))
        application.add_handler(CommandHandler("menu", self.menu_command))
        application.add_handler(CommandHandler("connect", self.connect_command))
        application.add_handler(CallbackQueryHandler(self.handle_menu, pattern=r"^menu_"))
        application.add_handler(CallbackQueryHandler(self.handle_menu, pattern=r"^viewbooking_"))
        application.add_handler(CallbackQueryHandler(self.handle_menu, pattern=r"^pay_booking_"))
        application.add_handler(CallbackQueryHandler(self.handle_menu, pattern=r"^cancel_booking_"))
        application.add_handler(CallbackQueryHandler(self.handle_menu, pattern=r"^confirm_cancel_"))
        application.add_handler(CallbackQueryHandler(self.handle_menu, pattern=r"^back_to_bookings"))
        application.add_handler(CallbackQueryHandler(self.handle_tour_detail, pattern=r"^tour_"))
        application.add_handler(CallbackQueryHandler(self.handle_book_init, pattern=r"^book_"))
        application.add_handler(CallbackQueryHandler(self.handle_booking_callback, pattern=r"^(bookdate_|bookadults_|bookchildren_|cancel_manual_)"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

        self.stdout.write(self.style.SUCCESS('Bot is running... Press Ctrl+C to stop.'))
        application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        telegram_user = await self._get_or_create_user(update)
        user = update.effective_user

        start_message = (
            f"Chào mừng {user.mention_html()} đến với VN Travel Advisor Bot! 🏖️✈️\n\n"
            "Vui lòng chọn chức năng bên dưới:"
        )

        await update.message.reply_html(start_message)
        await self._log_conversation(telegram_user, "bot", start_message)
        await self.send_main_menu(update)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        telegram_user = await self._get_or_create_user(update)
        await update.message.reply_text(
            "Danh sách lệnh có sẵn:\n\n"
            "/start - Bắt đầu sử dụng bot\n"
            "/tours - Xem danh sách tour du lịch\n"
            "/book - Đặt tour (sẽ có hướng dẫn)\n"
            "/connect - Liên kết tài khoản Web\n"
            "/help - Hiển thị trợ giúp này\n\n"
            "Nếu bạn cần hỗ trợ thêm, hãy liên hệ với đội ngũ VN Travel!"
        )
        await self._log_conversation(telegram_user, "bot", "Danh sách lệnh /help")

    async def list_tours(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List available tours."""
        telegram_user = await self._get_or_create_user(update)
        tours = await sync_to_async(list)(Tour.objects.filter(is_active=True)[:10])
        if not tours:
            await update.message.reply_text("Hiện tại chưa có tour nào khả dụng.")
            await self._log_conversation(telegram_user, "bot", "Hiện tại chưa có tour")
            return

        message = "🏖️ **Danh sách Tour Du Lịch VN Travel** 🏖️\n\n"
        for tour in tours:
            message += f"📍 **{tour.name}**\n"
            message += f"💰 Giá: {int(tour.price):,} VND\n"
            message += f"📅 Thời gian: {tour.duration} ngày\n"
            message += f"🌍 Địa điểm: {tour.location}\n"
            message += f"📝 {tour.description[:100]}...\n\n"

        message += "Để đặt tour, sử dụng lệnh /book"
        await update.message.reply_text(message, parse_mode='Markdown')
        await self._log_conversation(telegram_user, "bot", "Gửi danh sách tours")

    async def book_tour(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle tour booking request."""
        telegram_user = await self._get_or_create_user(update)
        tours = await sync_to_async(list)(Tour.objects.filter(is_active=True))
        if not tours:
            msg = "Hiện chưa có tour để đặt."
            await update.message.reply_text(msg)
            await self._log_conversation(telegram_user, "bot", msg)
            return

        keyboard = [
            [InlineKeyboardButton(f"{tour.name} • {int(tour.price):,} VND", callback_data=f"tour_{tour.id}")]
            for tour in tours
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")])

        msg = "Chọn tour để xem chi tiết và đặt qua bot:"
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        await self._log_conversation(telegram_user, "bot", msg)

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        telegram_user = await self._get_or_create_user(update)
        await self.send_main_menu(update)
        await self._log_conversation(telegram_user, "bot", "Hiển thị menu chính")

    async def connect_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /connect command to link Telegram account with Web account."""
        telegram_user = await self._get_or_create_user(update)
        
        # Generate Magic Link for connecting
        from django.conf import settings
        from django.core.signing import TimestampSigner
        import urllib.parse
        
        base_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        signer = TimestampSigner()
        
        # Sign the telegram_id to ensure security
        token = signer.sign(str(telegram_user.telegram_id))
        connect_url = f"{base_url}/telegram/connect/{token}/"
        
        msg = (
            "🔗 **LIÊN KẾT TÀI KHOẢN**\n\n"
            "Vui lòng nhấn vào link bên dưới để liên kết tài khoản Telegram này với tài khoản VN Travel của bạn:\n\n"
            f"👉 [Nhấn vào đây để liên kết]({connect_url})\n\n"
            "⚠️ Link chỉ có hiệu lực trong 60 phút.\n"
            "💡 Bạn cần đăng nhập vào website trước khi bấm link."
        )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        await self._log_conversation(telegram_user, "bot", "Gửi link liên kết tài khoản")

    async def handle_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        telegram_user = await self._get_or_create_user(update)

        data = query.data
        print(f"DEBUG: handle_menu called with callback data: {data}", flush=True)

        if data == "menu_search":
            telegram_user.conversation_state = "searching"
            await sync_to_async(telegram_user.save)()
            prompt = "Bạn muốn đi đâu? Nhập tên điểm đến (ví dụ: Đà Nẵng, Đà Lạt)."
            
            # Tạo inline keyboard với nút quay lại menu
            keyboard = [[InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(prompt, reply_markup=reply_markup)
            await self._log_conversation(telegram_user, "bot", prompt)
            return

        # Reset state for other menu actions
        telegram_user.conversation_state = ""
        await sync_to_async(telegram_user.save)()

        if data == "menu_tours":
            # Hiển thị tất cả tours
            tours = await sync_to_async(list)(Tour.objects.filter(is_active=True))
            if not tours:
                msg = "Hiện chưa có tour nào khả dụng."
                await query.edit_message_text(msg)
                await self._log_conversation(telegram_user, "bot", msg)
                return

            # Tạo message với thông tin tour
            msg = "📋 **DANH SÁCH TOUR DU LỊCH VN TRAVEL**\n\n"
            for i, tour in enumerate(tours, 1):
                available = 0
                if hasattr(tour, "get_available_seats"):
                    try:
                        available = await sync_to_async(tour.get_available_seats)()
                    except:
                        available = tour.max_people
                else:
                    available = tour.max_people
                
                msg += f"{i}. **{tour.name}**\n"
                msg += f"   📍 {tour.location}\n"
                msg += f"   💰 {int(tour.price):,} VND\n"
                msg += f"   ⏱ {tour.duration} ngày\n"
                msg += f"   👥 Còn {available}/{tour.max_people} chỗ\n\n"

            # Tạo keyboard để chọn tour
            keyboard = [
                [InlineKeyboardButton(f"{tour.name}", callback_data=f"tour_{tour.id}")]
                for tour in tours
            ]
            keyboard.append([InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")])

            msg += "Chọn tour để xem chi tiết:"
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            await self._log_conversation(telegram_user, "bot", msg)
            return

        if data == "menu_book":
            tours = await sync_to_async(list)(Tour.objects.filter(is_active=True))
            if not tours:
                msg = "Hiện chưa có tour để đặt."
                await query.edit_message_text(msg)
                await self._log_conversation(telegram_user, "bot", msg)
                return

            keyboard = [
                [InlineKeyboardButton(f"{tour.name} • {int(tour.price):,} VND", callback_data=f"tour_{tour.id}")]
                for tour in tours
            ]
            keyboard.append([InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")])

            msg = "Chọn tour để xem chi tiết và đặt qua bot:"
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            await self._log_conversation(telegram_user, "bot", msg)
            return

        if data == "menu_back":
            # Quay lại menu chính
            await self.send_main_menu(update)
            await self._log_conversation(telegram_user, "bot", "Quay lại menu chính")
            return

        if data == "menu_view":
            await self._show_bookings_list(update, telegram_user, query)
            return

        # Handler cho xem chi tiết booking
        if data.startswith("viewbooking_"):
            print(f"DEBUG: viewbooking handler called with data: {data}", flush=True)
            try:
                booking_id = int(data.split("_")[1])
                
                # Lấy django user
                django_user = await sync_to_async(lambda: telegram_user.django_user)()
                if not django_user:
                    msg = "❌ Bạn chưa liên kết tài khoản VN Travel."
                    keyboard = [[InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")]]
                    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                # Lấy booking
                booking = await sync_to_async(
                    Booking.objects.filter(id=booking_id, user=django_user).select_related('tour').first
                )()
                
                if not booking:
                    msg = "❌ Không tìm thấy booking này."
                    keyboard = [[InlineKeyboardButton("⬅️ Quay lại danh sách", callback_data="back_to_bookings")]]
                    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                # Hiển thị thông tin chi tiết booking
                # Use effective_status to be consistent with Web logic (handling expiration)
                effective_status = 'pending'
                if hasattr(booking, 'get_effective_status'):
                    effective_status = await sync_to_async(booking.get_effective_status)()
                else:
                    effective_status = booking.status

                status_emoji = {
                    'pending': '⏳',
                    'confirmed': '✅',
                    'paid': '💳',
                    'partial_paid': '💸',
                    'cancelled': '❌'
                }.get(effective_status, '📋')
                
                status_text = {
                    'pending': 'Chờ xác nhận',
                    'confirmed': 'Đã xác nhận',
                    'paid': 'Đã thanh toán',
                    'partial_paid': 'Đã đặt cọc',
                    'cancelled': 'Đã hủy'
                }.get(effective_status, effective_status)
                
                msg = f"📋 **CHI TIẾT BOOKING**\n\n"
                msg += f"🏷️ **Tour:** {booking.tour.name}\n"
                msg += f"📅 **Ngày đi:** {booking.booking_date.strftime('%d/%m/%Y')}\n"
                msg += f"👥 **Số người:** {booking.num_adults} người lớn"
                if booking.num_children > 0:
                    msg += f", {booking.num_children} trẻ em"
                msg += f"\n💰 **Tổng tiền:** {int(booking.total_price):,} VND\n"
                msg += f"🔖 **Trạng thái:** {status_emoji} {status_text}\n"
                
                # Thông tin thanh toán
                payment_status_text = {
                    'pending': '⏳ Chờ thanh toán',
                    'paid': '✅ Đã thanh toán',
                    'refunded': '💸 Đã hoàn tiền'
                }.get(booking.payment_status, booking.payment_status)
                msg += f"💳 **Thanh toán:** {payment_status_text}\n"
                
                # Thông tin đặt cọc nếu có
                if booking.deposit_required and booking.deposit_amount > 0:
                    deposit_pct = int(float(booking.deposit_percentage) * 100)
                    msg += f"\n💵 **Đặt cọc:** {deposit_pct}% = {int(booking.deposit_amount):,} VND\n"
                    if booking.deposit_paid:
                        msg += f"✅ **Đã cọc:** Có\n"
                        remaining = await sync_to_async(booking.get_remaining_amount)()
                        msg += f"💰 **Còn lại:** {int(remaining):,} VND\n"
                    else:
                        msg += f"⏳ **Đã cọc:** Chưa\n"
                
                msg += f"\n🕐 **Ngày đặt:** {booking.created_at.strftime('%d/%m/%Y %H:%M')}\n"
                
                # Tạo các nút hành động dựa trên trạng thái thanh toán
                keyboard = []
                
                # Nếu chưa thanh toán và chưa bị hủy (dựa trên effective_status)
                if booking.payment_status == 'pending' and effective_status != 'cancelled':
                    # Generate Magic Link for Payment
                    from django.conf import settings
                    from django.core.signing import TimestampSigner
                    import urllib.parse
                    
                    base_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
                    signer = TimestampSigner()
                    token = signer.sign(django_user.username)
                    auth_base = f"{base_url}/telegram/auth/{token}/"
                    
                    # Target path
                    target_path = f"/payment/booking/{booking.id}/payment/"
                    encoded_path = urllib.parse.quote(target_path)
                    magic_link = f"{auth_base}?next={encoded_path}"

                    keyboard.append([InlineKeyboardButton("💳 Thanh toán ngay", url=magic_link)])
                    keyboard.append([InlineKeyboardButton("❌ Huỷ booking", callback_data=f"cancel_booking_{booking.id}")])
                
                keyboard.append([InlineKeyboardButton("⬅️ Quay lại danh sách", callback_data="back_to_bookings")])
                
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
                await self._log_conversation(telegram_user, "bot", f"Hiển thị chi tiết booking {booking_id}")
                return
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in viewbooking: {e}")
                msg = "❌ Có lỗi xảy ra khi tải thông tin booking."
                keyboard = [[InlineKeyboardButton("⬅️ Quay lại danh sách", callback_data="back_to_bookings")]]
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                return

        # Handler cho thanh toán booking
        if data.startswith("pay_booking_"):
            try:
                booking_id = int(data.split("_")[2])
                
                # Lấy django user
                django_user = await sync_to_async(lambda: telegram_user.django_user)()
                if not django_user:
                    msg = "❌ Bạn chưa liên kết tài khoản VN Travel."
                    keyboard = [[InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")]]
                    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                # Lấy booking
                booking = await sync_to_async(
                    Booking.objects.filter(id=booking_id, user=django_user).select_related('tour').first
                )()
                
                if not booking:
                    msg = "❌ Không tìm thấy booking này."
                    keyboard = [[InlineKeyboardButton("⬅️ Quay lại danh sách", callback_data="back_to_bookings")]]
                    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                # Kiểm tra trạng thái thanh toán
                if booking.payment_status != 'pending':
                    msg = "✅ Booking này đã được thanh toán rồi!"
                    keyboard = [[InlineKeyboardButton("⬅️ Quay lại chi tiết", callback_data=f"viewbooking_{booking_id}")]]
                    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                # Hiển thị hướng dẫn thanh toán
                msg = "💳 **HƯỚNG DẪN THANH TOÁN**\n\n"
                msg += f"🏷️ **Tour:** {booking.tour.name}\n"
                msg += f"💰 **Số tiền:** {int(booking.total_price):,} VND\n\n"
                msg += "📱 **Để thanh toán, vui lòng:**\n\n"
                msg += "1️⃣ Truy cập website VN Travel\n"
                msg += "2️⃣ Đăng nhập vào tài khoản\n"
                msg += "3️⃣ Vào phần 'Booking của tôi'\n"
                msg += "4️⃣ Chọn booking này và thanh toán\n\n"
                msg += "🌐 **Link website:**\n"
                msg += "https://vntravel.com/bookings/\n\n"
                msg += "💡 _Sau khi thanh toán xong, trạng thái sẽ tự động cập nhật._"
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Làm mới trạng thái", callback_data=f"viewbooking_{booking_id}")],
                    [InlineKeyboardButton("⬅️ Quay lại chi tiết", callback_data=f"viewbooking_{booking_id}")]
                ]
                
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
                await self._log_conversation(telegram_user, "bot", f"Hiển thị hướng dẫn thanh toán cho booking {booking_id}")
                return
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in pay_booking: {e}")
                msg = "❌ Có lỗi xảy ra. Vui lòng thử lại sau."
                keyboard = [[InlineKeyboardButton("⬅️ Quay lại danh sách", callback_data="back_to_bookings")]]
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                return

        # Handler cho huỷ booking (hiển thị xác nhận)
        if data.startswith("cancel_booking_"):
            try:
                booking_id = int(data.split("_")[2])
                
                # Lấy django user
                django_user = await sync_to_async(lambda: telegram_user.django_user)()
                if not django_user:
                    msg = "❌ Bạn chưa liên kết tài khoản VN Travel."
                    keyboard = [[InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")]]
                    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                # Lấy booking
                booking = await sync_to_async(
                    Booking.objects.filter(id=booking_id, user=django_user).select_related('tour').first
                )()
                
                if not booking:
                    msg = "❌ Không tìm thấy booking này."
                    keyboard = [[InlineKeyboardButton("⬅️ Quay lại danh sách", callback_data="back_to_bookings")]]
                    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                # Kiểm tra xem có thể hủy không
                if booking.status == 'cancelled':
                    msg = "ℹ️ Booking này đã bị hủy rồi."
                    keyboard = [[InlineKeyboardButton("⬅️ Quay lại chi tiết", callback_data=f"viewbooking_{booking_id}")]]
                    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                if booking.payment_status == 'paid':
                    msg = "⚠️ Booking đã thanh toán không thể hủy qua bot.\n\nVui lòng liên hệ:\n📞 Hotline: 1900-xxxx\n📧 Email: support@vntravel.com"
                    keyboard = [[InlineKeyboardButton("⬅️ Quay lại chi tiết", callback_data=f"viewbooking_{booking_id}")]]
                    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                # Hiển thị xác nhận huỷ
                msg = "⚠️ **XÁC NHẬN HUỶ BOOKING**\n\n"
                msg += f"🏷️ **Tour:** {booking.tour.name}\n"
                msg += f"📅 **Ngày đi:** {booking.booking_date.strftime('%d/%m/%Y')}\n"
                msg += f"💰 **Tổng tiền:** {int(booking.total_price):,} VND\n\n"
                msg += "❓ **Bạn có chắc chắn muốn hủy booking này không?**\n\n"
                msg += "⚠️ _Hành động này không thể hoàn tác._"
                
                keyboard = [
                    [InlineKeyboardButton("✅ Xác nhận hủy", callback_data=f"confirm_cancel_{booking_id}")],
                    [InlineKeyboardButton("❌ Không, quay lại", callback_data=f"viewbooking_{booking_id}")]
                ]
                
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
                await self._log_conversation(telegram_user, "bot", f"Hiển thị xác nhận hủy booking {booking_id}")
                return
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in cancel_booking: {e}")
                msg = "❌ Có lỗi xảy ra. Vui lòng thử lại sau."
                keyboard = [[InlineKeyboardButton("⬅️ Quay lại danh sách", callback_data="back_to_bookings")]]
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                return

        # Handler cho xác nhận huỷ booking (thực hiện hủy)
        if data.startswith("confirm_cancel_"):
            try:
                booking_id = int(data.split("_")[2])
                
                # Lấy django user
                django_user = await sync_to_async(lambda: telegram_user.django_user)()
                if not django_user:
                    msg = "❌ Bạn chưa liên kết tài khoản VN Travel."
                    keyboard = [[InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")]]
                    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                # Lấy booking
                booking = await sync_to_async(
                    Booking.objects.filter(id=booking_id, user=django_user).select_related('tour').first
                )()
                
                if not booking:
                    msg = "❌ Không tìm thấy booking này."
                    keyboard = [[InlineKeyboardButton("⬅️ Quay lại danh sách", callback_data="back_to_bookings")]]
                    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                # Cập nhật trạng thái booking
                def update_booking_status():
                    booking.status = 'cancelled'
                    booking.save()
                
                await sync_to_async(update_booking_status)()
                
                # Hiển thị thông báo thành công
                msg = "✅ **ĐÃ HUỶ BOOKING THÀNH CÔNG**\n\n"
                msg += f"🏷️ **Tour:** {booking.tour.name}\n"
                msg += f"📅 **Ngày đi:** {booking.booking_date.strftime('%d/%m/%Y')}\n"
                msg += f"💰 **Số tiền:** {int(booking.total_price):,} VND\n\n"
                msg += "Booking đã được hủy. Cảm ơn bạn đã sử dụng dịch vụ VN Travel! 🙏"
                
                keyboard = [[InlineKeyboardButton("⬅️ Quay lại danh sách", callback_data="back_to_bookings")]]
                
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
                await self._log_conversation(telegram_user, "bot", f"Đã hủy booking {booking_id}")
                return
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in confirm_cancel: {e}")
                msg = "❌ Có lỗi xảy ra khi hủy booking. Vui lòng thử lại sau."
                keyboard = [[InlineKeyboardButton("⬅️ Quay lại danh sách", callback_data="back_to_bookings")]]
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                return

        # Handler cho quay lại danh sách bookings
        if data == "back_to_bookings":
            await self._show_bookings_list(update, telegram_user, query)
            return

        if data == "menu_ai":
            # Chuyển state sang asking_ai
            telegram_user.conversation_state = "asking_ai"
            await sync_to_async(telegram_user.save)()
            
            msg = (
                "🤖 **AI TRAVEL ADVISOR**\n\n"
                "Xin chào! Tôi là trợ lý AI của VN Travel.\n"
                "Tôi có thể giúp bạn:\n\n"
                "✈️ Tư vấn địa điểm du lịch\n"
                "💰 Gợi ý tour phù hợp với ngân sách\n"
                "📅 Lên kế hoạch lịch trình\n"
                "❓ Trả lời mọi câu hỏi về du lịch\n\n"
                "Hãy hỏi tôi bất cứ điều gì! 😊"
            )
            
            # Tạo inline keyboard với nút quay lại menu
            keyboard = [[InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=reply_markup)
            await self._log_conversation(telegram_user, "bot", msg)
            return

        responses = {
            "menu_search": "🔍 Chức năng tìm tour sẽ có ở bước tiếp theo (Ngày 17).",
            "menu_view": "📑 Xem booking qua bot sẽ được bật ở Ngày 21.",
        }
        message = responses.get(data, "Tính năng đang được cập nhật.")
        await query.edit_message_text(message)
        await self._log_conversation(telegram_user, "bot", message)

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        telegram_user = await self._get_or_create_user(update)
        state = (telegram_user.conversation_state or "").strip()
        text = (update.message.text or "").strip()

        if state == "searching":
            tours = await sync_to_async(list)(
                Tour.objects.filter(is_active=True, location__icontains=text)[:5]
            )

            if not tours:
                reply = (
                    f"Không tìm thấy tour cho điểm đến '{text}'.\n"
                    "Nhập địa điểm khác hoặc gõ /menu để quay lại."
                )
                await update.message.reply_text(reply)
                await self._log_conversation(telegram_user, "bot", reply)
                return

            # Reset state only khi có kết quả
            telegram_user.conversation_state = ""
            await sync_to_async(telegram_user.save)()

            keyboard = [
                [InlineKeyboardButton(f"{tour.name} • {int(tour.price):,} VND", callback_data=f"tour_{tour.id}")]
                for tour in tours
            ]
            # Thêm nút quay lại menu
            keyboard.append([InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")])
            
            await update.message.reply_text(
                "Chọn tour bên dưới để xem chi tiết:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            await self._log_conversation(
                telegram_user,
                "bot",
                f"Gợi ý tour cho điểm đến {text}",
            )
            return

        if state == "asking_ai":
            # Xử lý câu hỏi cho AI
            if not text:
                await update.message.reply_text("Vui lòng nhập câu hỏi của bạn.")
                return
            
            # Gửi typing indicator
            await update.message.chat.send_action("typing")
            
        # Handle manual booking input
        if state.startswith("waiting_adults_"):
            # waiting_adults_{tour_id}_{booking_date}
            try:
                parts = state.split("_")
                tour_id = parts[2]
                booking_date = "_".join(parts[3:])
                
                adults_count = int(text)
                if adults_count < 1:
                    await update.message.reply_text("Số người lớn phải ít nhất là 1. Vui lòng nhập lại:")
                    return
                
                # Move to next step: Ask children 
                # And we need to transition state. 
                
                # Correct logic:
                telegram_user.conversation_state = f"booking|{tour_id}|children|{booking_date}|{adults_count}"
                await sync_to_async(telegram_user.save)()
                
                # Call _ask_children. Helper needs 'query' object usually, but can adapt.
                # _ask_children uses query.edit_message_text. 
                # We need to send a NEW message because we are in handle_text (responding to text).
                
                keyboard = [
                    [InlineKeyboardButton("0 trẻ em", callback_data=f"bookchildren_{tour_id}_{booking_date}_{adults_count}_0")],
                    [InlineKeyboardButton("1 trẻ em", callback_data=f"bookchildren_{tour_id}_{booking_date}_{adults_count}_1")],
                    [InlineKeyboardButton("2 trẻ em", callback_data=f"bookchildren_{tour_id}_{booking_date}_{adults_count}_2")],
                    [InlineKeyboardButton("✏️ Nhập số lượng khác", callback_data=f"bookchildren_manual_{tour_id}_{booking_date}_{adults_count}")],
                    [InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_book")],
                ]
                msg = f"Đã ghi nhận {adults_count} người lớn.\nChọn số trẻ em:"
                await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                return

            except ValueError:
                await update.message.reply_text("Vui lòng nhập một con số hợp lệ (ví dụ: 2, 5).")
                return

        if state.startswith("waiting_children_"):
            # waiting_children_{tour_id}_{booking_date}_{adults}
            try:
                parts = state.split("_")
                tour_id = parts[2]
                booking_date = parts[3]
                adults = int(parts[4])
                
                children_count = int(text)
                if children_count < 0:
                    await update.message.reply_text("Số trẻ em không thể âm. Vui lòng nhập lại:")
                    return

                # Proceed to create booking
                # We reuse the logic in handle_booking_callback by simulating a callback or just calling the logic.
                # Since handle_booking_callback logic for creation is long, better to duplicate or refactor.
                # For safety, I will replicate the creation logic here or construct a special internal call.
                
                # Let's verify constraints first
                tour = await sync_to_async(Tour.objects.filter(is_active=True, id=tour_id).first)()
                if not tour:
                    await update.message.reply_text("Tour không còn tồn tại.")
                    return

                total_people = adults + children_count
                available_seats = None
                if hasattr(tour, "get_available_seats"):
                    try:
                        available_seats = await sync_to_async(tour.get_available_seats)()
                    except Exception:
                        available_seats = None
                
                if available_seats is not None and total_people > available_seats:
                    msg = f"Không đủ chỗ. Tour còn {available_seats} chỗ, bạn đang đặt {total_people}."
                    await update.message.reply_text(msg)
                    return

                # Create booking
                total_price = Decimal(tour.price) * Decimal(total_people)
                django_user = await self._get_or_create_site_user(telegram_user)

                await sync_to_async(Booking.objects.create)(
                    user=django_user,
                    tour=tour,
                    booking_date=datetime.strptime(booking_date, "%Y-%m-%d").date(),
                    num_adults=adults,
                    num_children=children_count,
                    total_price=total_price,
                    status="pending",
                    payment_status="pending",
                )

                telegram_user.conversation_state = ""
                await sync_to_async(telegram_user.save)()

                booking = await sync_to_async(Booking.objects.filter(
                    user=django_user, 
                    tour=tour, 
                    booking_date=datetime.strptime(booking_date, "%Y-%m-%d").date()
                ).latest)('created_at')
                
                booking_id = booking.id

                # Gửi email xác nhận
                from bookings.email_utils import send_booking_confirmation_email
                try:
                    await sync_to_async(send_booking_confirmation_email)(booking)
                except Exception as e:
                    print(f"Error sending email: {e}")

                # Generate Magic Link
                from django.conf import settings
                from django.core.signing import TimestampSigner
                import urllib.parse
                
                base_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
                signer = TimestampSigner()
                token = signer.sign(django_user.username)
                auth_base = f"{base_url}/telegram/auth/{token}/"
                
                def get_magic_link(path):
                    encoded_path = urllib.parse.quote(path)
                    return f"{auth_base}?next={encoded_path}"

                # Update message with confirmation
                msg = (
                    f"✅ Đặt tour thành công!\n\n"
                    f"📍 Tour: {tour.name}\n"
                    f"📅 Ngày: {booking_date}\n"
                    f"👥 Người lớn: {adults}, Trẻ em: {children_count}\n"
                    f"💰 Tổng tiền: {int(total_price):,} VND\n\n"
                    f"🔗 Mã booking: #{booking_id}\n\n"
                    "Vui lòng chọn phương thức thanh toán bên dưới:"
                )
                
                keyboard = [
                    [InlineKeyboardButton(
                        "💳 Chọn phương thức thanh toán", 
                        url=get_magic_link(f"/payment/booking/{booking_id}/payment/")
                    )],
                    [InlineKeyboardButton("📑 Xem chi tiết booking", url=get_magic_link(f"/booking/{booking_id}/"))],
                    [InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_book")],
                ]
                
                await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                return

            except ValueError:
                await update.message.reply_text("Vui lòng nhập một con số hợp lệ.")
                return
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in manual booking: {e}")
                await update.message.reply_text("Có lỗi xảy ra. Vui lòng thử lại sau.")
                return
            
            
            

        # Default handler: AI Chat
        if not state or state == "asking_ai":
            # Helper function để gửi tin nhắn thông minh
            async def send_smart_message(text, parse_mode='HTML'):
                import re
                
                # Hàm làm sạch HTML cho Telegram
                def cleanup_html_for_telegram(raw_text):
                    # 1. Thay thế các header tags h1-h6 bằng <b>
                    # VD: <h3>Tiêu đề</h3> -> <b>Tiêu đề</b>
                    cleaned = re.sub(r'<h[1-6]>(.*?)</h[1-6]>', r'<b>\1</b>', raw_text, flags=re.DOTALL)
                    
                    # 2. Xử lý thẻ <br> thành xuống dòng
                    cleaned = cleaned.replace('<br>', '\n').replace('<br/>', '\n')
                    
                    # 3. Xử lý thẻ <p> và <div> thành xuống dòng (nếu cần)
                    cleaned = re.sub(r'</(p|div)>', '\n', cleaned)
                    cleaned = re.sub(r'<(p|div)[^>]*>', '', cleaned)
                    
                    # 4. Xóa các thẻ markdown khác nếu còn sót lại (như <span>, <font>...)
                    # Telegram chỉ hỗ trợ: <b>, <strong>, <i>, <em>, <u>, <ins>, <s>, <strike>, <del>, <code>, <pre>, <a>
                    # Tuy nhiên regex để whitelist thì phức tạp, ta chỉ fix những lỗi hay gặp nhất từ AI.
                    
                    return cleaned

                # Làm sạch text trước khi xử lý
                text = cleanup_html_for_telegram(text)

                # Hàm chia tin nhắn an toàn hơn (split theo newline)
                def split_text_safe(text, limit=4000):
                    if len(text) <= limit:
                        return [text]
                    parts = []
                    while text:
                        if len(text) <= limit:
                            parts.append(text)
                            break
                        # Tìm vị trí xuống dòng gần nhất trước limit
                        split_at = text.rfind('\n', 0, limit)
                        if split_at == -1:
                            # Nếu không có newline, buộc phải cắt tại limit
                            split_at = limit
                        parts.append(text[:split_at])
                        text = text[split_at:].lstrip() # Xóa khoảng trắng thừa đầu dòng
                    return parts

                chunks = split_text_safe(text)
                
                for chunk in chunks:
                    try:
                        await update.message.reply_text(chunk, parse_mode=parse_mode)
                    except Exception as e:
                        # Nếu vẫn lỗi (thường do tag lồng nhau sai hoặc unclosed tag), gửi dạng text thường
                        # Strip mọi tag để dễ đọc hơn
                        strip_tags = re.sub(r'<[^>]*>', '', chunk)
                        await update.message.reply_text(strip_tags, parse_mode=None)

            try:
                # Khởi tạo AI advisor with Telegram mode
                advisor = TravelAdvisor(client_type='telegram')
                
                # Lấy câu trả lời từ AI
                ai_response = await sync_to_async(advisor.get_advice)(text, include_tours=True)
                
                # Gửi câu trả lời
                response_msg = f"🤖 <b>AI Travel Advisor</b>\n\n{ai_response}"
                
                # Log conversation
                await self._log_conversation(telegram_user, "user", text)
                await self._log_conversation(telegram_user, "bot", ai_response)

                # Gửi tin nhắn thông minh
                await send_smart_message(response_msg)
                
                # Gửi suggestion
                suggestion = "\n\n💡 Bạn có câu hỏi khác không? Hoặc gõ /menu để quay lại."
                await update.message.reply_text(suggestion)
                
            except Exception as e:
                error_msg = (
                    f"⚠️ Xin lỗi, đã có lỗi xảy ra: {str(e)}\n\n"
                    "Vui lòng thử lại hoặc gõ /menu để quay lại."
                )
                await update.message.reply_text(error_msg, parse_mode=None)
                await self._log_conversation(telegram_user, "bot", f"Error: {str(e)}")
            
            return

        # Booking flow bằng nút bấm; riêng stage date_manual cho phép nhập ngày
        if state.startswith("booking|"):
            parts = state.split("|")
            if len(parts) >= 3 and parts[2] == "date_manual":
                tour_id = parts[1]
                try:
                    booking_date = datetime.strptime(text, "%Y-%m-%d").date()
                    if booking_date < datetime.now().date():
                        raise ValueError
                except Exception:
                    msg = "Ngày không hợp lệ. Nhập lại theo định dạng YYYY-MM-DD (ví dụ 2025-12-31)."
                    await update.message.reply_text(msg)
                    await self._log_conversation(telegram_user, "bot", msg)
                    return

                telegram_user.conversation_state = f"booking|{tour_id}|adults|{booking_date}"
                await sync_to_async(telegram_user.save)()
                dummy_query = update.message  # placeholder to reuse ask_adults
                await self._ask_adults(dummy_query, tour_id, booking_date, via_message=True)
                return

            msg = "Hãy chọn nút trên màn hình để tiếp tục đặt tour."
            await update.message.reply_text(msg)
            await self._log_conversation(telegram_user, "bot", msg)
            return
    async def handle_tour_detail(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        telegram_user = await self._get_or_create_user(update)

        tour_id = query.data.replace("tour_", "")
        tour = await sync_to_async(Tour.objects.filter(is_active=True, id=tour_id).first)()
        if not tour:
            message = "Tour không còn tồn tại. Nhấn /menu để chọn chức năng khác."
            await query.edit_message_text(message)
            await self._log_conversation(telegram_user, "bot", message)
            return

        description = tour.description or ""
        detail = (
            f"📍 {tour.name}\n"
            f"Địa điểm: {tour.location}\n"
            f"Giá: {int(tour.price):,} VND\n"
            f"Thời gian: {tour.duration} ngày\n"
            f"Mô tả: {description[:240]}...\n"
        )

        keyboard = [
            [InlineKeyboardButton("📝 Đặt tour qua bot", callback_data=f"book_{tour.id}")],
            [InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_book")],
        ]

        await query.edit_message_text(detail, reply_markup=InlineKeyboardMarkup(keyboard))
        await self._log_conversation(telegram_user, "bot", detail)

    async def handle_book_init(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        telegram_user = await self._get_or_create_user(update)

        tour_id = query.data.replace("book_", "")
        tour = await sync_to_async(Tour.objects.filter(is_active=True, id=tour_id).first)()
        if not tour:
            message = "Tour không còn tồn tại. Nhấn /menu để chọn chức năng khác."
            await query.edit_message_text(message)
            await self._log_conversation(telegram_user, "bot", message)
            return

        telegram_user.conversation_state = f"booking|{tour_id}|date_select"
        await sync_to_async(telegram_user.save)()

        today = datetime.now().date()
        options = [today + timedelta(days=d) for d in (3, 7, 14)]
        keyboard = [
            [InlineKeyboardButton(date.strftime("%Y-%m-%d"), callback_data=f"bookdate_{tour_id}_{date}")]
            for date in options
        ]
        keyboard.append([InlineKeyboardButton("Chọn ngày khác (nhập)", callback_data=f"bookdate_{tour_id}_manual")])
        keyboard.append([InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_book")])

        prompt = (
            f"Đặt tour: {tour.name}\n"
            "Chọn ngày khởi hành bằng nút bên dưới hoặc chọn 'Chọn ngày khác (nhập)'."
        )
        await query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard))
        await self._log_conversation(telegram_user, "bot", prompt)

    async def handle_booking_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        telegram_user = await self._get_or_create_user(update)

        data = query.data

        if data.startswith("bookdate_"):
            parts = data.split("_")
            if len(parts) < 3:
                await self._reset_state_with_message_query(query, telegram_user, "Dữ liệu ngày không hợp lệ.")
                return
            tour_id = parts[1]
            date_part = "_".join(parts[2:])

            if date_part == "manual":
                telegram_user.conversation_state = f"booking|{tour_id}|date_manual"
                await sync_to_async(telegram_user.save)()
                
                keyboard = [[InlineKeyboardButton("⬅️ Quay lại chọn ngày", callback_data=f"cancel_manual_date_{tour_id}")]]
                
                msg = "Nhập ngày khởi hành (YYYY-MM-DD), ví dụ 2025-12-31."
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                await self._log_conversation(telegram_user, "bot", msg)
                return

            try:
                booking_date = datetime.strptime(date_part, "%Y-%m-%d").date()
            except Exception:
                await self._reset_state_with_message_query(query, telegram_user, "Ngày không hợp lệ.")
                return

            telegram_user.conversation_state = f"booking|{tour_id}|adults|{booking_date}"
            await sync_to_async(telegram_user.save)()
            await self._ask_adults(query, tour_id, booking_date)
            return

        if data.startswith("cancel_manual_date_"):
            tour_id = data.split("_")[3]
            # Reset state
            telegram_user.conversation_state = f"booking|{tour_id}|date_select"
            await sync_to_async(telegram_user.save)()
            
            # Show date options again (reuse helper logic effectively by calling handle_book_init logic or similar)
            # Since handle_book_init expects internal structure, we can just manually reconstruct the response here.
            
            tour = await sync_to_async(Tour.objects.filter(is_active=True, id=tour_id).first)()
            if not tour:
                await query.edit_message_text("Tour không tồn tại.")
                return

            today = datetime.now().date()
            options = [today + timedelta(days=d) for d in (3, 7, 14)]
            keyboard = [
                [InlineKeyboardButton(date.strftime("%Y-%m-%d"), callback_data=f"bookdate_{tour_id}_{date}")]
                for date in options
            ]
            keyboard.append([InlineKeyboardButton("Chọn ngày khác (nhập)", callback_data=f"bookdate_{tour_id}_manual")])
            keyboard.append([InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_book")])

            prompt = (
                f"Đặt tour: {tour.name}\n"
                "Chọn ngày khởi hành bằng nút bên dưới hoặc chọn 'Chọn ngày khác (nhập)'."
            )
            await query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard))
            return

        if data.startswith("bookadults_manual_"):
            parts = data.split("_")
            # bookadults_manual_{tour_id}_{booking_date}
            tour_id = parts[2]
            booking_date = "_".join(parts[3:])
            
            telegram_user.conversation_state = f"waiting_adults_{tour_id}_{booking_date}"
            await sync_to_async(telegram_user.save)()
            
            keyboard = [[InlineKeyboardButton("⬅️ Quay lại chọn số lượng", callback_data=f"cancel_manual_adults_{tour_id}_{booking_date}")]]
            
            await query.edit_message_text("Vui lòng nhập số người lớn (ví dụ: 5, 10):", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        if data.startswith("cancel_manual_adults_"):
            parts = data.split("_")
            tour_id = parts[3]
            booking_date = "_".join(parts[4:])
            
            # Reset state
            telegram_user.conversation_state = f"booking|{tour_id}|adults|{booking_date}"
            await sync_to_async(telegram_user.save)()
            
            # Show original options
            await self._ask_adults(query, tour_id, booking_date)
            return

        if data.startswith("bookchildren_manual_"):
            parts = data.split("_")
            # bookchildren_manual_{tour_id}_{booking_date}_{adults}
            tour_id = parts[2]
            booking_date = parts[3] # Date might contain dashes, but here assumes split works if no underscore in date? 
                                    # Wait, date format is YYYY-MM-DD, no underscores. Correct.
                                    # But we used split("_"). Let's check format again.
                                    # Format is YYYY-MM-DD. Safe.
            adults = parts[4]
            
            telegram_user.conversation_state = f"waiting_children_{tour_id}_{booking_date}_{adults}"
            await sync_to_async(telegram_user.save)()
            
            keyboard = [[InlineKeyboardButton("⬅️ Quay lại chọn số lượng", callback_data=f"cancel_manual_children_{tour_id}_{booking_date}_{adults}")]]
            
            await query.edit_message_text("Vui lòng nhập số trẻ em (ví dụ: 0, 2):", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        if data.startswith("cancel_manual_children_"):
            parts = data.split("_")
            # cancel_manual_children_{tour_id}_{booking_date}_{adults}
            tour_id = parts[3]
            booking_date = parts[4]
            try:
                adults_val = int(parts[5])
            except:
                adults_val = 1
            
            # Reset state
            telegram_user.conversation_state = f"booking|{tour_id}|children|{booking_date}|{adults_val}"
            await sync_to_async(telegram_user.save)()
            
            # Show original options
            await self._ask_children(query, tour_id, booking_date, adults_val)
            return

        if data.startswith("bookadults_"):
            parts = data.split("_")
            if len(parts) < 4:
                await self._reset_state_with_message_query(query, telegram_user, "Dữ liệu người lớn không hợp lệ.")
                return
            tour_id = parts[1]
            booking_date = parts[2]
            adults = parts[3]
            try:
                int_adults = int(adults)
                if int_adults < 1:
                    raise ValueError
            except Exception:
                await self._reset_state_with_message_query(query, telegram_user, "Số người lớn không hợp lệ.")
                return

            telegram_user.conversation_state = f"booking|{tour_id}|children|{booking_date}|{adults}"
            await sync_to_async(telegram_user.save)()
            await self._ask_children(query, tour_id, booking_date, int_adults)
            return

        if data.startswith("bookchildren_"):
            parts = data.split("_")
            if len(parts) < 5:
                await self._reset_state_with_message_query(query, telegram_user, "Dữ liệu trẻ em không hợp lệ.")
                return
            tour_id = parts[1]
            booking_date = parts[2]
            adults = parts[3]
            children = parts[4]

            try:
                booking_date_obj = datetime.strptime(booking_date, "%Y-%m-%d").date()
                int_adults = int(adults)
                int_children = int(children)
                if int_adults < 1 or int_children < 0:
                    raise ValueError
            except Exception:
                await self._reset_state_with_message_query(query, telegram_user, "Dữ liệu không hợp lệ.")
                return

            tour = await sync_to_async(Tour.objects.filter(is_active=True, id=tour_id).first)()
            if not tour:
                await self._reset_state_with_message_query(query, telegram_user, "Tour không còn tồn tại.")
                return

            total_people = int_adults + int_children
            available_seats = None
            if hasattr(tour, "get_available_seats"):
                try:
                    available_seats = await sync_to_async(tour.get_available_seats)()
                except Exception:
                    available_seats = None
            if available_seats is not None and total_people > available_seats:
                msg = f"Không đủ chỗ. Tour còn {available_seats} chỗ, bạn đang đặt {total_people}."
                await query.edit_message_text(msg)
                await self._log_conversation(telegram_user, "bot", msg)
                return

            total_price = Decimal(tour.price) * Decimal(total_people)
            django_user = await self._get_or_create_site_user(telegram_user)

            await sync_to_async(Booking.objects.create)(
                user=django_user,
                tour=tour,
                booking_date=booking_date_obj,
                num_adults=int_adults,
                num_children=int_children,
                total_price=total_price,
                status="pending",
                payment_status="pending",
            )

            telegram_user.conversation_state = ""
            await sync_to_async(telegram_user.save)()

            # Lấy booking vừa tạo để lấy ID
            booking = await sync_to_async(Booking.objects.filter(
                user=django_user, 
                tour=tour, 
                booking_date=booking_date_obj
            ).latest)('created_at')
            booking_id = booking.id

            # Gửi email xác nhận (chạy async để không block)
            from bookings.email_utils import send_booking_confirmation_email
            try:
                await sync_to_async(send_booking_confirmation_email)(booking)
            except Exception as e:
                print(f"Error sending email: {e}")

            msg = (
                f"✅ Đặt tour thành công!\n\n"
                f"📍 Tour: {tour.name}\n"
                f"📅 Ngày: {booking_date_obj}\n"
                f"👥 Người lớn: {int_adults}, Trẻ em: {int_children}\n"
                f"💰 Tổng tiền: {int(total_price):,} VND\n\n"
                f"🔗 Mã booking: #{booking_id}\n\n"
                "Vui lòng chọn phương thức thanh toán bên dưới:"
            )

            # Keyboard thanh toán
            from django.conf import settings
            from django.core.signing import TimestampSigner
            import urllib.parse
            
            base_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
            
            # Generate Token (Magic Link)
            signer = TimestampSigner()
            token = signer.sign(django_user.username)
            auth_base = f"{base_url}/telegram/auth/{token}/"
            
            # Helper to create magic link
            def get_magic_link(path):
                import urllib.parse
                encoded_path = urllib.parse.quote(path)
                return f"{auth_base}?next={encoded_path}"
            
            # Fix URL paths based on payments/urls.py
            # path('booking/<int:booking_id>/process/', views.process_payment) -> /payment/booking/{id}/process/
            
            # Xóa các nút chọn method cụ thể, dùng nút chung đến trang chọn phương thức
            keyboard = [
                [InlineKeyboardButton(
                    "💳 Chọn phương thức thanh toán", 
                    url=get_magic_link(f"/payment/booking/{booking_id}/payment/")
                )],
                [InlineKeyboardButton("📑 Xem chi tiết booking", url=get_magic_link(f"/booking/{booking_id}/"))],
                [InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_book")],
            ]

            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            await self._log_conversation(telegram_user, "bot", msg)
            return

        await self._reset_state_with_message_query(query, telegram_user, "Lựa chọn không hợp lệ. Gõ /menu để bắt đầu lại.")

    async def _ask_adults(self, target, tour_id: str, booking_date, via_message: bool = False):
        # target: callback query or message (for manual date case)
        keyboard = [
            [InlineKeyboardButton("1 người lớn", callback_data=f"bookadults_{tour_id}_{booking_date}_1")],
            [InlineKeyboardButton("2 người lớn", callback_data=f"bookadults_{tour_id}_{booking_date}_2")],
            [InlineKeyboardButton("3 người lớn", callback_data=f"bookadults_{tour_id}_{booking_date}_3")],
            [InlineKeyboardButton("✏️ Nhập số lượng khác", callback_data=f"bookadults_manual_{tour_id}_{booking_date}")],
            [InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_book")],
        ]
        msg = "Chọn số người lớn:"
        if via_message and hasattr(target, "reply_text"):
            await target.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await target.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        # Không log nhiều lần để tránh noise; log gọn
        # await self._log_conversation(telegram_user, "bot", msg)

    async def _ask_children(self, query, tour_id: str, booking_date: str, adults: int):
        keyboard = [
            [InlineKeyboardButton("0 trẻ em", callback_data=f"bookchildren_{tour_id}_{booking_date}_{adults}_0")],
            [InlineKeyboardButton("1 trẻ em", callback_data=f"bookchildren_{tour_id}_{booking_date}_{adults}_1")],
            [InlineKeyboardButton("2 trẻ em", callback_data=f"bookchildren_{tour_id}_{booking_date}_{adults}_2")],
            [InlineKeyboardButton("✏️ Nhập số lượng khác", callback_data=f"bookchildren_manual_{tour_id}_{booking_date}_{adults}")],
            [InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_book")],
        ]
        msg = "Chọn số trẻ em:"
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _reset_state_with_message_query(self, query, telegram_user: TelegramUser, message: str):
        telegram_user.conversation_state = ""
        await sync_to_async(telegram_user.save)()
        await query.edit_message_text(message)
        await self._log_conversation(telegram_user, "bot", message)

    async def send_main_menu(self, update: Update) -> None:
        keyboard = [
            [
                InlineKeyboardButton("📋 Xem tour", callback_data="menu_tours"),
            ],
            [
                InlineKeyboardButton("🔍 Tìm tour", callback_data="menu_search"),
                InlineKeyboardButton("📝 Đặt tour", callback_data="menu_book"),
            ],
            [
                InlineKeyboardButton("📑 Xem booking", callback_data="menu_view"),
                InlineKeyboardButton("🤖 Hỏi AI", callback_data="menu_ai"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.callback_query:
            await update.callback_query.edit_message_text("Chọn chức năng:", reply_markup=reply_markup)
        elif update.message:
            await update.message.reply_text("Chọn chức năng:", reply_markup=reply_markup)

    async def _get_or_create_user(self, update: Update):
        user = update.effective_user
        telegram_user, created = await sync_to_async(TelegramUser.objects.get_or_create)(
            telegram_id=user.id,
            defaults={
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        )

        if not created:
            telegram_user.username = user.username
            telegram_user.first_name = user.first_name
            telegram_user.last_name = user.last_name
            await sync_to_async(telegram_user.save)()
        await self._log_conversation(telegram_user, "user", update.effective_message.text if update.effective_message else "")
        return telegram_user

    async def _log_conversation(self, telegram_user: TelegramUser, message_type: str, text: str):
        if not text:
            return
        await sync_to_async(Conversation.objects.create)(
            telegram_user=telegram_user,
            message_type=message_type,
            message_text=text,
        )

    async def _get_or_create_site_user(self, telegram_user: TelegramUser):
        User = get_user_model()

        # Nếu đã liên kết sẵn
        if telegram_user.django_user_id:
            return await sync_to_async(User.objects.get)(id=telegram_user.django_user_id)

        username = f"tg_{telegram_user.telegram_id}"
        user, _ = await sync_to_async(User.objects.get_or_create)(
            username=username,
            defaults={
                "first_name": telegram_user.first_name or "",
                "last_name": telegram_user.last_name or "",
                "email": "",
            },
        )

        # Lưu liên kết để các booking sau dùng chung
        telegram_user.django_user = user
        await sync_to_async(telegram_user.save)()
        return user

    async def _reset_state_with_message(self, telegram_user: TelegramUser, update: Update, message: str):
        telegram_user.conversation_state = ""
        await sync_to_async(telegram_user.save)()
        await update.message.reply_text(message)
        await self._log_conversation(telegram_user, "bot", message)

    async def _show_bookings_list(self, update, telegram_user, query):
        """Helper to show user bookings"""
        try:
            # Get Django user linked to telegram user (async safe)
            django_user = await sync_to_async(lambda: telegram_user.django_user)()
            
            if not django_user:
                msg = (
                    "📋 **BOOKINGS CỦA BẠN**\n\n"
                    "Bạn chưa liên kết tài khoản VN Travel.\n"
                    "Vui lòng đăng ký/đăng nhập trên website để xem bookings.\n\n"
                    "🌐 https://vntravel.com"
                )
                keyboard = [[InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")]]
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
                await self._log_conversation(telegram_user, "bot", msg)
                return
            
            # Query user's bookings
            bookings = await sync_to_async(list)(
                Booking.objects.filter(user=django_user).select_related('tour').order_by('-created_at')[:10]
            )
            
            if not bookings:
                msg = (
                    "📋 **BOOKINGS CỦA BẠN**\n\n"
                    "Bạn chưa có booking nào.\n\n"
                    "Hãy đặt tour đầu tiên của bạn! 🎉"
                )
                keyboard = [
                    [InlineKeyboardButton("📝 Đặt tour ngay", callback_data="menu_book")],
                    [InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")]
                ]
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
                await self._log_conversation(telegram_user, "bot", msg)
                return
            
            # Display bookings list
            msg = "📋 **BOOKINGS CỦA BẠN**\n\n"
            keyboard = []
            
            for booking in bookings:
                # Use get_effective_status to sync with Web logic (check expiration)
                effective_status = 'pending'
                if hasattr(booking, 'get_effective_status'):
                    effective_status = await sync_to_async(booking.get_effective_status)()
                else:
                    effective_status = booking.status

                status_emoji = {
                    'pending': '⏳',
                    'confirmed': '✅',
                    'paid': '💳',
                    'partial_paid': '💸',
                    'cancelled': '❌'
                }.get(effective_status, '📋')
                
                status_text = {
                    'pending': 'Chờ xác nhận',
                    'confirmed': 'Đã xác nhận',
                    'paid': 'Đã thanh toán',
                    'partial_paid': 'Đã đặt cọc',
                    'cancelled': 'Đã hủy'
                }.get(effective_status, effective_status)
                
                msg += f"{status_emoji} **{booking.tour.name}**\n"
                msg += f"   📅 {booking.booking_date.strftime('%d/%m/%Y')}\n"
                msg += f"   👥 {booking.num_adults + booking.num_children} người\n"
                msg += f"   💰 {int(booking.total_price):,} VND\n"
                msg += f"   🔖 {status_text}\n\n"
                
                # Add button for each booking
                button_text = f"{booking.tour.name[:25]}... - {status_text}"
                callback_data = f"viewbooking_{booking.id}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            keyboard.append([InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")])
            
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            await self._log_conversation(telegram_user, "bot", "Hiển thị danh sách bookings")
            return
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in show_bookings_list: {e}")
            msg = "❌ Có lỗi xảy ra khi tải bookings. Vui lòng thử lại sau."
            keyboard = [[InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")]]
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            return