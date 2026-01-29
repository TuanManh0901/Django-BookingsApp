
import os

file_path = "/Users/tuanmanh/Phát triển hệ thống đặt tour du lịch thông minh với AI Travel Advisor cho công ty VN-Travel/BAOCAO_KLTN_DRAFT.md"

new_content = """### 3.3 CHI TIẾT CÁC USE CASE CHÍNH

Dưới đây là chi tiết các Use Case chính của hệ thống, được phân tích đầy đủ dựa trên nghiệp vụ thực tế và sơ đồ Use Case tổng quát.

**3.3.0 Biểu đồ Use Case Tổng quát**

```mermaid
usecaseDiagram
    actor KH as "Khách hàng"
    actor AD as "Admin"

    %% Nhóm Account
    usecase UC_Login as "Đăng nhập"
    usecase UC_Register as "Đăng ký"
    usecase UC_Profile as "Quản lý thông tin cá nhân"
    usecase UC_EditProfile as "Sửa thông tin cá nhân"
    usecase UC_ChangePass as "Đổi mật khẩu"
    usecase UC_ViewOrders as "Xem lịch sử đơn hàng"

    %% Nhóm Product/Tour
    usecase UC_Search as "Tìm kiếm Tour"
    usecase UC_ViewTour as "Xem chi tiết Tour"
    usecase UC_Booking as "Đặt Tour (Booking)"

    %% Nhóm Admin
    usecase UC_ManageCat as "Quản lý Danh mục"
    usecase UC_ManageTour as "Quản lý Tour"
    usecase UC_ManageBooking as "Quản lý Đơn hàng (Booking)"
    usecase UC_ManageUser as "Quản lý Người dùng"

    %% Relationships
    KH --> UC_Register
    KH --> UC_Login
    KH --> UC_Search
    KH --> UC_ViewTour
    KH --> UC_Booking
    KH --> UC_Profile
    
    UC_Profile <.. UC_EditProfile : <<extend>>
    UC_Profile <.. UC_ChangePass : <<extend>>
    UC_Profile <.. UC_ViewOrders : <<extend>>

    AD --> UC_Login
    AD --> UC_ManageCat
    AD --> UC_ManageTour
    AD --> UC_ManageBooking
    AD --> UC_ManageUser
```

#### 3.3.1 Nhóm Use Case Khách hàng

**3.3.1 Đăng ký tài khoản**
*   **Actor:** Khách hàng.
*   **Mục đích:** Khách hàng chưa có tài khoản đăng ký mới để sử dụng dịch vụ.
*   **Mô tả từng bước:**
    *   *B1:* Khách hàng truy cập trang Đăng ký, nhập thông tin: Họ tên, Email, Tên đăng nhập, Mật khẩu, Xác nhận mật khẩu.
    *   *B2:* Hệ thống kiểm tra tính hợp lệ (Email đúng định dạng, Mật khẩu khớp, Username chưa tồn tại).
    *   *B3:* Nếu thông tin hợp lệ, hệ thống tạo tài khoản mới và lưu vào cơ sở dữ liệu.
    *   *B4:* Hệ thống thông báo "Đăng ký thành công" và chuyển hướng về trang đăng nhập.
*   **Tiền điều kiện:** Khách hàng chưa đăng nhập, thông tin chưa tồn tại trong hệ thống.
*   **Hậu điều kiện:** Tài khoản được tạo, khách hàng có thể đăng nhập.

**3.3.2 Đăng nhập**
*   **Actor:** User (Khách hàng & Admin).
*   **Mục đích:** Truy cập vào hệ thống để sử dụng các chức năng phân quyền.
*   **Mô tả từng bước:**
    *   *B1:* Người dùng truy cập form đăng nhập, nhập Tên đăng nhập và Mật khẩu.
    *   *B2:* Hệ thống xác thực thông tin với cơ sở dữ liệu.
    *   *B3:* Nếu đúng, hệ thống cấp quyền truy cập (Session) và chuyển hướng tới trang chủ (với Khách) hoặc Dashboard (với Admin).
    *   *B4:* Nếu sai, thông báo lỗi "Tên đăng nhập hoặc mật khẩu không đúng".
*   **Tiền điều kiện:** Tài khoản đã được kích hoạt.
*   **Hậu điều kiện:** Người dùng đăng nhập thành công vào hệ thống.

**3.3.3 Tìm kiếm Tour**
*   **Actor:** Khách hàng.
*   **Mục đích:** Tìm kiếm các tour du lịch phù hợp theo nhu cầu (địa điểm, giá cả).
*   **Mô tả từng bước:**
    *   *B1:* Tại trang chủ hoặc trang Danh sách Tour, khách hàng nhập từ khóa hoặc chọn bộ lọc (Giá, Điểm đến).
    *   *B2:* Hệ thống truy vấn cơ sở dữ liệu dựa trên tiêu chí tìm kiếm.
    *   *B3:* Hệ thống hiển thị danh sách các Tour thỏa mãn điều kiện.
*   **Tiền điều kiện:** Không có.
*   **Hậu điều kiện:** Danh sách tour phù hợp được hiển thị.

**3.3.4 Xem chi tiết Tour**
*   **Actor:** Khách hàng.
*   **Mục đích:** Xem thông tin chi tiết về lịch trình, giá vé, hình ảnh của một tour cụ thể.
*   **Mô tả từng bước:**
    *   *B1:* Khách hàng click vào hình ảnh hoặc tên của một Tour trong danh sách.
    *   *B2:* Hệ thống tải dữ liệu chi tiết của Tour đó (Mô tả, Lịch trình, Giá, Ảnh, Bản đồ).
    *   *B3:* Hệ thống hiển thị trang Chi tiết Tour.
*   **Tiền điều kiện:** Tour tồn tại trong hệ thống.
*   **Hậu điều kiện:** Khách hàng nắm được đầy đủ thông tin tour.

**3.3.5 Đặt Tour (Booking)**
*   **Actor:** Khách hàng.
*   **Mục đích:** Tạo yêu cầu đặt chỗ cho tour đã chọn.
*   **Mô tả từng bước:**
    *   *B1:* Tại trang chi tiết tour, khách hàng nhấn nút "Đặt ngay".
    *   *B2:* Hệ thống hiển thị form đặt tour (Khách hàng nhập: Số lượng người lớn, Trẻ em, Ngày khởi hành).
    *   *B3:* Khách hàng xác nhận thông tin và nhấn "Xác nhận đặt tour".
    *   *B4:* Hệ thống kiểm tra số chỗ trống (Concurrency Check). Nếu đủ chỗ, hệ thống tạo Booking mới.
    *   *B5:* Hệ thống chuyển hướng sang trang thanh toán/chi tiết đơn hàng.
*   **Tiền điều kiện:** Khách hàng đã đăng nhập, Tour còn chỗ trống.
*   **Hậu điều kiện:** Đơn hàng được tạo với trạng thái ban đầu (Chờ thanh toán).

**3.3.6 Sửa thông tin cá nhân**
*   **Actor:** Khách hàng.
*   **Mục đích:** Cập nhật thông tin hồ sơ (Họ tên, SĐT, Địa chỉ, Avatar).
*   **Mô tả từng bước:**
    *   *B1:* Khách hàng truy cập trang "Hồ sơ cá nhân".
    *   *B2:* Chọn "Chỉnh sửa thông tin".
    *   *B3:* Nhập các thông tin mới cần thay đổi.
    *   *B4:* Nhấn "Lưu thay đổi".
    *   *B5:* Hệ thống cập nhật thông tin vào CSDL và thông báo thành công.
*   **Tiền điều kiện:** Đã đăng nhập.
*   **Hậu điều kiện:** Thông tin profile được cập nhật.

**3.3.7 Đổi mật khẩu**
*   **Actor:** Khách hàng.
*   **Mục đích:** Thay đổi mật khẩu đăng nhập để bảo mật tài khoản.
*   **Mô tả từng bước:**
    *   *B1:* Tại trang "Hồ sơ cá nhân", khách hàng chọn tab "Đổi mật khẩu".
    *   *B2:* Nhập Mật khẩu hiện tại, Mật khẩu mới và Nhập lại mật khẩu mới.
    *   *B3:* Hệ thống kiểm tra mật khẩu hiện tại có đúng không và mật khẩu mới có khớp không.
    *   *B4:* Nếu đúng, hệ thống cập nhật mật khẩu mới (đã mã hóa) vào DB. Thông báo thành công.
*   **Tiền điều kiện:** Đã đăng nhập.
*   **Hậu điều kiện:** Mật khẩu đăng nhập được thay đổi.

**3.3.8 Xem lịch sử đơn hàng (Quản lý Booking cá nhân)**
*   **Actor:** Khách hàng.
*   **Mục đích:** Theo dõi trạng thái, xem lại thông tin các tour đã đặt.
*   **Mô tả từng bước:**
    *   *B1:* Khách hàng truy cập menu "Booking của tôi".
    *   *B2:* Hệ thống hiển thị danh sách các đơn hàng (Mã đơn, Tên tour, Ngày đi, Tổng tiền, Trạng thái).
    *   *B3:* Khách hàng nhấn "Xem chi tiết" vào một đơn cụ thể để xem thông tin vé/thanh toán.
*   **Tiền điều kiện:** Đã đăng nhập.
*   **Hậu điều kiện:** Danh sách đơn hàng được hiển thị.

#### 3.3.2 Nhóm Use Case Admin (Quản trị viên)

**3.3.9 Quản lý Danh mục Tour**
*   **Actor:** Admin.
*   **Mục đích:** Quản lý các nhóm tour (Ví dụ: Miền Bắc, Miền Trung, Biển, Núi).
*   **Mô tả từng bước (Luồng Thêm mới):**
    *   *B1:* Admin truy cập trang "Quản lý Danh mục".
    *   *B2:* Nhấn "Thêm danh mục".
    *   *B3:* Nhập tên danh mục, mô tả.
    *   *B4:* Nhấn "Lưu". Hệ thống thêm danh mục mới vào CSDL.
*   **Tiền điều kiện:** Admin đã đăng nhập.
*   **Hậu điều kiện:** Danh mục mới xuất hiện trên hệ thống.

**3.3.10 Quản lý Tour (Sản phẩm)**
*   **Actor:** Admin.
*   **Mục đích:** Quản lý kho tour (Thêm mới, Cập nhật thông tin, Xóa/Ẩn tour).
*   **Mô tả từng bước (Luồng Thêm mới):**
    *   *B1:* Admin vào mục "Quản lý Tour", nhấn "Thêm Tour".
    *   *B2:* Nhập thông tin chi tiết: Tên tour, Danh mục, Giá, Số chỗ, Lịch trình (JSON), Upload hình ảnh.
    *   *B3:* Nhấn "Lưu". Hệ thống validate và lưu dữ liệu.
*   **Tiền điều kiện:** Admin đã đăng nhập.
*   **Hậu điều kiện:** Tour được đăng bán trên website.

**3.3.11 Quản lý Đơn hàng (Booking)**
*   **Actor:** Admin.
*   **Mục đích:** Xử lý và theo dõi các đơn đặt tour của khách hàng.
*   **Mô tả từng bước (Luồng Duyệt đơn):**
    *   *B1:* Admin xem danh sách Booking, lọc các đơn "Chờ thanh toán" hoặc "Đã thanh toán".
    *   *B2:* Admin xem chi tiết đơn hàng, kiểm tra thông tin thanh toán (đối chiếu MoMo).
    *   *B3:* Admin cập nhật trạng thái đơn (Ví dụ: Đã xác nhận/Hoàn thành).
    *   *B4:* Hệ thống lưu trạng thái mới và (tùy chọn) gửi email thông báo cho khách.
*   **Tiền điều kiện:** Có đơn hàng trong hệ thống.
*   **Hậu điều kiện:** Trạng thái đơn hàng được cập nhật.

**3.3.12 Quản lý Người dùng**
*   **Actor:** Admin.
*   **Mục đích:** Quản lý tài khoản khách hàng, hỗ trợ hoặc khóa tài khoản vi phạm.
*   **Mô tả từng bước:**
    *   *B1:* Admin truy cập danh sách "Người dùng".
    *   *B2:* Tìm kiếm khách hàng theo tên hoặc email.
    *   *B3:* Chọn "Sửa" để cập nhật thông tin hoặc "Khóa" để vô hiệu hóa tài khoản.
    *   *B4:* Xác nhận hành động.
*   **Tiền điều kiện:** Admin đã đăng nhập.
*   **Hậu điều kiện:** Thông tin/trạng thái người dùng thay đổi.

"""

with open(file_path, 'r', encoding='utf-8') as f:
    orig_content = f.read()

start_marker = "### 3.3 CHI TIẾT CÁC USE CASE CHÍNH"
end_marker = "### 3.4 THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE SCHEMA)"

start_idx = orig_content.find(start_marker)
end_idx = orig_content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    final_content = orig_content[:start_idx] + new_content + orig_content[end_idx:]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("Successfully updated BAOCAO_KLTN_DRAFT.md Section 3.3")
else:
    print("Could not find start/end markers in markdown file.")
    print(f"Start: {start_idx}, End: {end_idx}")
