from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer
from .services import get_site_product

class ProductViewSet(viewsets.ModelViewSet):
    """
    This ViewSet automatically provides 'list', 'create', 'retrieve',
    'update', and 'destroy' actions for Products.
    """
    serializer_class = ProductSerializer
    
    permission_classes = [permissions.IsAuthenticated] # ensures that only loggd-in users can access this endpoint
  
    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user) # user will only see the product they are tracking

    def perform_create(self, serializer):
        url = serializer.validated_data.get('jumia_url')
        scraped_data = get_site_product(url)

        if not scraped_data or not scraped_data.get('sku'):
            # triggers 400 bad request with a custom msg
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                "jumia_url" : "Invalid product page or SKU not found. Please double-check your link."
            })
        serializer.save(
            owner=self.request.user,
            name=scraped_data['name'],
            current_price=scraped_data['price'],
            sku=scraped_data['sku']
            ) # created tracking item (new url POST) sets the 'owner' to current logged-in user


