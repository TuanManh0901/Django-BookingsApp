import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def get_weather(city):
    """
    Get current weather for a city using OpenWeather API with caching
    """
    # Normalize city name to match OpenWeather database
    city_mapping = {
        'phú quốc': 'Duong Dong',  # Main city in Phu Quoc Island
        'phu quoc': 'Duong Dong',
        'đà lạt': 'Da Lat',
        'da lat': 'Da Lat',
        'hà nội': 'Hanoi',
        'hanoi': 'Hanoi',
        'hạ long': 'Ha Long',
        'ha long': 'Ha Long',
        'nha trang': 'Nha Trang',
        'đà nẵng': 'Da Nang',
        'da nang': 'Da Nang',
        'hội an': 'Hoi An',
        'hoi an': 'Hoi An',
        'huế': 'Hue',
        'hue': 'Hue',
        'sapa': 'Sa Pa',
        'sa pa': 'Sa Pa',
        'hồ chí minh': 'Ho Chi Minh City',
        'ho chi minh': 'Ho Chi Minh City',
        'sài gòn': 'Ho Chi Minh City',
        'saigon': 'Ho Chi Minh City',
        'mũi né': 'Phan Thiet',  # Mui Ne is part of Phan Thiet
        'mui ne': 'Phan Thiet',
        'phan thiết': 'Phan Thiet',
        'phan thiet': 'Phan Thiet',
        'cần thơ': 'Can Tho',
        'can tho': 'Can Tho',
        # Fix missing locations
        'đắk lắk': 'Buon Ma Thuot',  # Buôn Ma Thuột is capital of Đắk Lắk
        'dak lak': 'Buon Ma Thuot',
        'buôn ma thuột': 'Buon Ma Thuot',
        'buon ma thuot': 'Buon Ma Thuot',
        'bà rịa - vũng tàu': 'Vung Tau',  # Main city of Bà Rịa - Vũng Tàu
        'ba ria vung tau': 'Vung Tau',
        'vũng tàu': 'Vung Tau',
        'vung tau': 'Vung Tau',
        'côn đảo': 'Vung Tau',  # Use Vung Tau as nearest major city
        'con dao': 'Vung Tau',
        'quảng bình': 'Dong Hoi',  # Capital of Quảng Bình province
        'quang binh': 'Dong Hoi',
        'đồng hới': 'Dong Hoi',
        'dong hoi': 'Dong Hoi',
        'phong nha': 'Dong Hoi',  # Phong Nha is in Quảng Bình
    }
    
    # Normalize and map city name
    city_lower = city.lower().strip()
    mapped_city = city_mapping.get(city_lower, city)
    
    # Create cache key - use ASCII only to avoid memcached warnings
    import hashlib
    cache_key = f'weather_{hashlib.md5(city_lower.encode()).hexdigest()[:10]}'
    
    # Check cache first
    cached_weather = cache.get(cache_key)
    if cached_weather:
        return cached_weather
    
    # Get API key from settings
    api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
    if not api_key:
        logger.warning("OpenWeather API key not configured")
        return None
    
    try:
        # Call OpenWeather API with mapped city name
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': mapped_city,  # Use mapped name
            'appid': api_key,
            'units': 'metric',  # Celsius
            'lang': 'vi'
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            weather_data = {
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity'],
            }
            
            # Cache for 15 minutes
            cache.set(cache_key, weather_data, 60 * 15)
            
            return weather_data
        else:
            logger.error(f"Weather API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching weather for {city}: {e}")
        return None


def get_weather_icon_emoji(icon_code):
    """
    Convert OpenWeather icon code to emoji
    """
    icon_map = {
        '01d': '☀️',   # clear sky day
        '01n': '🌙',   # clear sky night
        '02d': '🌤️',   # few clouds day
        '02n': '☁️',   # few clouds night
        '03d': '☁️',   # scattered clouds
        '03n': '☁️',
        '04d': '☁️',   # broken clouds
        '04n': '☁️',
        '09d': '🌧️',   # shower rain
        '09n': '🌧️',
        '10d': '🌦️',   # rain day
        '10n': '🌧️',  # rain night
        '11d': '⛈️',   # thunderstorm
        '11n': '⛈️',
        '13d': '🌨️',   # snow
        '13n': '🌨️',
        '50d': '🌫️',   # mist
        '50n': '🌫️',
    }
    return icon_map.get(icon_code, '🌤️')
