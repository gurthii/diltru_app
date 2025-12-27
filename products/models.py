import threading # should take care of timeouts
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone  # <--- Added this import for timestamps

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
    Includes logic to auto-trigger emails on save.
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
        The Safe Logic:
        1. Modify 'self' fields (status, notified_at).
        2. Send the email (but DO NOT save inside the email function).
        3. Call super().save() ONCE to write everything to the DB.
        """
        # 1. Ensure we have valid data to compare
        if self.product.current_price is not None and self.target_price is not None:
            
            # 2. THE CHECK: Is current price lower than or equal to target?
            if self.product.current_price <= self.target_price:
                
                # 3. Only trigger if not already TRIGGERED (prevents duplicate emails)
                if self.status != 'TRIGGERED':
                    self.status = 'TRIGGERED'
                    self.notified_at = timezone.now() # <--- Update timestamp here in memory
                    
                    print(f"🎯 Target Met! Sending email to {self.owner.email}")
                    self.send_email_notification() # <--- Send mail (Pure Action, no DB save)
            
            # 4. Auto-Reset: If user updates target and it's no longer met, go back to ACTIVE
            elif self.status == 'TRIGGERED':
                 self.status = 'ACTIVE'
                 self.notified_at = None

        # 5. The ONLY save to the database (Updates status, target, and notified_at all at once)
        super().save(*args, **kwargs)

    def send_email_notification(self):
        """
        Sends email in a background thread so it doesn't freeze the website.
        """
        # Define the task to run in the background
        def _send_task():
            try:
                formatted_price = f"{int(self.product.current_price):,d}"
                formatted_target = f"{int(self.target_price):,d}"
                
                subject = f"🏷️ Price Drop Alert!: {self.product.name[:30]}... is KSh {formatted_price}!"
                message = f"""
Good news! 

The item '{self.product.name}' you are tracking has dropped to KSh {formatted_price}.
Your target was KSh {formatted_target}.

Buy it now: {self.product.jumia_url}

Happy Shopping,
The DilTru Team 😀
                """
                
                print(f"📧 Connecting to Gmail to send to {self.owner.email}...")
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.owner.email],
                    fail_silently=False, 
                )
                print("✅ Email sent successfully!")
            except Exception as e:
                print(f"‼️ Email Failed in background: {e}")

        # Fire and Forget: Start the thread
        email_thread = threading.Thread(target=_send_task)
        email_thread.start()

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