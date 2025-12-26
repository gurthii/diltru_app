from rest_framework import serializers
from .models import Product, PriceAlert, PriceHistory

class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['price', 'timestamp']

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the shared Product model.
    """
    history = PriceHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'jumia_url', 'sku', 'name', 
            'current_price', 'is_available', 
            'last_updated', 'history'
        ]

class PriceAlertSerializer(serializers.ModelSerializer):
    """
    The main serializer for the User Dashboard.
    It links the 'owner' to the 'product' details.
    """
    # Nested Serialization: returns the full product object instead of just an ID
    product = ProductSerializer(read_only=True)
    
    # Write-only field to accept URL input during POST
    jumia_url = serializers.URLField(write_only=True)

    class Meta:
        model = PriceAlert
        fields = [
            'id', 
            'product',      # The full nested product data
            'jumia_url',    # Input only
            'target_price', 
            'status', 
            'created_at'
        ]
        read_only_fields = ['status', 'created_at']

    def validate_jumia_url(self, value):
        if 'jumia.co.ke' not in value.lower():
            raise serializers.ValidationError("Only jumia.co.ke URLs are supported.")
        return value