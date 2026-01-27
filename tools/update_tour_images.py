#!/usr/bin/env python
"""
Script to create TourImage records for tours
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vn_travel.settings')
django.setup()

from tours.models import Tour, TourImage

# Mapping tour names to image paths
tour_images = {
    "Buôn Ma Thuột - Mùa Hoa Cà Phê": "tours/buon_ma_thuot.png",
    "Côn Đảo Tâm Linh & Nghỉ Dưỡng": "tours/con_dao.png",
    "Tuyệt Tình Cốc Đà Lạt - Làng Cù Lần": "tours/tuyet_tinh_coc.png",
    "Quy Nhơn - Kỳ Co - Eo Gió: Maldives Việt Nam": "tours/quy_nhon.png",
    "Động Phong Nha - Kẻ Bàng: Kỳ Quan Đệ Nhất Động": "tours/phong_nha.png",
    "Săn Mây Tà Xùa - Thiên Đường Hạ Giới": "tours/ta_xua.png",
    "Khám phá Hà Giang - Mùa Hoa Tam Giác Mạch": "tours/ha_giang.png",
}

print("Đang tạo TourImage records cho các tours...")
print("=" * 60)

created_count = 0
updated_count = 0
not_found = []

for tour_name, image_path in tour_images.items():
    try:
        tour = Tour.objects.get(name=tour_name)
        
        # Check if TourImage already exists for this tour with this image
        existing_image = TourImage.objects.filter(tour=tour, image=image_path).first()
        
        if existing_image:
            # Update to make it main image if not already
            if not existing_image.is_main:
                existing_image.is_main = True
                existing_image.alt_text = tour_name
                existing_image.save()
                print(f"🔄 Đã cập nhật: {tour_name}")
                updated_count += 1
            else:
                print(f"✅ Đã tồn tại: {tour_name}")
        else:
            # Create new TourImage
            # First, set all existing images for this tour to not main
            TourImage.objects.filter(tour=tour, is_main=True).update(is_main=False)
            
            # Create new main image
            TourImage.objects.create(
                tour=tour,
                image=image_path,
                alt_text=tour_name,
                is_main=True
            )
            print(f"✅ Đã tạo mới: {tour_name}")
            print(f"   → {image_path}")
            created_count += 1
            
    except Tour.DoesNotExist:
        print(f"❌ Không tìm thấy tour: {tour_name}")
        not_found.append(tour_name)
    except Exception as e:
        print(f"⚠️  Lỗi khi xử lý {tour_name}: {e}")

print("=" * 60)
print(f"\n📊 Kết quả:")
print(f"   - Đã tạo mới: {created_count} TourImage records")
print(f"   - Đã cập nhật: {updated_count} TourImage records")
print(f"   - Tổng cộng: {created_count + updated_count}/{len(tour_images)} tours")

if not_found:
    print(f"\n⚠️  Tours không tìm thấy trong database:")
    for name in not_found:
        print(f"   - {name}")
else:
    print("\n🎉 Tất cả tours đã được xử lý thành công!")
