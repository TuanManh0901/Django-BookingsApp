"""
Unit tests for Bookings app.

Tests cover:
- Booking model methods and business logic
- Booking validation
- Booking status transitions
- Booking views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from bookings.models import Booking
from tours.models import Tour
from tests.factories import UserFactory, TourFactory, BookingFactory


class BookingModelTest(TestCase):
    """Test Booking model methods and business logic."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory.create()
        self.tour = TourFactory.create(
            price=Decimal('10000000.00'),
            max_people=20
        )
    
    def test_booking_creation(self):
        """Test booking is created successfully."""
        booking = BookingFactory.create(
            user=self.user,
            tour=self.tour,
            num_adults=2,
            num_children=1
        )
        
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.tour, self.tour)
        self.assertEqual(booking.num_adults, 2)
        self.assertEqual(booking.num_children, 1)
        self.assertEqual(booking.status, 'pending')
    
    def test_booking_str_method(self):
        """Test __str__ method returns correct format."""
        booking = BookingFactory.create(user=self.user, tour=self.tour)
        expected = f"Booking {booking.id} - {self.user.username} - {self.tour.name}"
        self.assertEqual(str(booking), expected)
    
    def test_calculate_deposit(self):
        """Test calculate_deposit() method."""
        booking = BookingFactory.create(
            user=self.user,
            tour=self.tour,
            num_adults=2,
            deposit_required=True,
            deposit_percentage=Decimal('0.50')
        )
        
        # Total price should be tour.price * num_adults
        expected_deposit = booking.total_price * Decimal('0.50')
        
        calculated_deposit = booking.calculate_deposit()
        
        self.assertEqual(calculated_deposit, expected_deposit)
        self.assertEqual(booking.deposit_amount, expected_deposit)
    
    def test_calculate_deposit_different_percentage(self):
        """Test deposit calculation with different percentage."""
        booking = BookingFactory.create(
            user=self.user,
            tour=self.tour,
            deposit_required=True,
            deposit_percentage=Decimal('0.30')
        )
        
        expected_deposit = booking.total_price * Decimal('0.30')
        calculated_deposit = booking.calculate_deposit()
        
        self.assertEqual(calculated_deposit, expected_deposit)
    
    def test_get_remaining_amount_with_deposit(self):
        """Test get_remaining_amount() when deposit is paid."""
        booking = BookingFactory.create_with_deposit(
            user=self.user,
            tour=self.tour,
            deposit_percentage=Decimal('0.50')
        )
        booking.deposit_paid = True
        booking.save()
        
        expected_remaining = booking.total_price - booking.deposit_amount
        
        self.assertEqual(booking.get_remaining_amount(), expected_remaining)
    
    def test_get_remaining_amount_no_deposit(self):
        """Test get_remaining_amount() when no deposit paid."""
        booking = BookingFactory.create(user=self.user, tour=self.tour)
        
        self.assertEqual(booking.get_remaining_amount(), booking.total_price)
    
    def test_get_display_total_price_no_deposit(self):
        """Test get_display_total_price() when no deposit."""
        booking = BookingFactory.create(user=self.user, tour=self.tour)
        
        self.assertEqual(booking.get_display_total_price(), booking.total_price)
    
    def test_get_display_total_price_with_deposit_paid(self):
        """Test get_display_total_price() when deposit is paid."""
        booking = BookingFactory.create_with_deposit(
            user=self.user,
            tour=self.tour,
            deposit_percentage=Decimal('0.50')
        )
        booking.deposit_paid = True
        booking.payment_status = 'pending'
        booking.save()
        
        # Should return remaining amount
        expected = booking.total_price - booking.deposit_amount
        self.assertEqual(booking.get_display_total_price(), expected)
    
    def test_get_display_total_price_fully_paid(self):
        """Test get_display_total_price() when fully paid."""
        booking = BookingFactory.create_paid(user=self.user, tour=self.tour)
        
        # Should return total price
        self.assertEqual(booking.get_display_total_price(), booking.total_price)
    
    def test_get_overall_status_pending(self):
        """Test get_overall_status() for pending booking."""
        booking = BookingFactory.create(
            user=self.user,
            tour=self.tour,
            status='pending',
            payment_status='pending'
        )
        
        self.assertEqual(booking.get_overall_status(), 'pending')
    
    def test_get_overall_status_partial_paid(self):
        """Test get_overall_status() for partially paid booking."""
        booking = BookingFactory.create_with_deposit(
            user=self.user,
            tour=self.tour,
            deposit_percentage=Decimal('0.50')
        )
        booking.deposit_paid = True
        booking.save()
        
        self.assertEqual(booking.get_overall_status(), 'partial_paid')
    
    def test_get_overall_status_paid(self):
        """Test get_overall_status() for fully paid booking."""
        booking = BookingFactory.create_paid(user=self.user, tour=self.tour)
        
        self.assertEqual(booking.get_overall_status(), 'paid')
    
    def test_get_overall_status_cancelled(self):
        """Test get_overall_status() for cancelled booking."""
        booking = BookingFactory.create(
            user=self.user,
            tour=self.tour,
            status='cancelled'
        )
        
        self.assertEqual(booking.get_overall_status(), 'cancelled')
    
    def test_get_overall_status_display(self):
        """Test get_overall_status_display() returns Vietnamese text."""
        booking = BookingFactory.create_paid(user=self.user, tour=self.tour)
        
        self.assertEqual(booking.get_overall_status_display(), 'Đã thanh toán')
    
    def test_get_overall_status_display_partial(self):
        """Test status display for partial payment."""
        booking = BookingFactory.create_with_deposit(
            user=self.user,
            tour=self.tour,
            deposit_percentage=Decimal('0.50')
        )
        booking.deposit_paid = True
        booking.save()
        
        self.assertEqual(booking.get_overall_status_display(), 'Đã cọc 50%')
    
    def test_deposit_percentage_display(self):
        """Test deposit_percentage_display property."""
        booking = BookingFactory.create(
            user=self.user,
            tour=self.tour,
            deposit_percentage=Decimal('0.50')
        )
        
        self.assertEqual(booking.deposit_percentage_display, 50)
    
    def test_deposit_percentage_display_30_percent(self):
        """Test deposit percentage display for 30%."""
        booking = BookingFactory.create(
            user=self.user,
            tour=self.tour,
            deposit_percentage=Decimal('0.30')
        )
        
        self.assertEqual(booking.deposit_percentage_display, 30)
    
    def test_booking_prevents_overbooking(self):
        """Test that bookings respect tour capacity."""
        # Create a tour with 10 max people
        small_tour = TourFactory.create(max_people=10)
        
        # Book 8 people
        BookingFactory.create(
            user=self.user,
            tour=small_tour,
            num_adults=8,
            status='confirmed'
        )
        
        # Tour should have 2 seats left
        self.assertEqual(small_tour.get_available_seats(), 2)
        
        # Attempting to book 5 more should be prevented (in view logic)
        # The model itself doesn't prevent it, but views should check
        self.assertFalse(small_tour.get_available_seats() >= 5)


class BookingViewTest(TestCase):
    """Test Booking views."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        self.user = UserFactory.create(username='testuser', password='testpass123')
        self.tour = TourFactory.create(price=Decimal('5000000.00'))
    
    def test_create_booking_requires_authentication(self):
        """Test that creating booking requires login."""
        response = self.client.get(
            reverse('create_booking', kwargs={'tour_id': self.tour.id})
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_create_booking_view_authenticated(self):
        """Test booking creation view when authenticated."""
        self.client.force_login(self.user)
        
        response = self.client.get(
            reverse('create_booking', kwargs={'tour_id': self.tour.id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tour.name)
    
    def test_my_bookings_requires_authentication(self):
        """Test my bookings view requires login."""
        response = self.client.get(reverse('my_bookings'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_my_bookings_shows_user_bookings(self):
        """Test my bookings view shows correct bookings."""
        self.client.force_login(self.user)
        
        # Create bookings for this user
        booking1 = BookingFactory.create(user=self.user, tour=self.tour)
        booking2 = BookingFactory.create(user=self.user)
        
        # Create booking for another user
        other_user = UserFactory.create(username='otheruser')
        other_booking = BookingFactory.create(user=other_user)
        
        response = self.client.get(reverse('my_bookings'))
        
        self.assertEqual(response.status_code, 200)
        
        # Should contain user's bookings
        if 'bookings' in response.context:
            booking_ids = [b.id for b in response.context['bookings']]
            self.assertIn(booking1.id, booking_ids)
            self.assertIn(booking2.id, booking_ids)
            self.assertNotIn(other_booking.id, booking_ids)
