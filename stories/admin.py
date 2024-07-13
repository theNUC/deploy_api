from django.contrib import admin
from .models import StoryModel, StoryViewModel, StoryReactionModel, StoryReportModel

@admin.register(StoryModel)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'media', 'caption', 'created_at', 'expire_time', 'is_active')
    search_fields = ('user__username', 'caption')
    list_filter = ('is_active', 'expire_time')

@admin.register(StoryViewModel)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ('story', 'user', 'created_at')
    search_fields = ('story__id', 'user__username')
    list_filter = ('created_at',)

@admin.register(StoryReactionModel)
class StoryReactionAdmin(admin.ModelAdmin):
    list_display = ('story', 'user', 'reaction')
    search_fields = ('story__id', 'user__username')
    list_filter = ('reaction',)

@admin.register(StoryReportModel)
class StoryReportAdmin(admin.ModelAdmin):
    list_display = ('story', 'user', 'reason', 'created_at')
    search_fields = ('story__id', 'user__username', 'reason')
    list_filter = ('created_at',)