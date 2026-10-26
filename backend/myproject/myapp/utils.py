
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailOTP


def generate_and_send_otp(user, purpose="email_verification"):
    otp = f"{secrets.randbelow(1_000_000):06d}"

    EmailOTP.objects.filter(
        user=user,
        purpose=purpose,
        is_used=False,
    ).update(is_used=True)

    EmailOTP.objects.create(
        user=user,
        otp=otp,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(
            minutes=settings.EMAIL_OTP_EXPIRY_MINUTES
        ),
    )

    send_mail(
        subject="SpeQ Eyewear - Verification OTP",
        message=(
            f"Your OTP is {otp}.\n"
            f"It is valid for {settings.EMAIL_OTP_EXPIRY_MINUTES} minutes.\n"
            "Do not share this code with anyone."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
