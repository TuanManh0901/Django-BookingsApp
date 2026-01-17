from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.decorators import action
from .models import Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'tour', 'booking_date', 'num_adults', 'num_children', 'display_total_price', 'display_status', 'deposit_info', 'created_at']
    list_filter = ['status', 'payment_status', 'deposit_paid', 'booking_date', 'created_at']
    search_fields = ['user__username', 'tour__name', 'id']
    readonly_fields = ['created_at', 'updated_at']
    
    def display_total_price(self, obj):
        """Format total price with Vietnamese dot separator"""
        if obj.total_price:
            formatted = "{:,}".format(int(obj.total_price)).replace(',', '.')
            return f"{formatted} VND"
        return "0 VND"
    display_total_price.short_description = "Tổng tiền"
    display_total_price.admin_order_field = "total_price"
    
    def display_status(self, obj):
        """Hiển thị trạng thái tổng hợp"""
        return obj.get_overall_status_display()
    display_status.short_description = "Trạng thái"
    
    def deposit_info(self, obj):
        """Hiển thị thông tin cọc với Vietnamese format"""
        if obj.deposit_paid and obj.deposit_amount > 0:
            formatted = "{:,}".format(int(obj.deposit_amount)).replace(',', '.')
            return f"Đã cọc: {formatted} VND"
        elif obj.deposit_required and obj.deposit_amount > 0:
            formatted = "{:,}".format(int(obj.deposit_amount)).replace(',', '.')
            return f"Cần cọc: {formatted} VND"
        return "Không cần cọc"
    deposit_info.short_description = "Thông tin cọc"
    
    def cancel_bookings(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"Đã hủy {queryset.count()} booking.")
    cancel_bookings.short_description = "Hủy booking đã chọn"
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                actions['delete_selected'][0],
                'delete_selected',
                "Xóa booking đã chọn"
            )
        return actions
    
    actions = [cancel_bookings, 'delete_selected']
    actions_on_top = True

admin.site.register(Booking, BookingAdmin)
