import urllib.parse
import zlib
import base64

def encode_plantuml(plantuml_code):
    """Encodes PlantUML code to a URL-safe string."""
    zlibbed_str = zlib.compress(plantuml_code.encode('utf-8'))
    compressed_string = zlibbed_str[2:-4]
    return base64.urlsafe_b64encode(compressed_string).decode('utf-8')

def generate_uml_url(code):
    encoded = encode_plantuml(code)
    return f"http://www.plantuml.com/plantuml/svg/{encoded}"

use_cases = [
    {
        "id": "Register",
        "name": "Đăng ký",
        "boundary": "form DangKy",
        "control": "control_DangKy",
        "entity": "tbl user",
        "steps": [
            ("Khách hàng", "form DangKy", "Nhập thông tin tài khoản và xác nhận"),
            ("form DangKy", "control_DangKy", "Yêu cầu lưu thông tin"),
            ("control_DangKy", "tbl user", "Lưu thông tin"),
            ("tbl user", "control_DangKy", "Lưu thành công"),
            ("control_DangKy", "form DangKy", "Thông báo đăng ký thành công")
        ]
    },
    {
        "id": "Login",
        "name": "Đăng nhập",
        "boundary": "form DangNhap",
        "control": "control_DangNhap",
        "entity": "tbl user",
        "steps": [
            ("Khách hàng", "form DangNhap", "Nhập tên đăng nhập, mật khẩu"),
            ("form DangNhap", "control_DangNhap", "Yêu cầu kiểm tra đăng nhập"),
            ("control_DangNhap", "tbl user", "Kiểm tra thông tin"),
            ("tbl user", "control_DangNhap", "Kết quả (Đúng/Sai)"),
            ("control_DangNhap", "form DangNhap", "Thông báo kết quả/Chuyển trang")
        ]
    },
    {
        "id": "Search",
        "name": "Tìm kiếm Tour",
        "boundary": "form TimKiem",
        "control": "control_TimKiem",
        "entity": "tbl tour",
        "steps": [
            ("Khách hàng", "form TimKiem", "Nhập từ khóa/Chọn bộ lọc"),
            ("form TimKiem", "control_TimKiem", "Gửi tiêu chí tìm kiếm"),
            ("control_TimKiem", "tbl tour", "Truy vấn danh sách tour"),
            ("tbl tour", "control_TimKiem", "Trả về danh sách tour"),
            ("control_TimKiem", "form TimKiem", "Hiển thị danh sách kết quả")
        ]
    },
    {
        "id": "ViewDetail",
        "name": "Xem chi tiết Tour",
        "boundary": "form ChiTietTour",
        "control": "control_ChiTietTour",
        "entity": "tbl tour",
        "steps": [
            ("Khách hàng", "form ChiTietTour", "Chọn tour cần xem"),
            ("form ChiTietTour", "control_ChiTietTour", "Yêu cầu lấy thông tin tour"),
            ("control_ChiTietTour", "tbl tour", "Lấy dữ liệu tour (ID)"),
            ("tbl tour", "control_ChiTietTour", "Trả về thông tin chi tiết"),
            ("control_ChiTietTour", "form ChiTietTour", "Hiển thị thông tin tour")
        ]
    },
    {
        "id": "Booking",
        "name": "Đặt Tour",
        "boundary": "form DatTour",
        "control": "control_DatTour",
        "entity": "tbl booking",
        "steps": [
            ("Khách hàng", "form DatTour", "Nhập thông tin đặt tour (Ngày, SL)"),
            ("form DatTour", "control_DatTour", "Gửi yêu cầu đặt tour"),
            ("control_DatTour", "tbl booking", "Kiểm tra và Lưu đơn hàng"),
            ("tbl booking", "control_DatTour", "Lưu thành công"),
            ("control_DatTour", "form DatTour", "Chuyển sang bước thanh toán")
        ]
    },
    {
        "id": "EditProfile",
        "name": "Sửa thông tin cá nhân",
        "boundary": "form SuaThongTin",
        "control": "control_SuaThongTin",
        "entity": "tbl user",
        "steps": [
            ("Khách hàng", "form SuaThongTin", "Nhập thông tin mới"),
            ("form SuaThongTin", "control_SuaThongTin", "Gửi yêu cầu cập nhật"),
            ("control_SuaThongTin", "tbl user", "Cập nhật dữ liệu"),
            ("tbl user", "control_SuaThongTin", "Cập nhật thành công"),
            ("control_SuaThongTin", "form SuaThongTin", "Thông báo thành công")
        ]
    },
    {
        "id": "ChangePassword",
        "name": "Đổi mật khẩu",
        "boundary": "form DoiMatKhau",
        "control": "control_DoiMatKhau",
        "entity": "tbl user",
        "steps": [
            ("Khách hàng", "form DoiMatKhau", "Nhập mật khẩu cũ, mới"),
            ("form DoiMatKhau", "control_DoiMatKhau", "Yêu cầu đổi mật khẩu"),
            ("control_DoiMatKhau", "tbl user", "Kiểm tra và cập nhật"),
            ("tbl user", "control_DoiMatKhau", "Kết quả cập nhật"),
            ("control_DoiMatKhau", "form DoiMatKhau", "Thông báo kết quả")
        ]
    },
    {
        "id": "ViewHistory",
        "name": "Xem lịch sử đơn hàng",
        "boundary": "form LichSu",
        "control": "control_LichSu",
        "entity": "tbl booking",
        "steps": [
            ("Khách hàng", "form LichSu", "Yêu cầu xem lịch sử"),
            ("form LichSu", "control_LichSu", "Lấy danh sách đơn hàng"),
            ("control_LichSu", "tbl booking", "Truy vấn đơn hàng của User"),
            ("tbl booking", "control_LichSu", "Trả về danh sách"),
            ("control_LichSu", "form LichSu", "Hiển thị danh sách")
        ]
    },
    {
        "id": "ManageCategory",
        "name": "Quản lý Danh mục",
        "boundary": "form QLDanhMuc",
        "control": "control_QLDanhMuc",
        "entity": "tbl category",
        "steps": [
            ("Admin", "form QLDanhMuc", "Nhập thông tin danh mục"),
            ("form QLDanhMuc", "control_QLDanhMuc", "Yêu cầu Thêm/Sửa/Xóa"),
            ("control_QLDanhMuc", "tbl category", "Thực thi lệnh DB"),
            ("tbl category", "control_QLDanhMuc", "Kết quả thực thi"),
            ("control_QLDanhMuc", "form QLDanhMuc", "Cập nhật danh sách hiển thị")
        ]
    },
    {
        "id": "ManageTour",
        "name": "Quản lý Tour",
        "boundary": "form QLTour",
        "control": "control_QLTour",
        "entity": "tbl tour",
        "steps": [
            ("Admin", "form QLTour", "Nhập thông tin Tour"),
            ("form QLTour", "control_QLTour", "Gửi dữ liệu Tour"),
            ("control_QLTour", "tbl tour", "Lưu/Cập nhật Tour"),
            ("tbl tour", "control_QLTour", "Lưu thành công"),
            ("control_QLTour", "form QLTour", "Thông báo thành công")
        ]
    },
    {
        "id": "ManageBooking",
        "name": "Quản lý Đơn hàng",
        "boundary": "form QLDonHang",
        "control": "control_QLDonHang",
        "entity": "tbl booking",
        "steps": [
            ("Admin", "form QLDonHang", "Chọn đơn hàng cần xử lý"),
            ("form QLDonHang", "control_QLDonHang", "Gửi yêu cầu cập nhật trạng thái"),
            ("control_QLDonHang", "tbl booking", "Cập nhật trạng thái"),
            ("tbl booking", "control_QLDonHang", "Cập nhật thành công"),
            ("control_QLDonHang", "form QLDonHang", "Thông báo đã cập nhật")
        ]
    },
    {
        "id": "ManageUser",
        "name": "Quản lý Người dùng",
        "boundary": "form QLNguoiDung",
        "control": "control_QLNguoiDung",
        "entity": "tbl user",
        "steps": [
            ("Admin", "form QLNguoiDung", "Chọn User cần khóa/mở"),
            ("form QLNguoiDung", "control_QLNguoiDung", "Gửi yêu cầu cập nhật status"),
            ("control_QLNguoiDung", "tbl user", "Cập nhật bảng User"),
            ("tbl user", "control_QLNguoiDung", "Thực hiện xong"),
            ("control_QLNguoiDung", "form QLNguoiDung", "Refresh danh sách")
        ]
    }
]

for uc in use_cases:
    code = f"""
@startuml
skinparam style strictuml
hide footbox
skinparam sequenceMessageAlign center

frame "sd Biểu đồ tuần tự use case {uc['name']}" {{
    participant "Khách hàng" as Actor
    participant "{uc['boundary']}" as Boundary
    participant "{uc['control']}" as Control
    participant "{uc['entity']}" as Entity
"""
    if uc['id'].startswith("Manage"):
        code = code.replace('"Khách hàng" as Actor', '"Admin" as Actor')

    code += "\n    autonumber\n"
    
    # Activation logic: Activate roughly closely to the flow
    code += "    activate Actor\n"
    
    for src, dst, msg in uc['steps']:
        # Mapping names to aliases
        src_alias = "Actor" if src in ["Khách hàng", "Admin"] else "Boundary" if src == uc['boundary'] else "Control" if src == uc['control'] else "Entity"
        dst_alias = "Actor" if dst in ["Khách hàng", "Admin"] else "Boundary" if dst == uc['boundary'] else "Control" if dst == uc['control'] else "Entity"
        
        code += f'    {src_alias} -> {dst_alias} : {msg}\n'
        
        # Simple activation logic mimicking the diagonal flow in the image
        if src_alias == "Actor" and dst_alias == "Boundary":
            code += f'    activate {dst_alias}\n'
        elif src_alias == "Boundary" and dst_alias == "Control":
            code += f'    activate {dst_alias}\n'
        elif src_alias == "Control" and dst_alias == "Entity":
            code += f'    activate {dst_alias}\n'
        elif src_alias == "Entity" and dst_alias == "Control":
            code += f'    deactivate {src_alias}\n'
        elif src_alias == "Control" and dst_alias == "Boundary":
            code += f'    deactivate {src_alias}\n'
            
    code += "    deactivate Boundary\n"
    code += "    deactivate Actor\n"
    code += "}\n@enduml"
    
    url = generate_uml_url(code)
    print(f"URL_{uc['id']}: {url}")
