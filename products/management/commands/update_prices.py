from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail  # For emailing
from django.conf import settings
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

            # Record history only if price changed or it's been a while (optional optimization)
            # For Capstone, let's record every successful scrape for a nice graph
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
                self.trigger_notification(alert, new_price)

            # Be polite to Jumia server
            time.sleep(2) 

        self.stdout.write(self.style.SUCCESS('Successfully updated all prices.'))

    def trigger_notification(self, alert, new_price):
        """
        Sends an email and updates the alert status.
        """
        user = alert.owner
        product = alert.product
        
        subject = f"Price Drop Alert! {product.name}"
        message = (
            f"Hello {user.username},\n\n"
            f"Good news! The product you are tracking has dropped to KSh {new_price}.\n"
            f"Your target was KSh {alert.target_price}.\n\n"
            f"Buy it now: {product.jumia_url}\n\n"
            f"Happy Shopping,\nThe dilTru Team"
        )
        
        # 1. Send the Email (Console Backend for now)
        try:
            # We wrap this in try/except so email failures don't crash the scraper
            print(f"\n[EMAIL SIMULATION] To: {user.email} | Subject: {subject}\n")
            
            # Uncomment this when you configure SMTP settings in settings.py
            # send_mail(
            #     subject,
            #     message,
            #     settings.DEFAULT_FROM_EMAIL,
            #     [user.email],
            #     fail_silently=False,
            # )
            
            # 2. Update Alert State
            # We set it to TRIGGERED so we don't spam the user every hour
            alert.status = 'TRIGGERED'
            alert.notified_at = timezone.now()
            alert.save()
            
            print(f" -> Alert triggered for {user.username}")

        except Exception as e:
            print(f"Error sending email to {user.email}: {e}")