from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer
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