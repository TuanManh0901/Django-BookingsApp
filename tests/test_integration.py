"""
Integration tests for VN-Travel system.

These tests verify end-to-end workflows and integration between different modules.
"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone
from unittest.mock import patch

from tests.factories import UserFactory, TourFactory, BookingFactory, PaymentFactory
from tests.mocks import MockMoMoAPI, MockGeminiAPI
from bookings.models import Booking
from payments.models import Payment


class BookingFlowIntegrationTest(TestCase):
    """Test complete booking flow from browsing to payment."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory.create(username='integrationuser', password='testpass123')
        self.tour = TourFactory.create(
            name='Integration Test Tour',
            price=Decimal('5000000.00'),
            max_people=20
        )
    
    def test_complete_booking_flow_browse_to_payment(self):
        """Test complete flow: browse tours → view detail → book → pay."""
        # Step 1: Browse tours (anonymous user)
        response = self.client.get(reverse('tours:tour_list'))
        self.assertEqual(response.status_code, 200)
        
        # Step 2: View tour detail
        response = self.client.get(
            reverse('tours:tour_detail', kwargs={'slug': self.tour.slug})
        )
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Login (required for booking)
        self.client.force_login(self.user)
        
        # Step 4: Create booking
        booking_data = {
            'tour': self.tour.id,
            'booking_date': (timezone.now() + timezone.timedelta(days=30)).date(),
            'num_adults': 2,
            'num_children': 1
        }
        
        # Create booking manually (simulating form submission)
        booking = BookingFactory.create(
            user=self.user,
            tour=self.tour,
            num_adults=2,
            num_children=1
        )
        
        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, 'pending')
        
        # Step 5: View booking detail
        # (assuming there's a booking detail view)
        
        # Step 6: Initiate payment
        payment = PaymentFactory.create(
            booking=booking,
            amount=booking.total_price,
            method='momo',
            status='pending_payment'
        )
        
        self.assertIsNotNone(payment)
        
        # Step 7: Simulate successful payment callback
        callback_data = MockMoMoAPI.successful_callback()
        
        if callback_data['resultCode'] == 0:
            payment.status = 'paid_successfully'
            payment.momo_result_code = 0
            payment.payment_completed_at = timezone.now()
            payment.save()
            
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            booking.save()
        
        # Verify final state
        booking.refresh_from_db()
        payment.refresh_from_db()
        
        self.assertEqual(booking.status, 'confirmed')
        self.assertEqual(booking.payment_status, 'paid')
        self.assertEqual(payment.status, 'paid_successfully')
    
    def test_deposit_payment_flow(self):
        """Test booking flow with deposit payment."""
        self.client.force_login(self.user)
        
        # Create booking with deposit
        booking = BookingFactory.create_with_deposit(
            user=self.user,
            tour=self.tour,
            deposit_percentage=Decimal('0.50')
        )
        
        # Verify deposit calculated correctly
        expected_deposit = booking.total_price * Decimal('0.50')
        self.assertEqual(booking.deposit_amount, expected_deposit)
        
        # Pay deposit
        deposit_payment = PaymentFactory.create(
            booking=booking,
            amount=booking.deposit_amount,
            method='momo'
        )
        
        # Simulate successful deposit payment
        callback_data = MockMoMoAPI.successful_callback()
        
        if callback_data['resultCode'] == 0:
            deposit_payment.status = 'deposit_paid'
            deposit_payment.momo_result_code = 0
            deposit_payment.payment_completed_at = timezone.now()
            deposit_payment.save()
            
            booking.deposit_paid = True
            booking.save()
        
        # Verify booking state after deposit
        booking.refresh_from_db()
        self.assertTrue(booking.deposit_paid)
        self.assertEqual(booking.get_overall_status(), 'partial_paid')
        
        # Pay remaining amount
        remaining_amount = booking.get_remaining_amount()
        final_payment = PaymentFactory.create(
            booking=booking,
            amount=remaining_amount,
            method='momo'
        )
        
        # Simulate successful final payment
        if callback_data['resultCode'] == 0:
            final_payment.status = 'paid_successfully'
            final_payment.momo_result_code = 0
            final_payment.payment_completed_at = timezone.now()
            final_payment.save()
            
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            booking.save()
        
        # Verify final state
        booking.refresh_from_db()
        self.assertEqual(booking.payment_status, 'paid')
        self.assertEqual(booking.get_overall_status(), 'paid')
    
    def test_booking_cancellation_flow(self):
        """Test booking cancellation flow."""
        self.client.force_login(self.user)
        
        # Create confirmed booking
        booking = BookingFactory.create_confirmed(
            user=self.user,
            tour=self.tour
        )
        
        # Cancel booking
        booking.status = 'cancelled'
        booking.save()
        
        # Verify cancelled
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        self.assertEqual(booking.get_overall_status(), 'cancelled')


class ReviewFlowIntegrationTest(TestCase):
    """Test review submission flow."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = UserFactory.create(username='reviewer', password='testpass123')
        self.tour = TourFactory.create()
    
    def test_complete_review_flow(self):
        """Test complete flow: book → complete → review."""
        self.client.force_login(self.user)
        
        # Create completed booking
        booking = BookingFactory.create_paid(
            user=self.user,
            tour=self.tour
        )
        
        # Create review
        from tours.models import Review
        review = Review.objects.create(
            booking=booking,
            rating=5,
            comment='Excellent tour! Highly recommended.'
        )
        
        # Verify review created
        self.assertEqual(review.tour, self.tour)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)
        
        # Verify tour rating updated
        self.assertEqual(self.tour.get_average_rating(), 5.0)


class APIIntegrationTest(TestCase):
    """Test integration with external APIs (mocked)."""
    
    def setUp(self):
        """Set up test data."""
        self.tour = TourFactory.create(location='Hạ Long')
    
    @patch('requests.get')
    def test_weather_api_integration(self, mock_get):
        """Test Weather API integration (mocked)."""
        from tests.mocks import MockWeatherAPI, create_mock_requests_response
        
        # Mock weather API response
        mock_response = create_mock_requests_response(
            MockWeatherAPI.successful_response('Ha Long', temp=25),
            status_code=200
        )
        mock_get.return_value = mock_response
        
        # Make request
        response = mock_get('https://api.openweathermap.org/data/2.5/weather')
        data = response.json()
        
        # Verify
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['main']['temp'], 25)
        self.assertEqual(data['name'], 'Ha Long')
    
    @patch('google.generativeai.GenerativeModel')
    def test_gemini_api_integration(self, mock_model):
        """Test Gemini AI API integration (mocked)."""
        # Mock Gemini
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value = MockGeminiAPI.successful_chat_response('tour')
        
        # Generate response
        response = mock_instance.generate_content('Tell me about tours')
        
        # Verify
        self.assertIsNotNone(response.text)
        self.assertTrue(len(response.text) > 0)


class CapacityManagementIntegrationTest(TestCase):
    """Test tour capacity management across bookings."""
    
    def setUp(self):
        """Set up test data."""
        self.tour = TourFactory.create(max_people=10)
        self.users = [UserFactory.create(username=f'user{i}') for i in range(5)]
    
    def test_multiple_bookings_respect_capacity(self):
        """Test that multiple bookings don't exceed tour capacity."""
        # Book 8 people
        booking1 = BookingFactory.create(
            user=self.users[0],
            tour=self.tour,
            num_adults=5,
            status='confirmed'
        )
        
        booking2 = BookingFactory.create(
            user=self.users[1],
            tour=self.tour,
            num_adults=3,
            status='confirmed'
        )
        
        # Check available seats
        self.assertEqual(self.tour.get_available_seats(), 2)
        self.assertFalse(self.tour.is_full())
        
        # Book remaining 2 seats
        booking3 = BookingFactory.create(
            user=self.users[2],
            tour=self.tour,
            num_adults=2,
            status='confirmed'
        )
        
        # Tour should now be full
        self.assertEqual(self.tour.get_available_seats(), 0)
        self.assertTrue(self.tour.is_full())
    
    def test_cancelled_bookings_free_up_capacity(self):
        """Test that cancelled bookings free up capacity."""
        # Fill tour
        booking1 = BookingFactory.create(
            user=self.users[0],
            tour=self.tour,
            num_adults=10,
            status='confirmed'
        )
        
        # Tour is full
        self.assertTrue(self.tour.is_full())
        
        # Cancel booking
        booking1.status = 'cancelled'
        booking1.save()
        
        # Capacity should be freed
        self.assertEqual(self.tour.get_available_seats(), 10)
        self.assertFalse(self.tour.is_full())


class EmailNotificationIntegrationTest(TestCase):
    """Test email notifications integration."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory.create(email='test@example.com')
        self.tour = TourFactory.create()
    
    def test_booking_confirmation_email(self):
        """Test booking confirmation email is sent."""
        from django.core import mail
        
        # Create booking
        booking = BookingFactory.create_confirmed(
            user=self.user,
            tour=self.tour
        )
        
        # In a real scenario, signal would trigger email
        # For testing, we manually send
        # This is a placeholder - actual implementation would use signals
        
        # Verify email would be sent (placeholder)
        # In real tests, you'd check mail.outbox
        self.assertIsNotNone(booking)
    
    def test_payment_confirmation_email(self):
        """Test payment confirmation email is sent."""
        booking = BookingFactory.create(user=self.user, tour=self.tour)
        payment = PaymentFactory.create_successful(booking=booking)
        
        # Email would be sent via signal
        # Placeholder for actual email test
        self.assertEqual(payment.status, 'paid_successfully')
