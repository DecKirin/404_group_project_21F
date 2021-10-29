# Create your models here.
import uuid

from django.db import models
# from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from Author.models import User, Post
import uuid

# https://www.youtube.com/watch?v=GcqURKYfv00
ContentType = [
    ('text/markdown', 'text/markdown'),
    ('text/plain', 'text/plain'),
    ('application/base64', 'application/base64'),
    ('image/png;base64', 'image/png;base64'),
    ('image/jpeg;base64', 'image/jpeg;base64')
]


class PostLike(models.Model):
    published = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name='post_like', on_delete=models.CASCADE, null=True)
    who_like = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)

    class Meta:
        db_table = 'likes'


class PostComment(models.Model):
    id_comment = models.UUIDField(primary_key=True,default=uuid.uuid4,unique=True)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE, null=False)
    # the author make this comment
    author_comment = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE, null=False, default=1)  # TODO: edit default value
    comment_content = models.TextField()
    published = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('published',)
        db_table = 'postcomment'

    def __str__(self):
        return 'Comment by {} on {} with content{}'.format( author_comment.username, post.title,comment_content)
