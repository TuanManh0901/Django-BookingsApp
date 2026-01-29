
import zlib
import base64
import string

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

rectangle "Hệ thống Website VN-Travel" {
    
    usecase "Đăng ký" as UC_Register
    usecase "Đăng nhập" as UC_Login
    usecase "Tìm kiếm sản phẩm" as UC_Search
    usecase "Xem chi tiết sản phẩm" as UC_ViewTour
    
    usecase "Quản lý thông tin cá nhân" as UC_Profile
    usecase "Sửa thông tin cá nhân" as UC_EditInfo
    usecase "Đổi mật khẩu" as UC_ChangePass
    usecase "Xem đơn hàng" as UC_ViewOrder
    
    usecase "Quản lý giỏ hàng" as UC_Cart
    usecase "Thêm vào giỏ hàng" as UC_AddToCart
    usecase "Cập nhật giỏ hàng" as UC_UpdateCart
    usecase "Xóa khỏi giỏ hàng" as UC_RemoveCart
    
    usecase "Đặt hàng" as UC_Booking
    
    usecase "Quản lý danh mục" as UC_ManageCat
    usecase "Thêm danh mục" as UC_AddCat
    usecase "Sửa danh mục" as UC_EditCat
    usecase "Xóa danh mục" as UC_DelCat
    usecase "Tìm danh mục" as UC_SearchCat
    
    usecase "Quản lý mặt hàng" as UC_ManageProd
    usecase "Thêm mặt hàng" as UC_AddProd
    usecase "Sửa mặt hàng" as UC_EditProd
    usecase "Xóa mặt hàng" as UC_DelProd
    usecase "Tìm mặt hàng" as UC_SearchProd
    
    usecase "Quản lý người dùng" as UC_ManageUser
    usecase "Sửa thông tin" as UC_EditUser
    usecase "Xóa người dùng" as UC_DelUser
    
    usecase "Quản lý đơn hàng" as UC_ManageOrder
    usecase "Quản lý đơn hàng mới" as UC_ManageNewOrder
    usecase "Quản lý đơn đang giao" as UC_ManageDelivering
    usecase "Quản lý đơn thành công" as UC_ManageSuccess

    usecase "Tìm đơn mới" as UC_SearchNew
    usecase "Xóa đơn mới" as UC_DelNew
    usecase "Nhận đơn" as UC_AcceptOrder
    usecase "Xem chi tiết đơn" as UC_ViewDetailOrder

    usecase "Tìm đơn đang giao" as UC_SearchDelivering
    usecase "Hủy đơn" as UC_CancelOrder
    usecase "Xác nhận đã nhận hàng" as UC_ConfirmReceived

    usecase "Tìm đơn thành công" as UC_SearchSuccess
}

KH --|> US
AD --|> US

KH --> UC_Register
KH --> UC_Login
KH --> UC_Search
KH --> UC_ViewTour
KH --> UC_Profile
KH --> UC_Cart
KH --> UC_Booking

UC_Profile <.. UC_EditInfo : <<extend>>
UC_Profile <.. UC_ChangePass : <<extend>>
UC_Profile <.. UC_ViewOrder : <<extend>>

UC_Cart <.. UC_AddToCart : <<extend>>
UC_Cart <.. UC_UpdateCart : <<extend>>
UC_Cart <.. UC_RemoveCart : <<extend>>

AD --> UC_Login
AD --> UC_ManageCat
AD --> UC_ManageProd
AD --> UC_ManageUser
AD --> UC_ManageOrder

UC_ManageCat <.. UC_AddCat : <<extend>>
UC_ManageCat <.. UC_EditCat : <<extend>>
UC_ManageCat <.. UC_DelCat : <<extend>>
UC_ManageCat <.. UC_SearchCat : <<extend>>

UC_ManageProd <.. UC_AddProd : <<extend>>
UC_ManageProd <.. UC_EditProd : <<extend>>
UC_ManageProd <.. UC_DelProd : <<extend>>
UC_ManageProd <.. UC_SearchProd : <<extend>>

UC_ManageUser <.. UC_EditUser : <<extend>>
UC_ManageUser <.. UC_DelUser : <<extend>>

UC_ManageOrder <|-- UC_ManageNewOrder
UC_ManageOrder <|-- UC_ManageDelivering
UC_ManageOrder <|-- UC_ManageSuccess

UC_ManageNewOrder <.. UC_SearchNew : <<extend>>
UC_ManageNewOrder <.. UC_DelNew : <<extend>>
UC_ManageNewOrder <.. UC_AcceptOrder : <<extend>>
UC_ManageNewOrder <.. UC_ViewDetailOrder : <<extend>>

UC_ManageDelivering <.. UC_SearchDelivering : <<extend>>
UC_ManageDelivering <.. UC_CancelOrder : <<extend>>
UC_ManageDelivering <.. UC_ViewDetailOrder : <<extend>>
UC_ManageDelivering <.. UC_ConfirmReceived : <<extend>>

UC_ManageSuccess <.. UC_SearchSuccess : <<extend>>
UC_ManageSuccess <.. UC_ViewDetailOrder : <<extend>>

@enduml
"""

encoded = deflate_and_encode(plantuml_code)
print(f"http://www.plantuml.com/plantuml/svg/{encoded}")
