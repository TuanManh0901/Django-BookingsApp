"""
Factory classes for creating test data.

These factories help create consistent test data for unit and integration tests.
"""
from django.contrib.auth.models import User
from tours.models import Tour, Review, TourImage
from bookings.models import Booking
from payments.models import Payment
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random


class UserFactory:
    """Factory for creating test users."""
    
    @staticmethod
    def create(username='testuser', email='test@example.com', password='testpass123', **kwargs):
        """Create a test user with default or custom attributes."""
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
        return user
    
    @staticmethod
    def create_staff(username='staffuser', email='staff@vntravel.com', password='staffpass123'):
        """Create a staff user."""
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True
        )
        return user
    
    @staticmethod
    def create_superuser(username='admin', email='admin@vntravel.com', password='admin123'):
        """Create a superuser."""
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        return user


class TourFactory:
    """Factory for creating test tours."""
    
    @staticmethod
    def create(name='Test Tour to Ha Long Bay', location='Hạ Long', 
               price=Decimal('5000000.00'), duration=3, max_people=20, **kwargs):
        """Create a test tour with default or custom attributes."""
        # Generate unique slug if not provided
        if 'slug' not in kwargs:
            import re
            from django.utils.text import slugify
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while Tour.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            kwargs['slug'] = slug
        
        tour = Tour.objects.create(
            name=name,
            location=location,
            price=price,
            duration=duration,
            max_people=max_people,
            description=kwargs.pop('description', f'Amazing {duration}-day tour to {location}'),
            is_active=kwargs.pop('is_active', True),
            is_hot=kwargs.pop('is_hot', False),
            **kwargs
        )
        return tour
    
    @staticmethod
    def create_hot_tour(name='Hot Tour to Phu Quoc', location='Phú Quốc', **kwargs):
        """Create a hot/featured tour."""
        kwargs['is_hot'] = True
        return TourFactory.create(name=name, location=location, **kwargs)
    
    @staticmethod
    def create_full_tour(name='Full Tour to Nha Trang', **kwargs):
        """Create a tour that's already full (for testing booking limits)."""
        tour = TourFactory.create(name=name, max_people=10, **kwargs)
        # Create bookings to fill the tour
        user1 = UserFactory.create(username='user1_full_tour')
        user2 = UserFactory.create(username='user2_full_tour')
        
        BookingFactory.create(
            tour=tour, 
            user=user1, 
            num_adults=5, 
            num_children=0,
            status='confirmed'
        )
        BookingFactory.create(
            tour=tour, 
            user=user2, 
            num_adults=5, 
            num_children=0,
            status='confirmed'
        )
        return tour


class BookingFactory:
    """Factory for creating test bookings."""
    
    @staticmethod
    def create(user=None, tour=None, booking_date=None, num_adults=2, num_children=0, **kwargs):
        """Create a test booking with default or custom attributes."""
        if user is None:
            user = UserFactory.create(username=f'user_{random.randint(1000, 9999)}')
        if tour is None:
            tour = TourFactory.create()
        if booking_date is None:
            booking_date = timezone.now().date() + timedelta(days=30)
        
        # Calculate total price safely - ensure it doesn't exceed 10^8
        # Assuming children pay 70% of adult price
        base_price = min(tour.price, Decimal('50000000.00'))  # Cap price at 50M
        total_price = (base_price * num_adults) + (base_price * num_children * Decimal('0.7'))
        total_price = min(total_price, Decimal('99999999.99'))  # Ensure under 10^8
        
        booking = Booking.objects.create(
            user=user,
            tour=tour,
            booking_date=booking_date,
            num_adults=num_adults,
            num_children=num_children,
            total_price=total_price,
            status=kwargs.pop('status', 'pending'),
            payment_status=kwargs.pop('payment_status', 'pending'),
            deposit_required=kwargs.pop('deposit_required', False),
            deposit_percentage=kwargs.pop('deposit_percentage', Decimal('0.00')),
            deposit_amount=kwargs.pop('deposit_amount', Decimal('0.00')),
            deposit_paid=kwargs.pop('deposit_paid', False),
            **kwargs
        )
        return booking
    
    @staticmethod
    def create_with_deposit(user=None, tour=None, deposit_percentage=Decimal('0.50'), **kwargs):
        """Create a booking with deposit requirement."""
        booking = BookingFactory.create(
            user=user,
            tour=tour,
            deposit_required=True,
            deposit_percentage=deposit_percentage,
            **kwargs
        )
        booking.calculate_deposit()
        booking.save()
        return booking
    
    @staticmethod
    def create_confirmed(user=None, tour=None, **kwargs):
        """Create a confirmed booking."""
        kwargs['status'] = 'confirmed'
        return BookingFactory.create(user=user, tour=tour, **kwargs)
    
    @staticmethod
    def create_paid(user=None, tour=None, **kwargs):
        """Create a fully paid booking."""
        kwargs['status'] = 'confirmed'
        kwargs['payment_status'] = 'paid'
        return BookingFactory.create(user=user, tour=tour, **kwargs)


class PaymentFactory:
    """Factory for creating test payments."""
    
    @staticmethod
    def create(booking=None, user=None, amount=None, method='momo', **kwargs):
        """Create a test payment with default or custom attributes."""
        if booking is None:
            booking = BookingFactory.create()
        if user is None:
            user = booking.user
        if amount is None:
            amount = booking.total_price
        
        payment = Payment.objects.create(
            booking=booking,
            user=user,
            amount=amount,
            method=method,
            status=kwargs.pop('status', 'pending_payment'),
            transaction_ref=kwargs.pop('transaction_ref', f'TEST_{random.randint(100000, 999999)}'),
            **kwargs
        )
        return payment
    
    @staticmethod
    def create_successful(booking=None, **kwargs):
        """Create a successful payment."""
        kwargs['status'] = 'paid_successfully'
        kwargs['momo_result_code'] = 0
        kwargs['momo_message'] = 'Successful.'
        kwargs['payment_completed_at'] = timezone.now()
        return PaymentFactory.create(booking=booking, **kwargs)
    
    @staticmethod
    def create_failed(booking=None, **kwargs):
        """Create a failed payment."""
        kwargs['status'] = 'payment_failed'
        kwargs['momo_result_code'] = 1001
        kwargs['momo_message'] = 'Transaction failed.'
        return PaymentFactory.create(booking=booking, **kwargs)


class ReviewFactory:
    """Factory for creating test reviews."""
    
    @staticmethod
    def create(booking=None, rating=5, comment='Great tour!', **kwargs):
        """Create a test review with default or custom attributes."""
        if booking is None:
            # Create a confirmed booking for the review
            booking = BookingFactory.create_confirmed()
        
        review = Review.objects.create(
            booking=booking,
            tour=booking.tour,
            user=booking.user,
            rating=rating,
            comment=comment,
            is_featured=kwargs.pop('is_featured', False),
            **kwargs
        )
        return review
    
    @staticmethod
    def create_featured(booking=None, rating=5, **kwargs):
        """Create a featured review."""
        kwargs['is_featured'] = True
        return ReviewFactory.create(booking=booking, rating=rating, **kwargs)
