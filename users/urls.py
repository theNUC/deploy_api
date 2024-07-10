from django.urls import path
from users.views import LoginView, SignUpView, VerifyCodeView, UpdateUserAPIView, UpdateUserAvatarAPIView, LogoutView, \
    RefreshTokenView, UserListView

app_name = 'users'

urlpatterns = [
    path('register/', SignUpView.as_view(), name='user-register'),
    path('verify/', VerifyCodeView.as_view(), name='user-verify'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('update/', UpdateUserAPIView.as_view(), name='update'),
    path('avatar-update/', UpdateUserAvatarAPIView.as_view(), name='avatar'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),

    path('myself/', UserListView.as_view(), name='user-list'),
]