#!/usr/bin/env python
"""
Script to rename tours to correct capitalization
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vn_travel.settings')
django.setup()

from tours.models import Tour

renames = {
    "Buôn Ma Thuột - Mùa Hoa Cà Phê": "Buôn Ma Thuột - Mùa hoa cà phê",
    "Động Phong Nha - Kẻ Bàng: Kỳ Quan Đệ Nhất Động": "Động Phong Nha - Kẻ Bàng: Kỳ quan đệ nhất Động",
    "Săn Mây Tà Xùa - Thiên Đường Hạ Giới": "Săn mây Tà Xùa - Thiên đường hạ giới",
    "Khám phá Hà Giang - Mùa Hoa Tam Giác Mạch": "Khám phá Hà Giang - Mùa hoa Tam Giác Mạch"
}

print("Đang đổi tên các tours...")
print("=" * 60)

for old_name, new_name in renames.items():
    try:
        # Try to find by exact match first
        tour = Tour.objects.filter(name=old_name).first()
        
        if not tour:
            # Try case-insensitive match
            tour = Tour.objects.filter(name__iexact=old_name).first()
            
        if tour:
            print(f"🔄 Đổi: {tour.name}")
            print(f"   → {new_name}")
            tour.name = new_name
            tour.save()
            print("   ✅ Thành công")
        else:
            print(f"❌ Không tìm thấy tour: {old_name}")
            
    except Exception as e:
        print(f"⚠️ Lỗi khi xử lý {old_name}: {e}")

print("=" * 60)
print("🎉 Hoàn tất!")
