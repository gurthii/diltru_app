from rest_framework import serializers
from django.conf import settings
from .models import Product, PriceAlert, PriceHistory
from .services import get_site_product
import re

# ==========================================
# 1. HISTORY SERIALIZER (For Charts)
# ==========================================
class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['price', 'timestamp']

# ==========================================
# 2. PRODUCT SERIALIZERS
# ==========================================
class ProductSummarySerializer(serializers.ModelSerializer):
    """
    Used when nesting product info inside an Alert.
    Keeps the response clean.
    """
    class Meta:
        model = Product
        fields = ['id', 'name', 'current_price', 'jumia_url', 'sku', 'image_url']

class ProductSerializer(serializers.ModelSerializer):
    """
    Used for full product CRUD if needed.
    """
    class Meta:
        model = Product
        fields = '__all__'

# ==========================================
# 3. PRICE ALERT SERIALIZER (The Main Engine)
# ==========================================
class PriceAlertSerializer(serializers.ModelSerializer):
    # Read-only nested representation of the product
    product = ProductSummarySerializer(read_only=True)
    
    # Write-only input for the URL
    jumia_url = serializers.URLField(write_only=True)
    
    # Explicitly define target_price to ensure it is REQUIRED and WRITABLE
    target_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = PriceAlert
        fields = ['id', 'product', 'target_price', 'status', 'jumia_url']
        read_only_fields = ['status', 'product']

    def validate_jumia_url(self, value):
        if 'jumia.co.ke' not in value.lower():
            raise serializers.ValidationError("Only jumia.co.ke URLs are supported.")
        return value
    def create(self, validated_data):
            # 1. Capture User Input
            jumia_url = validated_data.pop('jumia_url')
            user_target_price = validated_data['target_price'] 
            user = self.context['request'].user

            print(f"DEBUG: Processing Alert for {user.username}")

            # 2. Get or Scrape the Product
            # We check if we already have this product in our DB
            product = Product.objects.filter(jumia_url=jumia_url).first()
            
            if not product:
                print(" -> Product is new. Scraping Jumia...")
                product_data = get_site_product(jumia_url)
                
                if not product_data:
                    raise serializers.ValidationError({"jumia_url": "Failed to scrape product. Check the link."})

                # SKU Fallback Logic
                sku_value = product_data.get('sku')
                if not sku_value:
                    match = re.search(r'-([a-zA-Z0-9]+)\.html', jumia_url)
                    sku_value = match.group(1) if match else "UNKNOWN-SKU"

                # Create the Product
                product = Product.objects.create(
                    jumia_url=jumia_url,
                    name=product_data['name'],
                    current_price=product_data['price'],
                    is_available=product_data.get('is_available', True),
                    sku=sku_value,
                    image_url=product_data.get('image_url')
                )
                
                # Create initial history point
                PriceHistory.objects.create(product=product, price=product_data['price'])
            
            # 3. Create or Update the Alert
            # We default status to 'ACTIVE'. 
            # The Model's save() method will automatically switch it to 'TRIGGERED' 
            # and send the email if the price is already met.
            alert, created = PriceAlert.objects.update_or_create(
                owner=user,
                product=product,
                defaults={
                    'target_price': user_target_price,
                    'status': 'ACTIVE' 
                }
            )
            
            print(f" -> Alert Saved. Final Status: {alert.status}")
            return alert

    def update(self, instance, validated_data):
            """
            Handle updates (e.g. User edits target price in Dashboard)
            """
            # 1. Update the Target Price
            instance.target_price = validated_data.get('target_price', instance.target_price)
            
            # 2. Save (This triggers the model's new logic automatically!)
            instance.save()
            
            return instance