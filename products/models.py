from django.db import models
from django.contrib.auth.models import User # to link user to product

class Product(models.Model):
    # Relationship
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # if user is deleted, tracked products will also be deleted thanks to 'on_delete'

    # Product identification
    jumia_url = models.URLField(
        max_length=500,
        unique=True, # dupes won't be tracked
        help_text="Type the full url of the Jumia product e.g.,'https://www.jumia.co.ke/samsung-22-essential-monitor-s3-s30gd-full-hd-monitor-ls22d300gamxue-1yr-wrty-313823901.html'"
    )

    # Product data
    name = models.CharField(
        max_length=255,
        blank=True, # iniitially blank as it will be obtained via scrapping
        null=True
    )

    # Price data
    current_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Timestamps for actions
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name or 'Unknown Product Name'} ({self.owner.username})"
    

