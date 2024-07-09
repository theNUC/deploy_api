from rest_framework import serializers
from blogs.models import Blog
from users.models import UserModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['uuid', 'avatar', 'username']


class BlogsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']
