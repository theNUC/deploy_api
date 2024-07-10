from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext as _
from rest_framework import serializers
import re
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from shared.utils import send_code_to_email
from users.models import UserModel, VIA_EMAIL, PHOTO, DONE, ConfirmationModel, CODE_VERIFIED

from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import UserModel


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_role']


class SignUpSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name', 'username']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_username(self, value):
        if UserModel.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = UserModel.objects.create_user(
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            username=validated_data.get('username'),
        )

        refresh = RefreshToken.for_user(user)
        verify_code = user.create_verify_code(VIA_EMAIL)

        send_code_to_email(user.email, verify_code)

        return {
            'user': user.pk,  # Return user's primary key instead of the object itself
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def to_representation(self, instance):
        # Customize the representation as needed
        return {
            'user': instance['user'],  # Return user's primary key instead of the object itself
            'refresh': instance['refresh'],
            'access': instance['access'],
        }

    def send_code_to_email(email, code):
        send_mail(
            'Verification Code',
            f'Your verification code is {code}',
            'sotvoldiyevazamat193@gmail.com',
            [email],
            fail_silently=False,
        )


class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate_code(self, value):
        if not ConfirmationModel.objects.filter(code=value, is_confirmed=False).exists():
            raise serializers.ValidationError("Invalid or expired code.")
        return value

    def save(self, **kwargs):
        code = self.validated_data['code']
        confirmation = ConfirmationModel.objects.get(code=code)
        confirmation.is_confirmed = True
        confirmation.save()
        confirmation.user.auth_status = CODE_VERIFIED
        confirmation.user.save()
        return confirmation.user


class UpdateUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, write_only=True, required=True)
    last_name = serializers.CharField(max_length=255, write_only=True, required=True)
    username = serializers.CharField(max_length=255, write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)

    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'username', 'email']

    def validate_username(self, username):
        if UserModel.objects.filter(username=username).exists():
            response = {
                "success": False,
                "message": "Username is already gotten"
            }
            raise serializers.ValidationError(response)
        return username

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        userinput = attrs.get('userinput')
        password = attrs.get('password')

        if userinput.endswith('@gmail.com'):
            user = UserModel.objects.filter(email=userinput).first()
        elif userinput.startswith('+'):
            user = UserModel.objects.filter(phone_number=userinput).first()
        else:
            user = UserModel.objects.filter(username=userinput).first()

        if user is None:
            raise serializers.ValidationError("Username or Password is invalid")

        auth_user = authenticate(username=user.username, password=password)
        if auth_user is None:
            raise serializers.ValidationError("Username or Password is invalid")

        refresh = RefreshToken.for_user(auth_user)
        response = {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
        return response



class UserAvatarSerializer(serializers.Serializer):
    avatar = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


def validate_username(value):
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError(
            'Foydalanuvchi nomi faqat harflar, raqamlar va tag chiziq (_) dan iborat bo\'lishi mumkin.')


def validate_password(value):
    if len(value) < 8:
        raise ValidationError('Parol kamida 8 ta belgidan iborat bo\'lishi kerak.')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Parolda kamida bitta katta harf bo\'lishi kerak.')
    if not re.search(r'[a-z]', value):
        raise ValidationError('Parolda kamida bitta kichik harf bo\'lishi kerak.')
    if not re.search(r'[0-9]', value):
        raise ValidationError('Parolda kamida bitta raqam bo\'lishi kerak.')
    if not re.search(r'[\W_]', value):
        raise ValidationError('Parolda kamida bitta maxsus belgi bo\'lishi kerak.')


def validate_email(email):
    validator = EmailValidator()
    try:
        validator(email)
    except ValidationError as e:
        raise ValidationError("Invalid email address.") from e


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
