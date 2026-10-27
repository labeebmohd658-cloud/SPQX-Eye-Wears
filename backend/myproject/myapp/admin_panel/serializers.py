
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data["email"]
        password = data["password"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid email or password"
            )

        from django.contrib.auth import authenticate

        user = authenticate(
            username=user.username,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid email or password"
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive"
            )

        if not user.is_staff:
            raise serializers.ValidationError(
                "You do not have admin access"
            )

        data["user"] = user
        return data

    def create(self, validated_data):
        from rest_framework_simplejwt.tokens import RefreshToken

        user = validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return {
            "message": "Admin login successful.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "is_active",
            "is_email_verified",
            "date_joined",
            "blocked_at",
        ]
