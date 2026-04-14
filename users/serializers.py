from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Write-only means we accept it for creation, but never send it back in the response
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'password']
        
    def create(self, validated_data):
        # We use create_user() instead of create() because it handles password hashing automatically
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'], # no get, as it is now mandatory
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password']
        )
        return user
    
class UserSerializer(serializers.ModelSerializer):
    """
    Used to view user profile details.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Used by admin-only endpoints to list / manage user accounts.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_active']