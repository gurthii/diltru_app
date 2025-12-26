from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, PriceAlert, PriceHistory, ScrapingLog
from .serializers import PriceAlertSerializer, ProductSerializer, PriceHistorySerializer
from .services import get_site_product

class PriceAlertViewSet(viewsets.ModelViewSet):
    """
    Handles creating and listing Price Alerts.
    The logic for scraping and creating products is now handled 
    entirely by the PriceAlertSerializer.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PriceAlertSerializer

    def get_queryset(self):
        # Only return alerts belonging to the logged-in user
        return PriceAlert.objects.filter(owner=self.request.user).select_related('product')

class ProductViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Public endpoints for viewing SPECIFIC products and their history.
    
    SECURITY CHANGE: 
    We removed 'ListModelMixin' (inherited from ReadOnlyModelViewSet previously).
    This means GET /api/products/ will now return 405 Method Not Allowed.
    Users can no longer browse the global database.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

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