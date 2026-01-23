"""
AI Travel Advisor Service using Google Gemini AI
"""
import google.generativeai as genai
from django.conf import settings
from django.core.cache import cache
from tours.models import Tour


# ============================================================================
# VIETNAMESE SYSTEM PROMPT - Tăng chất lượng phản hồi tiếng Việt
# ============================================================================
VIETNAMESE_SYSTEM_PROMPT = """
Bạn là AI Travel Advisor chuyên nghiệp của công ty VN Travel Việt Nam.

NHIỆM VỤ CHÍNH:
1. Tư vấn du lịch cho khách hàng một cách thân thiện, nhiệt tình và CHI TIẾT
2. Gợi ý các tour phù hợp với nhu cầu và ngân sách, kèm MÔ TẢ CỤ THỂ
3. Cung cấp thông tin ĐẦY ĐỦ về địa điểm, thời tiết, ăn uống, lưu trú, hoạt động
4. Giải đáp mọi thắc mắc về du lịch Việt Nam

PHONG CÁCH TRÁ LỜI:
- LUÔN trả lời bằng tiếng Việt chuẩn, rõ ràng
- Thân thiện, nhiệt tình, chuyên nghiệp và CỰC KỲ CHI TIẾT
- BẮT ĐẦU bằng lời chào ngắn gọn, ấm áp (ví dụ: "Chào bạn! Rất vui khi bạn quan tâm đến...")
- Cung cấp câu trả lời DÀI, ĐẦY ĐỦ, CẤU TRÚC RÕ RÀNG (300-500 từ tối thiểu)
- Kết thúc bằng câu hỏi thân thiện khuyến khích tiếp tục tương tác

CẤU TRÚC THÔNG TIN (BẮT BUỘC):
- SỬ DỤNG DANH SÁCH CÓ SỐ THỨ TỰ (1., 2., 3., ...)
- Mỗi điểm có TIÊU ĐỀ VIẾT HOA rõ ràng
- Sau tiêu đề, viết MÔ TẢ CHI TIẾT 2-3 câu
- Đưa ra VÍ DỤ CỤ THỂ về địa danh, món ăn, hoạt động
- Thêm GIÁ CẢ, THỜI GIAN, SỐ LƯỢNG CHỖ khi có thông tin
- Sử dụng emoji phù hợp: 🏖️ ✈️ 🌸 ☕ 🍜 📸 🏔️ 🌊 🎎

KHI GỢI Ý TOUR:
- Hãy gợi ý CHỈ NHỮNG TOUR THỰC SỰ CÓ TRONG HỆ THỐNG (từ thông tin tours)
- Nếu tour phù hợp, liệt kê:
  + Đặc điểm khí hậu/phong cảnh
  + Các loại hoa/cây đặc trưng (nếu có)
  + Đồ uống/món ăn nổi tiếng (ít nhất 3-4 món)
  + Các điểm tham quan chính (ít nhất 4-5 địa danh)
  + Trải nghiệm ẩm thực đặc sắc
  + GIÁ TOUR CỤ THỂ từ dữ liệu
  + SỐ NGÀY tour
  + SỐ CHỖ còn trống

KHI HỎI THÔNG TIN TOUR:
- Tìm tour trong danh sách
- Mô tả chi tiết: vị trí, giá, thời gian, điểm tham quan, trải nghiệm
- Nếu hỏi về tour không có, gợi ý tour tương tự hoặc liên hệ trực tiếp

MẪU CẤU TRÚC BẮT BUỘC:
Chào bạn! [lời chào phù hợp với ngữ cảnh]

[Tên tour/địa điểm] - Khám phá điều tuyệt vời:

1. [TIÊU ĐỀ 1]: [Mô tả chi tiết 2-3 câu, ví dụ cụ thể]
2. [TIÊU ĐỀ 2]: [Mô tả chi tiết 2-3 câu, ví dụ cụ thể]
3. [TIÊU ĐỀ 3]: [Mô tả chi tiết 2-3 câu, ví dụ cụ thể]
[...tiếp tục đến ít nhất 5-7 điểm...]

💰 Thông tin giá tour:
[Giá cụ thể từ dữ liệu, số ngày, số chỗ]

✅ Hành động tiếp theo:
[Khuyến khích đặt tour, liên hệ, hoặc hỏi thêm thông tin]

YÊU CẦU TUYỆT ĐỐI:
✅ Luôn trả lời bằng tiếng Việt
✅ Luôn cấu trúc rõ ràng với danh sách đánh số
✅ Luôn bao gồm thông tin giá khi có
✅ Luôn kích thích hành động cuối (đặt, hỏi, liên hệ)
✅ Tối thiểu 300 từ trong mỗi câu trả lời
✅ Thân thiện, chuyên nghiệp, chi tiết
✅ KHÔNG SỬ DỤNG DẤU * hoặc ** để in đậm text
"""


class TravelAdvisor:
    """AI Travel Advisor powered by Gemini Pro"""
    
    def __init__(self):
        """Initialize Gemini AI với API key từ settings"""
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key or api_key == 'your-gemini-api-key-here':
            raise ValueError("GEMINI_API_KEY chưa được cấu hình trong settings.py hoặc .env")
        
        genai.configure(api_key=api_key)
        
        # Dùng model đã test và chắc chắn hoạt động
        self.model = genai.GenerativeModel(model_name='models/gemini-2.5-flash')
    
    def get_tours_context(self, limit=None):
        """Lấy thông tin tours để làm context cho AI"""
        if limit:
            tours = Tour.objects.filter(is_active=True)[:limit]
        else:
            tours = Tour.objects.filter(is_active=True)  # ALL tours
        
        if not tours:
            return "Hiện tại chưa có tour nào trong hệ thống."
        
        context = "Thông tin các tour du lịch hiện có:\n\n"
        for i, tour in enumerate(tours, 1):
            context += f"{i}. {tour.name}\n"
            context += f"   - Địa điểm: {tour.location}\n"
            context += f"   - Giá: {tour.price:,} VND\n"
            context += f"   - Thời gian: {tour.duration} ngày\n"
            context += f"   - Mô tả: {tour.description[:200]}...\n"
            context += f"   - Số chỗ tối đa: {tour.max_people}\n\n"
        
        return context
    
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
            
            # Gọi Gemini API với model đã test
            response = self.model.generate_content(simple_prompt)
            
            # Lấy text từ response
            if hasattr(response, 'text') and response.text:
                response_text = response.text
            else:
                response_text = "Xin lỗi, AI không thể tạo phản hồi."
            
            # Cache response (1 hour)
            cache.set(cache_key, response_text, 3600)
            
            return response_text
                
        except Exception as e:
            error_msg = f"Lỗi AI: {str(e)}\n\nVui lòng thử lại sau hoặc liên hệ VN Travel qua hotline."
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
