from django.shortcuts import render
from rest_framework import generics, status, permissions
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.custom_pagination import CustomPagination
from shared.utils import send_code_to_email
from users.models import UserModel, ConfirmationModel, CODE_VERIFIED, DONE, PHOTO, VIA_EMAIL
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from users.serializers import SignUpSerializer, LoginSerializer, \
    VerifyCodeSerializer, UpdateUserSerializer, UserAvatarSerializer, LogoutSerializer, UserModelSerializer


class UserListView(generics.ListAPIView):
    serializer_class = UserModelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return UserModel.objects.all()


class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.save()
        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyCodeView(generics.GenericAPIView):
    serializer_class = VerifyCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "Verification successful", "user": user.username})


class UpdateUserAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer
    http_method_names = ['put', 'patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(UpdateUserAPIView, self).update(request, *args, **kwargs)
        response = {
            'success': True,
            'message': "Your account has been updated.",
            'auth_status': self.request.user.auth_status,
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)

    def partial_update(self, request, *args, **kwargs):
        super(UpdateUserAPIView, self).partial_update(request, *args, **kwargs)
        response = {
            'success': True,
            'message': "Your account has been updated.",
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class UpdateUserAvatarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserAvatarSerializer(data=request.data)

        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            response = {
                "success": True,
                "message": "Updated successfully",
                "auth_status": "PHOTO"
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)
        else:
            response = {
                "success": False,
                "message": "Invalid request",
                "errors": serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh = self.request.data['refresh']
        token = RefreshToken(token=refresh)
        token.blacklist()
        response = {
            'success': True,
            'message': "Logged out successfully",
        }
        return Response(response, status=status.HTTP_200_OK)


class RefreshTokenView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer
