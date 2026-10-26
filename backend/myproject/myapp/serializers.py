from django.contrib.auth import get_user_model
from rest_framework import serializers
from .utils import generate_and_send_otp
from django.utils import timezone  # Used to get the current time
from .models import EmailOTP
from .utils import generate_and_send_otp
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

# Gets the active User model configured in Django
User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    # Password is accepted as input but never returned in API responses.
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

   
    confirm_password = serializers.CharField(
        write_only=True
    )

    class Meta:

        model = User

        fields = [
            "full_name",
            "email",
            "password",
            "confirm_password",
        ]

    # Custom validation that checks whether the email already exists.
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    # Here, it checks the password and confirmation match.
    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return data

    # Creates a new user after the input passes validation.
    def create(self, validated_data):

        validated_data.pop("confirm_password")

        # Extracts the raw password before creating the user.
        password = validated_data.pop("password")

        # Uses the email as the username and supplies the remaining fields.
        user = User(
            username=validated_data["email"],
            **validated_data
        )

        # Hashes the password instead of storing it as plain text.
        user.set_password(password)

        # Keeps the account inactive until email verification is completed.
        user.is_active = False
        user.is_email_verified = False

        user.save()

        # Generates an OTP and sends it to the user's email.
        generate_and_send_otp(user)

        return user


class VerifyOTPSerializer(serializers.Serializer):
    # Accepts the email address of the account being verified.
    email = serializers.EmailField()

    otp = serializers.CharField(min_length=6, max_length=6)

    # Validates the email and OTP before allowing verification.
    def validate(self, data):
        email = data["email"]
        otp = data["otp"]

        # Finds the user by email, ignoring letter-case differences.
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": "No account found with this email."
            })

        # Prevents an already verified account from being verified again.
        if user.is_email_verified:
            raise serializers.ValidationError({
                "email": "This email is already verified."
            })

        # Finds the latest matching OTP that is unused and not expired.
        try:
            otp_record = user.email_otps.filter(
                otp=otp,
                is_used=False,
                expires_at__gt=timezone.now()
            ).latest("created_at")

        except EmailOTP.DoesNotExist:
            # Returns an error if no valid matching OTP is found.
            raise serializers.ValidationError({
                "otp": "Invalid or expired OTP."
            })

        # Adds the validated user and OTP record to the validated data.
        data["user"] = user
        data["otp_record"] = otp_record

        return data

    # Performs the actual email verification after validation succeeds.
    def save(self, **kwargs):
        user = self.validated_data["user"]
        otp_record = self.validated_data["otp_record"]

        # Marks the OTP as used so it cannot be reused.
        otp_record.is_used = True
        otp_record.save(update_fields=["is_used"])

        # Verifies the email and activates the user's account.
        user.is_email_verified = True
        user.is_active = True

        # Updates only the specified fields in the database.
        user.save(update_fields=["is_email_verified", "is_active"])

        # Returns the verified user instance.
        return user


class ResendOTPSerializer(serializers.Serializer):
    # Accepts the user's email address.
    email = serializers.EmailField()

    # Checks whether the email belongs to an existing user.
    def validate_email(self, value):
        try:
            # Finds the user by email, ignoring uppercase/lowercase differences.
            user = User.objects.get(email__iexact=value)

        except User.DoesNotExist:
            # Returns an error if no account exists.
            raise serializers.ValidationError(
                "No account found with this email."
            )

        # Prevents verified users from requesting another OTP.
        if user.is_email_verified:
            raise serializers.ValidationError(
                "This email is already verified."
            )

        # Stores the user instance for use in the create method.
        self.user = user

        # Returns the validated email address.
        return value

    # Generates and sends a new OTP after validation succeeds.
    def create(self, validated_data):
        user = self.user

        # Invalidates previous unused OTPs and sends a new OTP.
        generate_and_send_otp(user)

        # Returns a success message.
        return {
            "message": "A new OTP has been sent to your email."
        }


class ForgotPasswordSerializer(serializers.Serializer):
    # Accepts the email address for password recovery.
    email = serializers.EmailField()

    # Checks whether the email belongs to an existing user.
    def validate_email(self, value):
        try:
            # Finds the user, ignoring uppercase/lowercase differences.
            user = User.objects.get(email__iexact=value)

        except User.DoesNotExist:
            # Rejects emails that do not belong to an account.
            raise serializers.ValidationError(
                "No account found with this email."
            )

        # Prevents inactive accounts from requesting a reset OTP.
        if not user.is_active:
            raise serializers.ValidationError(
                "No account found with this email."
            )

        # Stores the user for use in the create method.
        self.user = user

        # Returns the validated email.
        return value

    # Generates and sends an OTP for password recovery.
    def create(self, validated_data):
        generate_and_send_otp(
            user=self.user,
            purpose="password_reset"
        )

        # Returns a success message.
        return {
            "message": "Password reset OTP sent successfully."
        }


class ResetPasswordSerializer(serializers.Serializer):
    # Accepts the email address of the account.
    email = serializers.EmailField()

    # Accepts the six-digit password-reset OTP.
    otp = serializers.CharField(min_length=6, max_length=6)

    # Accepts the new password without returning it in API responses.
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    # Accepts the new password again for confirmation.
    confirm_password = serializers.CharField(
        write_only=True,
    )

    # Validates the passwords, user account, and reset OTP.
    def validate(self, data):

        # Checks whether both passwords match.
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        # Finds the user using a case-insensitive email lookup.
        try:
            user = User.objects.get(
                email__iexact=data["email"]
            )
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": "No account found with this email."
            })

        # Finds the latest unused, unexpired password-reset OTP.
        try:
            otp_record = user.email_otps.filter(
                otp=data["otp"],
                purpose="password_reset",
                is_used=False,
                expires_at__gt=timezone.now(),
            ).latest("created_at")

        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError({
                "otp": "Invalid or expired password reset OTP."
            })

        # Stores the validated user and OTP for the create method.
        data["user"] = user
        data["otp_record"] = otp_record

        return data

    # Changes the password after all validations succeed.
    def create(self, validated_data):
        user = validated_data["user"]
        otp_record = validated_data["otp_record"]

        # Hashes the new password before saving it.
        user.set_password(validated_data["new_password"])
        user.save(update_fields=["password"])

        # Marks the OTP as used to prevent reuse.
        otp_record.is_used = True
        otp_record.save(update_fields=["is_used"])

        # Returns a success message.
        return {
            "message": "Password reset successfully."
        }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self,data):
        email = data["email"]
        password = data ["password"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "invalid email or password"
            )
        user = authenticate(
            username=user.username,
            password=password,

        )

        if user is None:
            raise serializers.ValidationError(
                "invalid email or password"
            )
        if not user.is_email_verified:
            raise serializers.ValidationError(
                "please verify youe email before loggin in"
            )
        data["user"]=user
        return data
    def create(self,validate_data):
        user = self.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return{
            "message":"Login successful",
            "access":str(refresh.access_token),
            "refresh":str(refresh),
        }

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only= True)

    def validate(self,data):
        email = data["email"]
        password = data["password"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "invalid email or password"
            )
        user = authenticate(
            username=user.username,
            password=password

        )

        if user is None:
            raise serializers.ValidationError(
                "invalid email or password"
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive"
            )
        if not user.is_staff:
            raise serializers.ValidationError(
                "You do not have admin access"
            )
        data ["user"]= user
        return data

    def create(self, validated_data):
        user = validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return {
            "message":"admin login successful",
            "access":str(refresh.access_token),
            "refresh":str(refresh),
        }



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "profile_picture",
            "is_email_verified",
        ]
        read_only_fields = fields

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self,data):
        try:
            token = RefreshToken(data["refresh"])
            token.blacklist()
        except Exception:
            raise serializers.ValidationError(
                {"refresh":"Invalid or expired refresh token"}
            )
        return data

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
            "blocked_at"
        ]


    

    
