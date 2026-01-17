from django.contrib import admin
from .models import ChatMessage

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'message', 'timestamp', 'is_ai_response']
    list_filter = ['is_ai_response', 'timestamp']
    search_fields = ['user__username', 'session_id', 'message']
    readonly_fields = ['timestamp']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                actions['delete_selected'][0],
                'delete_selected',
                "Xóa tin nhắn đã chọn"
            )
        return actions
    
    actions = ['delete_selected']
    actions_on_top = True

admin.site.register(ChatMessage, ChatMessageAdmin)
