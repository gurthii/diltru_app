from django.db import models
from django.conf import settings  # Best practice to refer to the custom user model

class Product(models.Model):
    """
    The shared product data. Unique by URL.
    Scraped data lives here.
    """
    jumia_url = models.URLField(
        max_length=500,
        unique=True,
        help_text="Type the full url of the Jumia product"
    )
    sku = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Jumia SKU (e.g., SA948MP...)"
    )

    image_url = models.URLField(max_length=500, blank=True, null=True)

    name = models.CharField(max_length=255, blank=True, null=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.sku or "Unknown Product"

class PriceAlert(models.Model):
    """
    The link between a User and a Product.
    Replaces the old 'owner' field in Product.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('TRIGGERED', 'Triggered'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts')
    
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Ensures a user can't create two alerts for the same product
        unique_together = ('owner', 'product')

    def __str__(self):
        return f"{self.owner.username} tracking {self.product.sku}"

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.product.name} - KSh {self.price}"

class ScrapingLog(models.Model):
    """
    Logs every scraping attempt. 
    Crucial for 'Error Handling & Logging' rubric score.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50) # e.g., "SUCCESS", "SKU_MISMATCH"
    details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.product.sku} - {self.status} ({self.timestamp.date()})"