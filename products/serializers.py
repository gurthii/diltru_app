from rest_framework import serializers
from .models import Product, PriceHistory

class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['price', 'timestamp']

class ProductSerializer(serializers.ModelSerializer):
    # We add 'owner_username' to display the username instead of just the owner's ID number, 
    # making the response more readable for the API user.
    owner_username = serializers.ReadOnlyField(source='owner.username')
    
    history = PriceHistorySerializer(many=True, read_only=True)
    # since one product has many history entries, we specify many=True
    # to prevent creation/update of history we limit it to read_only=True

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
            'sku',
            'current_price', 
            'created_at', 
            'last_updated',
            'history'
        ]

        # 3. Read Only Fields: Fields that the user cannot set during creation (POST) or update (PUT/PATCH).
        # The API should set these automatically.
        read_only_fields = [
            'owner', # The owner should be set by the logged-in user, not sent in the request body.
            'name', 
            'sku',
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
        

