from django.urls import path
from .views import (
    SignupView,
    VerifyOTPView,
    ResendOTPView,
    LoginView,
    ProfileView,
    LogutView
    )

urlpatterns = [
    path("signup/",SignupView.as_view(),name="signup"),
    path("verify-otp/",VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/",ResendOTPView.as_view(), name="resend-otp"),
    path("login/",LoginView.as_view(), name="login"),
    path("profile/",ProfileView.as_view(), name="profile"),
    path("logout/",LogutView.as_view(),name="logout")

]

