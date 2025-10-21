# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from dj_rest_auth.registration.views import SocialLoginView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests

from .adapters import CustomGoogleOAuth2Adapter
from .serializer import RegisterSerializer, MyTokenObtainPairSerializer
from .models import User

# ----------------------------
# Helper: Revoke Google Token
# ----------------------------
def revoke_google_token(access_token):
    """
    Revoke a Google OAuth2 token.
    """
    url = f'https://oauth2.googleapis.com/revoke?token={access_token}'
    response = requests.post(url)
    return response.status_code == 200

# ----------------------------
# Registration API
# ----------------------------
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=True, role='customer')
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------
# JWT Login API
# ----------------------------
@method_decorator(csrf_exempt, name='dispatch')
class MyTokenObtainPairView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MyTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

# ----------------------------
# Profile API
# ----------------------------
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'phone': user.phone,
            'address': user.address,
        })

# ----------------------------
# Logout API
# ----------------------------
@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        google_token = request.data.get("google_token")  # optional

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=400)

        try:
            # Blacklist the JWT refresh token (requires simplejwt token blacklist)
            token = RefreshToken(refresh_token)
            token.blacklist()

            user = request.user

            # Deactivate normal users (non-Google)
            if not user.socialaccount_set.exists():
                user.is_active = False
                user.save()

            # Revoke Google token if provided
            if google_token:
                revoke_google_token(google_token)

            return Response({"message": "Logged out successfully"}, status=205)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# ----------------------------
# Google Login API
# ----------------------------
@method_decorator(csrf_exempt, name='dispatch')
class GoogleLogin(SocialLoginView):
    permission_classes = [AllowAny]
    adapter_class = CustomGoogleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        try:
            # Perform Google login
            response = super().post(request, *args, **kwargs)

            # Get the logged-in user
            user = request.user

            # Auto-assign role if not set
            if user and not user.role:
                user.role = "customer"
                user.save()

            # Generate backend JWT tokens for the user
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            return Response({
                "access": access,
                "refresh": str(refresh),
                "user": {
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "phone": user.phone,
                    "address": user.address,
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
