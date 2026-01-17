# 📅 HƯỚNG DẪN CHI TIẾT HOÀN THÀNH DỰ ÁN TRONG 1 THÁNG VỚI DJANGO BUILT-IN FEATURES

## 🎯 MỤC TIÊU CUỐI CÙNG

Sau 1 tháng, bạn sẽ có **sản phẩm hoàn chỉnh** bao gồm:

- **Website đặt tour** với giao diện đẹp, chức năng đầy đủ
- **Telegram Bot AI** tư vấn và đặt tour tự động
- **Chat widget** ngữ cảnh trên trang chi tiết tour
- **Thanh toán** Momo test và QR với xác nhận admin
- **Dashboard admin** thống kê thời gian thực
- **Báo cáo đầy đủ** 17 mục + ERD + screenshots + video demo

**Triết lý:** Tận dụng tối đa Django ORM, Admin, Auth, Sessions, Cache, Signals, Transactions, Logging, Testing, Security để giảm code thủ công, tăng tốc triển khai và bảo mật.

---

## 📋 CHUẨN BỊ (NGÀY 0 - TRƯỚC KHI BẮT ĐẦU)

### 1. Chuẩn bị môi trường phát triển

**Bước 1.1: Cài đặt Python 3.8+**

- Mở trình duyệt web (Safari hoặc Chrome), truy cập trang python.org
- Tìm phần "Downloads" và click vào "Download Python 3.x.x" (chọn phiên bản mới nhất 3.8 trở lên)
- Mở file .pkg vừa download, follow hướng dẫn cài đặt, click Next cho đến khi hoàn thành
- Mở Terminal (nhấn Cmd + Space, gõ "Terminal", nhấn Enter)
- Gõ lệnh `python3 --version` và nhấn Enter để kiểm tra đã cài thành công (nên thấy "Python 3.x.x")

**Bước 1.2: Cài đặt PostgreSQL database và pgAdmin**

- Truy cập trang chủ postgresql.org, vào phần Downloads, chọn macOS, download phiên bản mới nhất.
- Mở file .dmg vừa download, chạy installer, follow hướng dẫn cài đặt (bao gồm PostgreSQL server và pgAdmin).
- Sau cài đặt, PostgreSQL sẽ tự động khởi động. Nếu không, mở System Preferences > PostgreSQL > Start.
- Mở pgAdmin 4 (tìm trong Applications hoặc Launchpad).
- Trong pgAdmin, click "Add New Server" (hoặc Servers > Create > Server).
- Trong tab General, nhập Name: "Local PostgreSQL".
- Trong tab Connection: Host name/address: "localhost", Port: "5432", Maintenance database: "postgres", Username: "postgres", Password: (nhập password đã set trong installer, thường là "postgres" hoặc để trống nếu không set).
- Click Save để kết nối.
- Right-click trên server vừa tạo, chọn "Create > Database".
- Nhập Database name: "vn_travel_db", click Save để tạo database.

**Bước 1.3: Cài đặt VS Code**

- Truy cập code.visualstudio.com, download phiên bản cho macOS
- Cài đặt VS Code theo hướng dẫn
- Mở VS Code, vào Extensions (Cmd + Shift + X), tìm "Python" và cài đặt extension của Microsoft
- Tìm "Django" extension và cài đặt

**Bước 1.4: Cài đặt Git**

- Mở Terminal, gõ `git --version` để kiểm tra đã có chưa
- Nếu chưa có, gõ `xcode-select --install` để cgit --versionài Command Line Tools (bao gồm Git)
- Hoặc download từ git-scm.com và cài đặt
- Để cập nhật Git lên phiên bản mới nhất (nếu đã có): gõ `softwareupdate --all --install --force` (cập nhật qua macOS) hoặc download lại từ git-scm.com và cài đè

**Bước 1.5: Tạo virtual environment**

- Mở Terminal (trên Mac, nhấn Cmd + Space, gõ "Terminal", nhấn Enter)
- Gõ `cd Desktop` (hoặc đường dẫn tới thư mục bạn muốn tạo project, ví dụ `cd /Users/your-username/Desktop`)
- Gõ `python3 -m venv venv` để tạo virtual environment tên "venv" (venv sẽ là thư mục chứa môi trường ảo)
- Activate venv: gõ `source venv/bin/activate` (sẽ thấy (venv) xuất hiện ở đầu dòng lệnh, nghĩa là venv đã được kích hoạt)
- Để deactivate sau này: gõ `deactivate`

### 2. Đăng ký các dịch vụ cần thiết

**Bước 2.1: Telegram Bot**

- Mở Telegram app trên điện thoại hoặc web.telegram.org
- Tìm và mở chat với @BotFather
- Gửi tin nhắn "/newbot"
- Theo hướng dẫn: nhập tên bot (ví dụ "VN Travel Bot"), username (phải kết thúc bằng "bot", ví dụ "vntravelbot")
- BotFather sẽ trả về token (lưu lại, ví dụ "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")

**Bước 2.2: Gemini AI**

- Truy cập trang Google AI Studio: https://aistudio.google.com/app/apikey (hoặc makersuite.google.com/app/apikey sẽ tự động redirect)
- Đăng nhập với tài khoản Google của bạn (nếu chưa có, tạo tài khoản miễn phí)
- Trên trang API keys, click nút "Create API key in new project" hoặc chọn project hiện có
- Nếu tạo project mới: Nhập tên project (ví dụ "VN Travel AI"), chọn organization nếu có, click "Create"
- Sau khi tạo key, copy API key vừa xuất hiện (lưu lại cẩn thận, ví dụ "AIzaSyD...xyz")
- Nếu cần quản lý project chi tiết: Vào console.cloud.google.com, tạo project, enable "Generative Language API" trong APIs & Services > Library, rồi tạo API key trong Credentials
- Lưu API key vào file .env với tên GEMINI_API_KEY

**Bước 2.3: OpenWeather**

- Truy cập openweathermap.org/api
- Click "Sign up", tạo tài khoản free
- Vào API keys, copy key (lưu lại)

**Bước 2.4: Google Maps (optional)**

- Truy cập console.cloud.google.com, đăng nhập với tài khoản Google của bạn (cùng tài khoản với Gemini nếu có thể để quản lý dễ dàng)
- Nếu chưa có project, click "Create Project" ở góc trên cùng bên phải, nhập tên project (ví dụ "VN Travel Maps"), chọn organization nếu có, click "Create"
- Chọn project vừa tạo hoặc project hiện có từ dropdown ở góc trên cùng
- Vào menu bên trái, click "APIs & Services" > "Library"
- Tìm kiếm "Maps Static API" (hoặc "Maps JavaScript API" nếu cần interactive map), click vào API đó, rồi click "Enable" để kích hoạt
- Quay lại menu, click "APIs & Services" > "Credentials"
- Click "Create Credentials" > "API key"
- API key sẽ được tạo, copy key đó (lưu lại cẩn thận, ví dụ "AIzaSyC...xyz")
- Để bảo mật, click vào key vừa tạo, trong phần "Application restrictions", chọn "HTTP referrers (web sites)", thêm domain của bạn (ví dụ "_.yourdomain.com" hoặc "_" cho test)
- Trong "API restrictions", chọn "Restrict key", tick vào "Maps Static API", click "Save"
- Lưu API key vào file .env với tên GOOGLE_MAPS_KEY

**Bước 2.5: MoMo Payment Gateway (Sandbox)**

- Dùng keys test mặc định đã có trong .env: MOMO_PARTNER_CODE=MOMOBKUN20180529, MOMO_ACCESS_KEY=klm05TvNBzhg7h7j, MOMO_SECRET_KEY=at67qH6mk8w5Y1nAyMoYKMWACiEi2bsa.
- Không cần đăng ký developer, dùng luôn cho test/sandbox.
- Trong project Django, tạo endpoint /payment/momo/test-payment/ để test thanh toán với keys này.

**Bước 2.6: Render.com**

- Truy cập render.com, tạo tài khoản free
- Verify email

### 3. Tạo cấu trúc project

**Lưu ý:** Thư mục hiện tại đã là thư mục project (có .gitignore, .env, venv/). Các bước đã hoàn thành sẽ được đánh dấu và bỏ qua.

**Bước 3.1: Tạo thư mục project** ✅ Đã hoàn thành (thư mục hiện tại là project).

**Bước 3.2: Tạo file .gitignore** ✅ Đã hoàn thành (file .gitignore đã có).

**Bước 3.3: Tạo file .env** ✅ Đã hoàn thành (file .env đã có với keys đầy đủ).

**Bước 3.4: Download templates**

- **Giải thích**: Trong Django, thư mục `static/` chứa các file tĩnh (CSS, JS, images) cho website. Bạn cần tạo thư mục này và download giao diện mẫu từ Argon để dùng làm base (thay vì code HTML từ đầu).
- **Các bước chi tiết**:
  1. Mở Terminal, gõ `mkdir -p static/argon static/argon-dashboard` (tạo thư mục `static/` và subfolders `argon/` và `argon-dashboard/` cùng lúc).
  2. Mở trình duyệt web, truy cập https://creative-tim.com/product/argon-design-system (phiên bản free).
  3. Click "Download Now" (có thể cần đăng ký tài khoản free nếu chưa có).
  4. Download file ZIP, giải nén (unzip) vào thư mục `static/argon/` vừa tạo (sao cho các file như index.html, assets/ nằm trực tiếp trong `static/argon/`).
  5. Quay lại trình duyệt, truy cập https://creative-tim.com/product/argon-dashboard (phiên bản free).
  6. Click "Download Now", download ZIP, giải nén vào thư mục `static/argon-dashboard/` (tương tự như trên).
- **Kết quả mong đợi**: Thư mục `static/argon/` và `static/argon-dashboard/` có các file HTML, CSS, JS mẫu để copy vào templates Django sau này.

**Bước 3.5: Tạo requirements.txt**

- Gõ `touch requirements.txt`
- Mở file, thêm:
  ```
  Django==4.2.7
  psycopg2-binary==2.9.7
  python-decouple==3.8
  requests==2.31.0
  python-telegram-bot==20.7
  google-generativeai==0.3.2
  pillow
  ```

### 4. Nghiên cứu tài liệu Django

**Bước 4.1: Đọc documentation**

- Truy cập docs.djangoproject.com/en/4.2/
- Đọc phần "Getting started" và "Models"
- Đọc về "Admin interface" và "Authentication"

**Bước 4.2: Hiểu concepts**

- ORM: cách Django tương tác với database mà không cần SQL
- Migrations: cách Django tạo và cập nhật database schema
- Admin: giao diện quản trị sẵn có
- Sessions: lưu trạng thái user giữa requests

---

## TUẦN 1 (NGÀY 1-7): NỀN TẢNG & QUẢN LÝ TOUR

### NGÀY 1: KHỞI TẠO DJANGO PROJECT

**Mục tiêu:** Có project Django cơ bản với database và admin sẵn sàng.

**Các bước thực hiện:**

**Bước 1.1: Mở Terminal và activate venv**

- Mở Terminal (Cmd + Space, gõ "Terminal")
- Gõ `cd 'Phát triển hệ thống đặt tour du lịch thông minh với AI Travel Advisor cho công ty VN-Travel'` (hoặc đường dẫn tới thư mục project)
- Gõ `source venv/bin/activate` (sẽ thấy (venv) xuất hiện)

**Bước 1.2: Cài đặt Django**

- Gõ `pip install -r requirements.txt`
- Chờ cài đặt hoàn thành (sẽ thấy "Successfully installed...")

**Bước 1.3: Tạo Django project**

- Gõ `django-admin startproject vn_travel .` (dấu chấm để tạo trong thư mục hiện tại)
- Nhấn Enter, chờ tạo xong (sẽ thấy thư mục vn_travel/ được tạo)

**Bước 1.4: Cấu hình settings.py**

- Mở VS Code, mở file vn_travel/settings.py
- Thêm 'tours', 'bookings' vào INSTALLED_APPS
- Cấu hình DATABASES với thông tin PostgreSQL
- Thêm SECRET_KEY từ file .env
- Cấu hình TEMPLATES với đường dẫn templates
- Thêm STATIC_URL, STATICFILES_DIRS, MEDIA_URL, MEDIA_ROOT

**Bước 1.5: Chạy migrations**

- Quay lại Terminal, gõ `python manage.py migrate`
- Nhấn Enter, chờ Django tạo tables (sẽ thấy "Applying migrations...")

**Bước 1.6: Tạo superuser**

- Gõ `python manage.py createsuperuser`
- Nhập username (ví dụ: admin), email, password

**Bước 1.7: Chạy server và test**

- Gõ `python manage.py runserver`
- Mở trình duyệt, truy cập http://127.0.0.1:8000/admin/
- Đăng nhập với superuser vừa tạo
- Kiểm tra admin interface hoạt động

**Kết quả mong đợi:** Django admin hoạt động, có thể đăng nhập với superuser.

### NGÀY 2: TẠO APP TOUR & MODEL CƠ BẢN

**Mục tiêu:** Có model Tour với Django ORM.

**Các bước thực hiện:**

**Bước 2.1: Tạo app tours**

- Mở Terminal, gõ `python manage.py startapp tours`
- Nhấn Enter, chờ tạo app (sẽ thấy thư mục tours/)

**Bước 2.2: Định nghĩa model Tour**

- Mở VS Code, mở file tours/models.py
- Tạo class Tour với các fields: name, slug, description, location, price, duration, max_people, is_active, created_at, updated_at
- Thêm method **str** trả về tên tour

**Bước 2.3: Đăng ký model vào admin**

- Mở file tours/admin.py
- Sử dụng @admin.register để đăng ký TourAdmin với list_display, list_filter, search_fields

**Bước 2.4: Chạy migrations**

- Quay Terminal, gõ `python manage.py makemigrations tours`
- Gõ `python manage.py migrate`

**Bước 2.5: Thêm dữ liệu mẫu**

- Gõ `python manage.py runserver`
- Truy cập /admin/, đăng nhập
- Vào Tours, click "Add Tour", thêm 3-5 tours mẫu với thông tin đầy đủ

**Kết quả mong đợi:** Có thể thêm/sửa/xóa tour qua Django Admin.

### NGÀY 3: UPLOAD ẢNH TOUR

**Mục tiêu:** Tour có thể có nhiều ảnh với Django FileField.

**Các bước thực hiện:**

**Bước 3.1: Tạo model TourImage**

- Mở tours/models.py, thêm class TourImage với ForeignKey đến Tour, ImageField cho ảnh, CharField cho alt_text, BooleanField cho is_main

**Bước 3.2: Cấu hình MEDIA trong settings.py**

- Đảm bảo đã có MEDIA_URL và MEDIA_ROOT như bước 1.4

**Bước 3.3: Đăng ký vào admin với inline**

- Mở tours/admin.py, tạo TourImageInline với TabularInline
- Thêm inlines vào TourAdmin

**Bước 3.4: Chạy migrations**

- Gõ `python manage.py makemigrations tours`
- Gõ `python manage.py migrate`

**Bước 3.5: Upload ảnh mẫu**

- Vào /admin/, edit tour, thêm ảnh qua inline
- Kiểm tra ảnh lưu trong media/tours/

**Kết quả mong đợi:** Mỗi tour có thể có nhiều ảnh, upload qua admin dễ dàng.

### NGÀY 4: AUTHENTICATION VỚI DJANGO AUTH

**Mục tiêu:** Đăng ký/đăng nhập với User model có sẵn.

**Các bước thực hiện:**

**Bước 4.1: Sử dụng User model mặc định**

- Django đã có User model, không cần tạo thêm

**Bước 4.2: Tạo URL patterns**

- Mở vn_travel/urls.py, thêm path cho login và logout sử dụng auth_views

**Bước 4.3: Tạo templates**

- Tạo thư mục templates/registration/
- Copy login.html từ Argon Design System, customize với form login
- Thêm CSRF token: `{% csrf_token %}`

**Bước 4.4: Cấu hình redirect**

- Trong settings.py, thêm LOGIN_REDIRECT_URL và LOGOUT_REDIRECT_URL

**Bước 4.5: Test đăng ký/đăng nhập**

- Chạy server, truy cập /login/
- Đăng nhập với superuser
- Kiểm tra navbar hiển thị user info

**Kết quả mong đợi:** User có thể đăng ký/đăng nhập, navbar thay đổi theo trạng thái.

### NGÀY 5: TRANG CHỦ & DANH SÁCH TOUR

**Mục tiêu:** Trang chủ hiển thị tours nổi bật.

**Các bước thực hiện:**

**Bước 5.1: Tạo view cho trang chủ**

- Mở tours/views.py, tạo TourListView kế thừa ListView với model Tour, template_name, context_object_name, paginate_by

**Bước 5.2: Tạo template base**

- Tạo templates/base.html từ Argon Design System
- Thêm navbar với user info

**Bước 5.3: Hiển thị tours**

- Trong template, loop qua tours, hiển thị cards với ảnh, tên, giá

**Bước 5.4: Thêm pagination**

- Sử dụng `{% for tour in page_obj %}` và pagination links

**Bước 5.5: Thêm filter**

- Thêm form filter theo location và price

**Kết quả mong đợi:** Trang chủ đẹp với tours, có thể filter và phân trang.

### NGÀY 6: CHI TIẾT TOUR

**Mục tiêu:** Trang xem chi tiết tour với gallery ảnh.

**Các bước thực hiện:**

**Bước 6.1: Tạo DetailView**

- Trong tours/views.py, tạo TourDetailView kế thừa DetailView với model Tour và template_name

**Bước 6.2: Query ảnh liên quan**

- Trong template, sử dụng `{% for image in tour.images.all %}`

**Bước 6.3: Tạo carousel**

- Sử dụng HTML/CSS từ Argon để tạo gallery

**Bước 6.4: Tính chỗ còn lại**

- Trong template: `{{ tour.max_people|sub:tour.bookings.count }}`

**Bước 6.5: Thêm nút đặt tour**

- Link đến form booking

**Kết quả mong đợi:** Chi tiết tour hiển thị đầy đủ, có nút đặt tour.

### NGÀY 7: DASHBOARD ADMIN CƠ BẢN

**Mục tiêu:** Admin có thể xem tổng quan.

**Các bước thực hiện:**

**Bước 7.1: Tạo view dashboard**

- Tạo tours/views.py với function view admin_dashboard, sử dụng aggregate để tính thống kê tours và bookings

**Bước 7.2: Hiển thị trong template**

- Tạo template admin/dashboard.html với cards hiển thị stats

**Bước 7.3: Thêm links**

- Links đến changelist của Tours, Bookings

**Bước 7.4: Test CRUD**

- Thêm/sửa/xóa tours qua admin

**Kết quả tuần 1:** Website có thể xem tours, admin quản lý được tours với ảnh.

---

## TUẦN 2 (NGÀY 8-14): ĐẶT TOUR & THANH TOÁN

### NGÀY 8: MODEL BOOKING

**Mục tiêu:** Có model Booking với Django ORM.

**Các bước thực hiện:**

**Bước 8.1: Tạo app bookings**

- Mở Terminal, gõ `python manage.py startapp bookings`
- Nhấn Enter, chờ tạo app

**Bước 8.2: Định nghĩa model Booking**

- Mở bookings/models.py, tạo class Booking với ForeignKey đến User và Tour, các fields cho booking_date, num_adults, num_children, total_price, status, payment_status, created_at, updated_at

**Bước 8.3: Đăng ký vào admin**

- Mở bookings/admin.py, sử dụng @admin.register cho BookingAdmin với list_display, list_filter, search_fields, và thêm actions confirm_bookings, cancel_bookings

**Bước 8.4: Chạy migrations**

- Gõ `python manage.py makemigrations bookings`
- Gõ `python manage.py migrate`

**Bước 8.5: Thêm vào INSTALLED_APPS**

- Mở settings.py, thêm 'bookings' vào INSTALLED_APPS

**Kết quả mong đợi:** Admin có thể xem và quản lý bookings.

### NGÀY 9: FORM ĐẶT TOUR

**Mục tiêu:** User có thể đặt tour qua form.

**Các bước thực hiện:**

**Bước 9.1: Tạo ModelForm**

- Mở bookings/forms.py, tạo file mới, tạo BookingForm kế thừa ModelForm với Meta class, thêm **init** method, clean_booking_date, clean methods

**Bước 9.2: Tạo view đặt tour**

- Mở bookings/views.py, tạo function view create_booking với decorator login_required, sử dụng get_object_or_404, xử lý POST request với form validation, tạo booking và redirect

**Bước 9.3: Tạo URL**

- Mở vn_travel/urls.py, thêm path cho create_booking với tour_id parameter

**Bước 9.4: Tạo template**

- Tạo templates/bookings/create_booking.html với form từ Argon

**Bước 9.5: Test đặt tour**

- Chạy server, đăng nhập, vào tour detail, click "Đặt tour", điền form, submit

**Kết quả mong đợi:** User đăng nhập có thể đặt tour thành công.

### NGÀY 10: TRANG MY BOOKINGS

**Mục tiêu:** User xem danh sách bookings của mình.

**Các bước thực hiện:**

**Bước 10.1: Tạo ListView**

- Trong bookings/views.py, tạo MyBookingsView kế thừa ListView với model Booking, template_name, context_object_name, paginate_by, và override get_queryset để filter theo request.user

**Bước 10.2: Tạo URL**

- Thêm vào urls.py: path cho my-bookings sử dụng MyBookingsView.as_view()

**Bước 10.3: Tạo template**

- Tạo templates/bookings/my_bookings.html
- Hiển thị table với thông tin booking
- Thêm buttons: View detail, Pay, Cancel

**Bước 10.4: Thêm filter form**

- Thêm form filter theo status trong template

**Bước 10.5: Test với nhiều bookings**

- Tạo vài bookings, kiểm tra hiển thị đúng

**Kết quả mong đợi:** User có thể xem tất cả bookings cá nhân.

### NGÀY 11: CHI TIẾT & HỦY BOOKING

**Mục tiêu:** User xem chi tiết và hủy booking nếu được phép.

**Các bước thực hiện:**

**Bước 11.1: Tạo DetailView**

- Thêm vào bookings/views.py: BookingDetailView kế thừa DetailView với model Booking, template_name, và override get_queryset để filter theo user

**Bước 11.2: Tạo view hủy booking**

- Thêm function view cancel_booking với login_required decorator, sử dụng get_object_or_404, kiểm tra status, update status và redirect

**Bước 11.3: Tạo template chi tiết**

- Hiển thị timeline trạng thái
- Form POST để hủy với confirmation

**Bước 11.4: Thêm URL**

- Thêm path cho booking detail và cancel booking vào urls.py

**Bước 11.5: Test hủy booking**

- Vào chi tiết booking pending, click hủy, confirm

**Kết quả mong đợi:** User có thể hủy booking đúng điều kiện.

### NGÀY 12: ADMIN XỬ LÝ BOOKINGS

**Mục tiêu:** Admin xác nhận/hủy bookings qua Django Admin.

**Các bước thực hiện:**

**Bước 12.1: Sử dụng admin có sẵn**

- Đã cấu hình ở Ngày 8

**Bước 12.2: Cấu hình list_filter**

- Đảm bảo có list_filter theo status, date

**Bước 12.3: Test bulk actions**

- Chọn nhiều bookings, chọn action "confirm_bookings", execute

**Bước 12.4: Kiểm tra status thay đổi**

- Refresh page, xem status updated

**Bước 12.5: Test cancel**

- Chọn action "cancel_bookings", execute

**Kết quả mong đợi:** Admin xử lý bookings hiệu quả qua admin.

### NGÀY 13: THANH TOÁN MOMO

**Mục tiêu:** Thanh toán qua Momo sandbox.

**Các bước thực hiện:**

**Bước 13.1: Tạo model Payment**

- Tạo payments/models.py với class Payment có ForeignKey đến Booking, fields cho amount, method, transaction_ref, status, momo_result_code, created_at

**Bước 13.2: Tạo view initiate Momo**

- Tạo payments/views.py với function tạo payment request cho Momo

**Bước 13.3: Cấu hình callback URL**

- Tạo view xử lý callback từ Momo, update payment status

**Bước 13.4: Test flow**

- Tạo booking, chọn thanh toán Momo, redirect tới Momo test, thanh toán, callback

**Bước 13.5: Update booking status**

- Sử dụng signals để auto-update khi payment success

**Kết quả mong đợi:** Thanh toán Momo hoạt động từ đặt tour đến xác nhận.

### NGÀY 14: THANH TOÁN QR

**Mục tiêu:** Thanh toán qua QR với upload ảnh xác nhận.

**Các bước thực hiện:**

**Bước 14.1: Thêm ImageField**

- Thêm `receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)` vào Payment model

**Bước 14.2: Tạo view QR payment**

- Generate VietQR URL hoặc static QR

**Bước 14.3: Tạo form upload**

- Form để user upload ảnh bill

**Bước 14.4: Admin confirm**

- Trong admin, view ảnh và confirm payment

**Bước 14.5: Test flow QR**

- Đặt tour, chọn QR, upload ảnh, admin confirm

**Kết quả tuần 2:** Đặt tour và thanh toán hoạt động hoàn chỉnh.

---

## TUẦN 3 (NGÀY 15-21): CHATBOT & AI

### NGÀY 15: TELEGRAM BOT CƠ BẢN

**Mục tiêu:** Bot Telegram có thể nhận tin nhắn.

**Các bước thực hiện:**

**Bước 15.1: Tạo app telegram_bot**

- Gõ `python manage.py startapp telegram_bot`

**Bước 15.2: Cài đặt python-telegram-bot**

- Gõ `pip install python-telegram-bot`

**Bước 15.3: Tạo model TelegramUser**

- Trong telegram_bot/models.py, tạo class TelegramUser với fields telegram_id, username, first_name, last_name, is_active, created_at

**Bước 15.4: Tạo management command**

- Tạo telegram_bot/management/commands/run_telegram_bot.py với class Command kế thừa BaseCommand, tạo Application với token, thêm handler cho /start command, lưu user vào database

**Bước 15.5: Test bot**

- Gõ `python manage.py run_telegram_bot`
- Vào Telegram, tìm bot, gõ /start

**Kết quả mong đợi:** Bot nhận được tin nhắn và lưu user.

### NGÀY 16: MENU CHÍNH BOT

**Mục tiêu:** Bot có menu với các chức năng chính.

**Các bước thực hiện:**

**Bước 16.1: Tạo model Conversation**

- Thêm vào models.py: class Conversation với ForeignKey đến TelegramUser, fields message_type, message_text, created_at

**Bước 16.2: Tạo menu chính**

- Thêm handler main_menu với InlineKeyboardMarkup chứa buttons Tìm tour, Đặt tour, Xem booking, Hỏi AI

**Bước 16.3: Thêm CallbackQueryHandler**

- Thêm vào application: `application.add_handler(CallbackQueryHandler(handle_menu))`

**Bước 16.4: Test menu**

- Gõ /menu, xem keyboard hiển thị
- Click button, xem callback được xử lý

**Bước 16.5: Lưu conversation**

- Trong mỗi handler, lưu message vào Conversation

**Kết quả mong đợi:** Bot có menu tương tác.

### NGÀY 17: TÌM TOUR QUA BOT

**Mục tiêu:** User tìm tour qua Telegram.

**Các bước thực hiện:**

**Bước 17.1: Tạo state machine**

- Thêm conversation_state vào TelegramUser model

**Bước 17.2: Handler tìm tour**

- Khi user chọn "Tìm tour", chuyển state thành 'searching'
- Hỏi user: "Bạn muốn đi đâu?"

**Bước 17.3: Xử lý destination**

- Nhận destination, query Tour.objects.filter(location\_\_icontains=destination)
- Hiển thị danh sách tours với buttons

**Bước 17.4: Chi tiết tour**

- Khi user click tour, hiển thị detail với button "Đặt tour"

**Bước 17.5: Test flow tìm tour**

- Từ menu, chọn tìm tour, nhập destination, xem kết quả

**Kết quả mong đợi:** User tìm được tour qua bot.

### NGÀY 18: ĐẶT TOUR QUA BOT

**Mục tiêu:** User đặt tour trực tiếp qua Telegram.

**Các bước thực hiện:**

**Bước 18.1: Kiểm tra đăng nhập**

- Kiểm tra user đã link với Django user chưa
- Nếu chưa, hướng dẫn đăng ký qua web

**Bước 18.2: Thu thập thông tin**

- Hỏi ngày khởi hành
- Hỏi số người lớn, trẻ em

**Bước 18.3: Tạo booking**

- Validate thông tin, tạo Booking với status 'pending'
- Gửi confirmation message

**Bước 18.4: Thanh toán qua bot**

- Hiển thị options: Momo, QR
- Generate payment link hoặc QR

**Bước 18.5: Test đặt tour**

- Từ tour detail, click đặt, điền thông tin, tạo booking

**Kết quả mong đợi:** Đặt tour hoàn chỉnh qua bot.

### NGÀY 19: AI TRAVEL ADVISOR

**Mục tiêu:** Bot có AI tư vấn du lịch.

**Các bước thực hiện:**

**Bước 19.1: Cài đặt google-generativeai**

- Gõ `pip install google-generativeai`

**Bước 19.2: Tạo service AI**

- Tạo ai_advisor/services.py với class TravelAdvisor, sử dụng google.generativeai để configure API key và tạo model Gemini Pro, method get_advice với prompt cho AI Travel Advisor

**Bước 19.3: Tạo handler AI**

- Trong bot, khi user chọn "Hỏi AI", chuyển state thành 'asking_ai'
- Nhận câu hỏi, gọi TravelAdvisor, trả lời

**Bước 19.4: Context từ tours**

- Khi hỏi về tour cụ thể, thêm thông tin tour vào context

**Bước 19.5: Test AI advisor**

- Hỏi "Tour Đà Lạt có gì hay?", xem AI trả lời

**Kết quả mong đợi:** AI tư vấn du lịch thông minh.

### NGÀY 20: WEBHOOK THAY POLLING

**Mục tiêu:** Bot sử dụng webhook thay vì polling.

**Các bước thực hiện:**

**Bước 20.1: Tạo view webhook**

- Trong telegram_bot/views.py, tạo function telegram_webhook với decorator csrf_exempt, xử lý POST request với json.loads, trả về HttpResponse OK

**Bước 20.2: Cấu hình URL**

- Thêm vào urls.py: `path('telegram/webhook/', views.telegram_webhook)`

**Bước 20.3: Set webhook**

- Trong management command, thêm function set_webhook để gọi application.bot.set_webhook với URL

**Bước 20.4: Deploy và test**

- Deploy lên server, set webhook URL
- Test bot nhận message qua webhook

**Bước 20.5: Remove polling**

- Comment out run_polling(), chỉ dùng webhook

**Kết quả mong đợi:** Bot hoạt động với webhook.

### NGÀY 21: HOÀN THIỆN BOT

**Mục tiêu:** Bot có đầy đủ tính năng.

**Các bước thực hiện:**

**Bước 21.1: Thêm xem bookings**

- Handler cho "Xem booking", query bookings của user

**Bước 21.2: Hủy booking qua bot**

- Thêm button hủy trong chi tiết booking

**Bước 21.3: Thông báo tự động**

- Sử dụng signals để gửi message khi booking status thay đổi

**Bước 21.4: Error handling**

- Thêm try-except trong tất cả handlers

**Bước 21.5: Test toàn bộ flow**

- Từ start đến đặt tour, thanh toán, nhận thông báo

**Kết quả tuần 3:** Chatbot AI hoàn chỉnh với tất cả tính năng.

---

## TUẦN 4 (NGÀY 22-28): HOÀN THIỆN & TRIỂN KHAI

### NGÀY 22: DASHBOARD ADMIN ĐẦY ĐỦ

**Mục tiêu:** Dashboard thống kê chi tiết.

**Các bước thực hiện:**

**Bước 22.1: Tạo view dashboard**

- Tạo admin_dashboard/views.py với function admin_dashboard, sử dụng aggregate để tính thống kê tours và bookings, lấy recent bookings, render template

**Bước 22.2: Tạo template dashboard**

- Tạo templates/admin/dashboard.html với cards hiển thị stats

**Bước 22.3: Thêm URL**

- Thêm vào urls.py: `path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard')`

**Bước 22.4: Thêm charts đơn giản**

- Sử dụng HTML/CSS tạo bar chart cho revenue

**Bước 22.5: Test với dữ liệu thực**

- Tạo vài bookings, xem dashboard cập nhật

**Kết quả mong đợi:** Admin có overview toàn diện.

### NGÀY 23: KIỂM THỬ TOÀN DIỆN

**Mục tiêu:** Đảm bảo không có lỗi nghiêm trọng.

**Các bước thực hiện:**

**Bước 23.1: Tạo checklist**

- Tạo file checklist.txt với tất cả flows cần test

**Bước 23.2: Test web flows**

- Đăng ký → Xem tours → Đặt tour → Thanh toán → Xem bookings

**Bước 23.3: Test bot flows**

- /start → Tìm tour → Đặt tour → Hỏi AI

**Bước 23.4: Test admin flows**

- Thêm tours → Xem bookings → Confirm payments

**Bước 23.5: Fix bugs**

- Ghi chú và fix từng bug ngay lập tức

**Kết quả mong đợi:** Hệ thống chạy ổn định.

### NGÀY 24: BẢO MẬT & OPTIMIZATION

**Mục tiêu:** Bảo mật và tối ưu performance.

**Các bước thực hiện:**

**Bước 24.1: Bảo mật cơ bản**

- Đảm bảo CSRF enabled trong forms
- Set DEBUG=False trong production settings
- Validate file upload types và sizes

**Bước 24.2: Optimize queries**

- Thêm select_related() trong views
- Sử dụng prefetch_related() cho images
- Cache weather data với Django cache

**Bước 24.3: Rate limiting**

- Thêm middleware cơ bản cho API calls

**Bước 24.4: Test performance**

- Load trang với nhiều tours, check response time

**Bước 24.5: Security audit**

- Check SQL injection, XSS vulnerabilities

**Kết quả mong đợi:** Website an toàn và nhanh.

### NGÀY 25-26: VIẾT BÁO CÁO

**Mục tiêu:** Báo cáo đầy đủ 17 mục.

**Các bước thực hiện:**

**Bước 25.1: Viết từng mục**

- Theo cấu trúc chuẩn: Tóm tắt, Giới thiệu, v.v.

**Bước 25.2: Vẽ diagrams**

- ERD với draw.io
- Sequence diagrams cho bot flow

**Bước 25.3: Chụp screenshots**

- Giao diện web, admin, bot

**Bước 25.4: Viết code samples**

- Các function quan trọng

**Bước 25.5: Review và chỉnh sửa**

- Đọc lại, sửa lỗi chính tả, format

**Kết quả mong đợi:** Báo cáo hoàn chỉnh, chuyên nghiệp.

### NGÀY 27: TRIỂN KHAI LÊN RENDER

**Mục tiêu:** Website chạy live.

**Các bước thực hiện:**

**Bước 27.1: Chuẩn bị production settings**

- Tạo settings/production.py với DEBUG=False
- Cấu hình database PostgreSQL
- Set static files serving

**Bước 27.2: Tạo requirements.txt**

- Gõ `pip freeze > requirements.txt`

**Bước 27.3: Tạo Render web service**

- Connect GitHub repo
- Set build command: `pip install -r requirements.txt`
- Set start command: `python manage.py migrate && python manage.py collectstatic --noinput && gunicorn vn_travel.wsgi`

**Bước 27.4: Set environment variables**

- DJANGO_SECRET_KEY, DATABASE_URL, GEMINI_API_KEY, etc.

**Bước 27.5: Deploy và test**

- Push code, trigger deploy
- Test website live với domain Render

**Kết quả mong đợi:** Website accessible qua URL public.

### NGÀY 28: DEMO & CHUẨN BỊ BẢO VỆ

**Mục tiêu:** Sẵn sàng trình bày.

**Các bước thực hiện:**

**Bước 28.1: Quay video demo**

- Demo ngắn các flows chính: web, bot, admin

**Bước 28.2: Tạo slides**

- PowerPoint với screenshots và diagrams

**Bước 28.3: Ôn lại báo cáo**

- Đọc kỹ 17 mục, chuẩn bị Q&A

**Bước 28.4: Test lần cuối**

- Đảm bảo bot và website hoạt động

**Bước 28.5: Backup**

- Push final code lên GitHub
- Export database nếu cần

**Kết quả cuối cùng:** Sản phẩm hoàn chỉnh, sẵn sàng bảo vệ đồ án.

---

## ✅ CHECKLIST TỔNG THỂ CUỐI CÙNG

### Chức năng cốt lõi:

- [ ] Đăng ký/đăng nhập với Django Auth
- [ ] Xem danh sách/chi tiết tour với ORM
- [ ] Đặt tour với ModelForm validation
- [ ] Xem/hủy booking cá nhân
- [ ] Thanh toán Momo/QR với xác nhận admin
- [ ] Telegram bot tìm/đặt tour
- [ ] Chat widget ngữ cảnh
- [ ] Gemini AI cho câu hỏi mở
- [ ] Dashboard admin với aggregation
- [ ] Weather integration

### Báo cáo & Demo:

- [ ] Báo cáo 17 mục đầy đủ
- [ ] ERD + sequence diagrams
- [ ] Screenshots giao diện
- [ ] Video demo flows chính
- [ ] Slides trình bày

### Triển khai:

- [ ] Website chạy trên Render
- [ ] Bot hoạt động 24/7
- [ ] Không lỗi nghiêm trọng
- [ ] Performance ổn định

---

## 🎯 LƯU Ý QUAN TRỌNG

### Nguyên tắc thành công:

1. **Theo đúng thứ tự tuần/ngày** - không nhảy cóc
2. **Test ngay sau mỗi chức năng** - fix bugs sớm
3. **Ưu tiên Django built-in** - giảm code custom
4. **Commit code thường xuyên** - dễ rollback
5. **Document song song** - ghi chú khi làm

### Troubleshooting:

- Nếu gặp khó: đọc Django docs hoặc file hướng dẫn tương tự
- Không hiểu: search "Django + tên chức năng"
- Lỗi database: check migrations và .env
- Lỗi bot: test với BotFather trước

### Mindset:

- **Hoàn thành > Hoàn hảo** - MVP trước, optimize sau
- **Functional > Beautiful** - chạy được rồi mới đẹp
- **Simple > Complex** - dùng Django sẵn thay vì tự viết
- **Done > Perfect** - deadline quan trọng hơn perfect

**Bắt đầu từ Ngày 1 - từng bước một, bạn sẽ hoàn thành sản phẩm! 🚀**
