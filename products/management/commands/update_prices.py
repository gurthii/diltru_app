from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Product, PriceHistory, PriceAlert, ScrapingLog
from products.services import get_site_product
import time

class Command(BaseCommand):
    help = 'Scrapes all products and triggers alerts if prices drop.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting price update job...")
        
        # Only check active products to save resources
        products = Product.objects.filter(is_available=True)
        
        for product in products:
            self.stdout.write(f"Checking {product.sku}...")
            
            # 1. Scrape the fresh data
            data = get_site_product(product.jumia_url)
            
            if not data:
                # Log failure
                ScrapingLog.objects.create(
                    product=product,
                    status="FAILED",
                    details="Network error or blocked request."
                )
                continue # Skip to next product

            # 2. Update Product & History
            old_price = product.current_price
            new_price = data['price']
            
            product.current_price = new_price
            product.last_updated = timezone.now()
            product.save()

            # Record history
            PriceHistory.objects.create(product=product, price=new_price)
            
            ScrapingLog.objects.create(
                product=product, 
                status="SUCCESS", 
                details=f"Price updated from {old_price} to {new_price}"
            )

            # 3. CHECK ALERTS (The "Brain")
            # Find all ACTIVE alerts for this product where the target is met
            triggered_alerts = PriceAlert.objects.filter(
                product=product,
                status='ACTIVE',
                target_price__gte=new_price # Trigger if target >= current
            )

            for alert in triggered_alerts:
                self.stdout.write(f" -> Alert triggered for {alert.owner.username}")
                
                # REUSE THE LOGIC FROM MODELS.PY
                # This uses the threading AND the existing email template defined in the model
                alert.send_email_notification() 

                # Update status to avoid spamming (until user resets it)
                alert.status = 'TRIGGERED'
                alert.notified_at = timezone.now()
                alert.save(update_fields=['status', 'notified_at'])

            # Be polite to Jumia server
            time.sleep(2) 

        self.stdout.write(self.style.SUCCESS('Successfully updated all prices.'))