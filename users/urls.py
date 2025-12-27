from django.urls import path
from .views import RegisterView, ManageUserView

urlpatterns = [
    # This matches 'auth/register/' from the main include
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    
    # This matches 'users/me/' from the main include
    path('users/me/', ManageUserView.as_view(), name='user_me'),
]