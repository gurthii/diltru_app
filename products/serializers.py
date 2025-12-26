from rest_framework import serializers
from .models import Product, PriceAlert, PriceHistory

class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['price', 'timestamp']

# what the user sees in their Dashboard.
class ProductSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'sku', 
            'current_price', 
            'is_available', 
            'jumia_url' 
        ]

# Used only when clicking into a specific product page
class ProductSerializer(serializers.ModelSerializer):
    history = PriceHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class PriceAlertSerializer(serializers.ModelSerializer):
    # The user sees a clean product object, unaware of the complex history behind it.
    product = ProductSummarySerializer(read_only=True)
    
    jumia_url = serializers.URLField(write_only=True)

    class Meta:
        model = PriceAlert
        fields = [
            'id', 
            'product',      
            'target_price', 
            'status', 
            'jumia_url'    
        ]
        read_only_fields = ['status'] 

    def validate_jumia_url(self, value):
        if 'jumia.co.ke' not in value.lower():
            raise serializers.ValidationError("Only jumia.co.ke URLs are supported.")
        return value