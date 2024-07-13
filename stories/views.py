from datetime import timedelta
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from stories.models import StoryModel, StoryViewModel
from stories.serializers import StorySerializer, StoryViewSerializer


class StoryCreateAPIView(generics.CreateAPIView):
    queryset = StoryModel.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, expire_time=timezone.now() + timedelta(days=1), is_active=True)

class StoryViewCreateAPIView(generics.CreateAPIView):
    queryset = StoryViewModel.objects.all()
    serializer_class = StoryViewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        story_id = self.request.data['story']
        serializer.save(user=self.request.user, story_id=story_id)