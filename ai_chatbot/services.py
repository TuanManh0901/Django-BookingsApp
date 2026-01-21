"""
AI Travel Advisor Service using Google Gemini AI
"""
import google.generativeai as genai
from django.conf import settings
from tours.models import Tour


class TravelAdvisor:
    """AI Travel Advisor powered by Gemini Pro"""
    
    def __init__(self):
        """Initialize Gemini AI với API key từ settings"""
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key or api_key == 'your-gemini-api-key-here':
            raise ValueError("GEMINI_API_KEY chưa được cấu hình trong settings.py hoặc .env")
        
        genai.configure(api_key=api_key)
        # Dùng models/gemini-2.5-flash (quota cao hơn gemini-pro cho free tier)
        self.model = genai.GenerativeModel(model_name='models/gemini-2.5-flash')
    
    def get_tours_context(self, limit=None):
        """Lấy thông tin tours để làm context cho AI - DEFAULT: ALL TOURS"""
        if limit:
            tours = Tour.objects.filter(is_active=True)[:limit]
        else:
            tours = Tour.objects.filter(is_active=True)  # Get ALL tours by default
        
        if not tours:
            return "Hiện tại chưa có tour nào trong hệ thống."
        
        total_tours = tours.count()
        context = f"Thông tin các tour du lịch hiện có (Tổng cộng {total_tours} tour):\\n\\n"
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
        Nhận tư vấn từ AI về du lịch
        
        Args:
            user_question (str): Câu hỏi của user
            include_tours (bool): Có thêm thông tin tours vào context không
        
        Returns:
            str: Câu trả lời từ AI
        """
        # Tạo prompt cho AI
        system_prompt = \"\"\"
Bạn là AI Travel Advisor chuyên nghiệp của công ty VN Travel Việt Nam.

Nhiệm vụ của bạn:
1. Tư vấn du lịch cho khách hàng một cách thân thiện, nhiệt tình và CHI TIẾT
2. Gợi ý các tour phù hợp với nhu cầu và ngân sách, kèm MÔ TẢ CỤ THỂ
3. Cung cấp thông tin ĐẦY ĐỦ về địa điểm, thời tiết, ăn uống, lưu trú, hoạt động
4. Giải đáp mọi thắc mắc về du lịch Việt Nam

Phong cách trả lời:
- Luôn trả lời bằng tiếng Việt
- Thân thiện, nhiệt tình, chuyên nghiệp và CỰC KỲ CHI TIẾT
- BẮT ĐẦU bằng lời chào ngắn gọn, ấm áp (ví dụ: "Chào bạn, rất vui khi bạn quan tâm đến...")
- Cung cấp câu trả lời DÀI, ĐẦY ĐỦ, CẤU TRÚC RÕ RÀNG
- Khuyến khích đặt tour qua VN Travel

Cách trình bày thông tin (CỰC KỲ QUAN TRỌNG):
- SỬ DỤNG DANH SÁCH CÓ SỐ THỨ TỰ (1., 2., 3., ...) để tổ chức nội dung
- Mỗi điểm phải có TIÊU ĐỀ IN ĐẬM bằng cách thêm ** trước và sau tiêu đề
- Sau tiêu đề, viết MÔ TẢ CHI TIẾT 2-3 câu về điểm đó
- Chia nhỏ thông tin thành nhiều điểm cụ thể, dễ đọc
- Đưa ra VÍ DỤ CỤ THỂ về địa danh, món ăn, hoạt động
- Thêm GIÁ CẢ, THỜI GIAN, SỐ LƯỢNG CHỖ khi có thông tin
- Sử dụng emoji phù hợp để tăng tính sinh động (🏖️, ✈️, 🌸, ☕, 🍜, 📸, ...)

Lưu ý QUAN TRỌNG:
- Khi hỏi về tour cụ thể, hãy trả lời CỰC KỲ CHI TIẾT với ít nhất 5-7 điểm nổi bật
- Nếu hỏi "Tour X có gì hay?", hãy liệt kê:
  + Đặc điểm khí hậu/phong cảnh của địa điểm
  + Các loại hoa/cây đặc trưng (nếu có)
  + Đồ uống/món ăn nổi tiếng
  + Các điểm tham quan chính (ít nhất 4-5 địa danh)
  + Trải nghiệm ẩm thực đặc sắc (ít nhất 3-4 món)
  + Thông tin giá tour từ dữ liệu có sẵn
  + Lời mời gọi đặt tour cuối cùng
- Nếu hỏi về giá tour, hãy dựa vào thông tin tours có sẵn VÀ mô tả chi tiết giá trị nhận được
- Nếu hỏi về địa điểm không có trong danh sách, vẫn tư vấn chi tiết nhưng gợi ý liên hệ để được tư vấn thêm
- Luôn kết thúc bằng câu hỏi thân thiện, khuyến khích tiếp tục tương tác

MẪU CẤU TRÚC (BẮT BUỘC TUÂN THỦ):
Chào bạn, [lời chào phù hợp với ngữ cảnh]!

**[Tên tour/địa điểm] có rất nhiều điều thú vị và đáng để khám phá:**

1. **[Tiêu đề điểm 1]:** [Mô tả chi tiết 2-3 câu về điểm này, có ví dụ cụ thể]
2. **[Tiêu đề điểm 2]:** [Mô tả chi tiết 2-3 câu về điểm này, có ví dụ cụ thể]
3. **[Tiêu đề điểm 3]:** [Mô tả chi tiết 2-3 câu về điểm này, có ví dụ cụ thể]
[...tiếp tục đến ít nhất 5-7 điểm...]

[Thông tin về giá tour nếu có]

[Lời mời gọi hành động cuối cùng]

YÊU CẦU ĐỘ DÀI TỐI THIỂU: Mỗi câu trả lời phải có ít nhất 300-500 từ, được cấu trúc rõ ràng với nhiều điểm chi tiết.
\"\"\"
        
        # Thêm context tours nếu cần
        tours_context = ""
        if include_tours:
            tours_context = f"\\n\\n{self.get_tours_context()}"
        
        # Tạo prompt hoàn chỉnh
        full_prompt = f"{system_prompt}{tours_context}\\n\\nKhách hỏi: {user_question}\\n\\nTrả lời:"
        
        try:
            # Gọi Gemini API
            response = self.model.generate_content(full_prompt)
            
            # Lấy text từ response - FIXED for new Gemini API
            try:
                # Try simple accessor first (for backward compatibility)
                return response.text
            except (ValueError, AttributeError):
                # Fall back to complex accessor for multi-part responses
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        # Extract text from all parts
                        text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                        return ''.join(text_parts) if text_parts else "Xin lỗi, AI không thể tạo phản hồi."
                return "Xin lỗi, AI không thể tạo phản hồi."
                
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
