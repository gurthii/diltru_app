from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter() # Create a router and register our viewset with it.
router.register(r'products', ProductViewSet, basename='product') # The 'basename' is used for internal Django URL naming.

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]