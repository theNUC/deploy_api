from django.urls import path
from blogs.views import BlogListView, BlogCreateView, BlogUpdateAPIView, BlogDeleteAPIView, BlogDetailView, \
    UserBlogListView

app_name = 'users'

urlpatterns = [
    path('list/', BlogListView.as_view(), name='list'),
    path('myself/', UserBlogListView.as_view(), name='myself'),
    path('<int:pk>/detail/', BlogDetailView.as_view(), name='detail'),
    path('create/', BlogCreateView.as_view(), name='create'),
    path('<int:pk>/update/', BlogUpdateAPIView.as_view(), name='update'),
    path('<int:pk>/delete/', BlogDeleteAPIView.as_view(), name='delete'),
]