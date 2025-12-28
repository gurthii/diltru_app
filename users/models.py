from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # We inherit from AbstractUser, so we already get:
    # username, password, email, first_name, last_name, is_active, is_staff
    email = models.EmailField(unique=True, blank=False, null=False) # ensuring this is required at register

    # We add your specific requirement:
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Optional. Used for SMS alerts."
    )

    
    def __str__(self):
        return self.username