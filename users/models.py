import uuid
from datetime import timedelta
import random

from django.contrib.auth.models import AbstractUser, User
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import BaseModel
from django.db import models

VIA_EMAIL = "VIA_EMAIL"
ORDINARY_USER, MANAGER, ADMIN = "ORDINARY_USER", "MANAGER", "ADMIN"
NEW, CODE_VERIFIED, DONE, PHOTO = "NEW", "CODE_VERIFIED", "DONE", "PHOTO"


class UserModel(AbstractUser, BaseModel):
    AUTH_TYPES = (
        (VIA_EMAIL, VIA_EMAIL),
    )

    AUTH_STATUSES = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO, PHOTO)
    )

    USER_ROLES = (
        (ADMIN, ADMIN),
        (MANAGER, MANAGER),
        (ORDINARY_USER, ORDINARY_USER)
    )

    auth_type = models.CharField(max_length=128, choices=AUTH_TYPES, default=VIA_EMAIL)
    auth_status = models.CharField(max_length=128, choices=AUTH_STATUSES, default=NEW)
    user_role = models.CharField(max_length=128, choices=USER_ROLES, default=ORDINARY_USER)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    email = models.EmailField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.get_full_name()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def check_username(self):
        if not self.username:
            temp_username = f"instagram-{uuid.uuid4()}"
            while UserModel.objects.filter(username=temp_username).exists():
                self.check_username()
            self.username = temp_username

    def check_pass(self):
        if self.password:
            self.password = f"password-{uuid.uuid4()}"

    def check_email(self):
        self.email = str(self.email).lower()

    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def clean(self):
        self.check_username()
        self.check_pass()
        self.check_email()
        self.hashing_password()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.clean()
        super(UserModel, self).save(*args, **kwargs)

    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(1, 100) % 10) for _ in range(4)])
        ConfirmationModel.objects.create(
            code=code,
            user=self,
            verify_type=verify_type
        )
        return code

    def token(self):
        refresh = RefreshToken.for_user(self)
        response = {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }
        return response

    EMAIL_EXPIRATION_TIME = 4
    PHONE_EXPIRATION_TIME = 2

    class Meta:
        ordering = ('email',)
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class ConfirmationModel(BaseModel):
    objects = None
    VERIFY_TYPES = (
        (VIA_EMAIL, VIA_EMAIL),
    )

    verify_type = models.CharField(max_length=128, choices=VERIFY_TYPES, default=VIA_EMAIL)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='verification_codes')
    expiration_time = models.DateField()
    is_confirmed = models.BooleanField(default=False)
    code = models.CharField(max_length=4, default=0000)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.verify_type == VIA_EMAIL:
                self.expiration_time = timezone.now() + timedelta(minutes=EMAIL_EXPIRATION_TIME)
        super(ConfirmationModel, self).save(*args, **kwargs)
