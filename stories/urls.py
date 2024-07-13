from django.urls import path
from stories.views import StoryCreateAPIView, StoryViewCreateAPIView

app_name = 'stories'
urlpatterns = [
    path('upload/', StoryCreateAPIView.as_view(), name='upload'),
    path('view/', StoryViewCreateAPIView.as_view(), name='view-create'),
]