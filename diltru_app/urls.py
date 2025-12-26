from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token # <--- Import this
from users.views import CustomLoginView
urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes
    path('api/', include('products.urls')),
    path('api/auth/register/', include('users.urls')), # custom user registration
    path('api/auth/login/', CustomLoginView.as_view(), name='api_token_auth'), # issues a JSON token when POST username/password


    # Frontend routes
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
]