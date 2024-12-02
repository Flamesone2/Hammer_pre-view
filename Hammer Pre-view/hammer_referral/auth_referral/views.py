from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    RegistrationSerializer,
)
from .models import User, UserInviteCode, UserManager, InviteCode


# class RegisterOrLoginAPIView(APIView):
#
#     @staticmethod
#     def post(request):
#         serializer = RegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             phone = serializer.validated_data["phone"]
#
#             # Проверка, существует ли пользователь
#             user = User.objects.filter(phone=phone).first()
#             if user:
#                 verification_code = User.objects.generate_verification_code(phone)
#                 user.verification_code = verification_code
#                 user.save()
#                 return Response(
#                     {"message": "Verification code sent for login."},
#                     status=status.HTTP_200_OK,
#                 )
#
#             # Пользователь не существует — регистрация
#             invite_code = InviteCode.objects.create(
#                 code=UserManager.generate_invite_code()
#             )
#             new_user = User.objects.create(phone=phone)
#             UserInviteCode.objects.create(
#                 user=new_user, invite_code=invite_code, invite_code_type="own"
#             )
#             verification_code = User.objects.generate_verification_code(phone)
#             new_user.verification_code = verification_code
#             new_user.save()
#
#             return Response(
#                 {
#                     "message": "Verification code sent for registration. Complete registration by verifying the code."
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterOrLoginAPIView(APIView):

    @staticmethod
    def post(request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]

            # Проверка, существует ли пользователь
            user = User.objects.filter(phone=phone).first()
            if user:
                verification_code = User.objects.generate_verification_code(phone)
                user.verification_code = verification_code
                user.save()
                return Response(
                    {"message": "Verification code sent for login."},
                    status=status.HTTP_200_OK,
                )

            # Пользователь не существует — регистрация через создание нового пользователя
            user = User.objects.create_user(phone=phone)
            verification_code = User.objects.generate_verification_code(phone)
            user.verification_code = verification_code
            user.save()

            return Response(
                {
                    "message": "Verification code sent for registration. Complete registration by verifying the code."
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







class VerifyCodeView(APIView):
    @staticmethod
    def post(request):
        phone = request.data.get("phone")
        code = request.data.get("code")  # Учитываем реальное имя поля из запроса

        # Проверяем, что телефон и код указаны
        if phone is None or code is None:
            return Response(
                {"detail": "Both phone and verification code are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Проверяем, совпадает ли код
        if user.verification_code != code:  # Сравниваем с правильным полем
            return Response(
                {"detail": "Invalid verification code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Если код корректен, обновляем флаг авторизации
        user.is_authorized = True
        user.verification_code = None  # Очищаем код после использования
        user.save()

        return Response(
            {
                "message": "Verification successful.",
                "is_authorized": user.is_authorized,
            },
            status=status.HTTP_200_OK,
        )
