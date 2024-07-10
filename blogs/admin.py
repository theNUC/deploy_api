from django.contrib import admin
from django.contrib.admin import ModelAdmin

from blogs.models import Blog


@admin.register(Blog)
class BlogModelAdmin(ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'created_at')
    list_filter = ('created_at',)
