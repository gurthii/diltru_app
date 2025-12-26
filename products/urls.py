from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PriceAlertViewSet, ProductViewSet

router = DefaultRouter()

# We call the endpoint 'alerts' because it returns a list of alerts
router.register(r'alerts', PriceAlertViewSet, basename='price-alert')
router.register(r'products', ProductViewSet, basename='product')
urlpatterns = [
    path('', include(router.urls)),
]