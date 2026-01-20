"""
Email utilities for VN Travel
Handles sending various types of emails (booking confirmation, payment receipts, etc.)
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_booking_confirmation_email(booking):
    """
    Send booking confirmation email to customer
    
    Args:
        booking: Booking instance
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Prepare context for email template
        context = {
            'booking': booking,
            'site_url': settings.SITE_URL,
        }
        
        # Render HTML content
        html_content = render_to_string('emails/booking_confirmation.html', context)
        
        # Prepare user data
        user = booking.user
        user_name = f"{user.last_name} {user.first_name}" if (user.last_name or user.first_name) else user.username
        user_email = user.email or 'noemail@vntravel.com'
        user_phone = user.profile.phone if hasattr(user, 'profile') and user.profile.phone else 'N/A'
        
        # Plain text fallback  
        text_content = f"""
Xin chào {user_name},

Cảm ơn bạn đã đặt tour tại VN Travel!

THÔNG TIN ĐẶT TOUR:
- Mã đặt tour: #{booking.id}
- Tour: {booking.tour.name}
- Điểm đến: {booking.tour.location}
- Ngày đặt: {booking.booking_date.strftime('%d/%m/%Y')}
- Số khách: {booking.num_adults} người lớn + {booking.num_children} trẻ em
- Tổng chi phí: {booking.total_price:,.0f} VNĐ

Để xem chi tiết và thanh toán, vui lòng truy cập:
{settings.SITE_URL}/bookings/{booking.id}/

Cảm ơn bạn đã tin tưởng VN Travel!

---
VN Travel Team
Email: dulich@vntravel.com
Hotline: +84 842190901
        """
        
        # Create email
        subject = f'✅ Xác nhận đặt tour #{booking.id} - {booking.tour.name}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user_email]
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email,
        )
        msg.attach_alternative(html_content, "text/html")
        
        # Send email
        try:
            msg.send()
            logger.info(f"Booking confirmation email sent successfully for booking #{booking.id}")
            return True
        except Exception as send_error:
            # Email send failed (common on Render due to SMTP blocking)
            logger.warning(f"Email send failed for booking #{booking.id}: {str(send_error)}")
            # Log email content for admin review
            logger.info(f"Email subject: {subject}")
            logger.info(f"Email to: {user_email}")
            logger.info(f"Booking details: Tour={booking.tour.name}, ID={booking.id}, Amount={booking.total_price}")
            # Return False but don't crash the booking
            return False
        
    except Exception as e:
        logger.error(f"Failed to prepare booking confirmation email for booking #{booking.id}: {str(e)}")
        return False


def send_payment_confirmation_email(payment):
    """
    Send payment confirmation emailto customer
    
    Args:
        payment: Payment instance
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        booking = payment.booking
        
        context = {
            'payment': payment,
            'booking': booking,
            'site_url': settings.SITE_URL,
        }
        
        # For now, use plain text (can create HTML template later)
        text_content = f"""
Xin chào {booking.user.last_name} {booking.user.first_name},

Chúng tôi đã nhận được thanh toán của bạn!

THÔNG TIN THANH TOÁN:
- Mã giao dịch: {payment.transaction_id or 'N/A'}
- Mã đặt tour: #{booking.id}
- Tour: {booking.tour.name}
- Số tiền: {payment.amount:,.0f} VNĐ
- Phương thức: {payment.get_payment_method_display()}
- Trạng thái: {payment.get_payment_status_display()}

Cảm ơn bạn đã thanh toán. Chúng tôi sẽ xác nhận và gửi thông tin chi tiết sớm nhất.

Để xem chi tiết, vui lòng truy cập:
{settings.SITE_URL}/bookings/{booking.id}/

---
VN Travel Team
        """
        
        subject = f'💳 Xác nhận thanh toán #{payment.id} - Tour {booking.tour.name}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [booking.contact_email]
        
        if booking.user.email and booking.user.email != booking.contact_email:
            to_email.append(booking.user.email)
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email,
        )
        
        msg.send()
        
        logger.info(f"Payment confirmation email sent successfully for payment #{payment.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment confirmation email for payment #{payment.id}: {str(e)}")
        return False
