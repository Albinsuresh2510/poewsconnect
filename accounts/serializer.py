from rest_framework import serializers
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


# ---------------------------
# Registration Serializer
# ---------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'full_name', 'role', 'password', 'phone', 'address']

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            full_name=validated_data['full_name'],
            role=validated_data['role'],
            phone=validated_data.get('phone'),
            address=validated_data.get('address'),
            is_active=True  # ✅ user active by default
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


# ---------------------------
# Custom JWT Login Serializer
# ---------------------------
class MyTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "No account found with this email"})

        # ✅ Manual password check (bypass is_active check)
        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Invalid password"})

        # ✅ Reactivate user if inactive
        if not user.is_active:
            user.is_active = True
            user.save()

        # ✅ Generate JWT tokens manually
        refresh = RefreshToken.for_user(user)
        update_last_login(None, user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role,
            "full_name": user.full_name,
        }
