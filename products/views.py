from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from users.serializers import AdminUserSerializer
from django.contrib.auth import get_user_model

from .models import Product, PriceAlert, PriceHistory
from .serializers import PriceAlertSerializer, ProductSerializer, PriceHistorySerializer

User = get_user_model()


class PriceAlertViewSet(viewsets.ModelViewSet):
    """
    Handles creating and listing Price Alerts for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PriceAlertSerializer

    # Filtering, searching, and ordering
    filter_backends = [
        DjangoFilterBackend,    # Handles ?status=TRIGGERED
        filters.SearchFilter,   # Handles ?search=Sony
        filters.OrderingFilter  # Handles ?ordering=-target_price
    ]
    filterset_fields = ['status']
    search_fields = ['product__name', 'product__sku', 'product__jumia_url']
    ordering_fields = ['target_price', 'created_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        # Guard for drf-spectacular schema generation (fake view has no real user)
        if getattr(self, 'swagger_fake_view', False):
            return PriceAlert.objects.none()

        return PriceAlert.objects.filter(
            owner=self.request.user
        ).select_related('product')


class ProductViewSet(viewsets.ModelViewSet):
    """
    Allows authenticated users to see / manage all products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Custom endpoint: /api/products/{id}/history/
        Returns the price history for the product (for charts).
        """
        product = self.get_object()
        history_data = product.history.all().order_by('timestamp')
        serializer = PriceHistorySerializer(history_data, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    Allows Super Admin to see / manage user accounts.
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]