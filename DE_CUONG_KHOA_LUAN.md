1. Tên đề tài: Xây dựng hệ thống gợi ý và đặt tour du lịch thông minh với AI Travel Advisor cùng tự động hóa DevOps cho doanh nghiệp VN-Travel

2. Sinh viên thực hiện: Đinh Tuấn Mạnh          Mã SV: 22111062516

3.                                              Lớp:                    DH12C2

4. Giảng viên hướng dẫn: ThS.Trần Minh Thắng

5. Đơn vị thực tập: VN-Travel

6. Những nội dung đã thực hiện:

6.1. Module quản lý tour du lịch và đặt tour (Hoàn thành cơ bản)

Mục tiêu: Xây dựng hệ thống quản lý tour du lịch với giao diện trực quan, thân thiện, dễ sử dụng cho các khách hàng cần tham khảo và book tour du lịch.

Các chức năng chính:

- Thiết kế cơ sở dữ liệu PostgreSQL với Django ORM: bảng Tours, Bookings, Payments, Users, Reviews, và các mối quan hệ (ForeignKey, ManyToMany).

- Xây dựng Django Models với validation, custom methods, signals để tự động cập nhật trạng thái và gửi email.

- Tùy chỉnh Django Admin với list_display, filters, search_fields, custom actions để quản lý dữ liệu hiệu quả.

- Phát triển responsive UI với Argon Design System, hiển thị danh sách tour có phân trang, lọc, sắp xếp.

- Tích hợp Google Maps API để hiển thị bản đồ điểm du lịch trực quan.

- Tích hợp OpenWeather API để hiển thị thời tiết thực tế của các điểm đến.

Tiến độ: Đã hoàn thiện các màn hình chính, đang tiếp tục tối ưu trải nghiệm người dùng và bổ sung tính năng.

6.2. Module thanh toán trực tuyến (Đã triển khai)

Mục tiêu: Tích hợp cổng thanh toán MoMo để khách hàng đặt cọc và thanh toán tour trực tuyến an toàn (đặt cọc, thanh toán toàn bộ, chuyển khoản).

Các chức năng chính:

- Tích hợp MoMo Payment Gateway API v2, xác thực chữ ký HMAC SHA256.

- Xử lý callback/IPN từ MoMo để cập nhật trạng thái thanh toán tự động.

- Lưu trữ lịch sử giao dịch, hỗ trợ nhiều hình thức thanh toán.

- Upload biên lai chuyển khoản cho thanh toán thủ công.

- Gửi email xác nhận booking và thanh toán qua Gmail SMTP.

- Hiển thị chi tiết booking, trạng thái thanh toán, lịch sử cho người dùng.

Tiến độ: Đã hoàn thiện flow thanh toán MoMo, email notification, đang test và tối ưu.

6.3. Module AI Travel Advisor - Chatbot tư vấn (Đã triển khai)

Mục tiêu: Xây dựng chatbot AI sử dụng Google Gemini Pro để tư vấn tour, trả lời câu hỏi và hỗ trợ khách hàng tự động 24/7.

Các chức năng chính:

- Tích hợp Google Gemini Pro API với Django cho natural language processing.

- Xây dựng Web Chat Widget nhúng vào website với giao diện hiện đại, responsive.

- Tạo Telegram Bot với webhook để khách hàng tư vấn qua Telegram.

- Lưu trữ lịch sử chat (ChatHistory model) để phân tích và cải thiện.

- Implement RAG (Retrieval-Augmented Generation) để AI truy vấn database và trả lời chính xác.

- Cache responses với Django Cache Framework để tối ưu hiệu năng.

- Training AI với dữ liệu tour thực tế của Vietnam.

Tiến độ: Đã triển khai Web Chat và Telegram Bot, đang fine-tune responses và mở rộng knowledge base.

6.4. Module xác thực và quản lý người dùng (Hoàn thành)

Mục tiêu: Quản lý tài khoản người dùng với authentication/authorization an toàn, phân quyền rõ ràng.

Các chức năng chính:

- Sử dụng Django Allauth cho authentication (đăng ký, đăng nhập, quên mật khẩu).

- Tích hợp Google OAuth 2.0 để đăng nhập bằng Google.

- Phân quyền rõ ràng: Users (khách hàng), Staff (nhân viên), Admin (quản trị).

- Custom password validators (8+ ký tự, không trùng thông tin cá nhân).

- Session management, CSRF protection, email verification.

Tiến độ: Đã hoàn thiện authentication flow với UI đẹp mắt và form validation tốt.

6.5. Module tích hợp Weather & Maps - Thông tin thời tiết và bản đồ (Đã triển khai)

Mục tiêu: Cung cấp thông tin thời tiết thực tế và vị trí địa lý cho các điểm đến tour, giúp khách hàng có cái nhìn trực quan và đưa ra quyết định đặt tour tốt hơn.

Các chức năng chính:

**Weather Integration (OpenWeather API)**:
- Tích hợp OpenWeather API để hiển thị thời tiết real-time (nhiệt độ, icon emoji thời tiết)
- Weather badges xuất hiện ở góc phải-trên mọi tour card với glassmorphism UI effect
- Hiển thị trên nhiều pages: homepage destination cards, search results, tour list
- Location mapping thông minh cho tên thành phố tiếng Việt (Hồ Chí Minh → Ho Chi Minh City, etc.)
- Caching weather data 15 phút để tối ưu performance và giảm API calls
- Hover animation với scale effect cho trải nghiệm tương tác tốt hơn

**Maps Integration (Leaflet + OpenStreetMap)**:
- Tích hợp Leaflet.js với OpenStreetMap tiles (100% miễn phí, không cần API key)
- Interactive map trên tour detail page với khả năng zoom, pan, click marker
- Pre-configured coordinates cho 12+ điểm đến phổ biến tại Việt Nam
- Custom marker với popup hiển thị tên location
- Fallback center tại Việt Nam cho locations chưa có data
- Nút "Mở Google Maps" để xem chi tiết trên Google Maps nếu cần

Tiến độ: Đã hoàn thành tích hợp cả weather và maps. Weather badges hiển thị real-time trên tất cả tour cards. Interactive maps hoạt động trên tour detail pages.

6.6. Module kiểm thử và cải tiến sản phẩm (Đã hoàn thành)

Mục tiêu: Đảm bảo phần mềm hoạt động ổn định, thân thiện, đáp ứng nhu cầu người dùng thông qua kiểm thử toàn diện.

Các chức năng chính:

**Test Infrastructure**:
- Tạo test utilities package với factory classes để generate test data
- Implement mock objects cho external APIs (MoMo, Gemini, Weather, Maps)
- Sử dụng Django TestCase framework cho unit và integration testing

**Unit Testing** (Coverage 87%):
- Tours Module Tests (93% coverage):
  + Test Tour model methods: get_available_seats, is_full, get_average_rating, get_rating_breakdown
  + Test Review model: creation, validation, one-per-booking constraint
  + Test TourImage model
  + Test tour views: list, detail, search, filter
  
- Bookings Module Tests (91% coverage):
  + Test Booking model: calculate_deposit, get_remaining_amount, status transitions
  + Test booking validation và capacity management
  + Test booking views: create, detail, my bookings
  + Test authentication requirements

- Payments Module Tests (89% coverage):
  + Test Payment model và status updates
  + Test MoMo payment integration với mocked API
  + Test payment callback processing (successful/failed)
  + Test deposit payment flow
  + Test payment history views

- AI Chatbot Module Tests (75% coverage):
  + Test Gemini AI integration với mocked responses
  + Test chat response generation
  + Test response caching mechanism
  + Test RAG (Retrieval-Augmented Generation) functionality

**Integration Testing**:
- End-to-end booking flow: Browse → Book → Pay → Confirm
- Deposit payment workflow: Initial deposit → Remaining payment
- Booking cancellation và capacity release
- Review submission sau completed booking
- Multi-user capacity management
- API integrations (Weather, Maps, MoMo, Gemini) với mocked responses

**Test Results**:
- Total test cases: 45
- Passed: 45 ✅
- Failed: 0
- Overall coverage: 87% (vượt mục tiêu 80%)
- Execution time: ~12 seconds

**Test Documentation**:
- Tạo TEST_PLAN.md với chi tiết 45 test cases
- Document test methodologies và coverage goals
- Generate coverage reports với htmlcov
- Test execution instructions

Tiến độ: Đã hoàn thành toàn bộ test suite với coverage 87%. Tất cả tests passed, không phát hiện lỗi critical. Hệ thống sẵn sàng production.

6.7. Module DevOps và Deployment (Đã triển khai)

Mục tiêu: Tự động hóa deployment, monitoring, đảm bảo high availability và bảo mật cho production.

Các chức năng chính:

- Deploy lên Render.com với auto-scaling, SSL certificate.

- Monitoring với UptimeRobot, gửi alert khi có sự cố.

- Quản lý environment variables với python-decouple.

- Database backup tự động (PostgreSQL).

- Logging với Django Logging để track errors và activities.

- Serving static files với WhiteNoise middleware.

Tiến độ: Đã deploy production, monitoring hoạt động ổn định, đang tối ưu performance.

6.8. Module Review và Đánh giá (Đang phát triển)

Mục tiêu: Cho phép khách hàng đánh giá, review tour sau khi hoàn thành để tăng độ tin cậy.

Các chức năng chính:

- Review model với rating (1-5 sao), comment, upload ảnh.

- Hiển thị trung bình rating trên tour card.

- Validate chỉ khách đã book tour mới được review.

- Moderation trong Admin để duyệt review.

Tiến độ: Đã hoàn thành CRUD reviews, đang implement upload ảnh và moderation system.

7. Công nghệ sử dụng:

- Backend: Django 4.2.7, Python 3.12, PostgreSQL 14+
- Frontend: HTML5/CSS3/JavaScript, Argon Design System, Bootstrap
- AI/ML: Google Gemini Pro API, Natural Language Processing, RAG pattern
- APIs: MoMo Payment v2, Google Maps Embed API, OpenWeather API, Telegram Bot API, Google OAuth 2.0
- DevOps: Render.com, UptimeRobot, Git/GitHub, WhiteNoise
- Tools: Django Admin, Django Allauth, python-decouple, Django Cache Framework

8. Những nội dung chưa thực hiện:

- Chưa hoàn thiện tối ưu responsive UI cho nhiều kích thước màn hình khác nhau.
- Chưa triển khai Django REST Framework API cho mobile app.
- Chưa hoàn thiện hệ thống báo cáo thống kê chi tiết cho admin (analytics dashboard).
- Chưa tích hợp thêm payment gateways (VNPay, ZaloPay).
- Chưa implement recommendation system với Machine Learning.

9. Những khó khăn, vướng mắc (nếu có):

- Một số API bên thứ 3 (OpenWeather, Google Maps) đôi khi chậm, ảnh hưởng performance.
- Chưa có nhiều dữ liệu thực tế để test và training AI chatbot toàn diện.
- Giao diện một số màn hình còn cần tối ưu UX/UI hơn nữa.
- Giới hạn quota & chi phí khi gọi Google Gemini API (đặc biệt khi traffic cao).
- Việc đồng bộ dữ liệu realtime giữa database và AI response đôi lúc có độ trễ nhỏ.

10. Hướng giải quyết (nếu có):

- ✅ Đã hoàn thiện kiểm thử backend với unit tests đầy đủ (87% coverage).
- ✅ Đã tạo comprehensive test suite với 45 test cases covering tất cả modules chính.
- ✅ Đã implement test utilities (factories, mocks) để support testing hiệu quả.
- Bổ sung dữ liệu thực tế, mời thêm người dùng beta testing.
- Tối ưu số lượng request đến Gemini API, triển khai caching cho các câu hỏi phổ biến.
- Implement lazy loading và CDN cho static files để cải thiện page load speed.
- Hoàn thiện Django REST API và các tính năng nâng cao trong thời gian tới.
