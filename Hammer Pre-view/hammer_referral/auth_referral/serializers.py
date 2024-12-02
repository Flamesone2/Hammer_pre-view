from rest_framework import serializers
from .models import User, UserInviteCode, InviteCode, UserManager
import re


# class RegistrationSerializer(serializers.Serializer):
#     phone = serializers.CharField(max_length=12)
#
#     @staticmethod
#     def validate_phone(value):
#         if not re.match(r"^\+79\d{9}$", value):
#             raise serializers.ValidationError(
#                 "Invalid phone number format. Expected format: +79XXXXXXXXX."
#             )
#         return value
#
#     def create(self, validated_data):
#         phone = validated_data["phone"]
#         user = User.objects.filter(phone=phone).first()
#
#         if user:
#             verification_code = User.objects.generate_verification_code(phone)
#             user.verification_code = verification_code
#             user.save()
#             return {"message": "Verification code sent."}
#
#         invite_code = InviteCode.objects.create(code=UserManager.generate_invite_code())
#         user = User.objects.create(phone=phone)
#         UserInviteCode.objects.create(
#             user=user, invite_code=invite_code, invite_code_type="own"
#         )
#         verification_code = User.objects.generate_verification_code(phone)
#         user.verification_code = verification_code
#         user.save()
#         return {
#             "message": "Verification code sent. Complete registration by verifying the code."
#         }
class RegistrationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=12)

    @staticmethod
    def validate_phone(value):
        if not re.match(r"^\+79\d{9}$", value):
            raise serializers.ValidationError(
                "Invalid phone number format. Expected format: +79XXXXXXXXX."
            )
        return value

    def create(self, validated_data):
        phone = validated_data["phone"]
        user = User.objects.filter(phone=phone).first()

        if user:
            verification_code = User.objects.generate_verification_code(phone)
            user.verification_code = verification_code
            user.save()
            return {"message": "Verification code sent."}

        # Генерация инвайт-кода через менеджер
        user = User.objects.create_user(phone=phone)

        verification_code = User.objects.generate_verification_code(phone)
        user.verification_code = verification_code
        user.save()

        return {
            "message": "Verification code sent. Complete registration by verifying the code."
        }


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=12)
    verification_code = serializers.CharField(max_length=4)


class VerifyCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.IntegerField()

    def validate(self, data):
        phone = data.get("phone")
        code = data.get("code")
        try:
            user = User.objects.get(phone=phone, verification_code=code)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid phone or code")
        return user



