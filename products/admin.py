from django.contrib import admin
from .models import Product, PriceAlert, PriceHistory, ScrapingLog

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'current_price', 'last_updated', 'is_available')
    search_fields = ('name', 'sku', 'jumia_url')

@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ('owner', 'product', 'target_price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('owner__username', 'product__name')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'timestamp')
    list_filter = ('timestamp',)

@admin.register(ScrapingLog)
class ScrapingLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')