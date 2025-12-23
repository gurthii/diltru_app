from django.contrib import admin
from .models import Product, PriceHistory, ScrapingLog

# visualizing the Product and PriceHistory tables 
# you can also delete entries in the table using Django Admin UI
@admin.register(Product)  # admin.site.register(Product) # registered to allow use in admin interface
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'current_price', 'owner', 'last_updated')
    search_fields = ('name', 'sku')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'timestamp')
    list_filter = ('timestamp',)

@admin.register(ScrapingLog)
class ScrapingLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')