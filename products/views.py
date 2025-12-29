from rest_framework import viewsets, permissions, status, mixins, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, PriceAlert, PriceHistory, ScrapingLog
from .serializers import PriceAlertSerializer, ProductSerializer, PriceHistorySerializer
from .services import get_site_product

User = get_user_model()

class PriceAlertViewSet(viewsets.ModelViewSet):
    """
    Handles creating and listing Price Alerts.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PriceAlertSerializer

    def get_queryset(self):
        # Handling Schema Generation (Swagger)
        # If drf-spectacular is generating the schema, it uses a fake view.
        # We return an empty queryset to prevent the "AnonymousUser" error.
        if getattr(self, 'swagger_fake_view', False):
            return PriceAlert.objects.none()

        # Only return alerts belonging to the logged-in user
        return PriceAlert.objects.filter(owner=self.request.user).select_related('product')
    
    # 1. Enable tools
    filter_backends = [
        DjangoFilterBackend,    # Handles ?status=TRIGGERED
        filters.SearchFilter,   # Handles ?search=Sony
        filters.OrderingFilter  # Handles ?ordering=-target_price
    ]

    # 2. Define Filterable Fields
    filterset_fields = ['status'] # Allow filtering by 'ACTIVE', 'TRIGGERED'

    # 3. Define Searchable Fields
    # We use double underscore __ to search inside the related 'product' model
    search_fields = ['product__name', 'product__sku', 'product__jumia_url']

    # 4. Define Sortable Fields
    ordering_fields = ['target_price', 'created_at', 'status']
    ordering = ['-created_at'] # Default sort: Newest first

# --- 2. UPDATED PRODUCT VIEWSET (For Admin Visibility) ---
class ProductViewSet(viewsets.ModelViewSet):
    """
    Allows Admin to see/manage all products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated] 

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Custom endpoint: /api/products/{id}/history/
        Returns only the price history for charts.
        """
        product = self.get_object()
        history_data = product.history.all().order_by('timestamp')
        serializer = PriceHistorySerializer(history_data, many=True)
        return Response(serializer.data)


# --- 3. NEW USER VIEWSET (For Admin Management) ---
# Renamed from UserSerializer to AdminUserSerializer to avoid conflict ---
class AdminUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_active']

class UserViewSet(viewsets.ModelViewSet):
    """
    Allows Super Admin to see/manage users.
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer # Updated reference
    permission_classes = [permissions.IsAdminUser] # Strict security!