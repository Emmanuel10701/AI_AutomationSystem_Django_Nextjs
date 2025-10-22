from typing import Dict, Any, cast
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .models import User
from .serializer import UserSerializer, RegisterSerializer, LoginSerializer


# ------------------------------
# Register API
# ------------------------------
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User registered successfully"
        }, status=status.HTTP_201_CREATED)


# ------------------------------
# Login API
# ------------------------------
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: Dict[str, Any] = cast(Dict[str, Any], serializer.validated_data)
        user = cast(User, validated_data.get("user"))

        if not isinstance(user, User):
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        # Log in the user using Django session
        login(request, user)

        return Response({
            "user": UserSerializer(user).data,
            "message": "Login successful"
        }, status=status.HTTP_200_OK)


# ------------------------------
# User Profile API
# ------------------------------
class UserProfileAPI(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ------------------------------
# Logout API
# ------------------------------
class LogoutAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
