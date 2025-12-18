from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer

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
        serializer.save(owner=self.request.user) # created tracking item (new url POST) sets the 'owner' to current logged-in user