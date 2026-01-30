from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from tours.models import Tour

from .email_utils import send_booking_confirmation_email
from .forms import BookingForm
from .models import Booking

@login_required
def create_booking(request, tour_id):
    """Tạo booking tour mới với atomic transaction để tránh race condition."""
    with transaction.atomic():
        tour = get_object_or_404(Tour.objects.select_for_update(), pk=tour_id)
        
        if request.method == 'POST':
            form = BookingForm(request.POST, tour=tour, user=request.user)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.user = request.user
                booking.tour = tour
                booking.total_price = (booking.num_adults + booking.num_children) * tour.price
                
                custom_itinerary = request.POST.get('custom_itinerary')
                if custom_itinerary:
                    booking.custom_itinerary = custom_itinerary

                try:
                    booking.deposit_required = False
                    booking.deposit_percentage = 0
                    booking.deposit_amount = 0
                    booking.deposit_paid = False
                except Exception:
                    pass
                    
                booking.save()
            
                try:
                    email_sent = send_booking_confirmation_email(booking)
                    if email_sent:
                        messages.success(
                            request, 
                            f'Đặt tour thành công! Chúng tôi đã gửi email xác nhận đến {booking.user.email}'
                        )
                    else:
                        messages.success(
                            request, 
                            'Đặt tour thành công! (Email xác nhận gửi thất bại, vui lòng kiểm tra lại thông tin)'
                        )
                except Exception as e:
                    messages.success(request, f'Đặt tour thành công! (Không thể gửi email: {str(e)})')
            
                return redirect('my_bookings')
        else:
            form = BookingForm(tour=tour, user=request.user)
            
    return render(request, 'bookings/create_booking.html', {'form': form, 'tour': tour})

class MyBookingsView(LoginRequiredMixin, ListView):
    """Display user's bookings with automatic cleanup of expired bookings."""
    
    model = Booking
    template_name = 'bookings/my_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        Booking.cancel_expired_bookings()
        return Booking.objects.filter(
            user=self.request.user
        ).select_related('tour', 'review')
    
    def dispatch(self, request, *args, **kwargs):
        """Add no-cache headers to prevent browser caching."""
        response = super().dispatch(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
    def get_context_data(self, **kwargs):
        from tours.models import Review
        
        context = super().get_context_data(**kwargs)
        bookings = context.get('bookings') or context.get('object_list')
        
        for booking in bookings:
            try:
                booking.user_review = booking.review
            except Review.DoesNotExist:
                booking.user_review = None
            
        return context

class BookingDetailView(LoginRequiredMixin, DetailView):
    """Hiển thị chi tiết của một booking."""
    
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.get_object()
        
        if booking.status == 'pending' and booking.is_expired():
            booking.status = 'cancelled'
            booking.payment_status = 'cancelled'
            booking.save()
        
        has_receipt = booking.payments.filter(
            receipt_image__isnull=False
        ).exclude(receipt_image='').exists()
        context['has_receipt_uploaded'] = has_receipt
        
        return context

@login_required
def cancel_booking(request, pk):
    """Hủy booking và reset các trường deposit."""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.payment_status = 'cancelled'
        booking.deposit_required = False
        booking.deposit_paid = False
        booking.deposit_amount = 0
        booking.deposit_percentage = 0
        booking.save()
        messages.success(request, 'Đã hủy tour thành công.')
    else:
        messages.error(
            request, 
            'Không thể hủy tour này (Chỉ hủy được tour Đang xử lý hoặc Đã xác nhận).'
        )
    
    return redirect('my_bookings')


@login_required
def cancel_booking_ajax(request, pk):
    """API endpoint hủy booking qua AJAX (khi countdown frontend hết hạn)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    if booking.status not in ['pending', 'confirmed']:
        return JsonResponse({'success': False, 'message': 'Booking cannot be cancelled'}, status=400)

    booking.status = 'cancelled'
    booking.deposit_required = False
    booking.deposit_paid = False
    booking.deposit_amount = 0
    booking.deposit_percentage = 0
    booking.save()

    return JsonResponse({'success': True, 'message': 'Booking cancelled'})

@login_required
def pay_booking(request, pk):
    """Chuyển đến trang chọn phương thức thanh toán, hủy booking hết hạn trước."""
    Booking.cancel_expired_bookings()
    
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    if booking.status == 'cancelled':
        messages.error(request, "Đơn đặt tour đã bị hủy do quá hạn thanh toán.")
        return redirect('booking_detail', pk=booking.pk)
        
    if booking.payment_status == 'paid':
        messages.info(request, "This booking is already paid.")
        return redirect('booking_detail', pk=booking.pk)

    return redirect('payments:select_payment_method', booking_id=booking.pk)


@login_required
def submit_review(request, booking_id):
    """Gửi hoặc cập nhật đánh giá cho booking đã thanh toán."""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    if booking.payment_status != 'paid':
        messages.error(request, 'Bạn chỉ có thể đánh giá tour sau khi đã thanh toán hoàn tất.')
        return redirect('my_bookings')
    
    from tours.models import Review
    
    try:
        existing_review = booking.review
    except Review.DoesNotExist:
        existing_review = None
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        if not rating or not comment:
            messages.error(request, 'Vui lòng điền đầy đủ đánh giá và nhận xét.')
            return redirect('my_bookings')
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError()
        except (ValueError, TypeError):
            messages.error(request, 'Đánh giá không hợp lệ.')
            return redirect('my_bookings')
        
        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, 'Cập nhật đánh giá thành công!')
        else:
            Review.objects.create(
                booking=booking,
                tour=booking.tour,
                user=request.user,
                rating=rating,
                comment=comment,
                is_featured=False
            )
            messages.success(request, 'Cảm ơn bạn đã đánh giá! Review của bạn đã được gửi.')
        
        return redirect('my_bookings')
    
    return redirect('my_bookings')
