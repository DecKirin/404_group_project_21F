# Create your models here.
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
# https://www.youtube.com/watch?v=GcqURKYfv00
class Post(models.Model):
    published = models.DateTimeField(default=timezone.now)  # ISO 8601 TIMESTAMP
    visibility = {
        (1, "PUBLIC"),
        (2, "FRIEND ONLY"),
        (3, "PRIVATE"),
        (4, "UNLISTED"),
    }
    # author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    id = models.CharField(primary_key=True, max_length=128,unique=True)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=500)
    contentType = models.CharField(max_length=500)
    content = models.TextField(blank=True)
    #updated = models.DateTimeField(auto_now_add=True)
    description = models.CharField(blank=True, max_length=500)
    image = models.URLField(blank=True)
    source = models.URLField(blank=True)
    origin = models.URLField(blank=True)
    type = "post"
    categories = models.JSONField(null=True)
    size = models.IntegerField()
    count = models.IntegerField()
    #comments = models.CharField(blank=True, max_length=500)
    unlisted = models.BooleanField()

    class Meta:
        ordering = ['-published']


class POSTLIKE(models.Model):