from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import requests
import hashlib
import hmac
import json
import uuid
import time
import base64
import logging
from datetime import date
from decimal import Decimal
from .models import Payment
from bookings.models import Booking
from tours.models import Tour

logger = logging.getLogger(__name__)

# MoMo credentials from settings (.env)

@login_required
def select_payment_method(request, booking_id):
    """Trang chọn phương thức thanh toán"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

    # Kiểm tra trạng thái thanh toán
    if booking.payment_status == 'paid':
        messages.info(request, "Đơn đặt tour này đã được thanh toán.")
        return redirect('booking_detail', pk=booking.pk)

    return render(request, 'payments/select_method.html', {
        'booking': booking
    })


@login_required
def pay_deposit(request, booking_id):
    """Trang yêu cầu thanh toán cọc sau khi chọn COD"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

    if booking.payment_status == 'paid':
        messages.info(request, "Đơn đặt tour này đã được thanh toán.")
        return redirect('booking_detail', pk=booking.pk)

    if not booking.deposit_required:
        messages.error(request, "Đơn này không yêu cầu cọc.")
        return redirect('payments:select_payment_method', booking_id=booking_id)

    # Tạo hoặc lấy Payment record cho cọc QR (nếu chưa có hoặc chưa paid)
    payment = Payment.objects.filter(
        booking=booking,
        method='qr',
        status__in=['pending_payment', 'deposit_paid']
    ).first()
    
    if not payment:
        payment = Payment.objects.create(
            booking=booking,
            user=request.user,
            amount=booking.deposit_amount,
            method='qr',
            status='pending_payment'
        )

    return render(request, 'payments/pay_deposit.html', {
        'booking': booking,
        'payment': payment
    })

@login_required
def process_payment(request, booking_id):
    """Xử lý thanh toán từ form"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

    if request.method != 'POST':
        return redirect('payments:select_payment_method', booking_id=booking_id)

    payment_method = request.POST.get('payment_method')
    momo_payment_type = request.POST.get('momo_payment_type', 'ATM')

    # Xử lý theo phương thức
    if payment_method == 'momo':
        paying_deposit_only = request.POST.get('deposit_only') == '1'
        if paying_deposit_only and booking.deposit_required and not booking.deposit_paid:
            amount_to_pay = booking.deposit_amount
        elif booking.deposit_paid and booking.payment_status != 'paid':
            # Đã cọc rồi, chỉ thanh toán số tiền còn lại
            amount_to_pay = booking.get_remaining_amount()
        else:
            amount_to_pay = booking.total_price
        payment = Payment.objects.create(
            booking=booking,
            user=request.user,
            amount=amount_to_pay,
            method='momo',
            status='pending_payment',
            momo_payment_type=momo_payment_type
        )
        return redirect_to_momo(request, payment, momo_payment_type)

    elif payment_method == 'cod':
        # COD - yêu cầu cọc 50% (deposit) và chuyển người dùng quay lại trang chọn phương thức để thanh toán cọc qua MoMo/QR
        booking.deposit_required = True
        booking.deposit_percentage = Decimal('0.50')
        booking.calculate_deposit()
        booking.deposit_paid = False
        booking.payment_status = 'pending'
        booking.save()

        return redirect('payments:pay_deposit', booking_id=booking.pk)
    else:
        messages.error(request, 'Phương thức thanh toán không hợp lệ.')
        return redirect('payments:select_payment_method', booking_id=booking_id)

@login_required
def initiate_qr_payment(request, booking_id):
    """Khởi tạo thanh toán QR"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

    if booking.payment_status == 'paid':
        messages.info(request, "Đơn đặt tour này đã được thanh toán.")
        return redirect('booking_detail', pk=booking.pk)

    paying_deposit_only = request.POST.get('deposit_only') == '1'
    if paying_deposit_only and booking.deposit_required and not booking.deposit_paid:
        amount_to_pay = booking.deposit_amount
    elif booking.deposit_paid and booking.payment_status != 'paid':
        # Đã cọc rồi, chỉ thanh toán số tiền còn lại
        amount_to_pay = booking.get_remaining_amount()
    else:
        amount_to_pay = booking.total_price

    # Tạo Payment record
    payment = Payment.objects.create(
        booking=booking,
        user=request.user,
        amount=amount_to_pay,
        method='qr',
        status='pending_payment'
    )

    return render(request, 'payments/qr_payment.html', {
        'payment': payment,
        'booking': booking
    })

def redirect_to_momo(request, payment, payment_method='ATM'):
    """Tạo giao dịch MoMo và chuyển hướng - GIỐNG HỆT LARAVEL"""
    
    # ===== MOCK MODE FOR DEV =====
    if getattr(settings, 'MOMO_MOCK_ENABLED', False):
        logger.info(f"🎭 MOCK MODE: Processing payment {payment.id}")
        payment.momo_order_id = f"mock_{int(time.time())}_{payment.id}"
        payment.momo_request_id = str(uuid.uuid4())
        payment.status = 'paid_successfully'
        payment.payment_completed_at = timezone.now()
        payment.save()
        
        # Update booking
        b = payment.booking
        if b.deposit_required and not b.deposit_paid:
            b.deposit_paid = True
            if payment.amount >= b.total_price:
                b.payment_status = 'paid'
            b.save()
        elif b.deposit_paid and b.payment_status != 'paid':
            b.payment_status = 'paid'
            b.save()
        else:
            b.payment_status = 'paid'
            b.save()
        
        messages.success(request, "✅ [Mock Mode] Thanh toán thành công!")
        return redirect('booking_detail', pk=payment.booking.id)
    
    # ===== REAL MOMO API - GIỐNG CHÍNH XÁC LARAVEL =====
    booking = payment.booking
    
    # Base URL giống Laravel: config('app.url')
    base_url = settings.SITE_URL
    redirect_url = base_url + reverse('payments:momo_callback')
    ipn_url = base_url + reverse('payments:momo_ipn')
    
    # Order ID giống Laravel: time() . '_' . $order->id
    order_id = str(int(time.time())) + '_' + str(payment.id)
    
    # Request ID giống Laravel: uniqid() (13 chars hex)
    # PHP uniqid() = 13 chars hex based on microtime
    request_id = format(int(time.time() * 1000000) % 0x1000000000000, '013x')
    
    # Order info giống Laravel
    order_info = f"Thanh toán đơn hàng #{booking.id}"
    
    # Amount giống Laravel: (string) max(10000, (int) $order->total_price)
    amount = str(max(10000, int(payment.amount)))
    
    # Extra data giống Laravel: base64_encode(json_encode(['order_id' => $order->id]))
    extra_data = base64.b64encode(
        json.dumps({'order_id': booking.id}, separators=(',', ':')).encode()
    ).decode()
    
    # Request type giống Laravel
    request_type = get_momo_request_type(payment_method)
    
    # Raw signature GIỐNG CHÍNH XÁC LARAVEL (không có khoảng trắng)
    raw_signature = (
        f"accessKey={settings.MOMO_ACCESS_KEY}&"
        f"amount={amount}&"
        f"extraData={extra_data}&"
        f"ipnUrl={ipn_url}&"
        f"orderId={order_id}&"
        f"orderInfo={order_info}&"
        f"partnerCode={settings.MOMO_PARTNER_CODE}&"
        f"redirectUrl={redirect_url}&"
        f"requestId={request_id}&"
        f"requestType={request_type}"
    )
    
    signature = hmac.new(
        settings.MOMO_SECRET_KEY.encode('utf-8'),
        raw_signature.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Payload GIỐNG HỆT LARAVEL
    payload = {
        'partnerCode': settings.MOMO_PARTNER_CODE,
        'partnerName': 'YourStore',  # Giống Laravel
        'storeId': 'Store_01',  # Giống Laravel
        'requestId': request_id,
        'amount': amount,
        'orderId': order_id,
        'orderInfo': order_info,
        'redirectUrl': redirect_url,
        'ipnUrl': ipn_url,
        'lang': 'vi',
        'extraData': extra_data,
        'requestType': request_type,
        'signature': signature
    }

    logger.info(f"=== MoMo Payment Request (Laravel Style) ===")
    logger.info(f"Partner Code: {settings.MOMO_PARTNER_CODE}")
    logger.info(f"Order ID: {order_id}")
    logger.info(f"Amount: {amount}")
    logger.info(f"Request Type: {request_type}")
    logger.info(f"Raw Signature String:\n{raw_signature}")
    logger.info(f"Signature: {signature}")
    logger.info(f"Payload: {json.dumps(payload, indent=2)}")
    logger.info(f"==============================")

    try:
        headers = {
            'Content-Type': 'application/json; charset=UTF-8'  # Giống Laravel
        }
        response = requests.post(
            settings.MOMO_ENDPOINT, 
            json=payload, 
            headers=headers, 
            timeout=30,
            verify=True  # Giống Laravel withoutVerifying() nhưng safer
        )
        
        logger.info(f"MoMo Response Status: {response.status_code}")
        logger.info(f"MoMo Response: {response.text[:1000]}")

        if response.status_code == 200:
            try:
                response_data = response.json()
                result_code = response_data.get('resultCode')
                
                if result_code == 0 and response_data.get('payUrl'):
                    pay_url = response_data['payUrl']
                    # Lưu thông tin giống Laravel
                    payment.momo_request_id = request_id
                    payment.momo_order_id = order_id
                    payment.transaction_ref = order_id
                    payment.save()
                    logger.info(f"MoMo payment URL created: {pay_url}")
                    return redirect(pay_url)

                # Lỗi từ MoMo - message rõ ràng
                error_message = response_data.get('message', 'MoMo không trả về payUrl')
                payment.status = 'payment_failed'
                payment.momo_result_code = result_code
                payment.momo_message = error_message
                payment.save()
                logger.error(f"MoMo Error: resultCode={result_code}, message={error_message}")
                messages.error(request, f"Không tạo được link thanh toán MoMo: {error_message}")
                return redirect('booking_detail', pk=payment.booking.id)

            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Cannot parse MoMo response: {response.text}, error: {e}")
                messages.error(request, f"Lỗi phản hồi từ MoMo không hợp lệ")
                return redirect('booking_detail', pk=payment.booking.id)

        # HTTP error giống Laravel
        error_text = response.text[:500]
        payment.status = 'payment_failed'
        payment.momo_message = f"HTTP {response.status_code}"
        payment.save()
        logger.error(f"MoMo HTTP Error {response.status_code}: {error_text}")
        messages.error(request, f"Không thể kết nối MoMo ({response.status_code}). Vui lòng thử lại.")
        return redirect('booking_detail', pk=payment.booking.id)

    except Exception as e:
        payment.status = 'payment_failed'
        payment.momo_message = str(e)
        payment.save()
        logger.exception(f"MoMo request exception: {e}")
        messages.error(request, f"Lỗi khi tạo thanh toán MoMo: {str(e)}")
        return redirect('booking_detail', pk=payment.booking.id)


def get_momo_request_type(payment_method):
    """Xác định loại request MoMo - GIỐNG HỆT LARAVEL"""
    payment_method_upper = payment_method.upper()
    
    if payment_method_upper == 'ATM':
        return 'payWithATM'
    elif payment_method_upper in ['CC', 'CREDIT_CARD']:
        return 'payWithCC'
    elif payment_method_upper in ['WALLET', 'MOMO_WALLET']:
        return 'captureWallet'
    elif payment_method_upper == 'QR':
        return 'payWithQR'
    else:
        return 'payWithATM'  # Default giống Laravel

def momo_callback(request):
    """Callback từ MoMo sau thanh toán"""
    data = request.GET or {}
    result_code = data.get('resultCode')
    order_id = data.get('orderId')
    message = data.get('message', '')

    if not order_id:
        return redirect('my_bookings')

    payment = Payment.objects.filter(momo_order_id=order_id).last()
    if not payment:
        return redirect('my_bookings')

    # Cập nhật kết quả
    payment.momo_result_code = int(result_code) if result_code is not None else None
    payment.momo_message = message

    if str(result_code) == '0':
        payment.status = 'paid_successfully'
        payment.payment_completed_at = timezone.now()
        payment.save()

        # Nếu đây là thanh toán deposit
        b = payment.booking
        if b.deposit_required and not b.deposit_paid:
            # Đang thanh toán cọc
            b.deposit_paid = True
            # nếu deposit bằng tổng tiền, xem như đã thanh toán đầy đủ
            if payment.amount >= b.total_price:
                b.payment_status = 'paid'
            b.save()
        elif b.deposit_paid and b.payment_status != 'paid':
            # Đã cọc rồi, đang thanh toán phần còn lại
            b.payment_status = 'paid'
            b.save()
        else:
            # Thanh toán đầy đủ 1 lần
            b.payment_status = 'paid'
            b.save()

        if request.user.is_authenticated:
            messages.success(request, 'Thanh toán MoMo thành công!')
    else:
        payment.status = 'payment_failed'
        payment.save()

    return redirect('booking_detail', pk=payment.booking.pk)

def momo_ipn(request):
    """IPN từ MoMo"""
    # IPN từ MoMo (không yêu cầu đăng nhập)
    if request.method != 'POST':
        return JsonResponse({'resultCode': 1, 'message': 'Method not allowed'})

    try:
        data = json.loads(request.body.decode()) if request.body else request.POST
    except json.JSONDecodeError:
        data = request.POST

    order_id = data.get('orderId')
    result_code = data.get('resultCode')

    if not order_id:
        return JsonResponse({'resultCode': 1, 'message': 'Missing orderId'})

    payment = Payment.objects.filter(momo_order_id=order_id).last()
    if not payment:
        return JsonResponse({'resultCode': 1, 'message': 'Payment not found'})

    payment.momo_result_code = int(result_code) if result_code is not None else None

    if str(result_code) == '0':
        payment.status = 'paid_successfully'
        payment.payment_completed_at = timezone.now()
        payment.save()

        b = payment.booking
        if b.deposit_required and not b.deposit_paid:
            # Đang thanh toán cọc
            b.deposit_paid = True
            if payment.amount >= b.total_price:
                b.payment_status = 'paid'
            b.save()
        elif b.deposit_paid and b.payment_status != 'paid':
            # Đã cọc rồi, đang thanh toán phần còn lại
            b.payment_status = 'paid'
            b.save()
        else:
            # Thanh toán đầy đủ 1 lần
            b.payment_status = 'paid'
            b.save()
    else:
        payment.status = 'payment_failed'
        payment.save()

    return JsonResponse({'resultCode': 0, 'message': 'Received'})


@login_required
def argon_payments_dashboard(request):
    """Trang quản lý payments kiểu Argon Dashboard (chỉ staff)."""
    if not request.user.is_staff:
        return HttpResponse(status=403)

    queryset = Payment.objects.select_related('booking', 'user').order_by('-created_at')

    method_filter = request.GET.get('method')
    status_filter = request.GET.get('status')

    valid_methods = {choice[0] for choice in Payment.PAYMENT_METHOD_CHOICES}
    valid_statuses = {choice[0] for choice in Payment.PAYMENT_STATUS_CHOICES}

    if method_filter in valid_methods:
        queryset = queryset.filter(method=method_filter)

    if status_filter in valid_statuses:
        queryset = queryset.filter(status=status_filter)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'payments/argon_payments_dashboard.html',
        {
            'page_obj': page_obj,
            'method_filter': method_filter,
            'status_filter': status_filter,
            'method_choices': Payment.PAYMENT_METHOD_CHOICES,
            'status_choices': Payment.PAYMENT_STATUS_CHOICES,
            'method_labels': dict(Payment.PAYMENT_METHOD_CHOICES),
            'status_labels': dict(Payment.PAYMENT_STATUS_CHOICES),
        },
    )


@require_POST
@login_required
def argon_payments_bulk_delete(request):
    """Xóa nhiều payments một lần cho trang Argon (chỉ staff)."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'forbidden'}, status=403)

    ids = request.POST.getlist('ids[]') or request.POST.getlist('ids')

    if request.content_type == 'application/json':
        try:
            body = json.loads(request.body.decode() or '{}')
            ids = body.get('ids', ids)
        except json.JSONDecodeError:
            pass

    if not ids:
        return JsonResponse({'deleted': 0})

    qs = Payment.objects.filter(id__in=ids)
    deleted = qs.count()
    qs.delete()
    return JsonResponse({'deleted': deleted})

@login_required
def upload_qr_receipt(request, payment_id):
    """Upload biên lai QR"""
    payment = get_object_or_404(Payment, pk=payment_id, user=request.user)

    if request.method == 'POST' and request.FILES.get('receipt_image'):
        payment.receipt_image = request.FILES['receipt_image']
        # GIỮ NGUYÊN status pending_payment, chờ admin xác nhận
        payment.save()

        messages.success(request, 'Đã gửi biên lai! Admin sẽ xác nhận trong vòng 24h.')
        return redirect('booking_detail', pk=payment.booking.id)

    return render(request, 'payments/upload_receipt.html', {
        'payment': payment
    })