"""
AI Travel Advisor Service using Google Gemini AI - OPTIMIZED FOR SPEED
"""
import google.generativeai as genai
from django.conf import settings
from tours.models import Tour


class TravelAdvisor:
    """AI Travel Advisor powered by Gemini Flash - FAST responses"""
    
    def __init__(self):
        """Initialize Gemini AI với API key từ settings"""
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key or api_key == 'your-gemini-api-key-here':
            raise ValueError("GEMINI_API_KEY chưa được cấu hình trong settings.py hoặc .env")
        
        genai.configure(api_key=api_key)
        
        # SPEED OPTIMIZATION: Config for FASTER responses
        generation_config = {
            "temperature": 0.7,  # Lower = more focused, faster
            "top_p": 0.8,  # Reduce sampling space
            "top_k": 40,  # Limit token choices
            "max_output_tokens": 800,  # Shorter responses = faster (was unlimited)
        }
        
        self.model = genai.GenerativeModel(
            model_name='models/gemini-2.5-flash',  # Already fastest model
            generation_config=generation_config
        )
    
    def get_tours_context(self, limit=5):
        """Lấy thông tin tours để làm context cho AI"""
        tours = Tour.objects.filter(is_active=True)[:limit]
        
        if not tours:
            return "Hiện tại chưa có tour nào trong hệ thống."
        
        context = "Thông tin các tour du lịch hiện có:\\n\\n"
        for i, tour in enumerate(tours, 1):
            context += f"{i}. {tour.name}\\n"
            context += f"   - Địa điểm: {tour.location}\\n"
            context += f"   - Giá: {tour.price:,} VND\\n"
            context += f"   - Thời gian: {tour.duration} ngày\\n"
            context += f"   - Mô tả: {tour.description[:200]}...\\n"
            context += f"   - Số chỗ tối đa: {tour.max_people}\\n\\n"
        
        return context
    
    def get_advice(self, user_question, include_tours=True):
        """
        Nhận tư vấn từ AI về du lịch - OPTIMIZED FOR SPEED
        
        Args:
            user_question (str): Câu hỏi của user
            include_tours (bool): Có thêm thông tin tours vào context không
        
        Returns:
            str: Câu trả lời từ AI
        """
        # SPEED OPTIMIZATION: Prompt ngắn gọn hơn (từ 500+ từ xuống 150 từ)
        system_prompt = """Bạn là AI Travel Advisor của VN Travel Việt Nam.

Nhiệm vụ: Tư vấn du lịch nhanh chóng và hiệu quả.

Phong cách (QUAN TRỌNG - ĐỂ TRẢ LỜI NHANH):
- Trả lời bằng tiếng Việt, thân thiện
- Câu trả lời NGẮN GỌN (200-300 từ tối đa)
- Dùng danh sách số (1., 2., 3.) và in đậm **Tiêu đề**
- Thêm emoji 🏖️ ✈️ 🌸 ☕
- Kết thúc bằng câu hỏi ngắn

Cấu trúc:
Chào bạn! [1 câu giới thiệu]

**[Tên tour/địa điểm] có những điểm nổi bật:**
1. **[Tiêu đề]:** [Mô tả 1 câu]
2. **[Tiêu đề]:** [Mô tả 1 câu]
3. **[Tiêu đề]:** [Mô tả 1 câu]

💰 Giá: [nếu có] | 📞 Đặt tại VN Travel!

Bạn muốn biết thêm gì? 😊
"""
        
        # Thêm context tours nếu cần
        tours_context = ""
        if include_tours:
            tours_context = f"\\n\\n{self.get_tours_context()}"
        
        # Tạo prompt hoàn chỉnh
        full_prompt = f"{system_prompt}{tours_context}\\n\\nKhách hỏi: {user_question}\\n\\nTrả lời:"
        
        try:
            # Gọi Gemini API
            response = self.model.generate_content(full_prompt)
            
            # Lấy text từ response
            if hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
                
        except Exception as e:
            return f"Xin lỗi, AI hiện không khả dụng. Lỗi: {str(e)}\\n\\nVui lòng thử lại sau hoặc liên hệ trực tiếp với VN Travel qua hotline."
    
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
