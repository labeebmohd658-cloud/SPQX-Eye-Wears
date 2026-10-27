
from django.urls import path

from .users.views import (
    SignupView,
    VerifyOTPView,
    ResendOTPView,
    LoginView,
    ProfileView,
    LogoutView,
    ForgotPasswordView,
    ResetPasswordView,
)

from .admin_panel.views import (
    AdminLoginView,
    AdminUserListView,
)


urlpatterns = [
    path("signup/",SignupView.as_view(),name="signup"),
    path("verify-otp/",VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/",ResendOTPView.as_view(), name="resend-otp"),
    path("login/",LoginView.as_view(), name="login"),
    path("profile/",ProfileView.as_view(), name="profile"),
    path("logout/",LogoutView.as_view(),name="logout"),
    path("forgot-password/",ForgotPasswordView.as_view(),name="forgot-password"),
    path("reset-password/",ResetPasswordView.as_view(),name="reset-passwrod"),
    path("admin-login/",AdminLoginView.as_view(),name="admin-login"),
    path("admin/users/",AdminUserListView.as_view(), name="admin-user-list"),

]

