from django.core.management.base import BaseCommand
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
        application.add_handler(CallbackQueryHandler(self.handle_menu, pattern=r"^menu_"))
        application.add_handler(CallbackQueryHandler(self.handle_tour_detail, pattern=r"^tour_"))
        application.add_handler(CallbackQueryHandler(self.handle_book_init, pattern=r"^book_"))
        application.add_handler(CallbackQueryHandler(self.handle_booking_callback, pattern=r"^(bookdate_|bookadults_|bookchildren_)"))
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
            message += f"💰 Giá: {tour.price:,} VND\n"
            message += f"📅 Thời gian: {tour.duration} ngày\n"
            message += f"🌍 Địa điểm: {tour.location}\n"
            message += f"📝 {tour.description[:100]}...\n\n"

        message += "Để đặt tour, sử dụng lệnh /book"
        await update.message.reply_text(message, parse_mode='Markdown')
        await self._log_conversation(telegram_user, "bot", "Gửi danh sách tours")

    async def book_tour(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle tour booking request."""
        telegram_user = await self._get_or_create_user(update)
        await update.message.reply_text(
            "📝 **Đặt Tour Du Lịch**\n\n"
            "Để đặt tour, vui lòng truy cập website VN Travel:\n"
            "🌐 http://127.0.0.1:8000\n\n"
            "Hoặc liên hệ hotline: 1900-xxxx\n\n"
            "Chúng tôi sẽ hỗ trợ bạn đặt tour nhanh nhất có thể! 🚀"
        )
        await self._log_conversation(telegram_user, "bot", "Hướng dẫn đặt tour qua web")

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        telegram_user = await self._get_or_create_user(update)
        await self.send_main_menu(update)
        await self._log_conversation(telegram_user, "bot", "Hiển thị menu chính")

    async def handle_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        telegram_user = await self._get_or_create_user(update)

        data = query.data

        if data == "menu_search":
            telegram_user.conversation_state = "searching"
            await sync_to_async(telegram_user.save)()
            prompt = "Bạn muốn đi đâu? Nhập tên điểm đến (ví dụ: Đà Nẵng, Đà Lạt)."
            await query.edit_message_text(prompt)
            await self._log_conversation(telegram_user, "bot", prompt)
            return

        # Reset state for other menu actions
        telegram_user.conversation_state = ""
        await sync_to_async(telegram_user.save)()

        if data == "menu_tours":
            # Hiển thị tất cả tours
            tours = await sync_to_async(list)(Tour.objects.filter(is_active=True)[:10])
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
                msg += f"   💰 {tour.price:,} VND\n"
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
            tours = await sync_to_async(list)(Tour.objects.filter(is_active=True)[:5])
            if not tours:
                msg = "Hiện chưa có tour để đặt."
                await query.edit_message_text(msg)
                await self._log_conversation(telegram_user, "bot", msg)
                return

            keyboard = [
                [InlineKeyboardButton(f"{tour.name} • {tour.price:,} VND", callback_data=f"tour_{tour.id}")]
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
            # Xem bookings của user
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
                    status_emoji = {
                        'pending': '⏳',
                        'confirmed': '✅',
                        'paid': '💳',
                        'cancelled': '❌'
                    }.get(booking.status, '📋')
                    
                    status_text = {
                        'pending': 'Chờ xác nhận',
                        'confirmed': 'Đã xác nhận',
                        'paid': 'Đã thanh toán',
                        'cancelled': 'Đã hủy'
                    }.get(booking.status, booking.status)
                    
                    msg += f"{status_emoji} **{booking.tour.name}**\n"
                    msg += f"   📅 {booking.booking_date.strftime('%d/%m/%Y')}\n"
                    msg += f"   👥 {booking.num_adults + booking.num_children} người\n"
                    msg += f"   💰 {booking.total_price:,} VND\n"
                    msg += f"   🔖 {status_text}\n\n"
                    
                    # Add button for each booking
                    button_text = f"{booking.tour.name[:25]}... - {status_text}"
                    keyboard.append([InlineKeyboardButton(button_text, callback_data=f"viewbooking_{booking.id}")])
                
                keyboard.append([InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")])
                
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
                await self._log_conversation(telegram_user, "bot", "Hiển thị danh sách bookings")
                return
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in menu_view: {e}")
                msg = "❌ Có lỗi xảy ra khi tải bookings. Vui lòng thử lại sau."
                keyboard = [[InlineKeyboardButton("⬅️ Quay lại menu", callback_data="menu_back")]]
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
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
                "Hãy hỏi tôi bất cứ điều gì! 😊\n"
                "(Gõ /menu để quay lại)"
            )
            await query.edit_message_text(msg, parse_mode='Markdown')
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
                [InlineKeyboardButton(f"{tour.name} • {tour.price:,} VND", callback_data=f"tour_{tour.id}")]
                for tour in tours
            ]
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
            
            try:
                # Khởi tạo AI advisor
                advisor = TravelAdvisor()
                
                # Lấy câu trả lời từ AI
                ai_response = await sync_to_async(advisor.get_advice)(text, include_tours=True)
                
                # Gửi câu trả lời (plain text, không parse Markdown để tránh lỗi)
                response_msg = f"🤖 AI Travel Advisor:\n\n{ai_response}"
                
                # Split message nếu quá dài (Telegram limit 4096 chars)
                if len(response_msg) > 4000:
                    # Gửi phần đầu
                    await update.message.reply_text(response_msg[:4000])
                    # Gửi phần còn lại
                    await update.message.reply_text(response_msg[4000:])
                else:
                    await update.message.reply_text(response_msg)
                
                # Log conversation
                await self._log_conversation(telegram_user, "user", text)
                await self._log_conversation(telegram_user, "bot", ai_response)
                
                # Gửi suggestion
                suggestion = "\n\n💡 Bạn có câu hỏi khác không? Hoặc gõ /menu để quay lại."
                await update.message.reply_text(suggestion)
                
            except Exception as e:
                error_msg = (
                    f"⚠️ Xin lỗi, đã có lỗi xảy ra: {str(e)}\n\n"
                    "Vui lòng thử lại hoặc gõ /menu để quay lại."
                )
                await update.message.reply_text(error_msg)
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
            f"Giá: {tour.price:,} VND\n"
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
                msg = "Nhập ngày khởi hành (YYYY-MM-DD), ví dụ 2025-12-31."
                await query.edit_message_text(msg)
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

            msg = (
                f"✅ Đặt tour thành công!\n\n"
                f"📍 Tour: {tour.name}\n"
                f"📅 Ngày: {booking_date_obj}\n"
                f"👥 Người lớn: {int_adults}, Trẻ em: {int_children}\n"
                f"💰 Tổng tiền: {total_price:,} VND\n\n"
                f"🔗 Mã booking: #{booking_id}\n\n"
                "Vui lòng chọn phương thức thanh toán bên dưới:"
            )

            # Keyboard thanh toán
            from django.conf import settings
            base_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
            keyboard = [
                [InlineKeyboardButton(
                    "💳 Thanh toán MoMo", 
                    url=f"{base_url}/payments/process/{booking_id}/?method=momo"
                )],
                [InlineKeyboardButton(
                    "📱 Thanh toán QR Code", 
                    url=f"{base_url}/payments/process/{booking_id}/?method=qr"
                )],
                [InlineKeyboardButton(
                    "💵 Thanh toán khi nhận tour (COD)", 
                    url=f"{base_url}/payments/process/{booking_id}/?method=cod"
                )],
                [InlineKeyboardButton("📑 Xem chi tiết booking", url=f"{base_url}/bookings/{booking_id}/")],
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
            [InlineKeyboardButton("4 người lớn", callback_data=f"bookadults_{tour_id}_{booking_date}_4")],
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
            [InlineKeyboardButton("3 trẻ em", callback_data=f"bookchildren_{tour_id}_{booking_date}_{adults}_3")],
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