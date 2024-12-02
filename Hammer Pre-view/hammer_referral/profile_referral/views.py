from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from auth_referral.models import User, UserInviteCode, InviteCode


class ProfileView(APIView):

    @staticmethod
    def get(request):
        phone = request.query_params.get("phone")

        if not phone:
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not user.is_authorized:
            return Response(
                {"error": "User is not authorized."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Если пользователь авторизован, формируем ответ
        personal_invite_code = UserInviteCode.objects.filter(
            user=user, invite_code_type="own"
        ).first()
        used_invite_code = UserInviteCode.objects.filter(
            user=user, invite_code_type="another"
        ).first()

        response_data = {
            "phone": user.phone,
            "personal_invite_code": (
                personal_invite_code.invite_code.code if personal_invite_code else None
            ),
            "used_invite_code": (
                used_invite_code.invite_code.code if used_invite_code else None
            ),
            "invited_users": [u.phone for u in user.invited_users.all()]
,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        # Получаем номер телефона из query-параметра
        phone = request.query_params.get("phone")
        if not phone:
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(phone=phone, is_authorized=True)
        except User.DoesNotExist:
            return Response(
                {"error": "User not authorized or not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Получаем инвайт-код из тела запроса
        invite_code = request.data.get("invite_code")
        if not invite_code:
            return Response(
                {"error": "Invite code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Проверяем, не активировал ли пользователь уже чужой инвайт-код
            existing_relationship = UserInviteCode.objects.filter(
                user=user, invite_code_type="another"
            )
            if existing_relationship.exists():
                return Response(
                    {"error": "Invite code already used. Cannot activate another."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Получаем инвайт-код из базы данных
            invite = InviteCode.objects.get(code=invite_code)

            # Проверяем, не пытается ли пользователь активировать свой собственный код
            if invite.code == user.invite_code.code:
                return Response(
                    {"error": "Cannot activate your own invite code."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Создаем связь с типом "another" (то есть, активация чужого кода)
            UserInviteCode.objects.create(
                user=user, invite_code=invite, invite_code_type="another"
            )

            return Response({"message": "Invite code activated successfully."})

        except InviteCode.DoesNotExist:
            return Response(
                {"error": "Invite code does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
