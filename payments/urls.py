from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('booking/<int:booking_id>/payment/', views.select_payment_method, name='select_payment_method'),
    path('booking/<int:booking_id>/pay-deposit/', views.pay_deposit, name='pay_deposit'),
    path('booking/<int:booking_id>/process/', views.process_payment, name='process_payment'),
    path('booking/<int:booking_id>/payment/qr/', views.initiate_qr_payment, name='initiate_qr_payment'),
    path('momo/callback/', views.momo_callback, name='momo_callback'),
    path('momo/ipn/', views.momo_ipn, name='momo_ipn'),
    path('payment/<int:payment_id>/upload-receipt/', views.upload_qr_receipt, name='upload_qr_receipt'),
    # Argon dashboard styled payments management (staff only)
    path('admin/payments/', views.argon_payments_dashboard, name='argon_payments_dashboard'),
    path('admin/payments/bulk-delete/', views.argon_payments_bulk_delete, name='argon_payments_bulk_delete'),
]