from django.contrib import admin
from django.template.response import TemplateResponse
from .models import UserProfile
from django.contrib.auth.models import User, Group
from tours.models import Tour, TourImage
from bookings.models import Booking
from payments.models import Payment
from allauth.socialaccount.models import SocialApp, SocialToken, SocialAccount
from django.contrib.sites.models import Site

# Ẩn Group khỏi admin (không cần thiết cho project này)
admin.site.unregister(Group)


# Override admin index to include total_models count
original_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    """Custom admin index view that includes total model count and stats."""
    if extra_context is None:
        extra_context = {}
    
    # Get app_list from the original index
    response = original_index(request, extra_context=extra_context)
    
    # If it's a TemplateResponse, add total_models and stats to context
    if isinstance(response, TemplateResponse):
        app_list = response.context_data.get('app_list', [])
        total_models = sum(len(app.get('models', [])) for app in app_list)
        response.context_data['total_models'] = total_models
        
        # Add statistics
        try:
            from django.db.models import Sum
            from django.utils import timezone
            from datetime import datetime, timedelta
            import calendar
            
            total_tours = Tour.objects.count()
            active_tours = Tour.objects.filter(is_active=True).count()
            total_bookings = Booking.objects.count()
            confirmed_bookings = Booking.objects.filter(status='confirmed').count()
            pending_bookings = Booking.objects.filter(status='pending').count()
            cancelled_bookings = Booking.objects.filter(status='cancelled').count()
            total_payments = Payment.objects.count()
            paid_payments = Payment.objects.filter(status='paid_successfully').count()
            pending_payments = Payment.objects.filter(status='pending_payment').count()
            total_users = User.objects.count()
            
            # Tính tổng doanh thu từ các payment thành công
            total_revenue = Payment.objects.filter(
                status='paid_successfully'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Tính doanh thu theo 12 tháng gần nhất (tháng hiện tại trước, tháng cũ sau)
            monthly_revenue = []
            month_labels = []
            now = timezone.now()
            
            # Lấy 12 tháng gần nhất (từ tháng hiện tại lùi về: Jan, Dec, Nov, ..., Feb)
            for i in range(0, 12):  # 0, 1, 2, ..., 11
                # Tính tháng và năm (từ hiện tại lùi về)
                target_date = now - timedelta(days=i*30)  # Xấp xỉ
                month = target_date.month
                year = target_date.year
                
                # Ngày đầu tháng
                month_start = timezone.make_aware(datetime(year, month, 1, 0, 0, 0))
                
                # Ngày cuối tháng
                last_day = calendar.monthrange(year, month)[1]
                if month == now.month and year == now.year:
                    # Tháng hiện tại: lấy đến giờ
                    month_end = now
                else:
                    month_end = timezone.make_aware(datetime(year, month, last_day, 23, 59, 59))
                
                month_revenue = Payment.objects.filter(
                    status='paid_successfully',
                    created_at__gte=month_start,
                    created_at__lte=month_end
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                monthly_revenue.append(float(month_revenue))
                month_labels.append(month_start.strftime('%b'))
            
            # Tính số lượng booking theo 12 tháng gần nhất (tháng hiện tại trước, tháng cũ sau)
            monthly_bookings = []
            for i in range(0, 12):  # 0, 1, 2, ..., 11
                # Tính tháng và năm (từ hiện tại lùi về)
                target_date = now - timedelta(days=i*30)  # Xấp xỉ
                month = target_date.month
                year = target_date.year
                
                # Ngày đầu tháng
                month_start = timezone.make_aware(datetime(year, month, 1, 0, 0, 0))
                
                # Ngày cuối tháng
                last_day = calendar.monthrange(year, month)[1]
                if month == now.month and year == now.year:
                    # Tháng hiện tại: lấy đến giờ
                    month_end = now
                else:
                    month_end = timezone.make_aware(datetime(year, month, last_day, 23, 59, 59))
                
                month_count = Booking.objects.filter(
                    created_at__gte=month_start,
                    created_at__lte=month_end
                ).count()
                
                monthly_bookings.append(month_count)
            
            response.context_data['stats'] = {
                'tours': {
                    'total': total_tours,
                    'active': active_tours,
                    'inactive': total_tours - active_tours,
                },
                'bookings': {
                    'total': total_bookings,
                    'confirmed': confirmed_bookings,
                    'pending': pending_bookings,
                    'cancelled': cancelled_bookings,
                },
                'payments': {
                    'total': total_payments,
                    'paid': paid_payments,
                    'pending': pending_payments,
                    'failed': total_payments - paid_payments - pending_payments,
                },
                'users': total_users,
                'revenue': float(total_revenue),
                'monthly_data': {
                    'labels': month_labels,
                    'revenue': monthly_revenue,
                    'bookings': monthly_bookings,
                }
            }
            
            # Add monthly data to context as JSON for charts
            import json
            response.context_data['monthly_revenue_json'] = json.dumps({
                'labels': month_labels,
                'lineData': monthly_revenue,
                'barData': monthly_bookings,
            })
        except Exception as e:
            print(f"Error calculating stats: {e}")
            response.context_data['stats'] = {}
            response.context_data['monthly_revenue_json'] = '{}'
    
    return response

admin.site.index = custom_admin_index


from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Define an inline admin descriptor for UserProfile model
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Thông tin chi tiết (Hồ sơ)'
    fk_name = 'user'

# Gộp SocialAccount vào User admin luôn cho gọn
class SocialAccountInline(admin.StackedInline):
    model = SocialAccount
    can_delete = True
    verbose_name_plural = 'Tài khoản Mạng xã hội (Google/Facebook)'
    fk_name = 'user'
    extra = 0

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, SocialAccountInline) # Thêm SocialAccountInline vào đây
    list_display = ('username', 'email', 'get_phone', 'get_full_name', 'is_staff')
    
    def get_phone(self, instance):
        if hasattr(instance, 'userprofile'):
            return instance.userprofile.phone
        return None
    get_phone.short_description = 'Số điện thoại'
    
    def get_full_name(self, instance):
        if hasattr(instance, 'userprofile'):
            # Combine Django's first/last name or use profile data if available
            return f"{instance.last_name} {instance.first_name}".strip() or instance.username
        return instance.username
    get_full_name.short_description = 'Họ tên đầy đủ'

# Re-register UserAdmin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, UserAdmin)

# Dọn dẹp Admin: Ẩn các model Social và Site không cần thiết
try:
    admin.site.unregister(SocialApp)
    admin.site.unregister(SocialToken)
    admin.site.unregister(Site)
    admin.site.unregister(SocialAccount) # Ẩn luôn SocialAccount vì đã gộp vào User
except admin.sites.NotRegistered:
    pass

# Không cần đăng ký riêng UserProfile nữa vì đã gộp vào User
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     ...


# Register TourImage separately to show in menu
class TourImageAdmin(admin.ModelAdmin):
    list_display = ('tour', 'image', 'alt_text', 'is_main', 'created_at')
    list_filter = ('is_main', 'created_at')
    search_fields = ('tour__name', 'alt_text')
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                actions['delete_selected'][0],
                'delete_selected',
                "Xóa hình ảnh đã chọn"
            )
        return actions
    
    actions = ['delete_selected']
    actions_on_top = True

admin.site.register(TourImage, TourImageAdmin)
