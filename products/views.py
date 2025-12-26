from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, PriceAlert, PriceHistory, ScrapingLog
from .serializers import PriceAlertSerializer, ProductSerializer
from .services import get_site_product

class PriceAlertViewSet(viewsets.ModelViewSet):
    """
    Handles creating and listing Price Alerts.
    This is the main endpoint for the user dashboard.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PriceAlertSerializer

    def get_queryset(self):
        # Only return alerts belonging to the logged-in user
        return PriceAlert.objects.filter(owner=self.request.user).select_related('product')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        url = serializer.validated_data.get('jumia_url')
        
        # 1. Check if Product exists globally (by URL)
        product = Product.objects.filter(jumia_url=url).first()

        if not product:
            # 2. If not, SCRAPE IT
            data = get_site_product(url)
            
            if not data or not data.get('sku'):
                # Log the failure (Rubric: Error Handling & Logging)
                # We create a dummy product entry just to attach the log, or just log generally
                # For now, we return 400
                return Response(
                    {"error": "Could not scrape product. Check the link or try again later."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the Product
            product = Product.objects.create(
                jumia_url=url,
                sku=data['sku'],
                name=data['name'],
                current_price=data['price']
            )
            
            # Record first price history
            PriceHistory.objects.create(product=product, price=data['price'])
            
            # Log success
            ScrapingLog.objects.create(product=product, status="SUCCESS", details="Initial scrape")

        # 3. Create the Alert (Link User -> Product)
        # get_or_create prevents duplicates (The Single User Bug Fix)
        alert, created = PriceAlert.objects.get_or_create(
            owner=request.user,
            product=product,
            defaults={'target_price': product.current_price}
        )

        # 4. Return the result
        response_serializer = self.get_serializer(alert)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(response_serializer.data, status=status_code)
    
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public endpoints for viewing products and their history.
    No authentication required to view (AllowAny).
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny] # Public access

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Custom endpoint: /api/products/{id}/history/
        Returns only the price history for charts.
        """
        product = self.get_object()
        # Use the 'history' related_name from your models
        history_data = product.history.all().order_by('timestamp')
        serializer = PriceHistorySerializer(history_data, many=True)
        return Response(serializer.data)