from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import User
from .serializers import UserSerializer

class RegisterUserView(generics.CreateAPIView):
    """
    API view to register a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class LogoutView(APIView):
    """
    API view to log out the user (client-side token deletion).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # In a stateless JWT system, 'logout' is handled by the client discarding the token.
        # This endpoint can be used for blacklisting tokens if needed in the future.
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
