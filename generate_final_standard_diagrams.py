
import urllib.parse
import zlib
import base64

def encode_plantuml(plantuml_code):
    """Encodes PlantUML code to a URL-safe string."""
    zlibbed_str = zlib.compress(plantuml_code.encode('utf-8'))
    # Remove header/checksum/footer from zlib
    compressed_string = zlibbed_str[2:-4]
    return base64.urlsafe_b64encode(compressed_string).decode('utf-8')

def generate_uml_url(code):
    encoded = encode_plantuml(code)
    return f"http://www.plantuml.com/plantuml/svg/{encoded}"

use_cases = [
    {
        "id": "1",
        "name": "Đăng ký",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Đăng ký" {
    participant "Khách hàng"
    participant "form DangKy"
    participant "control_DangKy"
    participant "auth_user"

    autonumber
    activate "Khách hàng"
    "Khách hàng" -> "form DangKy" : Nhập thông tin tài khoản và xác nhận
    activate "form DangKy"
    "form DangKy" -> "control_DangKy" : Yêu cầu lưu thông tin
    activate "control_DangKy"
    "control_DangKy" -> "auth_user" : Lưu thông tin
    activate "auth_user"
    "auth_user" --> "control_DangKy" : Lưu thành công
    deactivate "auth_user"
    "control_DangKy" --> "form DangKy" : Thông báo đăng ký thành công
    deactivate "control_DangKy"
    deactivate "form DangKy"
    deactivate "Khách hàng"
}
@enduml
"""
    },
    {
        "id": "2",
        "name": "Đăng nhập",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Đăng nhập" {
    participant "Khách hàng"
    participant "form DangNhap"
    participant "control_DangNhap"
    participant "auth_user"

    autonumber
    activate "Khách hàng"
    "Khách hàng" -> "form DangNhap" : Nhập tên đăng nhập, mật khẩu
    activate "form DangNhap"
    "form DangNhap" -> "control_DangNhap" : Yêu cầu kiểm tra đăng nhập
    activate "control_DangNhap"
    "control_DangNhap" -> "auth_user" : Kiểm tra thông tin
    activate "auth_user"
    "auth_user" --> "control_DangNhap" : Kết quả (Đúng/Sai)
    deactivate "auth_user"
    "control_DangNhap" --> "form DangNhap" : Thông báo kết quả/Chuyển trang
    deactivate "control_DangNhap"
    deactivate "form DangNhap"
    deactivate "Khách hàng"
}
@enduml
"""
    },
    {
        "id": "3",
        "name": "Tìm kiếm Tour",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Tìm kiếm Tour" {
    participant "Khách hàng"
    participant "form TimKiem"
    participant "control_TimKiem"
    participant "tours_tour"

    autonumber
    activate "Khách hàng"
    "Khách hàng" -> "form TimKiem" : Nhập từ khóa/Chọn bộ lọc
    activate "form TimKiem"
    "form TimKiem" -> "control_TimKiem" : Gửi tiêu chí tìm kiếm
    activate "control_TimKiem"
    "control_TimKiem" -> "tours_tour" : Truy vấn danh sách tour
    activate "tours_tour"
    "tours_tour" --> "control_TimKiem" : Trả về danh sách tour
    deactivate "tours_tour"
    "control_TimKiem" --> "form TimKiem" : Hiển thị danh sách kết quả
    deactivate "control_TimKiem"
    deactivate "form TimKiem"
    deactivate "Khách hàng"
}
@enduml
"""
    },
    {
        "id": "4",
        "name": "Xem chi tiết Tour",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Xem chi tiết Tour" {
    participant "Khách hàng"
    participant "form ChiTietTour"
    participant "control_ChiTietTour"
    participant "tours_tour"

    autonumber
    activate "Khách hàng"
    "Khách hàng" -> "form ChiTietTour" : Chọn tour cần xem
    activate "form ChiTietTour"
    "form ChiTietTour" -> "control_ChiTietTour" : Yêu cầu lấy thông tin tour
    activate "control_ChiTietTour"
    "control_ChiTietTour" -> "tours_tour" : Lấy dữ liệu tour (ID)
    activate "tours_tour"
    "tours_tour" --> "control_ChiTietTour" : Trả về thông tin chi tiết
    deactivate "tours_tour"
    "control_ChiTietTour" --> "form ChiTietTour" : Hiển thị thông tin tour
    deactivate "control_ChiTietTour"
    deactivate "form ChiTietTour"
    deactivate "Khách hàng"
}
@enduml
"""
    },
    {
        "id": "5",
        "name": "Đặt Tour",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Đặt Tour" {
    participant "Khách hàng"
    participant "form DatTour"
    participant "control_DatTour"
    participant "bookings_booking"

    autonumber
    activate "Khách hàng"
    "Khách hàng" -> "form DatTour" : Nhập thông tin đặt tour
    activate "form DatTour"
    "form DatTour" -> "control_DatTour" : Gửi yêu cầu đặt tour
    activate "control_DatTour"
    "control_DatTour" -> "bookings_booking" : Kiểm tra và Lưu đơn hàng
    activate "bookings_booking"
    "bookings_booking" --> "control_DatTour" : Lưu thành công
    deactivate "bookings_booking"
    "control_DatTour" --> "form DatTour" : Chuyển sang bước thanh toán
    deactivate "control_DatTour"
    deactivate "form DatTour"
    deactivate "Khách hàng"
}
@enduml
"""
    },
    {
        "id": "6",
        "name": "Sửa thông tin cá nhân",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Sửa thông tin cá nhân" {
    participant "Khách hàng"
    participant "form SuaThongTin"
    participant "control_SuaThongTin"
    participant "auth_user"

    autonumber
    activate "Khách hàng"
    "Khách hàng" -> "form SuaThongTin" : Nhập thông tin mới
    activate "form SuaThongTin"
    "form SuaThongTin" -> "control_SuaThongTin" : Gửi yêu cầu cập nhật
    activate "control_SuaThongTin"
    "control_SuaThongTin" -> "auth_user" : Cập nhật dữ liệu
    activate "auth_user"
    "auth_user" --> "control_SuaThongTin" : Cập nhật thành công
    deactivate "auth_user"
    "control_SuaThongTin" --> "form SuaThongTin" : Thông báo thành công
    deactivate "control_SuaThongTin"
    deactivate "form SuaThongTin"
    deactivate "Khách hàng"
}
@enduml
"""
    },
    {
        "id": "7",
        "name": "Đổi mật khẩu",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Đổi mật khẩu" {
    participant "Khách hàng"
    participant "form DoiMatKhau"
    participant "control_DoiMatKhau"
    participant "auth_user"

    autonumber
    activate "Khách hàng"
    "Khách hàng" -> "form DoiMatKhau" : Nhập mật khẩu cũ, mới
    activate "form DoiMatKhau"
    "form DoiMatKhau" -> "control_DoiMatKhau" : Yêu cầu đổi mật khẩu
    activate "control_DoiMatKhau"
    "control_DoiMatKhau" -> "auth_user" : Kiểm tra và cập nhật
    activate "auth_user"
    "auth_user" --> "control_DoiMatKhau" : Kết quả cập nhật
    deactivate "auth_user"
    "control_DoiMatKhau" --> "form DoiMatKhau" : Thông báo kết quả
    deactivate "control_DoiMatKhau"
    deactivate "form DoiMatKhau"
    deactivate "Khách hàng"
}
@enduml
"""
    },
    {
        "id": "8",
        "name": "Xem lịch sử",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Xem lịch sử đơn hàng" {
    participant "Khách hàng"
    participant "form LichSu"
    participant "control_LichSu"
    participant "bookings_booking"

    autonumber
    activate "Khách hàng"
    "Khách hàng" -> "form LichSu" : Yêu cầu xem lịch sử
    activate "form LichSu"
    "form LichSu" -> "control_LichSu" : Lấy danh sách đơn hàng
    activate "control_LichSu"
    "control_LichSu" -> "bookings_booking" : Truy vấn đơn hàng của User
    activate "bookings_booking"
    "bookings_booking" --> "control_LichSu" : Trả về danh sách
    deactivate "bookings_booking"
    "control_LichSu" --> "form LichSu" : Hiển thị danh sách
    deactivate "control_LichSu"
    deactivate "form LichSu"
    deactivate "Khách hàng"
}
@enduml
"""
    },
    {
        "id": "9",
        "name": "Quản lý Danh mục",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Quản lý Danh mục" {
    participant "Admin"
    participant "form QLDanhMuc"
    participant "control_QLDanhMuc"
    participant "tours_category"

    autonumber
    activate "Admin"
    "Admin" -> "form QLDanhMuc" : Nhập thông tin danh mục
    activate "form QLDanhMuc"
    "form QLDanhMuc" -> "control_QLDanhMuc" : Yêu cầu Thêm/Sửa/Xóa
    activate "control_QLDanhMuc"
    "control_QLDanhMuc" -> "tours_category" : Thực thi lệnh DB
    activate "tours_category"
    "tours_category" --> "control_QLDanhMuc" : Kết quả thực thi
    deactivate "tours_category"
    "control_QLDanhMuc" --> "form QLDanhMuc" : Cập nhật danh sách hiển thị
    deactivate "control_QLDanhMuc"
    deactivate "form QLDanhMuc"
    deactivate "Admin"
}
@enduml
"""
    },
    {
        "id": "10",
        "name": "Quản lý Tour",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Quản lý Tour" {
    participant "Admin"
    participant "form QLTour"
    participant "control_QLTour"
    participant "tours_tour"

    autonumber
    activate "Admin"
    "Admin" -> "form QLTour" : Nhập thông tin Tour
    activate "form QLTour"
    "form QLTour" -> "control_QLTour" : Gửi dữ liệu Tour
    activate "control_QLTour"
    "control_QLTour" -> "tours_tour" : Lưu/Cập nhật Tour
    activate "tours_tour"
    "tours_tour" --> "control_QLTour" : Lưu thành công
    deactivate "tours_tour"
    "control_QLTour" --> "form QLTour" : Thông báo thành công
    deactivate "control_QLTour"
    deactivate "form QLTour"
    deactivate "Admin"
}
@enduml
"""
    },
    {
        "id": "11",
        "name": "Quản lý Đơn hàng",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Quản lý Đơn hàng" {
    participant "Admin"
    participant "form QLDonHang"
    participant "control_QLDonHang"
    participant "bookings_booking"

    autonumber
    activate "Admin"
    "Admin" -> "form QLDonHang" : Chọn đơn hàng cần xử lý
    activate "form QLDonHang"
    "form QLDonHang" -> "control_QLDonHang" : Gửi yêu cầu cập nhật trạng thái
    activate "control_QLDonHang"
    "control_QLDonHang" -> "bookings_booking" : Cập nhật trạng thái
    activate "bookings_booking"
    "bookings_booking" --> "control_QLDonHang" : Cập nhật thành công
    deactivate "bookings_booking"
    "control_QLDonHang" --> "form QLDonHang" : Thông báo đã cập nhật
    deactivate "control_QLDonHang"
    deactivate "form QLDonHang"
    deactivate "Admin"
}
@enduml
"""
    },
    {
        "id": "12",
        "name": "Quản lý User",
        "code": """
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case Quản lý Người dùng" {
    participant "Admin"
    participant "form QLNguoiDung"
    participant "control_QLNguoiDung"
    participant "auth_user"

    autonumber
    activate "Admin"
    "Admin" -> "form QLNguoiDung" : Chọn User cần khóa/mở
    activate "form QLNguoiDung"
    "form QLNguoiDung" -> "control_QLNguoiDung" : Gửi yêu cầu cập nhật status
    activate "control_QLNguoiDung"
    "control_QLNguoiDung" -> "auth_user" : Cập nhật bảng User
    activate "auth_user"
    "auth_user" --> "control_QLNguoiDung" : Thực hiện xong
    deactivate "auth_user"
    "control_QLNguoiDung" --> "form QLNguoiDung" : Refresh danh sách
    deactivate "control_QLNguoiDung"
    deactivate "form QLNguoiDung"
    deactivate "Admin"
}
@enduml
"""
    }
]

for uc in use_cases:
    url = generate_uml_url(uc['code'])
    print(f"URL_{uc['id']}: {url}")
