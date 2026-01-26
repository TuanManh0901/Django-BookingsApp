from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('auth/<str:token>/', views.telegram_auto_login, name='telegram_auto_login'),
    path('connect/<str:token>/', views.telegram_connect, name='telegram_connect'),
]
