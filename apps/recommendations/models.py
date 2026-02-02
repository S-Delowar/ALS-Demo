from django.db import models
from django.conf import settings

class BaseContent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=1000)
    thumbnail = models.URLField(max_length=1000, blank=True, null=True)
    platform = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

class Article(BaseContent):
    author = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField(blank=True, null=True) # Assuming body might be large

class Course(BaseContent):
    course_objectives = models.JSONField(default=list, blank=True, null=True)
    instructor = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class Video(BaseContent):
    embed_url = models.URLField(max_length=1000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

class Book(BaseContent):
    author = models.CharField(max_length=255, blank=True, null=True)
    book_summary = models.TextField(blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
