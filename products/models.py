from django.db import models
from django.contrib.auth.models import User # to link user to product

class Product(models.Model):
    # Relationship
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # if user is deleted, tracked products will also be deleted thanks to 'on_delete'

    # Product identification
    jumia_url = models.URLField(
        max_length=500,
        unique=True, # dupes won't be tracked
        help_text="Type the full url of the Jumia product e.g.,'https://www.jumia.co.ke/samsung-22-essential-monitor-s3-s30gd-full-hd-monitor-ls22d300gamxue-1yr-wrty-313823901.html'"
    )

    # Product Availability
    is_available = models.BooleanField(default=True)
    
    # Product SKU
    sku = models.CharField(max_length=100, blank=True, null=True)

    # Product data
    name = models.CharField(
        max_length=255,
        blank=True, # iniitially blank as it will be obtained via scrapping
        null=True
    )

    # Price data
    current_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Timestamps for actions
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        product_name = self.name or 'Unknown Product Name'
        product_sku = self.sku or 'No SKU'
        return f"{product_name} - {product_sku} ({self.owner.username})"    

class PriceHistory(models.Model):
    # Relationship: Many PriceHistory entries belong to one Product
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='history'
    )
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    # We order them so the newest price is always first
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.product.name} - KSh {self.price} on {self.timestamp.strftime('%Y-%m-%d')}"

class ScrapingLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)  # e.g., "SKU_MISMATCH", "REDIRECT", "TIMEOUT"
    details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.product.name} - {self.status} ({self.timestamp.date()})"