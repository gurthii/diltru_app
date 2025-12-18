from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    # We add 'owner_username' to display the username instead of just the owner's ID number, 
    # making the response more readable for the API user.
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        # 1. Model: Tell the serializer which model to use.
        model = Product

        # 2. Fields: List the fields you want the API to handle.
        fields = [
            'id', 
            'owner', 
            'owner_username', 
            'jumia_url', 
            'name', 
            'current_price', 
            'created_at', 
            'last_updated'
        ]

        # 3. Read Only Fields: Fields that the user cannot set during creation (POST) or update (PUT/PATCH).
        # The API should set these automatically.
        read_only_fields = [
            'owner', # The owner should be set by the logged-in user, not sent in the request body.
            'name', 
            'current_price', 
            'created_at', 
            'last_updated'
        ]

        def validate_jumia_url(self, value):
            """
            Check that the provided URL is a Jumia Kenya link.
            """
            if 'jumia.co.ke' not in value.lower():
                # Raise a ValidationError which DRF automatically translates into 
                # a 400 Bad Request response with a helpful error message.
                raise serializers.ValidationError(
                    "The URL must be a valid Jumia Kenya product link (jumia.co.ke)."
                )
            return value      