from rest_framework import serializers
from django.core.mail import send_mail
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
        # A. Capture the User's Input
        jumia_url = validated_data.pop('jumia_url')
        user_target_price = validated_data['target_price'] 
        user = self.context['request'].user

        print(f"DEBUG: Processing Alert. User Target: {user_target_price}")

        # B. Get or Scrape the Product
        product = Product.objects.filter(jumia_url=jumia_url).first()
        
        if not product:
            print(" -> Product is new. Scraping Jumia...")
            product_data = get_site_product(jumia_url)
            
            if not product_data:
                raise serializers.ValidationError({"jumia_url": "Failed to scrape product. Check the link."})

            # --- SKU Handling Logic ---
            sku_value = product_data.get('sku')
            if not sku_value:
                # Fallback: Extract ID from URL (e.g. ...-sku12345.html)
                match = re.search(r'-([a-zA-Z0-9]+)\.html', jumia_url)
                sku_value = match.group(1) if match else "UNKNOWN-SKU"
            # --------------------------

            product = Product.objects.create(
                jumia_url=jumia_url,
                name=product_data['name'],
                current_price=product_data['price'],
                # Safe .get() prevents crash if key is missing
                is_available=product_data.get('is_available', True),
                sku=sku_value,
                image_url=product_data.get('image_url')
            )
            
            # Create first history point so chart isn't empty
            PriceHistory.objects.create(product=product, price=product_data['price'])
        
        # C. Check for Immediate Trigger & Send Email
        initial_status = 'ACTIVE'
        if product.current_price <= user_target_price:
            initial_status = 'TRIGGERED'
            
            # --- EMAIL NOTIFICATION LOGIC ---
            print(f"--- Instant Deal Detected! Sending email to {user.email} ---")
            try:
                short_product_name = " ".join(product.name.split()[:3])+"..."
                formatted_current_price = f"{int(product.current_price):,d}"
                formatted_target_price = f"{int(user_target_price):,d}"


                subject = f"Price Alert: {short_product_name} is now at KSh {formatted_current_price}!"
                message = f"""
Good news! 
                
The item '{product.name}' you are tracking has dropped to KSh {formatted_current_price}.

Your target was KSh {formatted_target_price}, buy it now at: {product.jumia_url}.

Happy Shopping,
The DilTru Team 😀"""
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False, 
                )
                print("--- Email Sent Successfully ---")
            except Exception as e:
                print(f"--- Email Failed: {e} ---")
            # --------------------------------

        # D. Save Alert (Using update_or_create to handle re-tracking)
        alert, created = PriceAlert.objects.update_or_create(
            owner=user,
            product=product,
            defaults={
                'target_price': user_target_price,
                'status': initial_status
            }
        )
        
        print(f" -> Alert Saved. Status: {alert.status} | Target: {alert.target_price}")
        return alert

    def update(self, instance, validated_data):
        """
        Handle updates (e.g. User edits target price in Dashboard)
        """
        # 1. Update the Target Price
        new_target = validated_data.get('target_price', instance.target_price)
        instance.target_price = new_target

        # 2. Re-evaluate Status
        if instance.product.current_price <= new_target:
            instance.status = 'TRIGGERED'
        else:
            instance.status = 'ACTIVE'
            
        instance.save()
        return instance