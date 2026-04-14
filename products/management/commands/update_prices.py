"""
Management command to scrape fresh prices for all active products
and trigger alerts whose target price has been met.

Usage:
    python manage.py update_prices
"""
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from products.models import Product, PriceHistory, PriceAlert, ScrapingLog
from products.services import get_site_product


class Command(BaseCommand):
    help = 'Scrapes all active products and triggers alerts if prices drop.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting price update job…")

        products = Product.objects.filter(is_available=True)

        for product in products:
            self.stdout.write(f"  Checking {product.sku} …")

            # 1. Scrape fresh data
            data = get_site_product(product.jumia_url)

            if not data:
                ScrapingLog.objects.create(
                    product=product,
                    status="FAILED",
                    details="Network error or blocked request.",
                )
                self.stderr.write(self.style.WARNING(
                    f"  ✗ Scrape failed for {product.sku}"
                ))
                continue

            # 2. Update product price and record history
            old_price = product.current_price
            new_price = data['price']

            product.current_price = new_price
            product.last_updated = timezone.now()
            product.save()

            PriceHistory.objects.create(product=product, price=new_price)

            ScrapingLog.objects.create(
                product=product,
                status="SUCCESS",
                details=f"Price updated from {old_price} to {new_price}",
            )

            # 3. Evaluate all ACTIVE alerts for this product
            active_alerts = PriceAlert.objects.filter(
                product=product,
                status='ACTIVE',
            )
            for alert in active_alerts:
                triggered = alert.check_and_trigger()
                if triggered:
                    self.stdout.write(self.style.SUCCESS(
                        f"  → Alert triggered for {alert.owner.username}"
                    ))

            # Be polite to Jumia's servers
            time.sleep(2)

        self.stdout.write(self.style.SUCCESS('Successfully updated all prices.'))