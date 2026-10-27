
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    BasePermission,
)

from .serializers import (
    AdminLoginSerializer,
    AdminUserListSerializer,
)

User = get_user_model()


class IsAdminUserPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class AdminLoginView(generics.GenericAPIView):
    serializer_class = AdminLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(result, status=200)


class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [
        IsAuthenticated,
        IsAdminUserPermission,
    ]

    def get_queryset(self):
        return User.objects.all().order_by("-date_joined")
