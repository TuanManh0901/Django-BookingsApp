from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'user', 'display_amount', 'method', 'status', 'receipt_preview', 'transaction_ref', 'created_at']
    list_filter = ['method', 'status', 'created_at']
    search_fields = ['booking__id', 'transaction_ref', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'receipt_preview_large']
    
    def display_amount(self, obj):
        """Format amount with Vietnamese dot separator"""
        if obj.amount:
            formatted = "{:,}".format(int(obj.amount)).replace(',', '.')
            return f"{formatted} VND"
        return "0 VND"
    display_amount.short_description = "Số tiền"
    display_amount.admin_order_field = "amount"
    
    fieldsets = (
        ('Thông tin thanh toán', {
            'fields': ('booking', 'user', 'amount', 'method', 'status')
        }),
        ('MoMo', {
            'fields': ('transaction_ref', 'momo_result_code', 'momo_message', 'momo_request_id', 'momo_order_id', 'momo_payment_type'),
            'classes': ('collapse',)
        }),
        ('QR/Chuyển khoản', {
            'fields': ('receipt_image', 'receipt_preview_large')
        }),
        ('Thời gian', {
            'fields': ('payment_completed_at', 'created_at', 'updated_at')
        }),
    )
    
    def receipt_preview(self, obj):
        """Hiển thị ảnh QR nhỏ trong danh sách"""
        if obj.receipt_image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" /></a>',
                obj.receipt_image.url,
                obj.receipt_image.url
            )
        return "Chưa có"
    receipt_preview.short_description = "Ảnh QR"
    
    def receipt_preview_large(self, obj):
        """Hiển thị ảnh QR lớn trong chi tiết"""
        if obj.receipt_image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 400px; max-height: 600px; border-radius: 8px; border: 2px solid #ddd;" /></a>',
                obj.receipt_image.url,
                obj.receipt_image.url
            )
        return "Chưa có ảnh"
    receipt_preview_large.short_description = "Ảnh chuyển khoản"
    
    def approve_payments(self, request, queryset):
        """Xác nhận thanh toán thành công"""
        count = 0
        for payment in queryset:
            # Kiểm tra: Payment method là 'qr' thì LUÔN là cọc 50%
            is_qr_payment = (payment.method == 'qr')
            
            if is_qr_payment:
                # QR Code -> Thanh toán cọc 50%
                if payment.status != 'deposit_paid':
                    payment.status = 'deposit_paid'
                    payment.payment_completed_at = timezone.now()
                    payment.save()
                    
                    # Update booking: set deposit_paid và deposit_percentage = 50%
                    booking = payment.booking
                    booking.deposit_paid = True
                    booking.deposit_required = True
                    booking.deposit_percentage = 0.50
                    booking.calculate_deposit()
                    booking.save()
                    count += 1
            else:
                # MoMo và các phương thức khác -> Thanh toán toàn bộ
                if payment.status != 'paid_successfully':
                    payment.status = 'paid_successfully'
                    payment.payment_completed_at = timezone.now()
                    payment.save()
                    
                    booking = payment.booking
                    if booking.deposit_required and not booking.deposit_paid:
                        # Đang thanh toán cọc
                        booking.deposit_paid = True
                        if payment.amount >= booking.total_price:
                            booking.payment_status = 'paid'
                        booking.save()
                    elif booking.deposit_paid and booking.payment_status != 'paid':
                        # Đã cọc rồi, đang thanh toán phần còn lại
                        booking.payment_status = 'paid'
                        booking.save()
                    else:
                        # Thanh toán đầy đủ 1 lần
                        booking.payment_status = 'paid'
                        booking.save()
                    count += 1
        
        self.message_user(request, f"Đã xác nhận {count} thanh toán thành công.")
    approve_payments.short_description = "Xác nhận thanh toán đã chọn"
    
    def reject_payments(self, request, queryset):
        """Từ chối thanh toán"""
        queryset.update(status='payment_failed')
        self.message_user(request, f"Đã từ chối {queryset.count()} thanh toán.")
    reject_payments.short_description = "Từ chối thanh toán đã chọn"
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                actions['delete_selected'][0],
                'delete_selected',
                "Xóa payment đã chọn"
            )
        return actions
    
    actions = [approve_payments, reject_payments, 'delete_selected']
    actions_on_top = True

admin.site.register(Payment, PaymentAdmin)
