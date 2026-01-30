"""Models cho Booking/Đặt tour VN Travel."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from tours.models import Tour


# Hằng số: Thời gian hết hạn booking (phút)
BOOKING_EXPIRATION_MINUTES = 15


class Booking(models.Model):
    """Model đặt tour với theo dõi cọc và thanh toán."""
    
    STATUS_CHOICES = [
        ('pending', 'Đang chờ'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Đang chờ'),
        ('paid', 'Đã thanh toán'),
        ('refunded', 'Đã hoàn tiền'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    booking_date = models.DateField()
    num_adults = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending'
    )
    
    # Các trường liên quan đến cọc (deposit)
    deposit_required = models.BooleanField(default=False)
    deposit_percentage = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    deposit_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    deposit_paid = models.BooleanField(default=False)
    
    # Trường tùy chỉnh AI - lịch trình do AI thiết kế
    custom_itinerary = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Lịch trình AI Design"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Booking {self.id} - {self.user.username} - {self.tour.name}"
    
    def is_expired(self) -> bool:
        """Kiểm tra booking đã hết hạn chưa (>15 phút, pending, chưa cọc)."""
        if self.payment_status != 'pending':
            return False
        if self.deposit_paid:
            return False
            
        grace_period = timedelta(minutes=BOOKING_EXPIRATION_MINUTES)
        return timezone.now() - self.created_at > grace_period
    
    def get_effective_status(self) -> str:
        """Trả về trạng thái thực tế - kiểm tra hết hạn mỗi lần gọi (bỏ qua cache DB)."""
        if self.payment_status == 'cancelled':
            return 'cancelled'
        elif self.payment_status == 'paid':
            return 'paid'
        
        if self.is_expired():
            return 'cancelled'
        
        if self.deposit_paid and self.deposit_amount > 0:
            return 'partial_paid'
        
        return 'pending'
    
    def get_overall_status(self) -> str:
        """Trả về trạng thái tổng hợp dựa trên booking status và payment status."""
        if self.status == 'cancelled':
            return 'cancelled'
        elif self.payment_status == 'paid':
            return 'paid'
        elif self.deposit_paid and self.deposit_amount > 0:
            return 'partial_paid'
        return 'pending'
    
    def get_overall_status_display(self) -> str:
        """Trả về text hiển thị cho trạng thái tổng hợp."""
        deposit_pct = int(float(self.deposit_percentage) * 100) if self.deposit_percentage else 0
        status_map = {
            'pending': 'Đang chờ',
            'partial_paid': f'Đã cọc {deposit_pct}%',
            'paid': 'Đã thanh toán',
            'cancelled': 'Đã hủy'
        }
        return status_map.get(self.get_effective_status(), 'Unknown')

    def calculate_deposit(self) -> Decimal:
        """Tính số tiền cọc dựa trên % cọc và tổng giá."""
        try:
            pct = Decimal(self.deposit_percentage)
        except Exception:
            pct = Decimal('0')

        self.deposit_amount = (self.total_price * pct).quantize(Decimal('0.01'))
        return self.deposit_amount
    
    @property
    def deposit_percentage_display(self) -> int:
        """Trả về % cọc dưới dạng số nguyên (0.50 -> 50)."""
        return int(float(self.deposit_percentage) * 100) if self.deposit_percentage else 0
    
    def get_remaining_amount(self) -> Decimal:
        """Tính số tiền còn lại sau khi đã cọc."""
        if self.deposit_paid and self.deposit_amount > 0:
            return (self.total_price - self.deposit_amount).quantize(Decimal('0.01'))
        return self.total_price
    
    def get_display_total_price(self) -> Decimal:
        """Trả về số tiền cần thanh toán (số tiền còn lại nếu đã cọc)."""
        if self.deposit_paid and self.payment_status != 'paid':
            return self.get_remaining_amount()
        return self.total_price
    
    @classmethod
    def cancel_expired_bookings(cls) -> int:
        """Hủy tất cả booking hết hạn hàng loạt (pending, chưa cọc, >15 phút)."""
        grace_period = timedelta(minutes=BOOKING_EXPIRATION_MINUTES)
        cutoff_time = timezone.now() - grace_period
        
        expired_bookings = cls.objects.filter(
            payment_status='pending',
            deposit_paid=False,
            created_at__lt=cutoff_time
        ).exclude(status='cancelled')
        
        count = expired_bookings.count()
        if count > 0:
            expired_bookings.update(
                status='cancelled', 
                payment_status='cancelled',
                deposit_required=False,
                deposit_percentage=0,
                deposit_amount=0
            )
        return count
