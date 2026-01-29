
import os

file_path = "/Users/tuanmanh/Phát triển hệ thống đặt tour du lịch thông minh với AI Travel Advisor cho công ty VN-Travel/BAOCAO_KLTN_DRAFT.html"

new_section_33 = """    <h3>3.3 CHI TIẾT CÁC USE CASE CHÍNH</h3>

    <p>Dưới đây là chi tiết các Use Case chính của hệ thống, được phân tích đầy đủ dựa trên nghiệp vụ thực tế và sơ đồ Use Case tổng quát.</p>

    <p><strong>3.3.0 Biểu đồ Use Case Tổng quát</strong></p>

    <!-- MERMAID DIAGRAM -->
    <div class="mermaid">
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
    
    UC_Profile <.. UC_EditProfile : &lt;&lt;extend&gt;&gt;
    UC_Profile <.. UC_ChangePass : &lt;&lt;extend&gt;&gt;
    UC_Profile <.. UC_ViewOrders : &lt;&lt;extend&gt;&gt;

    AD --> UC_Login
    AD --> UC_ManageCat
    AD --> UC_ManageTour
    AD --> UC_ManageBooking
    AD --> UC_ManageUser
    </div>

    <h4>3.3.1 Nhóm Use Case Khách hàng</h4>

    <p><strong>3.3.1 Đăng ký tài khoản</strong></p>
    <ul>
        <li><strong>Actor:</strong> Khách hàng.</li>
        <li><strong>Mục đích:</strong> Khách hàng chưa có tài khoản đăng ký mới để sử dụng dịch vụ.</li>
        <li><strong>Mô tả từng bước:</strong>
            <ul>
                <li><em>B1:</em> Khách hàng truy cập trang Đăng ký, nhập thông tin: Họ tên, Email, Tên đăng nhập, Mật khẩu, Xác nhận mật khẩu.</li>
                <li><em>B2:</em> Hệ thống kiểm tra tính hợp lệ (Email đúng định dạng, Mật khẩu khớp, Username chưa tồn tại).</li>
                <li><em>B3:</em> Nếu thông tin hợp lệ, hệ thống tạo tài khoản mới và lưu vào cơ sở dữ liệu.</li>
                <li><em>B4:</em> Hệ thống thông báo "Đăng ký thành công" và chuyển hướng về trang đăng nhập.</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Khách hàng chưa đăng nhập, thông tin chưa tồn tại trong hệ thống.</li>
        <li><strong>Hậu điều kiện:</strong> Tài khoản được tạo, khách hàng có thể đăng nhập.</li>
    </ul>

    <p><strong>3.3.2 Đăng nhập</strong></p>
    <ul>
        <li><strong>Actor:</strong> User (Khách hàng & Admin).</li>
        <li><strong>Mục đích:</strong> Truy cập vào hệ thống để sử dụng các chức năng phân quyền.</li>
        <li><strong>Mô tả từng bước:</strong>
            <ul>
                <li><em>B1:</em> Người dùng truy cập form đăng nhập, nhập Tên đăng nhập và Mật khẩu.</li>
                <li><em>B2:</em> Hệ thống xác thực thông tin với cơ sở dữ liệu.</li>
                <li><em>B3:</em> Nếu đúng, hệ thống cấp quyền truy cập (Session) và chuyển hướng tới trang chủ (với Khách) hoặc Dashboard (với Admin).</li>
                <li><em>B4:</em> Nếu sai, thông báo lỗi "Tên đăng nhập hoặc mật khẩu không đúng".</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Tài khoản đã được kích hoạt.</li>
        <li><strong>Hậu điều kiện:</strong> Người dùng đăng nhập thành công vào hệ thống.</li>
    </ul>

    <p><strong>3.3.3 Tìm kiếm Tour</strong></p>
    <ul>
        <li><strong>Actor:</strong> Khách hàng.</li>
        <li><strong>Mục đích:</strong> Tìm kiếm các tour du lịch phù hợp theo nhu cầu (địa điểm, giá cả).</li>
        <li><strong>Mô tả từng bước:</strong>
            <ul>
                <li><em>B1:</em> Tại trang chủ hoặc trang Danh sách Tour, khách hàng nhập từ khóa hoặc chọn bộ lọc (Giá, Điểm đến).</li>
                <li><em>B2:</em> Hệ thống truy vấn cơ sở dữ liệu dựa trên tiêu chí tìm kiếm.</li>
                <li><em>B3:</em> Hệ thống hiển thị danh sách các Tour thỏa mãn điều kiện.</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Không có.</li>
        <li><strong>Hậu điều kiện:</strong> Danh sách tour phù hợp được hiển thị.</li>
    </ul>

    <p><strong>3.3.4 Xem chi tiết Tour</strong></p>
    <ul>
        <li><strong>Actor:</strong> Khách hàng.</li>
        <li><strong>Mục đích:</strong> Xem thông tin chi tiết về lịch trình, giá vé, hình ảnh của một tour cụ thể.</li>
        <li><strong>Mô tả từng bước:</strong>
            <ul>
                <li><em>B1:</em> Khách hàng click vào hình ảnh hoặc tên của một Tour trong danh sách.</li>
                <li><em>B2:</em> Hệ thống tải dữ liệu chi tiết của Tour đó (Mô tả, Lịch trình, Giá, Ảnh, Bản đồ).</li>
                <li><em>B3:</em> Hệ thống hiển thị trang Chi tiết Tour.</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Tour tồn tại trong hệ thống.</li>
        <li><strong>Hậu điều kiện:</strong> Khách hàng nắm được đầy đủ thông tin tour.</li>
    </ul>

    <p><strong>3.3.5 Đặt Tour (Booking)</strong></p>
    <ul>
        <li><strong>Actor:</strong> Khách hàng.</li>
        <li><strong>Mục đích:</strong> Tạo yêu cầu đặt chỗ cho tour đã chọn.</li>
        <li><strong>Mô tả từng bước:</strong>
            <ul>
                <li><em>B1:</em> Tại trang chi tiết tour, khách hàng nhấn nút "Đặt ngay".</li>
                <li><em>B2:</em> Hệ thống hiển thị form đặt tour (Khách hàng nhập: Số lượng người lớn, Trẻ em, Ngày khởi hành).</li>
                <li><em>B3:</em> Khách hàng xác nhận thông tin và nhấn "Xác nhận đặt tour".</li>
                <li><em>B4:</em> Hệ thống kiểm tra số chỗ trống (Concurrency Check). Nếu đủ chỗ, hệ thống tạo Booking mới.</li>
                <li><em>B5:</em> Hệ thống chuyển hướng sang trang thanh toán/chi tiết đơn hàng.</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Khách hàng đã đăng nhập, Tour còn chỗ trống.</li>
        <li><strong>Hậu điều kiện:</strong> Đơn hàng được tạo với trạng thái ban đầu (Chờ thanh toán).</li>
    </ul>

    <p><strong>3.3.6 Sửa thông tin cá nhân</strong></p>
    <ul>
        <li><strong>Actor:</strong> Khách hàng.</li>
        <li><strong>Mục đích:</strong> Cập nhật thông tin hồ sơ (Họ tên, SĐT, Địa chỉ, Avatar).</li>
        <li><strong>Mô tả từng bước:</strong>
            <ul>
                <li><em>B1:</em> Khách hàng truy cập trang "Hồ sơ cá nhân".</li>
                <li><em>B2:</em> Chọn "Chỉnh sửa thông tin".</li>
                <li><em>B3:</em> Nhập các thông tin mới cần thay đổi.</li>
                <li><em>B4:</em> Nhấn "Lưu thay đổi".</li>
                <li><em>B5:</em> Hệ thống cập nhật thông tin vào CSDL và thông báo thành công.</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Đã đăng nhập.</li>
        <li><strong>Hậu điều kiện:</strong> Thông tin profile được cập nhật.</li>
    </ul>

    <p><strong>3.3.7 Đổi mật khẩu</strong></p>
    <ul>
        <li><strong>Actor:</strong> Khách hàng.</li>
        <li><strong>Mục đích:</strong> Thay đổi mật khẩu đăng nhập để bảo mật tài khoản.</li>
        <li><strong>Mô tả từng bước:</strong>
            <ul>
                <li><em>B1:</em> Tại trang "Hồ sơ cá nhân", khách hàng chọn tab "Đổi mật khẩu".</li>
                <li><em>B2:</em> Nhập Mật khẩu hiện tại, Mật khẩu mới và Nhập lại mật khẩu mới.</li>
                <li><em>B3:</em> Hệ thống kiểm tra mật khẩu hiện tại có đúng không và mật khẩu mới có khớp không.</li>
                <li><em>B4:</em> Nếu đúng, hệ thống cập nhật mật khẩu mới (đã mã hóa) vào DB. Thông báo thành công.</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Đã đăng nhập.</li>
        <li><strong>Hậu điều kiện:</strong> Mật khẩu đăng nhập được thay đổi.</li>
    </ul>

    <p><strong>3.3.8 Xem lịch sử đơn hàng (Quản lý Booking cá nhân)</strong></p>
    <ul>
        <li><strong>Actor:</strong> Khách hàng.</li>
        <li><strong>Mục đích:</strong> Theo dõi trạng thái, xem lại thông tin các tour đã đặt.</li>
        <li><strong>Mô tả từng bước:</strong>
            <ul>
                <li><em>B1:</em> Khách hàng truy cập menu "Booking của tôi".</li>
                <li><em>B2:</em> Hệ thống hiển thị danh sách các đơn hàng (Mã đơn, Tên tour, Ngày đi, Tổng tiền, Trạng thái).</li>
                <li><em>B3:</em> Khách hàng nhấn "Xem chi tiết" vào một đơn cụ thể để xem thông tin vé/thanh toán.</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Đã đăng nhập.</li>
        <li><strong>Hậu điều kiện:</strong> Danh sách đơn hàng được hiển thị.</li>
    </ul>

    <h4>3.3.2 Nhóm Use Case Admin (Quản trị viên)</h4>

    <p><strong>3.3.9 Quản lý Danh mục Tour</strong></p>
    <ul>
        <li><strong>Actor:</strong> Admin.</li>
        <li><strong>Mục đích:</strong> Quản lý các nhóm tour (Ví dụ: Miền Bắc, Miền Trung, Biển, Núi).</li>
        <li><strong>Mô tả từng bước (Luồng Thêm mới):</strong>
            <ul>
                <li><em>B1:</em> Admin truy cập trang "Quản lý Danh mục".</li>
                <li><em>B2:</em> Nhấn "Thêm danh mục".</li>
                <li><em>B3:</em> Nhập tên danh mục, mô tả.</li>
                <li><em>B4:</em> Nhấn "Lưu". Hệ thống thêm danh mục mới vào CSDL.</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Admin đã đăng nhập.</li>
        <li><strong>Hậu điều kiện:</strong> Danh mục mới xuất hiện trên hệ thống.</li>
    </ul>

    <p><strong>3.3.10 Quản lý Tour (Sản phẩm)</strong></p>
    <ul>
        <li><strong>Actor:</strong> Admin.</li>
        <li><strong>Mục đích:</strong> Quản lý kho tour (Thêm mới, Cập nhật thông tin, Xóa/Ẩn tour).</li>
        <li><strong>Mô tả từng bước (Luồng Thêm mới):</strong>
            <ul>
                <li><em>B1:</em> Admin vào mục "Quản lý Tour", nhấn "Thêm Tour".</li>
                <li><em>B2:</em> Nhập thông tin chi tiết: Tên tour, Danh mục, Giá, Số chỗ, Lịch trình (JSON), Upload hình ảnh.</li>
                <li><em>B3:</em> Nhấn "Lưu". Hệ thống validate và lưu dữ liệu.</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Admin đã đăng nhập.</li>
        <li><strong>Hậu điều kiện:</strong> Tour được đăng bán trên website.</li>
    </ul>

    <p><strong>3.3.11 Quản lý Đơn hàng (Booking)</strong></p>
    <ul>
        <li><strong>Actor:</strong> Admin.</li>
        <li><strong>Mục đích:</strong> Xử lý và theo dõi các đơn đặt tour của khách hàng.</li>
        <li><strong>Mô tả từng bước (Luồng Duyệt đơn):</strong>
            <ul>
                <li><em>B1:</em> Admin xem danh sách Booking, lọc các đơn "Chờ thanh toán" hoặc "Đã thanh toán".</li>
                <li><em>B2:</em> Admin xem chi tiết đơn hàng, kiểm tra thông tin thanh toán (đối chiếu MoMo).</li>
                <li><em>B3:</em> Admin cập nhật trạng thái đơn (Ví dụ: Đã xác nhận/Hoàn thành).
                <li><em>B4:</em> Hệ thống lưu trạng thái mới và (tùy chọn) gửi email thông báo cho khách.</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Có đơn hàng trong hệ thống.</li>
        <li><strong>Hậu điều kiện:</strong> Trạng thái đơn hàng được cập nhật.</li>
    </ul>

    <p><strong>3.3.12 Quản lý Người dùng</strong></p>
    <ul>
        <li><strong>Actor:</strong> Admin.</li>
        <li><strong>Mục đích:</strong> Quản lý tài khoản khách hàng, hỗ trợ hoặc khóa tài khoản vi phạm.</li>
        <li><strong>Mô tả từng bước:</strong>
            <ul>
                <li><em>B1:</em> Admin truy cập danh sách "Người dùng".</li>
                <li><em>B2:</em> Tìm kiếm khách hàng theo tên hoặc email.</li>
                <li><em>B3:</em> Chọn "Sửa" để cập nhật thông tin hoặc "Khóa" để vô hiệu hóa tài khoản.</li>
                <li><em>B4:</em> Xác nhận hành động.</li>
            </ul>
        </li>
        <li><strong>Tiền điều kiện:</strong> Admin đã đăng nhập.</li>
        <li><strong>Hậu điều kiện:</strong> Thông tin/trạng thái người dùng thay đổi.</li>
    </ul>

"""

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "<h3>3.3 CHI TIẾT CÁC USE CASE CHÍNH</h3>"
end_marker = "<h3>3.4 THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE SCHEMA)</h3>"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_section_33 + content[end_idx:]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully updated BAOCAO_KLTN_DRAFT.html Section 3.3")
else:
    print("Could not find markers in HTML file")

