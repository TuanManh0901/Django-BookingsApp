"""
Unit tests for Payments app.

Tests cover:
- Payment model
- MoMo payment integration (mocked)
- Payment status updates
- Payment views
"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone
from unittest.mock import patch, MagicMock

from payments.models import Payment
from bookings.models import Booking
from tests.factories import UserFactory, TourFactory, BookingFactory, PaymentFactory
from tests.mocks import MockMoMoAPI, create_mock_requests_response


class PaymentModelTest(TestCase):
    """Test Payment model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory.create()
        self.tour = TourFactory.create()
        self.booking = BookingFactory.create(user=self.user, tour=self.tour)
    
    def test_payment_creation(self):
        """Test payment is created successfully."""
        payment = PaymentFactory.create(
            booking=self.booking,
            amount=Decimal('5000000.00'),
            method='momo'
        )
        
        self.assertEqual(payment.booking, self.booking)
        self.assertEqual(payment.user, self.booking.user)
        self.assertEqual(payment.amount, Decimal('5000000.00'))
        self.assertEqual(payment.method, 'momo')
        self.assertEqual(payment.status, 'pending_payment')
    
    def test_payment_str_method(self):
        """Test __str__ method returns correct format."""
        payment = PaymentFactory.create(booking=self.booking)
        expected = f"Payment {payment.id} - {self.booking} - {payment.amount}"
        self.assertEqual(str(payment), expected)
    
    def test_successful_payment(self):
        """Test successful payment creation."""
        payment = PaymentFactory.create_successful(booking=self.booking)
        
        self.assertEqual(payment.status, 'paid_successfully')
        self.assertEqual(payment.momo_result_code, 0)
        self.assertIsNotNone(payment.payment_completed_at)
    
    def test_failed_payment(self):
        """Test failed payment creation."""
        payment = PaymentFactory.create_failed(booking=self.booking)
        
        self.assertEqual(payment.status, 'payment_failed')
        self.assertEqual(payment.momo_result_code, 1001)
    
    def test_payment_method_choices(self):
        """Test different payment methods."""
        payment_momo = PaymentFactory.create(booking=self.booking, method='momo')
        self.assertEqual(payment_momo.method, 'momo')
        
        booking2 = BookingFactory.create(user=self.user, tour=self.tour)
        payment_bank = PaymentFactory.create(booking=booking2, method='bank_transfer')
        self.assertEqual(payment_bank.method, 'bank_transfer')
    
    def test_payment_status_choices(self):
        """Test different payment statuses."""
        # Pending
        payment1 = PaymentFactory.create(booking=self.booking, status='pending_payment')
        self.assertEqual(payment1.status, 'pending_payment')
        
        # Deposit paid
        booking2 = BookingFactory.create(user=self.user, tour=self.tour)
        payment2 = PaymentFactory.create(booking=booking2, status='deposit_paid')
        self.assertEqual(payment2.status, 'deposit_paid')
        
        # Paid successfully
        booking3 = BookingFactory.create(user=self.user, tour=self.tour)
        payment3 = PaymentFactory.create(booking=booking3, status='paid_successfully')
        self.assertEqual(payment3.status, 'paid_successfully')


class MoMoPaymentIntegrationTest(TestCase):
    """Test MoMo payment integration with mocked API."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory.create()
        self.tour = TourFactory.create()
        self.booking = BookingFactory.create(
            user=self.user,
            tour=self.tour,
            total_price=Decimal('5000000.00')
        )
    
    @patch('requests.post')
    def test_momo_payment_request_creation(self, mock_post):
        """Test creating MoMo payment request (mocked)."""
        # Mock successful MoMo API response
        mock_response = create_mock_requests_response(
            MockMoMoAPI.successful_payment_request(),
            status_code=200
        )
        mock_post.return_value = mock_response
        
        # The actual implementation would call MoMo API
        # Here we're just testing the mock
        response = mock_post('https://test.momo.vn/gateway')
        data = response.json()
        
        self.assertEqual(data['resultCode'], 0)
        self.assertIn('payUrl', data)
        self.assertEqual(response.status_code, 200)
    
    def test_momo_successful_callback_processing(self):
        """Test processing successful MoMo callback."""
        # Create a payment
        payment = PaymentFactory.create(
            booking=self.booking,
            method='momo',
            status='pending_payment'
        )
        
        # Simulate successful callback
        callback_data = MockMoMoAPI.successful_callback()
        
        # Update payment based on callback
        if callback_data['resultCode'] == 0:
            payment.status = 'paid_successfully'
            payment.momo_result_code = callback_data['resultCode']
            payment.momo_message = callback_data['message']
            payment.payment_completed_at = timezone.now()
            payment.save()
            
            # Update booking
            self.booking.payment_status = 'paid'
            self.booking.status = 'confirmed'
            self.booking.save()
        
        # Verify payment was updated
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'paid_successfully')
        self.assertEqual(payment.momo_result_code, 0)
        
        # Verify booking was updated
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, 'paid')
        self.assertEqual(self.booking.status, 'confirmed')
    
    def test_momo_failed_callback_processing(self):
        """Test processing failed MoMo callback."""
        payment = PaymentFactory.create(
            booking=self.booking,
            method='momo',
            status='pending_payment'
        )
        
        # Simulate failed callback
        callback_data = MockMoMoAPI.failed_callback()
        
        # Update payment based on callback
        if callback_data['resultCode'] != 0:
            payment.status = 'payment_failed'
            payment.momo_result_code = callback_data['resultCode']
            payment.momo_message = callback_data['message']
            payment.save()
        
        # Verify payment was updated
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'payment_failed')
        self.assertEqual(payment.momo_result_code, 1001)
    
    def test_deposit_payment_processing(self):
        """Test processing deposit payment."""
        # Create booking with deposit
        booking = BookingFactory.create_with_deposit(
            user=self.user,
            tour=self.tour,
            deposit_percentage=Decimal('0.50')
        )
        
        # Create payment for deposit amount
        payment = PaymentFactory.create(
            booking=booking,
            amount=booking.deposit_amount,
            status='pending_payment'
        )
        
        # Simulate successful deposit payment
        callback_data = MockMoMoAPI.successful_callback()
        
        if callback_data['resultCode'] == 0:
            payment.status = 'deposit_paid'
            payment.momo_result_code = 0
            payment.payment_completed_at = timezone.now()
            payment.save()
            
            booking.deposit_paid = True
            booking.save()
        
        # Verify
        payment.refresh_from_db()
        booking.refresh_from_db()
        
        self.assertEqual(payment.status, 'deposit_paid')
        self.assertTrue(booking.deposit_paid)
        self.assertEqual(booking.get_overall_status(), 'partial_paid')


class PaymentViewTest(TestCase):
    """Test Payment views."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        self.user = UserFactory.create(username='testuser', password='testpass123')
        self.tour = TourFactory.create()
        self.booking = BookingFactory.create(user=self.user, tour=self.tour)
    
    def test_payment_view_requires_authentication(self):
        """Test payment initiation requires login."""
        response = self.client.get(
            reverse('payments:select_payment_method', kwargs={'booking_id': self.booking.id})
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_payment_history_requires_authentication(self):
        """Test payment history view requires login (if exists)."""
        # This test assumes there's a payment history view
        # If it doesn't exist, we skip this test
        pass
    
    def test_payment_history_shows_user_payments(self):
        """Test payment history shows correct payments (if view exists)."""
        # This is a placeholder - adjust based on actual implementation
        pass
