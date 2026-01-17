from django.contrib import admin
from .models import TelegramUser, Conversation

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'username', 'first_name', 'last_name', 'django_user', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    readonly_fields = ['telegram_id', 'created_at', 'updated_at']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                actions['delete_selected'][0],
                'delete_selected',
                "Xóa người dùng Telegram đã chọn"
            )
        return actions
    
    actions = ['delete_selected']
    actions_on_top = True
    
    fieldsets = (
        ('Thông tin Telegram', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name', 'django_user')
        }),
        ('Trạng thái', {
            'fields': ('conversation_state', 'is_active')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['telegram_user', 'message_type', 'short_text', 'created_at']
    list_filter = ['message_type', 'created_at']
    search_fields = ['message_text', 'telegram_user__username', 'telegram_user__telegram_id']
    readonly_fields = ['telegram_user', 'message_type', 'message_text', 'created_at']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                actions['delete_selected'][0],
                'delete_selected',
                "Xóa cuộc trò chuyện đã chọn"
            )
        return actions
    
    actions = ['delete_selected']
    actions_on_top = True

    def short_text(self, obj):
        return obj.message_text[:50]
    short_text.short_description = "Nội dung"
