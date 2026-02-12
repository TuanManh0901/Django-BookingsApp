"""Models cho Tour du lịch VN Travel."""
from datetime import timedelta
from typing import List, Dict

from django.db import models
from django.utils import timezone


class Tour(models.Model):
    """Model gói tour với giá, địa điểm và thông tin đặt chỗ."""
    
    name = models.CharField(max_length=200, verbose_name="Tên tour")
    slug = models.SlugField(unique=True, max_length=200, verbose_name="Slug")
    description = models.TextField(verbose_name="Mô tả")
    location = models.CharField(max_length=100, verbose_name="Địa điểm")
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Giá")
    duration = models.PositiveIntegerField(verbose_name="Thời gian (ngày)")
    max_people = models.PositiveIntegerField(verbose_name="Số người tối đa")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    is_hot = models.BooleanField(
        default=False, 
        verbose_name="Tour Hot 🔥", 
        help_text="Đánh dấu tour này là hot/bán chạy"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Tour"
        verbose_name_plural = "Tours"

    def __str__(self) -> str:
        return self.name
    
    def get_total_booked_people(self) -> int:
        """Tính tổng số người đã đặt (loại trừ booking đã hủy/hết hạn)."""
        from bookings.models import Booking
        
        today = timezone.now().date()
        bookings = Booking.objects.filter(
            tour=self,
            status__in=['pending', 'confirmed']
        )
        
        total = 0
        for booking in bookings:
            tour_end_date = booking.booking_date + timedelta(days=self.duration)
            if tour_end_date >= today:
                total += (booking.num_adults + booking.num_children)
        
        return total
    
    def get_available_seats(self) -> int:
        """Tính số chỗ còn trống."""
        booked = self.get_total_booked_people()
        return max(0, self.max_people - booked)
    
    def is_full(self) -> bool:
        """Kiểm tra xem tour đã đầy chưa."""
        return self.get_available_seats() <= 0
    
    # Mapping địa điểm với hình ảnh fallback tương ứng
    LOCATION_IMAGE_MAP = {
        'mekong': 'images/mekong_delta.png',
        'cần thơ': 'images/mekong_delta.png',
        'đồng bằng': 'images/mekong_delta.png',
        'nha trang': 'images/nha_trang.png',
        'đà lạt': 'images/da_lat.png',
        'da lat': 'images/da_lat.png',
        'dalat': 'images/da_lat.png',
        'huế': 'images/hue.png',
        'hue': 'images/hue.png',
        'sapa': 'images/sapa.png',
        'sa pa': 'images/sapa.png',
        'hà nội': 'images/hanoi_city.png',
        'hanoi': 'images/hanoi_city.png',
        'ha noi': 'images/hanoi_city.png',
        'hạ long': 'images/ha_long_bay.png',
        'ha long': 'images/ha_long_bay.png',
        'phú quốc': 'images/phu_quoc_resort.png',
        'phu quoc': 'images/phu_quoc_resort.png',
    }
    
    def get_fallback_image(self) -> str:
        """Trả về hình ảnh fallback dựa trên địa điểm tour."""
        location_lower = self.location.lower()
        name_lower = self.name.lower()
        
        # Kiểm tra location và name trong mapping
        for keyword, image_path in self.LOCATION_IMAGE_MAP.items():
            if keyword in location_lower or keyword in name_lower:
                return image_path
        
        # Mặc định trả về hình Hạ Long
        return 'images/ha_long_bay.png'
    
    def get_average_rating(self) -> float:
        """Tính rating trung bình từ tất cả reviews."""
        reviews = self.reviews.all()
        if reviews.exists():
            total = sum(review.rating for review in reviews)
            return round(total / reviews.count(), 1)
        return 0.0
    
    def get_rating_breakdown(self) -> List[Dict[str, int]]:
        """Tính phân bổ rating (5★: x%, 4★: y%, v.v.)."""
        reviews = self.reviews.all()
        total_count = reviews.count()
        
        if total_count == 0:
            return [
                {'rating': rating, 'count': 0, 'percentage': 0}
                for rating in range(5, 0, -1)
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
    """Model hình ảnh tour - hỗ trợ nhiều ảnh cho mỗi tour."""
    
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE, 
        related_name='images', 
        verbose_name="Tour"
    )
    image = models.ImageField(upload_to='tours/', verbose_name="Ảnh")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Alt text")
    is_main = models.BooleanField(default=False, verbose_name="Ảnh chính")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Ảnh Tour"
        verbose_name_plural = "Ảnh Tours"

    def __str__(self) -> str:
        return f"Ảnh của {self.tour.name}"


class Review(models.Model):
    """Model đánh giá tour - liên kết với từng booking cụ thể."""
    
    RATING_CHOICES = [(i, f"{i} sao") for i in range(1, 6)]
    
    booking = models.OneToOneField(
        'bookings.Booking', 
        on_delete=models.CASCADE, 
        related_name='review', 
        verbose_name="Booking",
        null=True, 
        blank=True
    )
    tour = models.ForeignKey(
        Tour, 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        verbose_name="Tour"
    )
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE, 
        verbose_name="Người dùng"
    )
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Đánh giá")
    comment = models.TextField(verbose_name="Nhận xét")
    is_featured = models.BooleanField(
        default=False, 
        verbose_name="Nổi bật", 
        help_text="Hiển thị trên trang chủ"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Đánh giá"
        verbose_name_plural = "Đánh giá"
    
    def __str__(self) -> str:
        booking_info = f"Booking #{self.booking.id}" if self.booking else "No Booking"
        return f"{self.user.username} - {self.tour.name} ({booking_info}) ({self.rating}★)"
    
    def save(self, *args, **kwargs):
        """Tự động điền tour và user từ booking."""
        if self.booking_id and not self.tour_id:
            self.tour = self.booking.tour
        if self.booking_id and not self.user_id:
            self.user = self.booking.user
        super().save(*args, **kwargs)
    
    def get_star_display(self) -> str:
        """Trả về số sao dưới dạng chuỗi (★★★★★)."""
        return "★" * self.rating + "☆" * (5 - self.rating)
