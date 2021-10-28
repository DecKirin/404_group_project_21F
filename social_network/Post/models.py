# Create your models here.
from django.db import models
#from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from Author.models import User,Post
# https://www.youtube.com/watch?v=GcqURKYfv00
ContentType = [
    ('text/markdown','text/markdown'),
    ('text/plain','text/plain'),
    ('application/base64','application/base64'),
    ('image/png;base64','image/png;base64'),
    ('image/jpeg;base64','image/jpeg;base64')
]
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
    contentType = models.TextField(null=False, choices=ContentType, default='text/plain')
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
    #comments = models.CharFieled(blank=True, max_length=500)
    unlisted = models.BooleanField()

    class Meta:
        ordering = ['-published']

    def visibility_


class Postlike(models.Model):
    published  = models.DateTimeField(auto_now_add=True)
    id_like = models.UUIDField(primary_key=True,default=uuid.uuid4,unique=True)
    post_id = models.ForeignKey(Post, related_name='post_like', on_delete=models.CASCADE, null=True)
    give_like_author =  models.ForeignKey(User, on_delete=models.CASCADE)
    
class Postcomment(models.Model):
    id_comment = models.UUIDField(primary_key=True,default=uuid.uuid4,unique=True)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE, null=False)
    # the author make this comment
    author_comment = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE, null=False, default=1)  # TODO: edit default value
    name = models.CharField(max_length=80)
    comment = models.TextField()
    published = models.DateTimeField(auto_now_add=True)
    url_comment = models.URLField()
    class Meta:
        ordering = ('published',)

    def __str__(self):
        return 'Comment by {} on {} with content{}'.format(self.name, self.post,comment)