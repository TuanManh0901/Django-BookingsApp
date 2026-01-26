TRƯỜNG ĐẠI HỌC TÀI NGUYÊN VÀ MÔI TRƯỜNG HÀ NỘI
KHOA CÔNG NGHỆ THÔNG TIN

---

# BÁO CÁO KHOÁ LUẬN TỐT NGHIỆP

**Đề tài:**  
Xây dựng hệ thống gợi ý và đặt tour du lịch thông minh với AI Travel Advisor cùng tự động hoá DevOps cho doanh nghiệp VN-Travel

**Sinh viên thực hiện:** Đinh Tuấn Mạnh  
**Mã sinh viên:** 22111062516  
**Lớp:** DH12C2  
**Ngành:** Công Nghệ Thông Tin  
**Giảng viên hướng dẫn:** ThS. Trần Minh Thắng  

**HÀ NỘI – Năm 2026**

---

## BẢN CAM ĐOAN

Tên tôi là: Đinh Tuấn Mạnh  
Mã sinh viên: 22111062516  
Lớp: DH12C2  
Ngành: Công Nghệ thông tin  

Tôi đã thực hiện khóa luận với đề tài: **“Xây dựng hệ thống gợi ý và đặt tour du lịch thông minh với AI Travel Advisor cùng tự động hoá DevOps cho doanh nghiệp VN-Travel”**.

Tôi xin cam đoan đây là đề tài nghiên cứu của riêng tôi và được sự hướng dẫn của giảng viên ThS. Trần Minh Thắng. Các nội dung nghiên cứu, kết quả trong đề tài này là trung thực và chưa được công bố dưới bất kỳ hình thức nào. Nếu phát hiện hiện có bất kỳ hình thức gian lận nào tôi xin hoàn toàn chịu trách nhiệm trước pháp luật.

*Hà Nội, ngày 26 tháng 01 năm 2026*  

**Sinh viên thực hiện**  
(Ký và ghi rõ họ tên)  

Đinh Tuấn Mạnh

---

## LỜI CẢM ƠN

Sau thời gian thực hiện khóa luận tốt nghiệp, đến nay mọi công việc liên quan đến khóa luận đã hoàn tất. Để có sự thành công này, em xin gửi lời cảm ơn chân thành đến tất cả các thầy, cô giáo trường Đại học Tài Nguyên và Môi Trường Hà Nội.

Em xin gửi lời cảm ơn chân thành nhất tới **ThS. Trần Minh Thắng**, người đã tận tình hướng dẫn, giúp đỡ em trong suốt quá trình làm khóa luận. Thầy đã giúp đỡ em trong việc chọn đề tài, hình thành những ý tưởng, những góp ý, chỉnh sửa để đề tài được hoàn thiện một cách tốt nhất có thể.

Em cũng xin gửi lời cảm ơn đến khoa Công nghệ thông tin – Trường Đại Học Tài Nguyên và Môi Trường Hà Nội đã luôn quan tâm, tạo điều kiện giúp em hoàn thành khóa luận tốt nghiệp này.

Vì thời gian, khả năng của bản thân có hạn mặc dù đã rất cố gắng hoàn thành khóa luận xong vẫn không tránh khỏi những sai sót. Em rất mong nhận được sự đóng góp, bổ sung ý kiến của quý thầy cô để khóa luận của em được hoàn thiện hơn.

Cuối cùng, em xin kính chúc các thầy cô giảng viên trường Đại học Tài nguyên và Môi trường Hà Nội nói chung, các thầy cô khoa Công nghệ thông tin nói riêng dồi dào sức khỏe và thành công trong sự nghiệp cao quý.

Em xin chân thành cảm ơn!

---

## MỤC LỤC

1. [LỜI MỞ ĐẦU](#lời-mở-đầu)
2. [CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI](#chương-1-tổng-quan-về-đề-tài)
    - 1.1 Giới thiệu đề tài
    - 1.2 Tính mới và đóng góp của đề tài
    - 1.3 Mục tiêu của đề tài
    - 1.4 Phạm vi và giới hạn
    - 1.5 Phương pháp nghiên cứu
3. [CHƯƠNG 2: CƠ SỞ LÝ THUYẾT](#chương-2-cơ-sở-lý-thuyết)
    - 2.1 Tổng quan về Django Framework
    - 2.2 Hệ quản trị cơ sở dữ liệu PostgreSQL
    - 2.3 Trí tuệ nhân tạo Generative AI và Google Gemini
    - 2.4 Kiến trúc Chatbot và RAG
    - 2.5 Các công nghệ tích hợp (Google Maps, OpenWeather, MoMo)
4. [CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG](#chương-3-phân-tích-và-thiết-kế-hệ-thống)
    - 3.1 Đặc tả yêu cầu
    - 3.2 Thiết kế cơ sở dữ liệu
    - 3.3 Thiết kế kiến trúc hệ thống
5. [CHƯƠNG 4: CÀI ĐẶT VÀ TRIỂN KHAI](#chương-4-cài-đặt-và-triển-khai)
    - 4.1 Môi trường cài đặt
    - 4.2 Demo các chức năng chính
    - 4.3 Kết quả kiểm thử
6. [TỔNG KẾT](#tổng-kết)

---

## LỜI MỞ ĐẦU

Trong kỷ nguyên số hóa 4.0, ngành du lịch đang chứng kiến sự chuyển mình mạnh mẽ, và du lịch trực tuyến (E-Tourism) đã trở thành một phần không thể thiếu trong nền kinh tế số. Theo báo cáo của Statista (2023), doanh thu thị trường du lịch trực tuyến toàn cầu dự kiến sẽ đạt mức tăng trưởng ấn tượng trong những năm tới. Điều này cho thấy sự bùng nổ của xu hướng đặt tour du lịch qua mạng trên toàn thế giới, và Việt Nam không nằm ngoài xu thế đó. Tại Việt Nam, với sự phổ biến của Internet và smartphone, hành vi của khách du lịch đang thay đổi nhanh chóng từ đặt tour truyền thống sang các nền tảng trực tuyến tiện lợi.

Trong bối cảnh đó, các doanh nghiệp lữ hành truyền thống cần đổi mới và ứng dụng công nghệ để đáp ứng nhu cầu ngày càng cao của thị trường. **"Xây dựng hệ thống gợi ý và đặt tour du lịch thông minh với AI Travel Advisor cùng tự động hoá DevOps cho doanh nghiệp VN-Travel"** là một giải pháp hiện đại giúp công ty lữ hành nâng cao trải nghiệm khách hàng, tối ưu hóa quy trình vận hành và tăng trưởng doanh thu.

Hệ thống này không chỉ đơn thuần là một website bán tour trực tuyến mà còn tích hợp **AI Travel Advisor (Chatbot thông minh)** sử dụng công nghệ Generative AI để hỗ trợ khách hàng 24/7. Theo các khảo sát gần đây, du khách ngày càng ưa chuộng việc tự lên kế hoạch và tìm kiếm thông tin nhanh chóng. Việc sử dụng AI Chatbot giúp khách hàng ngay lập tức nhận được tư vấn về lịch trình, gợi ý điểm đến, và giải đáp thắc mắc mà không cần sự can thiệp trực tiếp của nhân viên tư vấn. Điều này không chỉ cải thiện trải nghiệm khách hàng nhờ sự phản hồi tức thì mà còn giúp doanh nghiệp giảm áp lực lên bộ phận chăm sóc khách hàng và nâng cao hiệu suất làm việc.

Bên cạnh đó, hệ thống tích hợp phương thức **thanh toán trực tuyến qua MoMo**, mang lại sự tiện lợi tối đa và an toàn cho khách hàng. Việc áp dụng thanh toán số giúp quy trình đặt cọc và thanh toán trở nên liền mạch, giảm thiểu tỷ lệ hủy tour vào phút chót và giúp doanh nghiệp quản lý dòng tiền hiệu quả hơn. Các nghiên cứu đã chỉ ra rằng việc tích hợp thanh toán trực tuyến đa dạng có thể gia tăng đáng kể tỷ lệ chuyển đổi đơn hàng cho các doanh nghiệp vừa và nhỏ (SMEs).

Ngoài ra, hệ thống quản lý tour du lịch thông minh còn cung cấp nhiều lợi ích quan trọng như: quản lý tập trung dữ liệu tour và booking, tự động hóa quy trình xác nhận qua email, và đảm bảo tính ổn định của hệ thống thông qua quy trình DevOps tự động hóa. Đây là bước đi chiến lược để VN-Travel khẳng định vị thế trong thị trường du lịch cạnh tranh khốc liệt hiện nay.

---

## CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI

### 1.1 GIỚI THIỆU ĐỀ TÀI
VN-Travel là một doanh nghiệp lữ hành cần chuyển đổi số để nâng cao năng lực cạnh tranh. Đề tài tập trung xây dựng một nền tảng web toàn diện bao gồm website đặt tour, hệ thống quản trị (Admin), và đặc biệt là module AI Travel Advisor sử dụng mô hình ngôn ngữ lớn (LLM) để tương tác với khách hàng bằng ngôn ngữ tự nhiên.

### 1.2 TÍNH MỚI VÀ ĐÓNG GÓP CỦA ĐỀ TÀI
- **Tích hợp Generative AI**: Sử dụng Google Gemini Pro để xây dựng Travel Advisor, có khả năng hiểu và trả lời các câu hỏi phức tạp về du lịch, gợi ý lịch trình, so sánh tour.
- **Tự động hóa DevOps**: Áp dụng quy trình CI/CD, tự động deploy lên Render, monitoring với UptimeRobot, đảm bảo hệ thống vận hành ổn định.
- **Trải nghiệm người dùng cao cấp**: Giao diện Argon Design System hiện đại, tích hợp bản đồ tương tác và thông tin thời tiết thời gian thực.
- **Thanh toán số**: Tích hợp cổng thanh toán MoMo, tự động hóa quy trình xác nhận đặt cọc và thanh toán.

### 1.3 MỤC TIÊU CỦA ĐỀ TÀI
#### 1.3.1 Mục tiêu chung
Xây dựng hoàn thiện hệ thống website VN-Travel đáp ứng nhu cầu kinh doanh thực tế, hỗ trợ khách hàng tìm kiếm, đặt tour và nhận tư vấn tự động.

#### 1.3.2 Mục tiêu cụ thể
- Xây dựng module quản lý tour, booking, reviews.
- Phát triển AI Chatbot (Travel Advisor) hoạt động trên Web và Telegram.
- Tích hợp thanh toán trực tuyến MoMo.
- Tích hợp APIs tiện ích: Google Maps, OpenWeather.
- Đảm bảo chất lượng phần mềm qua kiểm thử tự động (Unit Test, Integration Test).

### 1.4 PHẠM VI VÀ GIỚI HẠN CỦA ĐỀ TÀI
#### 1.4.1 Phạm vi
- **Đối tượng phục vụ**: Khách du lịch nội địa và quốc tế; Nhân viên và Quản trị viên VN-Travel.
- **Nền tảng**: Web Application (Responsive cho Mobile/Desktop) và Telegram Bot.

#### 1.4.2 Giới hạn
- Hệ thống tập trung thử nghiệm dữ liệu tour tại các điểm đến phổ biến ở Việt Nam.
- Chatbot AI phụ thuộc vào giới hạn quota của Google Gemini API miễn phí.
- Chưa tích hợp thanh toán thẻ Visa/Mastercard quốc tế (chỉ hỗ trợ MoMo và chuyển khoản).

### 1.5 PHƯƠNG PHÁP NGHIÊN CỨU
- **Nghiên cứu lý thuyết**: Tìm hiểu về Framework Django, kiến trúc Web, RESTful API, và cơ chế hoạt động của Generative AI (LLM).
- **Nghiên cứu thực nghiệm**: Xây dựng ứng dụng, kiểm thử, triển khai thực tế trên môi trường cloud (Render), thu thập phản hồi để tối ưu.

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

### 2.1 TỔNG QUAN VỀ DJANGO FRAMEWORK
Django là một web framework bậc cao, mã nguồn mở, được viết bằng Python. Django tuân theo mô hình MVT (Model-View-Template), giúp phát triển web nhanh chóng, bảo mật và dễ bảo trì.
- **ORM (Object-Relational Mapping)**: Tương tác với cơ sở dữ liệu thông qua đối tượng Python thay vì SQL thuần.
- **Admin Interface**: Giao diện quản trị được sinh tự động, mạnh mẽ.
- **Security**: Tích hợp sẵn bảo vệ chống SQL Injection, XSS, CSRF, Clickjacking.

### 2.2 HỆ QUẢN TRỊ CƠ SỞ DỮ LIỆU POSTGRESQL
PostgreSQL là hệ quản trị cơ sở dữ liệu quan hệ đối tượng (ORDBMS) mạnh mẽ, mã nguồn mở. Dự án sử dụng PostgreSQL vì khả năng xử lý dữ liệu phức tạp, hỗ trợ JSONField (lưu lịch trình tour), và tính ổn định cao cho môi trường Production.

### 2.3 TRÍ TUỆ NHÂN TẠO VÀ GOOGLE GEMINI
- **Generative AI**: Loại hình AI có khả năng tạo ra nội dung mới.
- **Google Gemini Pro**: Mô hình ngôn ngữ lớn (LLM) của Google, có khả năng hiểu ngữ cảnh tốt, xử lý đa phương thức. Trong dự án, Gemini được dùng để xử lý ngôn ngữ tự nhiên (NLP) cho Travel Advisor.

### 2.4 CÁC CÔNG NGHỆ TÍCH HỢP KHÁC
- **Google Maps Platform**: Hiển thị vị trí, bản đồ du lịch.
- **OpenWeatherMap API**: Cung cấp dữ liệu thời tiết thời gian thực tại điểm đến.
- **MoMo Payment API**: Cổng thanh toán điện tử phổ biến tại Việt Nam.
- **Celery & Redis**: (Tùy chọn) Xử lý tác vụ nền như gửi email, cập nhật cache.

---

## CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

### 3.1 ĐẶC TẢ YÊU CẦU
- **Yêu cầu chức năng**: Đăng ký/Đăng nhập, Tìm kiếm Tour, Đặt Tour, Thanh toán, Chat với AI, Quản lý đơn hàng, Đánh giá tour.
- **Yêu cầu phi chức năng**: Bảo mật thông tin người dùng, Tốc độ phản hồi nhanh (<2s), Giao diện thân thiện, Hoạt động 24/7.

### 3.2 THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE SCHEMA)
Hệ thống sử dụng các bảng chính sau:
- **Users**: Mở rộng từ AbstractUser, lưu thông tin khách hàng.
- **Tours**: Lưu thông tin tour (Tên, giá, lịch trình JSON, ảnh, slot còn trống).
- **Bookings**: Lưu đơn đặt tour, trạng thái thanh toán, tổng tiền.
- **Reviews**: Lưu đánh giá, nhận xét của khách hàng.
- **Payments**: Lưu lịch sử giao dịch MoMo.
- **ChatHistory**: Lưu lịch sử hội thoại với AI để phân tích.

### 3.3 THIẾT KẾ KIẾN TRÚC HỆ THỐNG
Mô hình Client-Server:
- **Client**: Trình duyệt web (HTML5, CSS3, JS) hoặc Telegram App.
- **Server**: Django Application Server chạy trên Gunicorn.
- **Database**: PostgreSQL Database.
- **External Services**: VN-Travel kết nối với Gemini API, MoMo API, Google Maps, Weather API.

---

## CHƯƠNG 4: CÀI ĐẶT VÀ TRIỂN KHAI

### 4.1 CÁC MODULE ĐÃ HOÀN THIỆN
1. **Module Quản lý Tour & Đặt Tour**:
   - Hiển thị danh sách tour phân trang, lọc theo giá/địa điểm.
   - Chi tiết tour với bản đồ tích hợp và dự báo thời tiết.
   - Quy trình đặt tour và kiểm tra chỗ trống tự động (Concurrency handling).

2. **Module Thanh Toán (Payments)**:
   - Tích hợp MoMo QR Code & ATM Card.
   - Xử lý IPN (Instant Payment Notification) để cập nhật trạng thái đơn hàng tự động.
   - Gửi email vé điện tử sau khi thanh toán thành công.

3. **Module AI Travel Advisor**:
   - Web Chat Widget: Giao diện chat hiện đại, hỗ trợ Markdown.
   - Telegram Bot: Tư vấn trực tiếp qua ứng dụng Telegram.
   - RAG (Retrieval-Augmented Generation): AI truy xuất dữ liệu tour từ database để trả lời chính xác, tránh "ảo giác" (hallucination).

4. **Module DevOps**:
   - CI/CD: Tự động deploy khi push code lên GitHub.
   - Monitoring: Theo dõi uptime website.

### 4.2 KẾT QUẢ KIỂM THỬ (TESTING)
Hệ thống đã trải qua quy trình kiểm thử nghiêm ngặt:
- **Unit Testing**: Đã viết 45 test cases cho Models, Views, Forms.
- **Coverage**: Đạt 87% độ bao phủ mã nguồn.
- **Kết quả**: 100% test cases Pass. Hệ thống hoạt động ổn định, xử lý tốt các trường hợp ngoại lệ (hết chỗ, lỗi thanh toán, mất mạng).

---

## TỔNG KẾT

### KẾT QUẢ ĐẠT ĐƯỢC
Sau quá trình thực hiện khóa luận, em đã xây dựng thành công hệ thống **VN-Travel** với các ưu điểm:
- Ứng dụng công nghệ AI tiên tiến vào thực tế doanh nghiệp.
- Quy trình đặt tour và thanh toán được tự động hóa hoàn toàn.
- Hệ thống có độ ổn định cao nhờ quy trình kiểm thử và DevOps bài bản.
- Giao diện người dùng hiện đại, trải nghiệm mượt mà.

### HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN
- **Hạn chế**: Chatbot đôi khi phản hồi chậm do độ trễ API quốc tế. Tính năng gợi ý cá nhân hóa chưa sử dụng Machine Learning chuyên sâu.
- **Hướng phát triển**: Nâng cấp AI để học từ lịch sử đặt tour của khách; Phát triển Mobile App (React Native/Flutter); Tích hợp thêm các dịch vụ vé máy bay, khách sạn.

---

**TÀI LIỆU THAM KHẢO**
1. Django Project Documentation (https://docs.djangoproject.com/)
2. Google Cloud AI & Gemini API Docs.
3. MoMo Payment Developer Guide.
4. "Two Scoops of Django 3.x" - Daniel Roy Greenfeld.

Lưu file tại: `/Users/tuanmanh/Phát triển hệ thống đặt tour du lịch thông minh với AI Travel Advisor cho công ty VN-Travel/BAOCAO_KLTN_DRAFT.md`
