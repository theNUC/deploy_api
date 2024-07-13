from django.utils import timezone
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from shared.utils import send_code_to_email, send_code_to_phone
from users.models import UserModel, ConfirmationModel, CODE_VERIFIED, VIA_EMAIL, VIA_PHONE
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.serializers import SignUpSerializer, UpdateUserSerializer, UpdateAvatarSerializer, LoginSerializer, LogoutSerializer, ForgetPasswordSerializer


class SignUpCreateAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = SignUpSerializer
    model = UserModel

class CodeVerifiedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = request.data.get('code')

        verification_code = ConfirmationModel.objects.filter(
            code=code, is_confirmed=False, user_id=user.id,
            expiration_time__gte=timezone.now()
        )
        if not verification_code.exists():
            response = {
                "success": False,
                "message": "Verification code is not valid"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        ConfirmationModel.objects.update(is_confirmed=True)

        user.auth_status = CODE_VERIFIED
        user.save()

        response = {
            "success": True,
            "message": "You are successfully verified",
            "auth_status": user.auth_status
        }
        return Response(response, status=status.HTTP_200_OK)

class ResendVerifyCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user

        verification_code = ConfirmationModel.objects.filter(is_confirmed=False, user_id=user.id,
                                                             expiration_time__gte=timezone.now())
        if verification_code.exists():
            response = {
                "success": False,
                "message": "You have active verification code"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        self.send_code()
        response = {
            "success": True,
            "message": "New code is sent"
        }
        return Response(response, status=status.HTTP_200_OK)

    def send_code(self):
        user = self.request.user
        new_code = user.create_verify_code(verify_type=user.auth_type)
        if user.auth_type == VIA_EMAIL:
            send_code_to_email(user.email, new_code)
        else:
            send_code_to_phone(user.phone_number, new_code)

class UserUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer
    http_method_names = ['put', 'patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(UserUpdateAPIView, self).update(request, *args, **kwargs)
        response = {
            "success": True,
            "message": "User updated successfully",
            "auth_status": self.request.user.auth_status
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)

    def partial_update(self, request, *args, **kwargs):
        super(UserUpdateAPIView, self).partial_update(request, *args, **kwargs)
        response = {
            "success": True,
            "message": "User updated successfully"
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)

class UpdateAvatarAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateAvatarSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            serializer.update(user, serializer.validated_data)
            response = {
                "success": True,
                "message": "User avatar is updated successfully"
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)

        else:
            response = {
                "success": False,
                "message": "Invalid data"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh = self.request.data['refresh']
        token = RefreshToken(token=refresh)
        token.blacklist()
        response = {
            "success": True,
            "message": "User logged out successfully"
        }
        return Response(response, status=status.HTTP_200_OK)

class RefreshTokenView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer


class ForgetPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = ForgetPasswordSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            email_phone_number = serializer.validated_data.get('email_phone_number')
            user = serializer.validated_data.get("user")

            if email_phone_number.endswith('@gmail.com'):
                new_code = user.create_verify_code(VIA_EMAIL)
                send_code_to_email(user.email, new_code)
            else:
                new_code = user.create_verify_code(VIA_PHONE)
                send_code_to_phone(user.phone_number, new_code)
            response = {
                "success": True,
                "message": "Code is sent to user",
                "access_token": user.token()['access_token']
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                "success": False,
                "message": "Invalid data"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)