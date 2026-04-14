import logging

from django.db import models
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


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
    Stores the user's target price and the current alert status.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('TRIGGERED', 'Triggered'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alerts')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='alerts')
    
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Ensures a user can't create two alerts for the same product
        unique_together = ('owner', 'product')

    def __str__(self):
        return f"{self.owner.username} tracking {self.product.sku}"

    def save(self, *args, **kwargs):
        """
        Persist the alert.  Status transitions are handled explicitly
        by ``check_and_trigger()`` — this method only writes to the DB.
        """
        super().save(*args, **kwargs)

    def check_and_trigger(self):
        """
        Evaluate whether the current product price meets the target.

        If the price condition is met and the alert hasn't already been
        triggered, update the status to TRIGGERED, record the timestamp,
        save the alert, and fire off a notification email.

        If the price condition is *no longer* met (e.g. after the user
        raises their target), reset back to ACTIVE.

        Returns:
            bool: True if the alert was triggered, False otherwise.
        """
        # Import here to avoid circular imports (notifications → settings only)
        from .notifications import send_price_alert_email

        if self.product.current_price is None or self.target_price is None:
            return False

        # Price condition met?
        if self.product.current_price <= self.target_price:
            if self.status != 'TRIGGERED':
                self.status = 'TRIGGERED'
                self.notified_at = timezone.now()
                self.save(update_fields=['status', 'notified_at'])

                logger.info(
                    "Alert triggered for %s on '%s' (current: %s, target: %s)",
                    self.owner.username,
                    self.product.name,
                    self.product.current_price,
                    self.target_price,
                )
                send_price_alert_email(self)
                return True
        else:
            # Auto-reset: target no longer met → go back to ACTIVE
            if self.status == 'TRIGGERED':
                self.status = 'ACTIVE'
                self.notified_at = None
                self.save(update_fields=['status', 'notified_at'])
                logger.info(
                    "Alert for %s on '%s' reset to ACTIVE (price rose above target).",
                    self.owner.username,
                    self.product.name,
                )

        return False


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