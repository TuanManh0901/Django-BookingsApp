from django.db import models

class Tour(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên tour")
    slug = models.SlugField(unique=True, max_length=200, verbose_name="Slug")
    description = models.TextField(verbose_name="Mô tả")
    location = models.CharField(max_length=100, verbose_name="Địa điểm")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá")
    duration = models.PositiveIntegerField(verbose_name="Thời gian (ngày)")
    max_people = models.PositiveIntegerField(verbose_name="Số người tối đa")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    is_hot = models.BooleanField(default=False, verbose_name="Tour Hot 🔥", 
                                  help_text="Đánh dấu tour này là hot/bán chạy")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Tour"
        verbose_name_plural = "Tours"

    def __str__(self):
        return self.name
    
    def get_total_booked_people(self):
        """Tính tổng số người đã đặt (chỉ tính booking chưa bị hủy và chưa qua ngày tour)"""
        from bookings.models import Booking
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        bookings = Booking.objects.filter(
            tour=self,
            status__in=['pending', 'confirmed']  # Không tính booking đã hủy
        )
        
        total = 0
        for b in bookings:
            # Tính ngày kết thúc tour = booking_date + duration
            tour_end_date = b.booking_date + timedelta(days=self.duration)
            
            # Chỉ đếm booking chưa qua ngày kết thúc tour
            if tour_end_date >= today:
                total += (b.num_adults + b.num_children)
        
        return total
    
    def get_available_seats(self):
        """Tính số chỗ còn trống"""
        booked = self.get_total_booked_people()
        return max(0, self.max_people - booked)
    
    def is_full(self):
        """Kiểm tra tour đã đầy chưa"""
        return self.get_available_seats() <= 0
    
    def get_fallback_image(self):
        """Trả về hình ảnh fallback dựa trên địa điểm tour"""
        location_lower = self.location.lower()
        name_lower = self.name.lower()
        
        # Map địa điểm với hình ảnh tương ứng
        if 'mekong' in location_lower or 'mekong' in name_lower or 'cần thơ' in location_lower or 'đồng bằng' in name_lower:
            return 'images/mekong_delta.png'
        elif 'nha trang' in location_lower or 'nha trang' in name_lower:
            return 'images/nha_trang.png'
        elif 'đà lạt' in location_lower or 'da lat' in location_lower or 'đà lạt' in name_lower or 'dalat' in name_lower:
            return 'images/da_lat.png'
        elif 'huế' in location_lower or 'hue' in location_lower or 'huế' in name_lower:
            return 'images/hue.png'
        elif 'sapa' in location_lower or 'sa pa' in location_lower or 'sapa' in name_lower:
            return 'images/sapa.png'
        elif 'hà nội' in location_lower or 'hanoi' in location_lower or 'ha noi' in name_lower or 'hà nội' in name_lower:
            return 'images/hanoi_city.png'
        elif 'hạ long' in location_lower or 'ha long' in location_lower or 'hạ long' in name_lower:
            return 'images/ha_long_bay.png'
        elif 'phú quốc' in location_lower or 'phu quoc' in location_lower or 'phú quốc' in name_lower:
            return 'images/phu_quoc_resort.png'
        else:
            # Default fallback cho các địa điểm khác
            return 'images/ha_long_bay.png'
    
    def get_average_rating(self):
        """Tính rating trung bình từ reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            total = sum(review.rating for review in reviews)
            return round(total / reviews.count(), 1)
        return 0
    
    def get_rating_breakdown(self):
        """Tính phân bổ rating (5★: x%, 4★: y%...)"""
        reviews = self.reviews.all()
        total_count = reviews.count()
        
        if total_count == 0:
            return [
                {'rating': 5, 'count': 0, 'percentage': 0},
                {'rating': 4, 'count': 0, 'percentage': 0},
                {'rating': 3, 'count': 0, 'percentage': 0},
                {'rating': 2, 'count': 0, 'percentage': 0},
                {'rating': 1, 'count': 0, 'percentage': 0},
            ]
        
        breakdown = []
        for rating in range(5, 0, -1):
            count = reviews.filter(rating=rating).count()
            percentage = round((count / total_count) * 100)
            breakdown.append({
                'rating': rating,
                'count': count,
                'percentage': percentage
            })
        
        return breakdown


class TourImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images', verbose_name="Tour")
    image = models.ImageField(upload_to='tours/', verbose_name="Ảnh")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Alt text")
    is_main = models.BooleanField(default=False, verbose_name="Ảnh chính")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Ảnh Tour"
        verbose_name_plural = "Ảnh Tours"

    def __str__(self):
        return f"Ảnh của {self.tour.name}"


class Review(models.Model):
    """Model for tour reviews and ratings - linked to individual bookings"""
    RATING_CHOICES = [(i, f"{i} sao") for i in range(1, 6)]
    
    # Primary link: Each booking can have one review (nullable temporarily for migration)
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, 
                                   related_name='review', verbose_name="Booking",
                                   null=True, blank=True)
    
    # Denormalized fields for efficient querying (auto-populated from booking)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reviews', verbose_name="Tour")
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="Người dùng")
    
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Đánh giá")
    comment = models.TextField(verbose_name="Nhận xét")
    is_featured = models.BooleanField(default=False, verbose_name="Nổi bật", 
                                      help_text="Hiển thị trên trang chủ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Đánh giá"
        verbose_name_plural = "Đánh giá"
        # No unique_together - booking OneToOne already ensures uniqueness
    
    def __str__(self):
        booking_info = f"Booking #{self.booking.id}" if self.booking else "No Booking"
        return f"{self.user.username} - {self.tour.name} ({booking_info}) ({self.rating}★)"
    
    def save(self, *args, **kwargs):
        # Auto-populate tour and user from booking
        if self.booking_id and not self.tour_id:
            self.tour = self.booking.tour
        if self.booking_id and not self.user_id:
            self.user = self.booking.user
        super().save(*args, **kwargs)
    
    def get_star_display(self):
        """Return stars as string (★★★★★)"""
        return "★" * self.rating + "☆" * (5 - self.rating)
