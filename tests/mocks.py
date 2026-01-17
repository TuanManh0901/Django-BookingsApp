"""
Mock objects for external APIs.

These mocks simulate responses from third-party services without making actual API calls.
"""
import json
from unittest.mock import Mock, MagicMock


class MockMoMoAPI:
    """Mock MoMo payment gateway API responses."""
    
    @staticmethod
    def successful_payment_request():
        """Mock successful payment request creation."""
        return {
            'partnerCode': 'MOMO',
            'orderId': 'TEST_ORDER_123456',
            'requestId': 'TEST_REQ_123456',
            'amount': 5000000,
            'responseTime': 1234567890,
            'message': 'Successful.',
            'resultCode': 0,
            'payUrl': 'https://test.momo.vn/pay?token=TEST_TOKEN',
            'deeplink': 'momo://pay?token=TEST_TOKEN',
            'qrCodeUrl': 'https://test.momo.vn/qr/TEST_QR'
        }
    
    @staticmethod
    def successful_callback():
        """Mock successful payment callback/IPN from MoMo."""
        return {
            'partnerCode': 'MOMO',
            'orderId': 'TEST_ORDER_123456',
            'requestId': 'TEST_REQ_123456',
            'amount': 5000000,
            'orderInfo': 'Thanh toán tour du lịch',
            'orderType': 'momo_wallet',
            'transId': 2234567890,
            'resultCode': 0,
            'message': 'Successful.',
            'payType': 'qr',
            'responseTime': 1234567890,
            'extraData': '',
            'signature': 'test_signature_hash'
        }
    
    @staticmethod
    def failed_callback(result_code=1001, message='Transaction failed'):
        """Mock failed payment callback."""
        return {
            'partnerCode': 'MOMO',
            'orderId': 'TEST_ORDER_123456',
            'requestId': 'TEST_REQ_123456',
            'amount': 5000000,
            'resultCode': result_code,
            'message': message,
            'responseTime': 1234567890,
            'signature': 'test_signature_hash'
        }
    
    @staticmethod
    def insufficient_balance_callback():
        """Mock callback for insufficient balance."""
        return MockMoMoAPI.failed_callback(
            result_code=1005,
            message='Insufficient balance'
        )


class MockGeminiAPI:
    """Mock Google Gemini AI API responses."""
    
    @staticmethod
    def successful_chat_response(prompt=''):
        """Mock successful chat response from Gemini."""
        mock_response = MagicMock()
        
        # Default responses based on common prompts
        if 'tour' in prompt.lower() or 'du lịch' in prompt.lower():
            response_text = """Chúng tôi có nhiều tour du lịch tuyệt vời! 
            Bạn quan tâm đến tour nào? Chúng tôi có:
            - Tour Hạ Long Bay 3 ngày 2 đêm
            - Tour Phú Quốc 4 ngày 3 đêm  
            - Tour Sapa 3 ngày 2 đêm
            
            Bạn muốn biết thêm chi tiết về tour nào?"""
        elif 'giá' in prompt.lower() or 'price' in prompt.lower():
            response_text = "Giá tour dao động từ 3.000.000đ - 10.000.000đ tùy theo điểm đến và thời gian."
        else:
            response_text = "Xin chào! Tôi là AI Travel Advisor. Tôi có thể giúp gì cho bạn?"
        
        mock_response.text = response_text
        mock_response.candidates = [MagicMock(content=MagicMock(parts=[MagicMock(text=response_text)]))]
        
        return mock_response
    
    @staticmethod
    def error_response(error_message='API Error'):
        """Mock error response from Gemini."""
        raise Exception(error_message)
    
    @staticmethod
    def mock_generate_content(prompt):
        """Mock generateContent method."""
        return MockGeminiAPI.successful_chat_response(prompt)


class MockWeatherAPI:
    """Mock OpenWeather API responses."""
    
    @staticmethod
    def successful_response(city='Hanoi', temp=25, weather='Clear'):
        """Mock successful weather API response."""
        return {
            'coord': {'lon': 105.85, 'lat': 21.03},
            'weather': [
                {
                    'id': 800,
                    'main': weather,
                    'description': 'clear sky',
                    'icon': '01d'
                }
            ],
            'base': 'stations',
            'main': {
                'temp': temp,
                'feels_like': temp - 2,
                'temp_min': temp - 3,
                'temp_max': temp + 2,
                'pressure': 1013,
                'humidity': 70
            },
            'visibility': 10000,
            'wind': {'speed': 3.5, 'deg': 180},
            'clouds': {'all': 0},
            'dt': 1234567890,
            'sys': {
                'type': 1,
                'id': 9308,
                'country': 'VN',
                'sunrise': 1234567800,
                'sunset': 1234567900
            },
            'timezone': 25200,
            'id': 1581130,
            'name': city,
            'cod': 200
        }
    
    @staticmethod
    def error_response(status_code=404):
        """Mock error response from weather API."""
        return {
            'cod': str(status_code),
            'message': 'city not found'
        }
    
    @staticmethod
    def rainy_weather(city='Ho Chi Minh City'):
        """Mock rainy weather response."""
        return MockWeatherAPI.successful_response(
            city=city,
            temp=28,
            weather='Rain'
        )


class MockGoogleMapsAPI:
    """Mock Google Maps API responses."""
    
    @staticmethod
    def successful_geocode_response(location='Hanoi'):
        """Mock successful geocoding response."""
        coordinates = {
            'Hanoi': {'lat': 21.0285, 'lng': 105.8542},
            'Ho Chi Minh City': {'lat': 10.8231, 'lng': 106.6297},
            'Da Nang': {'lat': 16.0544, 'lng': 108.2022},
            'Hue': {'lat': 16.4637, 'lng': 107.5909},
            'Nha Trang': {'lat': 12.2388, 'lng': 109.1967},
            'Da Lat': {'lat': 11.9404, 'lng': 108.4583},
            'Phu Quoc': {'lat': 10.2899, 'lng': 103.9840},
            'Ha Long': {'lat': 20.9599, 'lng': 107.0431},
            'Sapa': {'lat': 22.3364, 'lng': 103.8438},
        }
        
        coord = coordinates.get(location, {'lat': 21.0285, 'lng': 105.8542})
        
        return {
            'results': [
                {
                    'geometry': {
                        'location': coord
                    },
                    'formatted_address': f'{location}, Vietnam'
                }
            ],
            'status': 'OK'
        }
    
    @staticmethod
    def error_response():
        """Mock error response from Google Maps."""
        return {
            'results': [],
            'status': 'ZERO_RESULTS'
        }


class MockTelegramAPI:
    """Mock Telegram Bot API responses."""
    
    @staticmethod
    def successful_send_message():
        """Mock successful message send."""
        return {
            'ok': True,
            'result': {
                'message_id': 123,
                'chat': {'id': 456, 'type': 'private'},
                'date': 1234567890,
                'text': 'Test message'
            }
        }
    
    @staticmethod
    def error_response(error_code=400, description='Bad Request'):
        """Mock error response from Telegram."""
        return {
            'ok': False,
            'error_code': error_code,
            'description': description
        }


# Helper function to create mock requests
def create_mock_requests_response(json_data, status_code=200):
    """Create a mock requests.Response object."""
    mock_response = Mock()
    mock_response.json.return_value = json_data
    mock_response.status_code = status_code
    mock_response.text = json.dumps(json_data)
    mock_response.ok = (200 <= status_code < 300)
    return mock_response
