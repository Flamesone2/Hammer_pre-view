from auth_referral.models import UserInviteCode, User
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    personal_invite_code = serializers.SerializerMethodField()
    used_invite_code = serializers.SerializerMethodField()
    invited_users = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["phone", "personal_invite_code", "used_invite_code", "invited_users"]

    @staticmethod
    def get_personal_invite_code(obj):
        return (
            UserInviteCode.objects.filter(user=obj, invite_code_type="own")
            .first()
            .invite_code.code
        )

    @staticmethod
    def get_used_invite_code(obj):
        used_code = UserInviteCode.objects.filter(
            user=obj, invite_code_type="another"
        ).first()
        return used_code.invite_code.code if used_code else None

    @staticmethod
    def get_invited_users(obj):
        invite_code = (
            UserInviteCode.objects.filter(user=obj, invite_code_type="own")
            .first()
            .invite_code
        )
        invited = UserInviteCode.objects.filter(
            invite_code=invite_code, invite_code_type="another"
        )
        return [u.user.phone for u in invited]
