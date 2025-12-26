from django.contrib import admin
from .models import Product, ProductTracker, PriceHistory, ScrapingLog

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # REMOVED 'owner' from list_display
    list_display = ('name', 'sku', 'current_price', 'last_updated', 'is_available')
    
    # This remains exactly the same as before - NO CHANGE NEEDED
    search_fields = ('name', 'sku') 

@admin.register(ProductTracker)
class ProductTrackerAdmin(admin.ModelAdmin):
    # This lets you see who is tracking what
    list_display = ('owner', 'product', 'target_price', 'created_at')
    
    # NEW: Allows you to search by Username OR Product Name in the Tracker list
    search_fields = ('owner__username', 'product__name', 'product__sku')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'timestamp')
    list_filter = ('timestamp',)

@admin.register(ScrapingLog)
class ScrapingLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')