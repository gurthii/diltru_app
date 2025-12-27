from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .serializers import UserRegistrationSerializer, UserSerializer
from django.contrib.auth import get_user_model

class RegisterView(generics.CreateAPIView):
    """
    Endpoint: POST /api/auth/register/
    Permits any user to create an account.
    """
    queryset = get_user_model().objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    # Add this method to fix the 405 error in the browser
    def get(self, request, *args, **kwargs):
        """
        Allows us to view the API form in the browser.
        """
        return Response(status=status.HTTP_200_OK)

class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Return Token AND Username
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email
        })
    
class ManageUserView(generics.RetrieveAPIView):
    """
    Endpoint: GET /api/users/me/
    Purpose: Retrieves the profile details of the currently logged-in user.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # Only logged-in users

    def get_object(self):
        # Returns the user making the request, not a user found by ID in the URL
        return self.request.user