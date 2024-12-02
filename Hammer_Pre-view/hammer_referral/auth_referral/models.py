from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import random


class InviteCode(models.Model):
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return self.code


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")

        # Генерация и сохранение инвайт-кода
        invite_code = InviteCode.objects.create(code=self.generate_invite_code())

        user = self.model(phone=phone, invite_code=invite_code, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        UserInviteCode.objects.create(
            user=user, invite_code=invite_code, invite_code_type="own"
        )

        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone, password, **extra_fields)

    def activate_invite_code(self, user, invite_code):
        if not self.can_activate_invite_code(user):
            raise ValueError("User has already activated another invite code.")

        try:
            invite = InviteCode.objects.get(code=invite_code)
        except InviteCode.DoesNotExist:
            raise ValueError("Invite code does not exist.")

        # Создаем запись в UserInviteCode для активации чужого инвайт кода
        UserInviteCode.objects.create(
            user=user, invite_code=invite, invite_code_type="another"
        )

    @staticmethod
    def can_activate_invite_code(user):
        """Check if the user can activate another invite code."""
        return not UserInviteCode.objects.filter(
            user=user, invite_code_type="another"
        ).exists()

    @staticmethod
    def generate_invite_code():
        """Generate a unique 6-character invite code."""
        import random
        import string

        while True:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not InviteCode.objects.filter(code=code).exists():
                print("Invite code has been generated.")
                return code

    @staticmethod
    def generate_verification_code(phone):
        code = str(random.randint(1000, 9999))
        print(f"Sending SMS to {phone}: Your verification code is {code}")
        return code


class User(AbstractBaseUser):
    phone = models.CharField(max_length=12, unique=True)
    verification_code = models.CharField(max_length=4, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_authorized = models.BooleanField(default=False)
    invite_code = models.ForeignKey(InviteCode, on_delete=models.PROTECT)


    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def invited_users(self):
        """
        Возвращает список пользователей, которые использовали персональный инвайт-код текущего пользователя.
        """
        return User.objects.filter(
            id__in=UserInviteCode.objects.filter(
                invite_code=self.invite_code, invite_code_type="another"
            ).values_list("user", flat=True)
        )


class UserInviteCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invite_code = models.ForeignKey(InviteCode, on_delete=models.CASCADE)
    invite_code_type = models.CharField(
        max_length=7, choices=[("own", "Own"), ("another", "Another")]
    )

    class Meta:
        unique_together = ("user", "invite_code", "invite_code_type")
