import logging
import re

from rest_framework import serializers

from .models import Product, PriceAlert, PriceHistory
from .services import get_site_product

logger = logging.getLogger(__name__)


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
        """
        Create (or update) a PriceAlert for the authenticated user.

        Workflow:
            1. Extract the Jumia URL and look up / scrape the product.
            2. Create the Product record if it doesn't exist yet.
            3. Create or update the alert via ``update_or_create``.
            4. Run ``check_and_trigger()`` to evaluate the price condition
               and send an email if the target is already met.
        """
        jumia_url = validated_data.pop('jumia_url')
        user_target_price = validated_data['target_price']
        user = self.context['request'].user

        logger.debug("Processing alert for user=%s, url=%s", user.username, jumia_url)

        # --- Get or scrape the product ---
        product = Product.objects.filter(jumia_url=jumia_url).first()

        if not product:
            logger.info("Product not in DB — scraping Jumia for %s", jumia_url)
            product_data = get_site_product(jumia_url)

            if not product_data:
                raise serializers.ValidationError(
                    {"jumia_url": "Failed to scrape product. Check the link."}
                )

            # SKU fallback: try to extract from the URL slug
            sku_value = product_data.get('sku')
            if not sku_value:
                match = re.search(r'-([a-zA-Z0-9]+)\.html', jumia_url)
                sku_value = match.group(1) if match else "UNKNOWN-SKU"

            product = Product.objects.create(
                jumia_url=jumia_url,
                name=product_data['name'],
                current_price=product_data['price'],
                is_available=product_data.get('is_available', True),
                sku=sku_value,
                image_url=product_data.get('image_url'),
            )

            # Record initial price history point
            PriceHistory.objects.create(product=product, price=product_data['price'])

        # --- Create or update the alert ---
        alert, created = PriceAlert.objects.update_or_create(
            owner=user,
            product=product,
            defaults={
                'target_price': user_target_price,
                'status': 'ACTIVE',
            },
        )

        # Evaluate whether the price condition is already met
        alert.check_and_trigger()

        logger.debug("Alert saved (created=%s). Final status: %s", created, alert.status)
        return alert

    def update(self, instance, validated_data):
        """
        Handle updates (e.g. user edits target price in Dashboard).
        """
        instance.target_price = validated_data.get('target_price', instance.target_price)
        instance.save()

        # Re-evaluate the price condition after target change
        instance.check_and_trigger()
        return instance