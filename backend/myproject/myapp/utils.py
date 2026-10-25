import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailOTP

def generate_and_send_otp(user):
    
    otp = f"{secrets.randbelow(1_000_000):06d}" #genrate random 6 digit otp

    #expire older, unused OTPs for this user
    EmailOTP.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)

    #save the new otp with its expire time
    EmailOTP.objects.create(
        user=user,
        otp=otp,
        expires_at=timezone.now()+timedelta(
            minutes=settings.EMAIL_OTP_EXPIRY_MINUTES
        )
    )

    send_mail(
        subject="SpeQ Eyewear - Email Verification OTP",
        message=(
            f"your verification OTP is {otp}.\n"
            "it is valid for 5 minutes.\n"
            "Do not share this code with anyone"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
