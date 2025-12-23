from django.core.management.base import BaseCommand
from products.models import Product, PriceHistory, ScrapingLog
from products.services import get_site_product
import time

class Command(BaseCommand):
    help = 'Scrapes Jumia for updated prices and records history if changed'
    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        self.stdout.write(f"Starting update for {products.count()} products...")

        for product in products:
            try:
                self.stdout.write(f"Checking: {product.name}...")
                data = get_site_product(product.jumia_url)

                # 1. Check if we actually got data AND the SKU matches
                # This handles the redirect case
                if data and data.get('sku') == product.sku:
                    new_price = data['price']
                    
                    if not product.is_available:
                        product.is_available = True
                        self.stdout.write(self.style.SUCCESS("  Product is back online!"))

                    if new_price != product.current_price:
                        self.stdout.write(self.style.SUCCESS(f"  Price change: {product.current_price} -> {new_price}"))
                        product.current_price = new_price
                        PriceHistory.objects.create(product=product, price=new_price)
                    
                    product.save()

                else:
                    # Logging the fails
                    status_type = "REDIRECT_OR_NOT_FOUND" if not data else "SKU_MISMATCH"
                    ScrapingLog.objects.create(
                        product=product,
                        status=status_type,
                        details=f"Scraped SKU: {data.get('sku') if data else 'None'}"
                    )

                    # 2. Handle redirects or unlisted products
                    if product.is_available:
                        product.is_available = False # updates is available value
                        product.save()

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                # More logging
                ScrapingLog.objects.create(
                    product=product,
                    status="CRASH",
                    details=str(e)
                )
                continue 

        self.stdout.write(self.style.SUCCESS("Price update complete!"))