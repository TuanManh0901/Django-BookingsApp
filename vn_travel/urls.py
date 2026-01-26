"""
URL configuration for vn_travel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from tours.views import (
    home_view, SearchToursView, TourDetailView, admin_dashboard,
    vietnam_destinations_view, cambodia_destinations_view, laos_destinations_view,
    responsibility_view, about_us_view, education_view,
    about_view, contact_view, faq_view
)
from bookings.views import create_booking, MyBookingsView, BookingDetailView, cancel_booking, cancel_booking_ajax, pay_booking, submit_review
from .views import user_profile, register, edit_profile
from .health import health_check_view, readiness_check_view, liveness_check_view
from telegram_bot import views as telegram_views
# from .admin import admin_site  # Import custom admin site


urlpatterns = [
    # Language switcher (must be before i18n_patterns)
    path('i18n/', include('django.conf.urls.i18n')),
    
    # DevOps Health Checks
    path('health/', health_check_view, name='health_check'),
    path('ready/', readiness_check_view, name='readiness_check'),
    path('live/', liveness_check_view, name='liveness_check'),
    
    path("admin/", admin.site.urls),  # Use default admin site
    path('accounts/', include('allauth.urls')),
    path('register/', register, name='register'),
    path('profile/', user_profile, name='user_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    
    # Homepage & Search
    path('', home_view, name='home'),
    path('search/', SearchToursView.as_view(), name='search_tours'),
    path('tours/', SearchToursView.as_view(), name='tour_list'),  # Legacy redirect
    
    # Tours
    path('tour/<int:pk>/', TourDetailView.as_view(), name='tour_detail'),
    path('tour/<int:tour_id>/book/', create_booking, name='create_booking'),
    
    # Destinations
    path('destinations/vietnam/', vietnam_destinations_view, name='vietnam_destinations'),
    path('destinations/cambodia/', cambodia_destinations_view, name='cambodia_destinations'),
    path('destinations/laos/', laos_destinations_view, name='laos_destinations'),
    
    # Content Pages
    path('responsibility/', responsibility_view, name='responsibility'),
    path('about/', about_us_view, name='about_us'),
    path('education/', education_view, name='education'),
    
    # Additional Pages (legacy)
    path('contact/', contact_view, name='contact'),
    path('faq/', faq_view, name='faq'),

    
    # Bookings
    path('my-bookings/', MyBookingsView.as_view(), name='my_bookings'),
    path('booking/<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('booking/<int:pk>/cancel/', cancel_booking, name='cancel_booking'),
    path('bookings/<int:booking_id>/review/', submit_review, name='submit_review'),
    path('booking/<int:pk>/cancel-ajax/', cancel_booking_ajax, name='cancel_booking_ajax'),
    path('booking/<int:pk>/pay/', pay_booking, name='pay_booking'),
    # Aliases for legacy /bookings/... URLs
    path('bookings/my-bookings/', MyBookingsView.as_view(), name='my_bookings_legacy'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking_detail_legacy'),
    path('bookings/<int:pk>/cancel/', cancel_booking, name='cancel_booking_legacy'),
    path('bookings/<int:pk>/pay/', pay_booking, name='pay_booking_legacy'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('ai-chat/', include('ai_chatbot.urls')),
    path('payment/', include('payments.urls')),
    # Telegram Bot Webhook
    path('telegram/', include('telegram_bot.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
