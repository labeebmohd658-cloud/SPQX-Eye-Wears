from django.urls import path
from .views import (
    SignupView,
    VerifyOTPView,
    ResendOTPView,
    LoginView,
    ProfileView,
    LogutView,
    ForgetPasswordView,
    ResetPasswordView,
    AdminLoginView,
    AdminUserListView,
    )

urlpatterns = [
    path("signup/",SignupView.as_view(),name="signup"),
    path("verify-otp/",VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/",ResendOTPView.as_view(), name="resend-otp"),
    path("login/",LoginView.as_view(), name="login"),
    path("profile/",ProfileView.as_view(), name="profile"),
    path("logout/",LogutView.as_view(),name="logout"),
    path("forgot-password/",ForgetPasswordView.as_view(),name="forgot-password"),
    path("reset-password/",ResetPasswordView.as_view(),name="reset-passwrod"),
    path("admin-login/",AdminLoginView.as_view(),name="admin-login"),
    path("admin/users/",AdminUserListView.as_view(), name="admin-user-list"),

]

