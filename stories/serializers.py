from rest_framework import serializers
from blogs.serializers import UserSerializer
from stories.models import StoryModel, StoryViewModel


class StorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    expire_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = StoryModel
        fields = '__all__'

class StoryViewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StoryViewModel
        fields = '__all__'