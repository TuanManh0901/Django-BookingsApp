"""Models cho Payment/Thanh toán VN Travel."""
from django.conf import settings
from django.db import models

from bookings.models import Booking


class Payment(models.Model):
    """Model giao dịch thanh toán - hỗ trợ nhiều phương thức thanh toán."""
    
    PAYMENT_METHOD_CHOICES = [
        ('momo', 'MoMo'),
        ('qr', 'QR Code'),
        ('bank_transfer', 'Bank Transfer'),
        ('cod', 'Cash on Delivery'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending_payment', 'Chờ thanh toán'),
        ('deposit_paid', 'Đã cọc 50%'),
        ('paid_successfully', 'Đã thanh toán'),
        ('payment_failed', 'Thanh toán thất bại'),
        ('cancelled', 'Đã hủy'),
    ]

    MOMO_PAYMENT_TYPE_CHOICES = [
        ('ATM', 'Thẻ ATM'),
        ('CC', 'Thẻ Credit Card'),
        ('WALLET', 'Ví MoMo'),
        ('QR', 'QR Code'),
    ]

    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        default='momo'
    )
    status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending_payment'
    )

    # Các trường riêng cho MoMo
    transaction_ref = models.CharField(max_length=100, blank=True, null=True)
    momo_result_code = models.IntegerField(blank=True, null=True)
    momo_message = models.TextField(blank=True, null=True)
    momo_request_id = models.CharField(max_length=100, blank=True, null=True)
    momo_order_id = models.CharField(max_length=100, blank=True, null=True)
    momo_payment_type = models.CharField(
        max_length=10, 
        choices=MOMO_PAYMENT_TYPE_CHOICES, 
        default='ATM'
    )

    # Các trường cho thanh toán QR
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)

    # Thời gian
    payment_completed_at = models.DateTimeField(blank=True, null=True)
    payment_completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Payment {self.id} - {self.booking} - {self.amount}"