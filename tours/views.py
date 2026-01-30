from django.contrib import admin as django_admin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from .models import Review, Tour
from .utils import get_weather, get_weather_icon_emoji

POPULAR_DESTINATIONS = [
    {'city': 'Hà Nội', 'query_param': 'Hà Nội'},
    {'city': 'Hạ Long', 'query_param': 'Hạ Long'},
    {'city': 'Phú Quốc', 'query_param': 'Phú Quốc'},
]


def home_view(request):
    """Trang chủ với tours nổi bật và đánh giá."""
    featured_reviews = Review.objects.all().select_related(
        'user', 'tour'
    ).order_by('-created_at')[:6]
    
    destinations_with_weather = []
    for dest in POPULAR_DESTINATIONS:
        weather_data = get_weather(dest['city'])
        dest['weather'] = weather_data
        dest['icon_emoji'] = get_weather_icon_emoji(
            weather_data.get('icon', '01d')
        ) if weather_data else '🌤️'
        destinations_with_weather.append(dest)
    
    return render(request, 'home.html', {
        'featured_reviews': featured_reviews,
        'destinations_weather': destinations_with_weather
    })


def vietnam_destinations_view(request):
    """Trang điểm đến Việt Nam - hiển thị tất cả tours Việt Nam."""
    vietnam_tours = Tour.objects.filter(
        is_active=True
    ).exclude(
        Q(location__icontains='Cambodia') | 
        Q(location__icontains='Campuchia') |
        Q(location__icontains='Laos') |
        Q(location__icontains='Lào')
    ).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-created_at')
    
    locations = set(tour.location for tour in vietnam_tours)
    
    return render(request, 'destinations/vietnam.html', {
        'tours': vietnam_tours,
        'locations': sorted(locations),
        'total_tours': vietnam_tours.count()
    })


def cambodia_destinations_view(request):
    """Trang điểm đến Campuchia."""
    cambodia_tours = Tour.objects.filter(
        is_active=True
    ).filter(
        Q(location__icontains='Cambodia') | 
        Q(location__icontains='Campuchia') |
        Q(location__icontains='Angkor')
    ).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-created_at')
    
    return render(request, 'destinations/cambodia.html', {
        'tours': cambodia_tours,
        'total_tours': cambodia_tours.count()
    })


def laos_destinations_view(request):
    """Trang điểm đến Lào."""
    laos_tours = Tour.objects.filter(
        is_active=True
    ).filter(
        Q(location__icontains='Laos') | 
        Q(location__icontains='Lào') |
        Q(location__icontains='Luang Prabang')
    ).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-created_at')
    
    return render(request, 'destinations/laos.html', {
        'tours': laos_tours,
        'total_tours': laos_tours.count()
    })


def responsibility_view(request):
    """Trang Du lịch có trách nhiệm và Bền vững."""
    return render(request, 'pages/responsibility.html')


def about_us_view(request):
    """Trang Về chúng tôi - VN Travel."""
    return render(request, 'pages/about.html')


def team_view(request):
    """Trang giới thiệu đội ngũ."""
    return render(request, 'pages/team.html')


def education_view(request):
    """Trang Giáo dục du lịch và Tài nguyên."""
    return render(request, 'pages/education.html')


class SearchToursView(ListView):
    """Tìm kiếm và lọc tours với phân trang."""
    
    model = Tour
    template_name = 'search_tours.html'
    context_object_name = 'tours'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Tour.objects.filter(is_active=True)
        
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queries = {
                search_query, 
                search_query.title(), 
                search_query.upper(), 
                search_query.lower()
            }
            
            query = Q()
            for q_str in queries:
                query |= Q(name__icontains=q_str)
                query |= Q(description__icontains=q_str)
                query |= Q(location__icontains=q_str)
            
            queryset = queryset.filter(query)
        
        location = self.request.GET.get('location', '').strip()
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        duration = self.request.GET.get('duration')
        if duration:
            try:
                queryset = queryset.filter(duration=int(duration))
            except ValueError:
                pass
        
        min_duration = self.request.GET.get('min_duration')
        max_duration = self.request.GET.get('max_duration')
        if min_duration:
            try:
                queryset = queryset.filter(duration__gte=int(min_duration))
            except ValueError:
                pass
        if max_duration:
            try:
                queryset = queryset.filter(duration__lte=int(max_duration))
            except ValueError:
                pass
        
        is_hot = self.request.GET.get('is_hot', '').lower()
        if is_hot == 'true':
            queryset = queryset.filter(is_hot=True)
        
        sort_by = self.request.GET.get('sort_by', '-created_at')
        valid_sorts = {
            'price_low': 'price',
            'price_high': '-price',
            'duration_short': 'duration',
            'duration_long': '-duration',
            'name_az': 'name',
            'name_za': '-name',
            'newest': '-created_at',
            'oldest': 'created_at',
        }
        
        if sort_by in valid_sorts:
            queryset = queryset.order_by(valid_sorts[sort_by])
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add weather data for each tour
        tours_with_weather = []
        for tour in context['tours']:
            weather = get_weather(tour.location)
            tour.weather_data = weather
            if weather:
                tour.weather_emoji = get_weather_icon_emoji(weather.get('icon', '01d'))
            else:
                tour.weather_emoji = '🌤️'
            tours_with_weather.append(tour)
        
        context['tours'] = tours_with_weather
        
        # Add filter context for UI
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_location'] = self.request.GET.get('location', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['selected_duration'] = self.request.GET.get('duration', '')
        context['selected_sort'] = self.request.GET.get('sort_by', 'newest')
        
        # Get unique locations for filter dropdown
        context['locations'] = Tour.objects.filter(is_active=True).values_list('location', flat=True).distinct().order_by('location')
        
        # Get duration range
        context['durations'] = sorted(set(Tour.objects.filter(is_active=True).values_list('duration', flat=True)))
        
        # Count active filters
        active_filters = 0
        if context['search_query']: active_filters += 1
        if context['selected_location']: active_filters += 1
        if context['min_price']: active_filters += 1
        if context['max_price']: active_filters += 1
        if context['selected_duration']: active_filters += 1
        context['active_filters_count'] = active_filters
        
        return context

class TourListView(ListView):
    """Tour list page with weather data"""
    model = Tour
    template_name = 'tour_list.html'
    context_object_name = 'tours'
    paginate_by = 9
    
    def get_queryset(self):
        return Tour.objects.filter(is_active=True).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add weather data to each tour"""
        from tours.utils import get_weather, get_weather_icon_emoji
        
        context = super().get_context_data(**kwargs)
        
        # Add weather data for each tour in the current page
        tours_list = list(context['tours'])
        for tour in tours_list:
            weather_data = get_weather(tour.location)
            tour.weather_data = weather_data if weather_data else None
            tour.weather_emoji = get_weather_icon_emoji(weather_data.get('icon', '01d')) if weather_data else '☀️'
        
        context['tours'] = tours_list
        
        # Filter options for UI
        context['locations'] = Tour.objects.filter(is_active=True).values_list('location', flat=True).distinct().order_by('location')
        context['durations'] = sorted(set(Tour.objects.filter(is_active=True).values_list('duration', flat=True)))
        
        return context

class TourDetailView(DetailView):
    model = Tour
    template_name = 'tour_detail.html'
    context_object_name = 'tour'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour = self.object  # DetailView sets self.object
        
        # Reviews context
        reviews = tour.reviews.select_related('user').order_by('-created_at')
        context['reviews'] = reviews
        context['avg_rating'] = tour.get_average_rating()
        context['rating_breakdown'] = tour.get_rating_breakdown()
        context['total_reviews'] = reviews.count()
        
        return context

def about_view(request):
    """About Us page"""
    context = {
        'page_title': 'Về Chúng Tôi - VN Travel',
        'team_members': [
            {
                'name': 'Nguyễn Văn A',
                'position': 'CEO & Founder',
                'image': 'https://ui-avatars.com/api/?name=Nguyen+Van+A&size=200&background=667eea&color=fff',
                'bio': '15 năm kinh nghiệm trong ngành du lịch'
            },
            {
                'name': 'Trần Thị B',
                'position': 'Marketing Director',
                'image': 'https://ui-avatars.com/api/?name=Tran+Thi+B&size=200&background=11998e&color=fff',
                'bio': 'Chuyên gia marketing du lịch'
            },
            {
                'name': 'Lê Văn C',
                'position': 'Tour Operations Manager',
                'image': 'https://ui-avatars.com/api/?name=Le+Van+C&size=200&background=f093fb&color=fff',
                'bio': 'Quản lý vận hành tour chuyên nghiệp'
            },
        ],
        'stats': {
            'years': '15+',
            'tours': '500+',
            'customers': '10,000+',
            'rating': '4.8/5'
        }
    }
    return render(request, 'about.html', context)

def contact_view(request):
    """Contact page with form handling"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        
        # Here you would normally send email or save to database
        # For now, just show success message
        messages.success(request, f'Cảm ơn {name}! Chúng tôi đã nhận được tin nhắn của bạn và sẽ phản hồi sớm nhất.')
        return redirect('contact')
    
    context = {
        'page_title': 'Liên Hệ - VN Travel',
    }
    return render(request, 'contact.html', context)

def faq_view(request):
    """FAQ page"""
    faqs = [
        {
            'category': 'Đặt Tour',
            'questions': [
                {
                    'q': 'Làm thế nào để đặt tour?',
                    'a': 'Bạn chỉ cần chọn tour yêu thích, click "Đặt Tour Ngay", điền thông tin và thanh toán. Rất đơn giản!'
                },
                {
                    'q': 'Tôi có thể hủy tour không?',
                    'a': 'Có, bạn có thể hủy tour trước 7 ngày để được hoàn tiền 100%. Vui lòng xem chính sách hủy tour chi tiết.'
                },
            ]
        },
        {
            'category': 'Thanh Toán',
            'questions': [
                {
                    'q': 'Các phương thức thanh toán nào được hỗ trợ?',
                    'a': 'Chúng tôi hỗ trợ thanh toán qua MoMo, chuyển khoản ngân hàng, và thanh toán trực tiếp.'
                },
                {
                    'q': 'Có an toàn khi thanh toán online không?',
                    'a': 'Hoàn toàn an toàn! Chúng tôi sử dụng mã hóa SSL và các cổng thanh toán uy tín.'
                },
            ]
        },
    ]
    
    context = {
        'page_title': 'Câu Hỏi Thường Gặp - VN Travel',
        'faqs': faqs
    }
    return render(request, 'faq.html', context)

def admin_dashboard(request):
    total_tours = Tour.objects.count()
    active_tours = Tour.objects.filter(is_active=True).count()
    total_images = Tour.objects.aggregate(total_images=Count('images'))['total_images'] or 0

    try:
        app_list = django_admin.site.get_app_list(request)
        total_models = sum(len(app.get('models', [])) for app in app_list)
    except Exception:
        app_list = []
        total_models = 0

    context = {
        'total_tours': total_tours,
        'active_tours': active_tours,
        'total_images': total_images,
        'app_list': app_list,
        'total_models': total_models,
    }
    return render(request, 'admin/index.html', context)
