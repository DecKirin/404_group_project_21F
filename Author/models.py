from django.db import models
from django.contrib.auth.models import User, AbstractUser
from friends.models import FriendRequest
import uuid
import base64
from django.utils import timezone

# for slug and unique id
# https://www.youtube.com/watch?v=dJqWO-lSgWY
from social_network import settings


class RegisterControl(models.Model):
    free_registration = models.BooleanField(default=True)

    def __str__(self):
        return 'New User Confirmation Required'


class User(AbstractUser):
    type = 'author'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    # id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    profile_image = models.TextField()
    email = models.CharField(max_length=20, unique=True)
    # url path of user profile images
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    u_phone = models.CharField(max_length=20, verbose_name='phone_number', default='', blank=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    github = models.CharField(max_length=100, blank=True)
    url = models.URLField()
    host = models.URLField()
    api_url = models.URLField()


    class Meta:
        db_table = 'sys_user_info'
        verbose_name = 'Author'
        verbose_name_plural = verbose_name


ContentType = [
    ('text/markdown', 'text/markdown'),
    ('text/plain', 'text/plain'),
    ('application/base64', 'application/base64'),
    ('image/png;base64', 'image/png;base64'),
    ('image/jpeg;base64', 'image/jpeg;base64')
]


class Post(models.Model):
    visibility_choices = (
        (1, "PUBLIC"),
        (2, "FRIEND ONLY"),
        (3, "PRIVATE"),
        (4, "UNLISTED"),
    )
    type = 'post'
    title = models.CharField(max_length=128)
    id = models.CharField(max_length=128, primary_key=True)
    url = models.URLField(editable=True)
    api_url = models.URLField(editable=True)
    source = models.URLField(blank=True)
    origin = models.URLField(blank=True)
    description = models.CharField(max_length=500, blank=True)
    contentType = models.TextField(null=False, choices=ContentType, default='text/plain')
    content = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE, null=False,
                               default=1)  # TODO: edit default value
    # categories = models.JSONField(null=True)
    categories = models.CharField(max_length=500, blank=True)
    # author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    count = models.IntegerField(default=0)
    # comments = models.CharField(max_length=500,blank=True)
    published = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    visibility = models.SmallIntegerField(default=1, choices=visibility_choices)
    unlisted = models.BooleanField(default=False)
    #image_file = models.ImageField(upload_to='post_image')
    select_user = models.CharField(max_length=20, blank=True)
    image = models.TextField()

    class Meta:
        ordering = ('published',)
        db_table = 'posts'




class Inbox(models.Model):
    type = "inbox"
    author = models.ForeignKey(User, related_name='inbox', on_delete=models.CASCADE, null=False)
    #items = models.CharField(blank=True, max_length=200)
    items = models.JSONField(default=list, max_length=10000)
    #requests = models.ForeignKey(FriendRequest, related_name='inbox', on_delete=models.CASCADE, null=False, blank=True)
    #created = models.DateTimeField(auto_now_add=True)
    # Todo:Fetch Posts


'''add external host server(node)'''


class Node(models.Model):
    host = models.URLField(default="", primary_key=True, unique=True)
    allow_connection = models.BooleanField(default=True)
    def get_host(self):
        return self.host
