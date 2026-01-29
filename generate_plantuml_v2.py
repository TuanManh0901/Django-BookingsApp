
import zlib
import base64

def deflate_and_encode(text):
    zlibbed = zlib.compress(text.encode('utf-8'))[2:-4]
    return encode64(zlibbed)

def encode64(data):
    r = ""
    for i in range(0, len(data), 3):
        if i + 2 == len(data):
            r += append3bytes(data[i], data[i+1], 0)
        elif i + 1 == len(data):
            r += append3bytes(data[i], 0, 0)
        else:
            r += append3bytes(data[i], data[i+1], data[i+2])
    return r

def append3bytes(b1, b2, b3):
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    r = ""
    r += encode6bit(c1 & 0x3F)
    r += encode6bit(c2 & 0x3F)
    r += encode6bit(c3 & 0x3F)
    r += encode6bit(c4 & 0x3F)
    return r

def encode6bit(b):
    if b < 10:
        return chr(48 + b)
    b -= 10
    if b < 26:
        return chr(65 + b)
    b -= 26
    if b < 26:
        return chr(97 + b)
    b -= 26
    if b == 0:
        return '-'
    if b == 1:
        return '_'
    return '?'

plantuml_code = """
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Khách hàng" as KH
actor "Admin" as AD
actor "User" as US

rectangle "Hệ thống VN-Travel" {
    
    usecase "Đăng ký" as UC_Register
    usecase "Đăng nhập" as UC_Login
    usecase "Tìm kiếm Tour" as UC_Search
    usecase "Xem chi tiết Tour" as UC_ViewTour
    usecase "Đặt Tour (Booking)" as UC_BookTour
    
    usecase "Quản lý thông tin cá nhân" as UC_Profile
    usecase "Sửa thông tin" as UC_EditInfo
    usecase "Đổi mật khẩu" as UC_ChangePass
    usecase "Xem lịch sử đặt tour" as UC_ViewHistory
    
    usecase "Quản lý Danh mục" as UC_ManageCat
    usecase "Thêm danh mục" as UC_AddCat
    usecase "Sửa danh mục" as UC_EditCat
    usecase "Xóa danh mục" as UC_DelCat
    
    usecase "Quản lý Tour" as UC_ManageTour
    usecase "Thêm Tour mới" as UC_AddTour
    usecase "Cập nhật Tour" as UC_EditTour
    usecase "Xóa/Ẩn Tour" as UC_DelTour
    usecase "Tìm kiếm Tour (Admin)" as UC_SearchTourAdmin
    
    usecase "Quản lý Người dùng" as UC_ManageUser
    usecase "Khóa tài khoản" as UC_LockUser
    usecase "Reset mật khẩu" as UC_ResetPass
    
    usecase "Quản lý Đơn hàng (Booking)" as UC_ManageBooking
    usecase "Duyệt đơn hàng" as UC_ApproveBooking
    usecase "Hủy đơn hàng" as UC_CancelBooking
    usecase "Xem chi tiết đơn" as UC_ViewBookingDetail
}

KH --|> US
AD --|> US

KH --> UC_Register
KH --> UC_Login
KH --> UC_Search
KH --> UC_ViewTour
KH --> UC_BookTour
KH --> UC_Profile

UC_Profile <.. UC_EditInfo : <<extend>>
UC_Profile <.. UC_ChangePass : <<extend>>
UC_Profile <.. UC_ViewHistory : <<extend>>

AD --> UC_Login
AD --> UC_ManageCat
AD --> UC_ManageTour
AD --> UC_ManageUser
AD --> UC_ManageBooking

UC_ManageCat <.. UC_AddCat : <<extend>>
UC_ManageCat <.. UC_EditCat : <<extend>>
UC_ManageCat <.. UC_DelCat : <<extend>>

UC_ManageTour <.. UC_AddTour : <<extend>>
UC_ManageTour <.. UC_EditTour : <<extend>>
UC_ManageTour <.. UC_DelTour : <<extend>>
UC_ManageTour <.. UC_SearchTourAdmin : <<extend>>

UC_ManageUser <.. UC_LockUser : <<extend>>
UC_ManageUser <.. UC_ResetPass : <<extend>>

UC_ManageBooking <.. UC_ApproveBooking : <<extend>>
UC_ManageBooking <.. UC_CancelBooking : <<extend>>
UC_ManageBooking <.. UC_ViewBookingDetail : <<extend>>

@enduml
"""

encoded = deflate_and_encode(plantuml_code)
print(f"http://www.plantuml.com/plantuml/svg/{encoded}")
