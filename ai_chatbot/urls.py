from django.urls import path
from . import views

app_name = 'ai_chatbot'

urlpatterns = [
    path('', views.ai_chat_view, name='chat'),
    path('api/chat/', views.ai_chat_api, name='chat_api'),
    path('api/chat/history/', views.chat_history_api, name='chat_history_api'),
    path('api/sessions/', views.chat_sessions_list_api, name='chat_sessions_list_api'),
    path('api/sessions/delete/', views.delete_session_api, name='delete_session_api'),
]