from rest_framework import viewsets, permissions, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from shared.custom_pagination import CustomPagination
from .models import Blog
from blogs.serializers import BlogsSerializer
from .permissions import IsoOwner


class BlogListView(generics.ListAPIView):
    serializer_class = BlogsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Blog.objects.all().order_by('-created_at')


class UserBlogListView(generics.ListAPIView):
    serializer_class = BlogsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Blog.objects.filter(user=self.request.user)


class BlogDetailView(generics.RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogsSerializer
    permission_classes = [IsAuthenticated]


class BlogCreateView(generics.CreateAPIView):
    serializer_class = BlogsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BlogUpdateAPIView(APIView):
    serializer_class = BlogsSerializer
    permission_classes = [IsAuthenticated, IsoOwner]

    def put(self, request, pk):
        post = Blog.objects.filter(pk=pk)
        if not post.exists():
            response = {
                "status": True,
                "message": "Post does not found"
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        serializer = BlogsSerializer(post.first(), data=request.data, context={'request': request})
        if serializer.is_valid():
            self.check_object_permissions(obj=post.first(), request=request)
            serializer.save()
            response = {
                "status": True,
                "message": "Successfully updated"

            }
            return Response(response, status=status.HTTP_202_ACCEPTED)
        else:
            response = {
                "status": True,
                "message": "Invalid request",
                "errors": serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class BlogDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsoOwner]

    def delete(self, request, pk):
        post = Blog.objects.filter(pk=pk)
        if not post.first():
            response = {
                "status": False,
                "message": "Post does not found"
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(post.first(), request)
        post.delete()
        response = {
            "status": True,
            "message": "Successfully deleted"

        }
        return Response(response, status=status.HTTP_202_ACCEPTED)
