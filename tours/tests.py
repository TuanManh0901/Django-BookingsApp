"""
Unit tests for Tours app.

Tests cover:
- Tour model methods and business logic
- Review model and validation
- TourImage model
- Tour views and templates
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from tours.models import Tour, Review, TourImage
from bookings.models import Booking
from tests.factories import UserFactory, TourFactory, BookingFactory, ReviewFactory


class TourModelTest(TestCase):
    """Test Tour model methods and business logic."""
    
    def setUp(self):
        """Set up test data."""
        self.tour = TourFactory.create(
            name='Test Tour to Ha Long',
            location='Hạ Long',
            price=Decimal('5000000.00'),
            duration=3,
            max_people=20
        )
        self.user = UserFactory.create()
    
    def test_tour_creation(self):
        """Test tour is created successfully."""
        self.assertEqual(self.tour.name, 'Test Tour to Ha Long')
        self.assertEqual(self.tour.location, 'Hạ Long')
        self.assertEqual(self.tour.price, Decimal('5000000.00'))
        self.assertEqual(self.tour.max_people, 20)
        self.assertTrue(self.tour.is_active)
    
    def test_tour_str_method(self):
        """Test __str__ method returns tour name."""
        self.assertEqual(str(self.tour), 'Test Tour to Ha Long')
    
    def test_get_available_seats_empty_tour(self):
        """Test available seats when no bookings exist."""
        self.assertEqual(self.tour.get_available_seats(), 20)
    
    def test_get_available_seats_with_bookings(self):
        """Test available seats calculation with existing bookings."""
        # Create a booking for 5 people
        BookingFactory.create(
            tour=self.tour,
            user=self.user,
            num_adults=3,
            num_children=2,
            status='confirmed'
        )
        
        # Should have 15 seats left (20 - 5)
        self.assertEqual(self.tour.get_available_seats(), 15)
    
    def test_get_available_seats_excludes_cancelled_bookings(self):
        """Test that cancelled bookings don't count toward capacity."""
        # Create confirmed booking
        BookingFactory.create(
            tour=self.tour,
            user=self.user,
            num_adults=5,
            status='confirmed'
        )
        
        # Create cancelled booking
        user2 = UserFactory.create(username='user2')
        BookingFactory.create(
            tour=self.tour,
            user=user2,
            num_adults=10,
            status='cancelled'
        )
        
        # Should only count confirmed booking (20 - 5 = 15)
        self.assertEqual(self.tour.get_available_seats(), 15)
    
    def test_is_full_method(self):
        """Test is_full() returns True when tour is at capacity."""
        # Fill the tour completely
        BookingFactory.create(
            tour=self.tour,
            user=self.user,
            num_adults=20,
            status='confirmed'
        )
        
        self.assertTrue(self.tour.is_full())
    
    def test_is_not_full_method(self):
        """Test is_full() returns False when tour has availability."""
        BookingFactory.create(
            tour=self.tour,
            user=self.user,
            num_adults=10,
            status='confirmed'
        )
        
        self.assertFalse(self.tour.is_full())
    
    def test_get_total_booked_people(self):
        """Test get_total_booked_people() counts correctly."""
        # Create multiple bookings
        BookingFactory.create(
            tour=self.tour,
            user=self.user,
            num_adults=3,
            num_children=2,
            status='confirmed'
        )
        
        user2 = UserFactory.create(username='user2')
        BookingFactory.create(
            tour=self.tour,
            user=user2,
            num_adults=5,
            num_children=0,
            status='pending'
        )
        
        # Total should be 3 + 2 + 5 = 10
        self.assertEqual(self.tour.get_total_booked_people(), 10)
    
    def test_get_average_rating_no_reviews(self):
        """Test average rating is 0 when no reviews exist."""
        self.assertEqual(self.tour.get_average_rating(), 0)
    
    def test_get_average_rating_with_reviews(self):
        """Test average rating calculation with multiple reviews."""
        # Create bookings and reviews
        booking1 = BookingFactory.create_confirmed(tour=self.tour, user=self.user)
        ReviewFactory.create(booking=booking1, rating=5)
        
        user2 = UserFactory.create(username='user2')
        booking2 = BookingFactory.create_confirmed(tour=self.tour, user=user2)
        ReviewFactory.create(booking=booking2, rating=4)
        
        user3 = UserFactory.create(username='user3')
        booking3 = BookingFactory.create_confirmed(tour=self.tour, user=user3)
        ReviewFactory.create(booking=booking3, rating=3)
        
        # Average should be (5 + 4 + 3) / 3 = 4.0
        self.assertEqual(self.tour.get_average_rating(), 4.0)
    
    def test_get_rating_breakdown_no_reviews(self):
        """Test rating breakdown when no reviews exist."""
        breakdown = self.tour.get_rating_breakdown()
        
        self.assertEqual(len(breakdown), 5)
        for item in breakdown:
            self.assertEqual(item['count'], 0)
            self.assertEqual(item['percentage'], 0)
    
    def test_get_rating_breakdown_with_reviews(self):
        """Test rating breakdown calculation."""
        # Create 10 reviews: 5★×5, 4★×3, 3★×2
        users = [UserFactory.create(username=f'user{i}') for i in range(10)]
        bookings = [BookingFactory.create_confirmed(tour=self.tour, user=user) for user in users]
        
        # 5 five-star reviews
        for i in range(5):
            ReviewFactory.create(booking=bookings[i], rating=5)
        
        # 3 four-star reviews
        for i in range(5, 8):
            ReviewFactory.create(booking=bookings[i], rating=4)
        
        # 2 three-star reviews
        for i in range(8, 10):
            ReviewFactory.create(booking=bookings[i], rating=3)
        
        breakdown = self.tour.get_rating_breakdown()
        
        # Check 5-star breakdown
        five_star = next(item for item in breakdown if item['rating'] == 5)
        self.assertEqual(five_star['count'], 5)
        self.assertEqual(five_star['percentage'], 50)
        
        # Check 4-star breakdown
        four_star = next(item for item in breakdown if item['rating'] == 4)
        self.assertEqual(four_star['count'], 3)
        self.assertEqual(four_star['percentage'], 30)
        
        # Check 3-star breakdown
        three_star = next(item for item in breakdown if item['rating'] == 3)
        self.assertEqual(three_star['count'], 2)
        self.assertEqual(three_star['percentage'], 20)
    
    def test_get_fallback_image_ha_long(self):
        """Test fallback image for Ha Long tours."""
        tour = TourFactory.create(name='Tour Hạ Long', location='Hạ Long')
        self.assertEqual(tour.get_fallback_image(), 'images/ha_long_bay.png')
    
    def test_get_fallback_image_phu_quoc(self):
        """Test fallback image for Phu Quoc tours."""
        tour = TourFactory.create(name='Tour Phú Quốc', location='Phú Quốc')
        self.assertEqual(tour.get_fallback_image(), 'images/phu_quoc_resort.png')
    
    def test_get_fallback_image_default(self):
        """Test default fallback image."""
        tour = TourFactory.create(name='Tour Unknown', location='Unknown')
        self.assertEqual(tour.get_fallback_image(), 'images/ha_long_bay.png')


class ReviewModelTest(TestCase):
    """Test Review model and validation."""
    
    def setUp(self):
        """Set up test data."""
        self.user = UserFactory.create()
        self.tour = TourFactory.create()
        self.booking = BookingFactory.create_confirmed(tour=self.tour, user=self.user)
    
    def test_review_creation(self):
        """Test review is created successfully."""
        review = ReviewFactory.create(
            booking=self.booking,
            rating=5,
            comment='Great tour experience!'
        )
        
        self.assertEqual(review.booking, self.booking)
        self.assertEqual(review.tour, self.tour)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great tour experience!')
    
    def test_review_auto_populate_tour_and_user(self):
        """Test that tour and user are auto-populated from booking."""
        review = Review.objects.create(
            booking=self.booking,
            rating=4,
            comment='Good tour'
        )
        
        # Tour and user should be auto-populated
        self.assertEqual(review.tour, self.booking.tour)
        self.assertEqual(review.user, self.booking.user)
    
    def test_review_str_method(self):
        """Test __str__ method returns correct format."""
        review = ReviewFactory.create(booking=self.booking, rating=5)
        expected = f"{self.user.username} - {self.tour.name} (Booking #{self.booking.id}) (5★)"
        self.assertEqual(str(review), expected)
    
    def test_get_star_display(self):
        """Test get_star_display() method."""
        review = ReviewFactory.create(booking=self.booking, rating=3)
        self.assertEqual(review.get_star_display(), '★★★☆☆')
        
        review2 = ReviewFactory.create(
            booking=BookingFactory.create_confirmed(tour=self.tour),
            rating=5
        )
        self.assertEqual(review2.get_star_display(), '★★★★★')
    
    def test_review_one_per_booking(self):
        """Test that only one review is allowed per booking."""
        # Create first review
        ReviewFactory.create(booking=self.booking, rating=5)
        
        # Attempting to create another review for same booking should fail
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                booking=self.booking,
                rating=4,
                comment='Another review'
            )
    
    def test_featured_review(self):
        """Test featured review creation."""
        review = ReviewFactory.create_featured(booking=self.booking, rating=5)
        self.assertTrue(review.is_featured)


class TourViewTest(TestCase):
    """Test Tour views."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        self.user = UserFactory.create()
        
        # Create some tours
        self.tour1 = TourFactory.create(
            name='Ha Long Bay Tour',
            location='Hạ Long',
            price=Decimal('5000000.00')
        )
        self.tour2 = TourFactory.create(
            name='Phu Quoc Beach Tour',
            location='Phú Quốc',
            price=Decimal('7000000.00')
        )
        self.tour3 = TourFactory.create_hot_tour(
            name='Sapa Adventure',
            location='Sapa',
            price=Decimal('4000000.00')
        )
    
    def test_tour_list_view(self):
        """Test tour list view displays tours."""
        response = self.client.get(reverse('tour_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ha Long Bay Tour')
        self.assertContains(response, 'Phu Quoc Beach Tour')
        self.assertContains(response, 'Sapa Adventure')
    
    def test_tour_detail_view(self):
        """Test tour detail view shows correct information."""
        response = self.client.get(
            reverse('tour_detail', kwargs={'pk': self.tour1.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tour1.name)
        self.assertContains(response, self.tour1.location)
    
    def test_tour_detail_view_404_for_invalid_pk(self):
        """Test tour detail view returns 404 for invalid pk."""
        response = self.client.get(
            reverse('tour_detail', kwargs={'pk': 99999})
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_hot_tours_displayed(self):
        """Test that hot tours are properly marked."""
        response = self.client.get(reverse('tour_list'))
        
        self.assertContains(response, 'Sapa Adventure')
        # The tour3 should have is_hot=True
        tour_in_context = None
        if 'tours' in response.context:
            tour_in_context = next(
                (t for t in response.context['tours'] if t.id == self.tour3.id),
                None
            )
        
        if tour_in_context:
            self.assertTrue(tour_in_context.is_hot)
    
    def test_inactive_tours_not_displayed(self):
        """Test that inactive tours are not shown in list."""
        inactive_tour = TourFactory.create(
            name='Inactive Tour',
            is_active=False
        )
        
        response = self.client.get(reverse('tour_list'))
        
        self.assertNotContains(response, 'Inactive Tour')
