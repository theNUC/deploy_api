from django.contrib import admin

from users.models import UserModel, ConfirmationModel


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username']


@admin.register(ConfirmationModel)
class ConfirmationModelAdmin(admin.ModelAdmin):
    list_display = ['code']