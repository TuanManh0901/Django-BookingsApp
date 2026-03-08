"""
AI Travel Advisor Service using Google Gemini AI
"""
import google.generativeai as genai
import time
from django.conf import settings
from django.core.cache import cache
from tours.models import Tour
from tours.utils import get_weather


# ============================================================================
# VIETNAMESE SYSTEM PROMPT - BASE
# ============================================================================
BASE_SYSTEM_PROMPT = """
Bạn là AI Travel Advisor chuyên nghiệp của công ty VN Travel Việt Nam.

NHIỆM VỤ CHÍNH:
1. Tư vấn du lịch cho khách hàng một cách thân thiện, nhiệt tình và CHI TIẾT
2. Gợi ý các tour phù hợp với nhu cầu và ngân sách, kèm MÔ TẢ CỤ THỂ
3. Cung cấp thông tin ĐẦY ĐỦ về địa điểm, thời tiết, ăn uống, lưu trú, hoạt động
4. Giải đáp mọi thắc mắc về du lịch Việt Nam

PHONG CÁCH TRÁ LỜI:
- LUÔN trả lời bằng tiếng Việt chuẩn, rõ ràng
- Thân thiện, nhiệt tình, chuyên nghiệp và CỰC KỲ CHI TIẾT
- BẮT ĐẦU bằng lời chào ngắn gọn, ấm áp
- Cung cấp câu trả lời DÀI, ĐẦY ĐỦ, CẤU TRÚC RÕ RÀNG (300-500 từ tối thiểu)
- CẬP NHẬT TÌNH HÌNH THỜI TIẾT THỰC TẾ: Dựa vào thông tin context, hãy đưa ra lời khuyên phù hợp.

KHI GỢI Ý TOUR:
- Hãy gợi ý CHỈ NHỮNG TOUR THỰC SỰ CÓ TRONG HỆ THỐNG (từ thông tin tours)
- Nếu tour phù hợp, liệt kê:
  + Đặc điểm khí hậu/phong cảnh (KÈM THÔNG TIN THỜI TIẾT HIỆN TẠI)
  + Các loại hoa/cây đặc trưng (nếu có)
  + Đồ uống/món ăn nổi tiếng (ít nhất 3-4 món)
  + Các điểm tham quan chính (ít nhất 4-5 địa danh)
  + Trải nghiệm ẩm thực đặc sắc
  + GIÁ TOUR CỤ THỂ từ dữ liệu
  + SỐ NGÀY tour
  + SỐ CHỖ còn trống
"""

# ============================================================================
# FORMAT INSTRUCTIONS
# ============================================================================
HTML_FORMAT_INSTRUCTION = """
CẤU TRÚC THÔNG TIN (WEB/HTML):
- SỬ DỤNG DANH SÁCH CÓ SỐ THỨ TỰ (1., 2., 3., ...) cho các mục chính
- Sử dụng GẠCH ĐẦU DÒNG (-) cho các mẩu tin chi tiết
- Mã màu và icon emoji phong phú.

KHI KHÁCH HÀNG YÊU CẦU LÊN LỊCH TRÌNH (ITINERARY) HOẶC GỢI Ý ĐI ĐÂU:
Thay vì trả về text thông thường, hãy trả về mã HTML CHUẨN (không cần thẻ html/body, chỉ div content) theo cấu trúc sau:

<div class="itinerary-timeline">
  <div class="day-node">
    <div class="day-header">📅 Ngày 1: [Tên chủ đề ngày]</div>
    <div class="timeline-card">
      <div class="activity-item">
        <span class="activity-time">08:00</span>
        <div class="activity-content">
          <strong>[Tên hoạt động/Địa điểm]</strong><br>
          <small class="text-muted">[Mô tả ngắn/Địa chỉ/Món ăn]</small>
        </div>
      </div>
       <!-- Thêm các activity khác -->
    </div>
  </div>
   <!-- Các ngày tiếp theo tương tự -->
</div>

<div class="text-center mt-3">
   <div class="price-tag">💰 Tổng chi phí dự kiến: [Số tiền] VNĐ</div>
   <br>
   <a href="javascript:void(0)" onclick="bookItinerary()" class="book-btn-mini mt-3">👉 Đặt lịch trình này ngay</a>
</div>

LƯU Ý QUAN TRỌNG:
1. NẾU khách chỉ hỏi bâng quơ, trả lời text bình thường.
2. NẾU khách hỏi "Lên lịch trình", "Gợi ý đi Đà Lạt 3 ngày", "Plan cho tôi chuyến đi"... -> BẮT BUỘC dùng cấu trúc HTML trên.
3. KHÔNG được bọc HTML trong backtick, hãy trả về RAW HTML.
4. TUYỆT ĐỐI KHÔNG dùng ký hiệu heading markdown như ##, ###, ####. Nếu cần tiêu đề, chỉ dùng tối đa 1 dấu # hoặc dùng thẻ HTML <strong>.
"""


MARKDOWN_FORMAT_INSTRUCTION = """
CẤU TRÚC THÔNG TIN (TELEGRAM/HTML):
- SỬ DỤNG thẻ HTML được Telegram hỗ trợ để định dạng văn bản.
- <b>In đậm</b> cho các tiêu đề quan trọng.
- <i>In nghiêng</i> cho các ghi chú.
- Sử dụng emoji phong phú: 🏖️ ✈️ 🌸 ☕ 🍜 📸 🏔️ 🌊 ☀️ 🌧️

KHI KHÁCH HÀNG YÊU CẦU LÊN LỊCH TRÌNH (ITINERARY):
Hãy trình bày theo dạng Timeline rõ ràng:

📅 <b>Ngày 1: [Tên chủ đề ngày]</b>
━━━━━━━━━━━━━━━━━━
🕗 <b>08:00 - [Tên hoạt động]</b>
<i>[Mô tả ngắn/Địa chỉ]</i>

🕐 <b>14:00 - [Tên hoạt động]</b>
<i>[Mô tả ngắn]</i>
...

📅 <b>Ngày 2: [Tên chủ đề ngày]</b>
━━━━━━━━━━━━━━━━━━
...

💰 <b>Tổng chi phí dự kiến:</b> [Số tiền] VNĐ

👉 <i>Gõ lệnh /book để đặt tour ngay!</i>

YÊU CẦU TUYỆT ĐỐI:
✅ KHÔNG dùng dấu sao (*) hay gạch dưới (_) để định dạng.
✅ CHỈ dùng thẻ <b>, <i>, <u>, <a>, <code>.
✅ KHÔNG dùng thẻ <div>, <span>, <br>, <h1>-<h6>.
✅ Trình bày thoáng, xuống dòng rõ ràng.
✅ TUYỆT ĐỐI KHÔNG dùng ký hiệu heading markdown như ##, ###, ####. Nếu cần tiêu đề, chỉ dùng tối đa 1 dấu # hoặc dùng <b>.
"""


class TravelAdvisor:
    """AI Travel Advisor powered by Gemini Pro"""
    
    def __init__(self, client_type='web'):
        """
        Initialize Gemini AI
        Args:
            client_type (str): 'web' or 'telegram' to determine output format
        """
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key or api_key == 'your-gemini-api-key-here':
            raise ValueError("GEMINI_API_KEY chưa được cấu hình trong settings.py hoặc .env")
        
        genai.configure(api_key=api_key)
        
        # Select prompt based on client
        if client_type == 'telegram':
            system_instruction = BASE_SYSTEM_PROMPT + "\n\n" + MARKDOWN_FORMAT_INSTRUCTION
        else:
            system_instruction = BASE_SYSTEM_PROMPT + "\n\n" + HTML_FORMAT_INSTRUCTION
            
        # Dùng model đã test và chắc chắn hoạt động
        self.model = genai.GenerativeModel(
            model_name='models/gemini-3-flash-preview',
            system_instruction=system_instruction
        )
    
    def get_tours_context(self, limit=None):
        """Lấy thông tin tours để làm context cho AI"""
        if limit:
            tours = Tour.objects.filter(is_active=True)[:limit]
        else:
            tours = Tour.objects.filter(is_active=True)  # ALL tours
        
        if not tours:
            return "Hiện tại chưa có tour nào trong hệ thống."
        
        context = "Thông tin các tour du lịch hiện có (bao gồm thời tiết thực tế):\n\n"
        for i, tour in enumerate(tours, 1):
            context += f"{i}. {tour.name}\n"
            context += f"   - Địa điểm: {tour.location}\n"
            
            # Fetch real-time weather using existing utility
            weather = get_weather(tour.location)
            if weather:
                context += f"   - Thời tiết hiện tại: {weather['temp']}°C, {weather['description']}, Độ ẩm {weather['humidity']}%\n"
            else:
                context += "   - Thời tiết hiện tại: Không có dữ liệu\n"
                
            context += f"   - Giá: {tour.price:,} VND\n"
            context += f"   - Thời gian: {tour.duration} ngày\n"
            context += f"   - Mô tả: {tour.description[:200]}...\n"
            context += f"   - Số chỗ tối đa: {tour.max_people}\n\n"
        
        return context
    
    def get_advice_stream(self, user_question, include_tours=True):
        """
        Streaming version: yield từng chunk text từ Gemini thay vì chờ toàn bộ response.
        Dùng cho Server-Sent Events (SSE) endpoint.
        
        Yields:
            str: Từng đoạn text nhỏ từ Gemini
        """
        try:
            tours_context = ""
            if include_tours:
                tours_context = f"\n\n{self.get_tours_context()}"

            simple_prompt = f"Trả lời bằng tiếng Việt: {user_question}{tours_context}"

            # Dùng stream=True → Gemini trả về generator
            response = self.model.generate_content(simple_prompt, stream=True)

            import re
            for chunk in response:
                if chunk.text:
                    text = chunk.text
                    text = text.replace("*", "")      # bỏ bold/italic markdown
                    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)  # bỏ ### ## #
                    text = re.sub(r'\n{3,}', '\n\n', text)
                    yield text

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str:
                yield "🤖 <i>(Hệ thống đang quá tải)</i>\n\nAI đang nhận quá nhiều yêu cầu, vui lòng đợi 1-2 phút rồi hỏi lại nhé! 🙏"
            else:
                yield f"⚠️ Lỗi kết nối AI. Vui lòng thử lại sau."

    def get_advice(self, user_question, include_tours=True):
        """
        Nhận tư vấn từ AI về du lịch
        
        Args:
            user_question (str): Câu hỏi của user
            include_tours (bool): Có thêm thông tin tours vào context không
        
        Returns:
            str: Câu trả lời từ AI
        """
        # Kiểm tra cache trước
        cache_key = f"ai_response_{hash(user_question) % 10000}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
        
        try:
            # Tạo tours context nếu cần
            tours_context = ""
            if include_tours:
                tours_context = f"\n\n{self.get_tours_context()}"
            
            # Prompt đơn giản hơn để tránh lỗi
            simple_prompt = f"Trả lời bằng tiếng Việt: {user_question}{tours_context}"
            
            # Wrapper retry logic for Rate Limits (429)
            max_retries = 3
            base_delay = 2
            
            headers = None
            response = None
            
            for attempt in range(max_retries):
                try:
                    # Gọi Gemini API với model đã test
                    response = self.model.generate_content(simple_prompt)
                    break # Success, exit loop
                except Exception as e:
                    error_str = str(e).lower()
                    if "429" in error_str or "quota" in error_str:
                        if attempt < max_retries - 1:
                            sleep_time = base_delay * (2 ** attempt) # 2s, 4s...
                            time.sleep(sleep_time)
                            continue
                    raise e # Re-raise other errors or if retries exhausted
            
            # Lấy text từ response
            # Lấy text từ response
            if hasattr(response, 'text') and response.text:
                response_text = response.text
                
                # CLEANUP FORMATTING
                import re
                response_text = response_text.replace("*", "")             # bỏ bold/italic
                response_text = re.sub(r'^#{1,6}\s*', '', response_text, flags=re.MULTILINE)  # bỏ ###
                response_text = re.sub(r'\n\s*\n', '\n', response_text)   # bỏ dòng trống thừa
                
            else:
                response_text = "Xin lỗi, AI không thể tạo phản hồi."
            
            # Cache response (1 hour)
            cache.set(cache_key, response_text, 3600)
            
            
            return response_text
                
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str or "resource" in error_str:
                return (
                    "🤖 <i>(Hệ thống đang quá tải)</i>\n\n"
                    "Hiện tại AI đang nhận quá nhiều yêu cầu, bạn vui lòng đợi <b>1-2 phút</b> rồi hỏi lại nhé! 🙏\n"
                    "Trong lúc chờ, bạn có thể gõ <b>/menu</b> để xem các tour du lịch có sẵn."
                )
            
            error_msg = f"⚠️ Lỗi kết nối AI: {str(e)[:100]}...\nVui lòng thử lại sau."
            return error_msg
    
    def get_tour_recommendation(self, budget=None, location=None, duration=None):
        """
        Gợi ý tour dựa trên tiêu chí
        
        Args:
            budget (int): Ngân sách (VND)
            location (str): Địa điểm mong muốn
            duration (int): Số ngày
        
        Returns:
            str: Gợi ý tour từ AI
        """
        # Tạo query
        query_parts = []
        if budget:
            query_parts.append(f"ngân sách khoảng {budget:,} VND")
        if location:
            query_parts.append(f"muốn đi {location}")
        if duration:
            query_parts.append(f"trong khoảng {duration} ngày")
        
        if not query_parts:
            query = "Tôi muốn đi du lịch, bạn có thể gợi ý tour nào phù hợp không?"
        else:
            query = f"Tôi {', '.join(query_parts)}. Bạn có thể gợi ý tour nào phù hợp không?"
        
        return self.get_advice(query, include_tours=True)
