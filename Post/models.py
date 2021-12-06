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
    type = 'like'
    published = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name='post_like', on_delete=models.CASCADE, null=True, blank=True)
    who_like = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE, blank=True, null=True)

    author = models.JSONField(default=dict, max_length=2000,blank=False)
    object = models.URLField(max_length=200)
    summary = models.CharField(max_length=120)

    class Meta:
        db_table = 'likes'
    '''
    def save(self, *args, **kwargs):
        try:
            name = self.author.displayname
        except Exception:
            name = self.author.username

        self.summary = '{} likes your post'.format(name)
        super(PostLike, self).save(*args, **kwargs)

    def __str__(self):
        try:
            name = self.author.displayname
        except Exception:
            name = self.author.username
        return '{} likes your post'.format(name)
    '''

class PostComment(models.Model):
    type = 'comment'
    id_comment = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE, null=False)
    # the author make this comment
    author_comment = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE, default=1, blank=True, null=True)  # TODO: edit default value
    author = models.JSONField(default=dict, max_length=2000,null=True,blank=True)
    comment = models.TextField()
    published = models.DateTimeField(auto_now_add=True)
    url = models.URLField(editable=False, default="")
    api_url = models.URLField(editable=False,default="")
    # contentType = models.CharField(default="text/plain")
    class Meta:
        ordering = ('published',)
        db_table = 'postcomment'
    '''
    def __str__(self):
        return 'Comment by {} on {} with content{}'.format(self.author.username, self.post.title,
                                                        self.comment)
    '''