from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from users.views import CustomLoginView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Import the ViewSets
from products.views import PriceAlertViewSet, ProductViewSet, UserViewSet

# 1. Create the Router
# This handles the standard endpoints:
# - /api/alerts/ (List, Create, Delete)
# - /api/products/ (List, History)
# - /api/users/ (Admin List of Users)
router = DefaultRouter()
router.register(r'alerts', PriceAlertViewSet, basename='alert')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),

    # 2. Custom User Routes (Must come BEFORE router to prevent conflicts)
    # This grabs the paths from users/urls.py:
    # - /api/auth/register/
    # - /api/users/me/
    path('api/', include('users.urls')),

    # 3. The Router's Standard Routes
    # This appends the ViewSet paths defined above
    path('api/', include(router.urls)),
    
    # 4. Auth Token Login
    path('api/auth/login/', CustomLoginView.as_view(), name='api_token_auth'), 

    # 5. Frontend Routes (HTML Pages)
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),

    # 6. Documentation URLs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
