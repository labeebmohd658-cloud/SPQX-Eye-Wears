from rest_framework import generics  #provide resubale APIview
from rest_framework.permissions import AllowAny #allows unathenticated users to access signup
from .serializers import (
    SignupSerializer,
    VerifyOTPSerializer,
    ResendOTPSerializer,
    LoginSerializer,
    ProfileSerializer,
    LogoutSerializer,
    )
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes=[AllowAny]

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                "message":"Email verified successfully",
                "email":user.email,
            },
            status=status.HTTP_200_OK,
        )
class ResendOTPView(generics.GenericAPIView):
    serializer_class=ResendOTPSerializer
    permission_classes=[AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            result,
            status=status.HTTP_200_OK
        )

class LoginView(generics.GenericAPIView):
    serializer_class=LoginSerializer
    permission_classes=[AllowAny]

    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            result,
            status=status.HTTP_200_OK
        )

class ProfileView(generics.RetrieveAPIView):
    serializer_class=ProfileSerializer
    permission_classes=[IsAuthenticated]

    def get_object(self):
        return self.request.user

class LogutView(generics.GenericAPIView):
    serializer_class=LogoutSerializer
    permission_classes=[IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"message":"Logout successful"},
            status=status.HTTP_200_OK
        )

    
