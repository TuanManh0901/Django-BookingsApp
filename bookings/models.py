from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from tours.models import Tour

class Booking(models.Model):
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
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    # Deposit fields
    deposit_required = models.BooleanField(default=False)
    deposit_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    deposit_paid = models.BooleanField(default=False)
    
    # AI Custom Field
    custom_itinerary = models.TextField(blank=True, null=True, verbose_name="Lịch trình AI Design")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Booking {self.id} - {self.user.username} - {self.tour.name}"
    
    def is_expired(self):
        """Check if booking has expired (> 15 minutes old, pending, no deposit)"""
        from django.utils import timezone
        from datetime import timedelta
        
        if self.payment_status != 'pending':
            return False
        if self.deposit_paid:
            return False
            
        grace_period = timedelta(minutes=15)
        return timezone.now() - self.created_at > grace_period
    
    def get_effective_status(self):
        """
        Return REAL-TIME status - checks expiration every time called
        This bypasses database field to solve browser cache issues
        """
        # First check database payment_status
        if self.payment_status == 'cancelled':
            return 'cancelled'
        elif self.payment_status == 'paid':
            return 'paid'
        
        # If pending, check if expired
        if self.is_expired():
            return 'cancelled'
        
        # Check deposit status
        if self.deposit_paid and self.deposit_amount > 0:
            return 'partial_paid'
        
        return 'pending'
    
    def get_overall_status(self):
        """Trả về status tổng hợp dựa trên booking status và payment status"""
        if self.status == 'cancelled':
            return 'cancelled'
        elif self.payment_status == 'paid':
            return 'paid'
        elif self.deposit_paid and self.deposit_amount > 0:
            return 'partial_paid'
        else:
            return 'pending'
    
    def get_overall_status_display(self):
        """Trả về display text cho status tổng hợp"""
        # Convert deposit_percentage to integer percentage (0.50 -> 50)
        deposit_pct = int(float(self.deposit_percentage) * 100) if self.deposit_percentage else 0
        status_map = {
            'pending': 'Đang chờ',
            'partial_paid': f'Đã cọc {deposit_pct}%',
            'paid': 'Đã thanh toán',
            'cancelled': 'Đã hủy'
        }
        return status_map.get(self.get_effective_status(), 'Unknown')

    def calculate_deposit(self):
        """Tính deposit_amount dựa trên deposit_percentage và total_price"""
        try:
            pct = Decimal(self.deposit_percentage)
        except Exception:
            pct = Decimal('0')

        self.deposit_amount = (self.total_price * pct).quantize(Decimal('0.01'))
        return self.deposit_amount
    
    @property
    def deposit_percentage_display(self):
        """Trả về deposit_percentage dưới dạng số nguyên (0.50 -> 50)"""
        return int(float(self.deposit_percentage) * 100) if self.deposit_percentage else 0
    
    def get_remaining_amount(self):
        """Tính số tiền còn lại sau khi đã cọc"""
        if self.deposit_paid and self.deposit_amount > 0:
            return (self.total_price - self.deposit_amount).quantize(Decimal('0.01'))
        return self.total_price
    
    def get_display_total_price(self):
        """Trả về số tiền cần thanh toán (nếu đã cọc thì trả về số tiền còn lại)"""
        if self.deposit_paid and self.payment_status != 'paid':
            return self.get_remaining_amount()
        return self.total_price
    
    @classmethod
    def cancel_expired_bookings(cls):
        """
        Class method to cancel all expired bookings in bulk.
        Logic: Cancel if pending, no deposit, and created > 15 mins ago.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        grace_period = timedelta(minutes=15)
        cutoff_time = timezone.now() - grace_period
        
        expired_bookings = cls.objects.filter(
            payment_status='pending',
            deposit_paid=False,
            created_at__lt=cutoff_time
        ).exclude(status='cancelled')
        
        count = expired_bookings.count()
        if count > 0:
            # We use update() for bulk efficiency, but if we need signals, loop is better.
            # Here fast cleanup is prioritized.
            expired_bookings.update(
                status='cancelled', 
                payment_status='cancelled',
                deposit_required=False,
                deposit_percentage=0,
                deposit_amount=0
            )
        return count

    class Meta:
        ordering = ['-created_at']
