from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView
from tours.models import Tour
from .forms import BookingForm
from .models import Booking
from .email_utils import send_booking_confirmation_email

@login_required
def create_booking(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = BookingForm(request.POST, tour=tour, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.tour = tour
            booking.total_price = (booking.num_adults + booking.num_children) * tour.price
            # Ensure new booking has deposit fields set to defaults to avoid NULL constraint errors
            try:
                booking.deposit_required = False
                booking.deposit_percentage = 0
                booking.deposit_amount = 0
                booking.deposit_paid = False
            except Exception:
                # If fields don't exist (older schema), ignore
                pass
            booking.save()
            
            # Send booking confirmation email
            try:
                email_sent = send_booking_confirmation_email(booking)
                if email_sent:
                    messages.success(request, f'Đặt tour thành công! Chúng tôi đã gửi email xác nhận đến {booking.user.email}')
                else:
                    messages.success(request, 'Đặt tour thành công! (Email xác nhận gửi thất bại, vui lòng kiểm tra lại thông tin)')
            except Exception as e:
                messages.success(request, f'Đặt tour thành công! (Không thể gửi email: {str(e)})')
            
            return redirect('my_bookings')
    else:
        form = BookingForm(tour=tour, user=request.user)
    return render(request, 'bookings/create_booking.html', {'form': form, 'tour': tour})

class MyBookingsView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/my_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        import sys
        from django.utils import timezone
        from datetime import timedelta
        
        # AGGRESSIVE LOGGING - THIS SHOULD ALWAYS PRINT!
        print("=" * 80, file=sys.stderr)
        print("MY BOOKINGS get_queryset() CALLED!", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        
        queryset = Booking.objects.filter(user=self.request.user)
        
        # Auto-cancel expired pending bookings (15 minutes grace period)
        grace_period = timedelta(minutes=15)
        cutoff_time = timezone.now() - grace_period
        
        print(f"DEBUG AUTO-CANCEL: Current time: {timezone.now()}", file=sys.stderr)
        print(f"DEBUG AUTO-CANCEL: Cutoff time (15min ago): {cutoff_time}", file=sys.stderr)
        
        expired_bookings = queryset.filter(
            payment_status='pending',
            deposit_paid=False,
            created_at__lt=cutoff_time
        )
        
        print(f"DEBUG AUTO-CANCEL: Found {expired_bookings.count()} expired bookings", file=sys.stderr)
        
        # Cancel all expired bookings
        for booking in expired_bookings:
            print(f"DEBUG AUTO-CANCEL: Cancelling booking #{booking.id}, created at {booking.created_at}", file=sys.stderr)
            booking.payment_status = 'cancelled'
            booking.save()
            print(f"DEBUG AUTO-CANCEL: Successfully cancelled booking #{booking.id}", file=sys.stderr)
        
        # Return fresh queryset with updated statuses
        return Booking.objects.filter(user=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        """Add no-cache headers to prevent browser caching"""
        response = super().dispatch(request, *args, **kwargs)
        # Force browser to NEVER cache this page
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add review info for each booking
        from tours.models import Review
        
        # Determine which context variable to use (ListView uses both)
        bookings = context.get('bookings') or context.get('object_list')
        
        # Debugging
        print(f"DEBUG: MyBookingsView - Processing {len(bookings)} bookings")
        
        for booking in bookings:
            # Check if this booking has a review (OneToOne relationship)
            try:
                booking.user_review = booking.review
                print(f"DEBUG: Booking {booking.id} - Has review: True")
            except Review.DoesNotExist:
                booking.user_review = None
                print(f"DEBUG: Booking {booking.id} - Has review: False")
            
        return context

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        from django.utils import timezone
        from datetime import timedelta
        
        context = super().get_context_data(**kwargs)
        booking = self.get_object()
        
        # Auto-cancel if expired (15 minutes grace period)
        grace_period = timedelta(minutes=15)
        if (booking.payment_status == 'pending' and 
            not booking.deposit_paid and 
            booking.created_at < timezone.now() - grace_period):
            booking.payment_status = 'cancelled'
            booking.save()
            # Refresh from DB to get updated status
            booking.refresh_from_db()
        
        # Kiểm tra xem có payment nào đã upload receipt_image chưa
        has_receipt = booking.payments.filter(receipt_image__isnull=False).exclude(receipt_image='').exists()
        context['has_receipt_uploaded'] = has_receipt
        return context

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        # Nếu hủy, xem như không còn trạng thái cọc để tránh hiển thị "đã cọc 50%"
        booking.deposit_required = False
        booking.deposit_paid = False
        booking.deposit_amount = 0
        booking.deposit_percentage = 0
        booking.save()
    else:
        pass
    return redirect('my_bookings')


@login_required
def cancel_booking_ajax(request, pk):
    """API endpoint to cancel a booking via AJAX when frontend countdown expires."""
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
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.payment_status == 'paid':
        messages.info(request, "This booking is already paid.")
        return redirect('booking_detail', pk=booking.pk)

    # Chuyển sang luồng chọn phương thức thanh toán thống nhất
    return redirect('payments:select_payment_method', booking_id=booking.pk)


@login_required
def submit_review(request, booking_id):
    """Submit a review for a tour from My Bookings page"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    print(f"DEBUG: Submitting review for booking {booking_id}")
    print(f"DEBUG: Payment status: {booking.payment_status}")
    
    # Only allow reviews for paid bookings
    if booking.payment_status != 'paid':
        print("DEBUG: Status check failed")
        messages.error(request, 'Bạn chỉ có thể đánh giá tour sau khi đã thanh toán hoàn tất.')
        return redirect('my_bookings')
    
    # Check if this booking already has a review
    from tours.models import Review
    try:
        existing_review = booking.review  # OneToOne relationship
        print(f"DEBUG: Existing review found: {existing_review}")
    except Review.DoesNotExist:
        existing_review = None
        print("DEBUG: No existing review")
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        print(f"DEBUG: POST data - rating: {rating}, comment: {comment}")
        
        # Validation
        if not rating or not comment:
            print("DEBUG: Validation failed - missing data")
            messages.error(request, 'Vui lòng điền đầy đủ đánh giá và nhận xét.')
            return redirect('my_bookings')
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError()
        except (ValueError, TypeError):
            print("DEBUG: Validation failed - invalid rating")
            messages.error(request, 'Đánh giá không hợp lệ.')
            return redirect('my_bookings')
        
        # Create or update review
        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            print("DEBUG: Updated existing review")
            messages.success(request, 'Cập nhật đánh giá thành công!')
        else:
            Review.objects.create(
                booking=booking,
                tour=booking.tour,  # Explicitly set tour and user
                user=request.user,
                rating=rating,
                comment=comment,
                is_featured=False  # Admin can mark as featured later
            )
            print("DEBUG: Created new review")
            messages.success(request, 'Cảm ơn bạn đã đánh giá! Review của bạn đã được gửi.')
        
        return redirect('my_bookings')
    
    return redirect('my_bookings')
