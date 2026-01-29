
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
' Use default direction (top to bottom) but manipulate layout with arrows
skinparam packageStyle rectangle
skinparam usecase {
    BackgroundColor White
    BorderColor Black
    ArrowColor Black
}
skinparam actor {
    BackgroundColor White
    BorderColor Black
}

actor "Khách hàng" as KH
actor "Admin" as AD

' === SHARED / ACCOUNT (TOP) ===
usecase "Đăng nhập" as UC_Login
usecase "Đăng ký" as UC_Register

KH -up-> UC_Login
KH -up-> UC_Register
AD -up-> UC_Login

' === CUSTOMER SIDE (LEFT & BOTTOM) ===
usecase "Tìm kiếm Tour" as UC_Search
usecase "Xem chi tiết Tour" as UC_ViewTour
usecase "Đặt Tour (Booking)" as UC_BookTour

usecase "Quản lý cá nhân" as UC_Profile
usecase "Sửa thông tin" as UC_EditInfo
usecase "Đổi mật khẩu" as UC_ChangePass
usecase "Xem lịch sử đơn" as UC_ViewHistory

KH -left-> UC_Search
KH -left-> UC_ViewTour
KH -left-> UC_BookTour

KH -down-> UC_Profile
UC_Profile <.. UC_EditInfo : <<extend>>
UC_Profile <.. UC_ChangePass : <<extend>>
UC_Profile <.. UC_ViewHistory : <<extend>>

' === ADMIN SIDE (RIGHT & BOTTOM) ===
usecase "Quản lý Danh mục" as UC_ManageCat
usecase "Quản lý Tour" as UC_ManageTour
usecase "Quản lý Người dùng" as UC_ManageUser
usecase "Quản lý Đơn hàng" as UC_ManageBooking

' Detail Use Cases for Admin
usecase "Thêm/Sửa/Xóa Tour" as UC_CRUDTour
usecase "Duyệt/Hủy Đơn" as UC_ProcessBooking

AD -right-> UC_ManageCat
AD -right-> UC_ManageTour
AD -right-> UC_ManageUser
AD -right-> UC_ManageBooking

UC_ManageTour <.. UC_CRUDTour : <<include>>
UC_ManageBooking <.. UC_ProcessBooking : <<include>>

' Layout hints to keep actors central
KH -[hidden]right- AD

@enduml
"""

encoded = deflate_and_encode(plantuml_code)
print(f"http://www.plantuml.com/plantuml/svg/{encoded}")
