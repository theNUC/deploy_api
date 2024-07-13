from django.db import models
from shared.models import BaseModel
from users.models import UserModel

class StoryModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    media = models.FileField(upload_to='stories')
    caption = models.TextField(null=True, blank=True)
    expire_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.caption

    class Meta:
        ordering = ('-expire_time',)
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'

class StoryViewModel(BaseModel):
    story = models.ForeignKey(StoryModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.story.caption

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Story view'
        verbose_name_plural = 'Story views'

class StoryReactionModel(BaseModel):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('heart', 'Heart'),
    ]
    story = models.ForeignKey(StoryModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=50, choices=REACTION_CHOICES)

    def __str__(self):
        return self.story.caption

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Story reaction'
        verbose_name_plural = 'Story reactions'

class StoryReportModel(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    story = models.ForeignKey(StoryModel, on_delete=models.CASCADE)
    reason = models.TextField()

    def __str__(self):
        return self.reason

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Story report'
        verbose_name_plural = 'Story reports'