from django.contrib import admin
from .models import Tour, TourImage, Review
from allauth.socialaccount.models import SocialApp, SocialToken, SocialAccount

from django.contrib.sites.models import Site

# Dọn dẹp Admin: Ẩn các model Social và Site không cần thiết
try:
    admin.site.unregister(SocialApp)
    admin.site.unregister(SocialToken)
    admin.site.unregister(Site) # Ẩn mục Sites
    # admin.site.unregister(SocialAccount) # Giữ lại cái này để quản lý user link
except admin.sites.NotRegistered:
    pass


class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main')

class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'display_price', 'duration', 'max_people', 'is_active', 'created_at')
    list_filter = ('location', 'is_active', 'created_at')
    search_fields = ('name', 'location', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [TourImageInline]
    
    def display_price(self, obj):
        """Format price as Vietnamese currency with dot separator"""
        if obj.price:
            formatted = "{:,}".format(int(obj.price)).replace(',', '.')
            return f"{formatted} VND"
        return "0 VND"
    display_price.short_description = "Giá"
    display_price.admin_order_field = "price"
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                actions['delete_selected'][0],
                'delete_selected',
                "Xóa tour đã chọn"
            )
        return actions
    
    actions = ['delete_selected']
    actions_on_top = True

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

admin.site.register(Tour, TourAdmin)
# TourImage registered in vn_travel/admin.py to appear in admin menu


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'rating', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_featured', 'created_at')
    search_fields = ('user__username', 'tour__name', 'comment')
    list_editable = ('is_featured',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                actions['delete_selected'][0],
                'delete_selected',
                "Xóa đánh giá đã chọn"
            )
        return actions

admin.site.register(Review, ReviewAdmin)
