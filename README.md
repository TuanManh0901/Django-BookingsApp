# Hệ thống đặt tour du lịch thông minh với AI Travel Advisor

## 📋 Mô tả đề tài

Hệ thống quản lý và đặt tour du lịch tích hợp AI chatbot để tư vấn, gợi ý tour và hỗ trợ khách hàng tự động, tận dụng tối đa Django built-in features như ORM, Admin, ModelForm, Signals, Cache, Transactions, Sessions, FileField, Settings, Logging, Testing, và Security.

## 🎯 Tính năng chính

### 1. Quản lý Tour (Django Models + Admin)

**Hướng dẫn implementation**:

1. **Django Models**: Tạo Tour model với fields như name (CharField), description (TextField), price (DecimalField), duration (IntegerField), locations (ManyToManyField), itinerary (JSONField), images (ImageField), capacity (IntegerField), available_slots (IntegerField), created_at/updated_at (DateTimeField auto_now).
2. **Django Admin**: Register Tour model trong admin.py với list_display (name, price, available_slots), list_filter (duration, price), search_fields (name, description), custom actions (update_available_slots), inline cho locations và itinerary.
3. **Django Signals**: post_save signal để auto-update available_slots khi có booking mới.
4. **Django FileField**: Upload images với ImageField, auto-resize qua Pillow, validate file type/size.
5. **Django Cache**: Cache tour details và popular tours để giảm DB queries.

### 2. Quản lý Booking (Django ORM + Transactions)

**Hướng dẫn implementation**:

1. **Django Models**: Booking model với ForeignKey tới Tour và User, fields như booking_date (DateTimeField), status (CharField choices), number_of_people (IntegerField), total_price (DecimalField), payment_status (CharField choices).
2. **Django Transactions**: Sử dụng transaction.atomic() khi tạo booking để đảm bảo consistency (update tour.available_slots và create booking cùng lúc).
3. **Django Signals**: post_save signal cho Booking để send email confirmation qua Django email backend.
4. **Django Admin**: Custom admin với list_display (tour, user, status, total_price), filters, actions (confirm_booking, cancel_booking), readonly fields (created_at).
5. **Django ModelForm**: BookingForm với validation (check available_slots, calculate total_price), custom clean methods.

### 3. AI Chatbot Travel Advisor (Django Views + Sessions)

**Hướng dẫn implementation**:

1. **Django Models**: ChatHistory model với ForeignKey tới User, fields message (TextField), response (TextField), timestamp (DateTimeField), context (JSONField).
2. **Django Sessions**: Lưu conversation state trong session để maintain context giữa các messages.
3. **Django Views**: ChatView class-based view với get/post methods, validate user authentication, process message qua Gemini API, save to ChatHistory.
4. **Django Cache**: Cache AI responses cho common queries (tour recommendations) để improve performance.
5. **Django Signals**: post_save signal cho ChatHistory để log và trigger notifications nếu cần.
6. **Django Admin**: Admin interface để view chat logs, filter by user/date, export conversations.

### 4. Dashboard & Báo cáo (Django Admin + Aggregation)

**Hướng dẫn implementation**:

1. **Django Admin**: Custom admin site với dashboard widgets (total bookings, revenue, popular tours), charts qua django-admin-charts hoặc custom templates.
2. **Django ORM Aggregation**: Sử dụng annotate() và aggregate() để calculate statistics (Sum revenue, Count bookings, Avg ratings).
3. **Django Cache**: Cache dashboard data để avoid heavy queries on every load.
4. **Django Logging**: Log admin actions và report generations.
5. **Django FileField**: Export reports as CSV/PDF với custom admin actions.

### 5. Tích hợp APIs (Django Settings + Cache)

**Hướng dẫn implementation**:

1. **Django Settings**: Store API keys (Telegram token, Gemini API key, Google Maps key, Weather API key) trong settings.py hoặc .env với django-environ.
2. **Django Cache**: Cache API responses (weather data, map geocodes) với timeout để reduce external calls.
3. **Django Signals**: Signal để invalidate cache khi tour data changes.
4. **Django Logging**: Log API calls và errors cho monitoring.
5. **Django Testing**: Mock external APIs trong tests để isolate unit tests.

## 🛠️ Tech Stack (Django-centric)

### Backend (Django Framework)

- **Django ORM**: Thay thế SQL queries, sử dụng models, querysets, migrations.
- **Django Admin**: Interface quản lý data, custom actions, inlines, filters.
- **Django ModelForm**: Validation forms cho user input.
- **Django Sessions**: Manage user sessions cho chatbot và booking flow.
- **Django Cache Framework**: Cache data và API responses.
- **Django Signals**: Decouple logic, auto-updates.
- **Django Transactions**: Ensure data consistency.
- **Django FileField/ImageField**: Handle uploads an toàn.
- **Django Settings**: Configuration management.
- **Django Logging**: Audit và monitoring.
- **Django Testing**: Unit và integration tests.
- **Django Security**: CSRF, XSS protection, authentication.

### Database (PostgreSQL với Django)

- **Django Migrations**: Version control schema changes.
- **Django Models**: Define relationships, constraints, indexes.
- **Django Database Router**: Multi-database nếu cần (dev/prod).

### AI & External APIs (Django Integration)

- **Gemini Pro**: Integrate qua requests trong Django views, cache responses.
- **Telegram Bot API**: Webhook views trong Django để receive messages.
- **Google Maps API**: Geocode và display maps trong Django templates.
- **Weather API**: Fetch và cache weather data trong Django services.

### Frontend (Django Templates + Static Files)

- **Django Templates**: Render HTML với context processors.
- **Django Static Files**: Serve CSS/JS qua collectstatic.
- **Django Forms**: Render forms với crispy-forms hoặc custom widgets.

### DevOps (Django Deployment)

- **Django Settings**: Environment-specific configs (DEBUG, DATABASES).
- **Django Logging**: Production logging setup.
- **Django Security**: HTTPS, secure cookies.

## 📁 Cấu trúc Project (Django Apps)

```
travel_booking_system/
├── backend/
│   ├── api/
│   │   ├── auth.py
│   │   ├── tours.py
│   │   ├── bookings.py
│   │   └── chatbot.py
│   ├── ai/
│   │   ├── chatbot.py
│   │   ├── rag.py
│   │   └── embeddings.py
│   ├── models/
│   │   ├── tour.py
│   │   ├── booking.py
│   │   └── user.py
│   └── services/
│       ├── maps.py
│       └── weather.py
│
├── frontend/
│   ├── components/
│   ├── pages/
│   └── services/
│
├── database/
│   └── migrations/
│
└── docs/
    └── requirements.txt
```

## 📅 Timeline Implementation (Django-focused)

### Tuần 1-2: Django Setup & Models

**Hướng dẫn**:

1. **Django Project**: django-admin startproject, create apps.
2. **Django Models**: Define Tour, Booking, User models với relationships.
3. **Django Migrations**: python manage.py makemigrations, migrate.
4. **Django Admin**: Register models, customize list_display, filters.
5. **Django Fixtures**: Create mock data cho tours và locations.

### Tuần 3-4: Authentication & CRUD (Django Views + Forms)

**Hướng dẫn**:

1. **Django Authentication**: Sử dụng built-in auth views, login_required decorator.
2. **Django ModelForm**: Create TourForm, BookingForm với validation.
3. **Django Class-based Views**: ListView cho tours, CreateView cho bookings.
4. **Django Permissions**: Custom permissions cho admin vs user access.
5. **Django Sessions**: Track user preferences trong booking flow.

### Tuần 5-6: Frontend Integration (Django Templates)

**Hướng dẫn**:

1. **Django Templates**: Create base.html với blocks, extend cho pages.
2. **Django Context Processors**: Add common data (user info, cart) to all templates.
3. **Django Static Files**: Configure static URL, collectstatic.
4. **Django Forms Rendering**: Use form.as_p hoặc crispy-forms.
5. **Django Pagination**: Paginate tour listings với Paginator.

### Tuần 7-8: AI Chatbot (Django Views + Cache)

**Hướng dẫn**:

1. **Django Views**: Create ChatView để handle POST messages.
2. **Django Cache**: Cache AI responses và conversation context.
3. **Django Signals**: Log chat interactions.
4. **Django Sessions**: Maintain chat history per user.
5. **Django Testing**: Test chatbot responses với mock Gemini API.

### Tuần 9-10: Integrations & Dashboard (Django Services + Admin)

**Hướng dẫn**:

1. **Django Custom Management Commands**: Create commands để sync weather data.
2. **Django Admin Customization**: Add dashboard widgets, custom actions.
3. **Django Aggregation**: Build reports với QuerySet aggregation.
4. **Django Cache Invalidation**: Signals để clear cache khi data changes.
5. **Django Logging**: Setup logging cho API integrations.

### Tuần 11-12: Testing & Deployment (Django Testing + Settings)

**Hướng dẫn**:

1. **Django TestCase**: Write unit tests cho models, views, forms.
2. **Django Test Client**: Integration tests cho full request/response.
3. **Django Fixtures**: Load test data.
4. **Django Settings**: Production settings (DEBUG=False, secure cookies).
5. **Django Static/Media Files**: Configure serving qua web server.

## 🚀 Quick Start (Django Commands & Setup)

### 1. Django Project Setup

**Hướng dẫn**:

1. **Django Installation**: Install Django qua pip, create virtualenv.
2. **Django Project Creation**: django-admin startproject travel_booking_system.
3. **Django Apps Creation**: python manage.py startapp tours, bookings, etc.
4. **Django Settings Configuration**: Configure DATABASES, INSTALLED_APPS, SECRET_KEY.
5. **Django Environment Variables**: Use django-environ cho sensitive data.

### 2. Database Setup (Django Migrations)

**Hướng dẫn**:

1. **Django Models Definition**: Define all models với fields và relationships.
2. **Django Migrations Creation**: python manage.py makemigrations.
3. **Django Migrations Application**: python manage.py migrate.
4. **Django Superuser Creation**: python manage.py createsuperuser.
5. **Django Fixtures Loading**: python manage.py loaddata initial_data.json.

### 3. Development Server (Django Runserver)

**Hướng dẫn**:

1. **Django Runserver**: python manage.py runserver để start development server.
2. **Django Debug Toolbar**: Install và configure để debug queries.
3. **Django Admin Access**: Access /admin/ với superuser credentials.
4. **Django Static Files**: python manage.py collectstatic cho production.

## 📊 Database Schema (Django Models)

### Tour Model (Django ORM)

**Hướng dẫn**:

1. **Fields**: id (AutoField), name (CharField max_length=200), description (TextField), price (DecimalField), duration (IntegerField), locations (ManyToManyField), itinerary (JSONField), images (ImageField), capacity (IntegerField), available_slots (IntegerField), created_at (DateTimeField auto_now_add), updated_at (DateTimeField auto_now).
2. **Relationships**: ManyToMany với Location model.
3. **Methods**: Custom methods như is_available(), get_total_bookings().
4. **Meta**: ordering = ['-created_at'], db_table = 'tours'.

### Booking Model (Django ORM)

**Hướng dẫn**:

1. **Fields**: id (AutoField), tour (ForeignKey), user (ForeignKey), booking_date (DateTimeField), status (CharField choices), number_of_people (IntegerField), total_price (DecimalField), payment_status (CharField choices), created_at (DateTimeField auto_now_add).
2. **Relationships**: ForeignKey tới Tour và User (built-in auth.User hoặc custom).
3. **Methods**: Custom methods như calculate_total(), can_cancel().
4. **Meta**: ordering = ['-booking_date'], unique_together = ('tour', 'user', 'booking_date') nếu cần.

### User Model (Django Auth)

**Hướng dẫn**:

1. **Extend AbstractUser**: Add fields như phone (CharField), date_of_birth (DateField), preferences (JSONField).
2. **Permissions**: Custom permissions như can_book_tour, can_manage_tours.
3. **Groups**: Use Django groups cho roles (admin, customer, agent).
4. **Authentication**: Use built-in login/logout views.

### ChatHistory Model (Django ORM)

**Hướng dẫn**:

1. **Fields**: id (AutoField), user (ForeignKey), message (TextField), response (TextField), timestamp (DateTimeField auto_now_add), context (JSONField).
2. **Relationships**: ForeignKey tới User.
3. **Methods**: Custom methods như get_conversation_thread().
4. **Meta**: ordering = ['-timestamp'], indexes trên user và timestamp.

## 🤖 AI Chatbot Implementation (Django Integration)

### Capabilities (Django Views Logic)

**Hướng dẫn**:

1. **Tour Recommendation**: Parse user input (budget, preferences), query Tour model với filters, use Gemini để generate natural response.
2. **Location Info**: Query Location model, integrate Google Maps API cho coordinates.
3. **Weather Check**: Call Weather API, cache results, format response.
4. **Itinerary Planning**: Use Tour.itinerary field, customize với user preferences.
5. **Comparison**: Query multiple tours, use Gemini để compare features.

### AI Chatbot Architecture (Django-centric)

**Hướng dẫn**:

1. **Django Views**: ChatView handle POST requests, validate input, call AI service.
2. **Django Services**: Separate service classes cho Gemini integration, cache responses.
3. **Django Cache**: Cache common queries và AI responses.
4. **Django Sessions**: Store conversation context.
5. **Django Signals**: Log all interactions cho analysis.
6. **Django Admin**: Monitor chat logs, user satisfaction.

## 📝 Documentation (Django Guides)

### Core Guides (Django Implementation)

- [DATABASE_DESIGN.md](DATABASE_DESIGN.md) - Django Models design
- [AI_CHATBOT_GUIDE.md](AI_CHATBOT_GUIDE.md) - Django Views cho chatbot
- [AI_TECHNOLOGY.md](AI_TECHNOLOGY.md) - Django Cache/Sessions cho AI
- [TELEGRAM_BOT_GUIDE.md](TELEGRAM_BOT_GUIDE.md) - Django webhook views
- [SIMPLE_CHATBOT_GUIDE.md](SIMPLE_CHATBOT_GUIDE.md) - Django forms cho chat
- [TRAVEL_ADVISOR_GUIDE.md](TRAVEL_ADVISOR_GUIDE.md) - Django signals cho advisor
- [HUONG_DAN_TRAINING_AI.md](HUONG_DAN_TRAINING_AI.md) - Django models cho training data
- [MAPS_WEATHER_GUIDE.md](MAPS_WEATHER_GUIDE.md) - Django cache cho APIs
- [PAYMENT_MVP_GUIDE.md](PAYMENT_MVP_GUIDE.md) - Django models/admin cho payments

### Reference (Django Best Practices)

- Django ORM documentation
- Django Admin customization
- Django caching strategies
- Django security guidelines
- Django testing patterns

## 🎯 Mục tiêu điểm số (Django Excellence)

- **Tính ứng dụng**: 9/10 (Django Admin làm management dễ dàng)
- **Độ phức tạp kỹ thuật**: 8/10 (Django built-in features tận dụng tối đa)
- **AI/ML**: 8/10 (Django integration với Gemini)
- **Code quality**: 8/10 (Django best practices)
- **Documentation**: 9/10 (Detailed Django implementation guides)

**Tổng điểm dự kiến: 8-9/10**

---

**Triết lý**: Tận dụng tối đa Django built-in để build robust, scalable travel booking system với AI chatbot. Django ORM thay SQL, Admin thay custom UIs, Signals thay manual updates, Cache thay external calls. 🚀
